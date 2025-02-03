from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from core.models import UserFile
from core.permissions import CsrfExemptSessionAuthentication, IsAuthenticatedOrReadOnly
from rest_framework import permissions
from core.utils import JsonCORSResponse
from storage import blob
from rest_framework import status



from core.serializers import UserAccountDetailsSerializer

class UserAccountDetailsView(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication, TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserAccountDetailsSerializer(user)
        return Response(serializer.data)



cl = blob.new_client()


class FilesView(APIView):
    authentication_classes = [CsrfExemptSessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonCORSResponse({'message': 'You don\'t have permission to upload files'}, status=403)

        data = request.FILES.getlist('files')
        response = []
        for f in data:
            r = UserFile.objects.create(
                user=user,
                source=f,
            )
            response.append({"url": r.source.url, "id": r.id, "name": f.name})

        return JsonCORSResponse(response, safe=False, status=200)


@csrf_exempt
def files(request):
    user = request.user
    if not user.is_authenticated:
        return JsonCORSResponse({'message': 'You don\'t have permission to upload files'}, status=403)

    if request.method != 'POST':
        return JsonCORSResponse({'message': 'only POST supported'}, status=405)

    data = request.FILES.getlist('files')
    response = []
    for f in data:
        r = UserFile.objects.create(
            user=user,
            source=f,
        )
        response.append({"url": r.source.url, "id": r.id, "name": f.name})

    return JsonCORSResponse(response, safe=False, status=200)
