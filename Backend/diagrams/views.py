from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from django.db.models import Q
from rest_framework.pagination import PageNumberPagination
from core.permissions import CsrfExemptSessionAuthentication, IsAuthenticatedOrReadOnly
from core.utils import JsonCORSResponse
from diagrams.models import Category, DiagramFrame, ITToolProduct, RawDataBlock, PlatformAccess, DiagramLogs
import json
import requests
from diagrams.serializers import (
    CategorySerializer,
    ITToolProductSerializer,
    ListDiagramFrameSerializer,
    CreateUpdateDiagramFrameSerializer,
    ViewUpdateDiagramFrameSerializer,
    CreateUpdateITToolProductSerializer,
)



def request_yahoo_stock_history(ticker):
    url = f"https://yahoo-finance127.p.rapidapi.com/historic/{ticker}/1mo/5y"

    headers = {
        "X-RapidAPI-Key": "90d613dc06msh8947204cf1516a4p121d52jsn2663910f0714",
        "X-RapidAPI-Host": "yahoo-finance127.p.rapidapi.com"
    }
    print(f'--> request_yahoo_stock_history: send request to {url}')
    response = requests.get(url, headers=headers)
    result = response.json()
    if not response.ok:
        print(f'--> {result["message"]}')
        return None

    if 'message' in result and 'meta' not in result:
        print(f'--> {result["message"]}')
        return None
    return result


def get_user_and_access(request_obj):
    usr = None
    access = False
    if request_obj.user.is_authenticated:
        usr = request_obj.user

    if request_obj.META['SERVER_PORT'] == '8010' or usr:
        access = True
    return usr, access


@csrf_exempt
def custom_diagram_api_file(request, diagram_slug=None):
    usr, has_access = get_user_and_access(request)
    if not has_access:
        return JsonCORSResponse({'message': 'You don\'t have permission to upload files'}, status=403)

    if isinstance(diagram_slug, str) and diagram_slug.strip() == '':
        diagram_slug = None

    if not request.FILES or 'file' not in request.FILES:
        return JsonCORSResponse({'message': 'No input file'}, status=400)

    folder_prefix = 'iframe-diagrams-files/'
    if diagram_slug:
        folder_prefix = f'iframe-diagrams-files/{diagram_slug}/'

    file = request.FILES['file']
    initial_file_path = folder_prefix + file.name
    result_file_path = default_storage.get_available_name(initial_file_path)
    default_storage.save(result_file_path, file)
    return JsonCORSResponse({'url': settings.MEDIA_URL + result_file_path})


def raw_stock_history_data(request, ticker):
    # get raw json data with stock history saved in RawDataBlock
    ticker = ticker.lower().strip()
    datablock = RawDataBlock.objects.filter(slug=ticker, source_name='yahoo finance').first()
    if not datablock:
        datablock = RawDataBlock.objects.create(slug=ticker, source_name='yahoo finance')

    print('--> raw_stock_history_data: datablock.id = ', datablock.id)
    if not datablock.data:
        raw_data = request_yahoo_stock_history(datablock.slug)
        if raw_data:
            datablock.data = json.dumps(raw_data)
            datablock.active = True
        else:
            datablock.active = False

        datablock.save()

    # if not datablock.active:
    #    return JsonCORSResponse({'message': 'ticker not found'}, status=400)

    result = {}
    try:
        result = json.loads(datablock.data)
    except Exception as e:
        return JsonCORSResponse({'message': f'{e.__class__.__name__} - {str(e)}'}, status=400)

    return JsonCORSResponse(result)


# from django.utils.decorators import method_decorator

# @method_decorator(csrf_exempt, name='dispatch')
class DiagramsListAPIView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        # TODO
        # Ensure the session is modified and will be saved
        user = request.user
        diagram_type = request.GET.get('diagram_type', None)
        
        #! NEEDS ATTENTION
        # Start by selecting all diagrams that the current user owns or is marked as "accessible_by" the current user
        diags = DiagramFrame.objects.filter(Q(user=user) | Q(accessible_by=None) | Q(accessible_by=user) ) # if accessible_by is empty means the diagram is public
        
        # If the current user is not an admin, filter the queryset to only include the diagrams that are owned by the user or accessible by the user
        if not user.is_staff:
            diags = DiagramFrame.objects.filter(
                Q(user=user) | Q(accessible_by=user)
            )
        
        # If a diagram type is specified, filter the queryset to only include diagrams of that type
        if diagram_type:
            diags = diags.filter(diagram_type=diagram_type)
        
        serializer = ListDiagramFrameSerializer(diags, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = CreateUpdateDiagramFrameSerializer(data=request.data, context={'user': request.user, 'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





class DiagramView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    queryset = DiagramFrame
    serializer_class = ViewUpdateDiagramFrameSerializer
    lookup_field = "slug"
    
    def retrieve(self, request, *args, **kwargs):
        user = request.user
        diagram: DiagramFrame = self.get_object()
        pass_key = request.session.get(f"passKey_{diagram.slug}", None)

        # If the diagram is not protected, allow access
        if not diagram.is_protected:
            return super().retrieve(request, *args, **kwargs)

        # If the user is not authenticated, prompt for login
        if  not user.is_authenticated:
            return Response({"is_protected": True}, status=status.HTTP_206_PARTIAL_CONTENT)

        # If the user is the owner, allow access
        if diagram.user == user:
            return super().retrieve(request, *args, **kwargs)
        
        if user.is_staff or user.is_superuser:
            return super().retrieve(request, *args, **kwargs)

        # If restricted access is enabled, check if the user has access
        if diagram.accessible_by.exists() and not diagram.accessible_by.filter(id=user.id).exists():
            return Response({"restricted_access": "You do not have access to this diagram."}, status=status.HTTP_206_PARTIAL_CONTENT)

        # If the diagram is protected and no passkey is provided, prompt for a password
        if not pass_key:
            return Response({"password_required": True}, status=status.HTTP_206_PARTIAL_CONTENT)

        # If the provided passkey is incorrect, return an unauthorized response
        if not diagram.check_passkey(pass_key):
            return Response({"password": "Unauthorized access"}, status=status.HTTP_401_UNAUTHORIZED)

        # If all conditions are met, allow access
        return super().retrieve(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['user'] = self.request.user
        context["request"] = self.request
        return context




class VerifyDiagramPasskey(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    def post(self, request, slug,format=None):
        passkey = request.data.get("passkey", None)
        obj = DiagramFrame.objects.filter(slug=slug).first()
        
        if not obj:
            return Response({"message": "Object not found"}, status=status.HTTP_404_NOT_FOUND)
        
        if not passkey:
            return Response({"message": "passkey is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not obj.check_passkey(passkey):
            return Response({"message": "Invalid passkey"}, status=status.HTTP_400_BAD_REQUEST)
        
        self._save_key_to_session(request, passkey, obj)
        return Response({"message": "Passkey valid"}, status=status.HTTP_200_OK)

    def _save_key_to_session(self, request, pass_key, obj):
        request.session[f"passKey_{obj.slug}"] = pass_key
        request.session.modified = True


@csrf_exempt
def diagrams_all(request, diagram_slug=None):
    diags = DiagramFrame.objects.all()
    result = []
    for diag in diags:
        result.append({
            'id': diag.id, 'title': diag.title, 'slug': diag.slug, 'diagram_type': diag.diagram_type,
            'updated_user_name': diag.updated_user_name,
            'updated_time': diag.updated_time.strftime('%Y-%m-%d %H:%M')
        })
    return JsonCORSResponse(result, safe=False)




class RequestPlatformAccess(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def post(self, request):
        """
        Handle POST request to request platform access for the user.
        
        Returns:
            JsonCORSResponse: Response with the result of the platform access request
        """
        user = request.user
        access_level = "view_platform" # Default anyways
        if not user:
            return JsonCORSResponse({'message': 'User not found'}, status=404)
        if not user.is_active:
            return JsonCORSResponse({'message': 'User not active'}, status=404)
        
        platform_request = PlatformAccess.objects.filter(user=user, access_level=access_level)
        if platform_request and platform_request.filter(status="approved").exists():
            return JsonCORSResponse({'message': 'User already has access'}, status=400)

        if platform_request and platform_request.filter(status="pending").exists():
            return JsonCORSResponse({'message': 'User already has pending request'}, status=400)
        
        # if has rejected request, then can request again
        if not platform_request:
            platform_request = PlatformAccess(user=user, access_level=access_level)
            platform_request.save()
            
        result = {
            'id': platform_request.id,
            'user': user.username,
            'email': user.email,
            'access_level': access_level,
            'status': 'pending',
            'created': platform_request.created.strftime('%Y-%m-%d %H:%M'),
            'message': 'Platform access request sent'
        }
        return JsonCORSResponse(result)
    
    
    def get(self, request):
        """
        Handle GET request to retrieve platform access information for the user.
            
        Returns:
            JsonCORSResponse: Response with the platform access information
        """
        user = request.user
        if not user:
            return JsonCORSResponse({'message': 'User not found'}, status=404)
        platform_request = PlatformAccess.objects.filter(user=user).first()
        if not platform_request:
            return JsonCORSResponse({'message': 'User has no access', 'req_status': None}, status=403)
        if platform_request.status == 'rejected':
            return JsonCORSResponse({'message': 'User has rejected access', 'req_status':platform_request.status}, status=403)
        if platform_request.status == 'pending':
            return JsonCORSResponse({'message': 'User has pending request', 'req_status':platform_request.status}, status=403)
        
        result = {
            'id': platform_request.id,
            'user': user.username,
            'email': user.email,
            'access_level': platform_request.access_level,
            'status': platform_request.status,
            'created': platform_request.created.strftime('%Y-%m-%d %H:%M')
        }
        return JsonCORSResponse(result, safe=False, status=200)
    
    
    
class CustomPagination(PageNumberPagination):
    page_size = 10  # Adjust this to set the number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100

# CRUD for Category
class CategoryListCreateAPIView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticated]  

class CategoryRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

# CRUD for ITToolProduct
class ITToolProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = ITToolProduct.objects.all()
    pagination_class = CustomPagination
    serializer_class = ITToolProductSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateUpdateITToolProductSerializer
        return ITToolProductSerializer

class ITToolProductRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ITToolProduct.objects.all()
    serializer_class = CreateUpdateITToolProductSerializer
    permission_classes = [IsAuthenticated]
    


# !TO BE REMOVEd
        # pass_key = request.GET.get("passkey", None)
        # user = request.user
        # diagram: DiagramFrame = self.get_object()
        
        # if request.session.get("passKey", None):
        #     pass_key = request.session.get("passKey")
            
        
        # if not diagram.is_protected:
        #     return super().retrieve(request, *args, **kwargs)
        
        # if not user:
        #     return self._deny_access("Missing user")
        
        # if diagram.user == user:
        #     return super().retrieve(request, *args, **kwargs)
        
        # if (
        #     diagram.accessible_by.exists()
        #     and request.user not in diagram.accessible_by.all()
        # ):
        #     return self._deny_access("Unauthorized access")
        
        # if not pass_key:
        #     return self._deny_access("Missing passkey")
            
        # if diagram.is_protected and not diagram.check_passkey(pass_key):
        #     return self._deny_access("Unauthorized access")
        
        # request.session["passKey"] = pass_key
        # request.session.modified = True
        
        
        # def _deny_access(self, message):
        # return Response({"message": message}, status=status.HTTP_403_FORBIDDEN)