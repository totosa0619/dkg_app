from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.models import Group
from rest_framework import status, views, permissions, authentication, generics
from rest_framework.response import Response
from core.permissions import CsrfExemptSessionAuthentication, IsAuthenticatedOrReadOnly, IsAdminUserOrReadOnly
import logging
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.urls import reverse
from urllib.parse import quote_plus, urlencode
from django.contrib.auth import get_user_model

from diagrams.models import (
    DiagramFrame,
    DeployedDashboards
)

from rest_framework.authtoken.models import Token
logger = logging.getLogger("django")

User = get_user_model()


oauth = OAuth()


oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)

def home_redirect(request):
    if request.user.is_authenticated:
        return redirect('/admin-panel/')

    return redirect('login')


def login_page(request):
    nextPage = request.GET.get('next')
    if not nextPage or nextPage == request.path or '/login' in nextPage:
        nextPage = '/'

    if request.user.is_authenticated:
        return HttpResponseRedirect(nextPage)

    args = dict()
    form = AuthenticationForm(request)

    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user )
            token, created = Token.objects.get_or_create(user=user)
            response = HttpResponseRedirect(nextPage)
            response.set_cookie('auth_token', token.key)
            return response

    args['form'] = form
    args['next'] = nextPage
    context= {
        'next_page':nextPage
    }
    return render(request, 'login.html', args)


@require_http_methods(["POST"])
@csrf_exempt
def logout_view(request):
    logout(request)
    request.session.clear()
    return JsonResponse(data={})






def login_with_google(request):
    # Get the next parameter from the request
    next_page = request.GET.get('next', '')
    
    # Build the callback URL and include the next parameter if it exists
    callback_url = request.build_absolute_uri(reverse("callback"))
    if next_page:
        callback_url = f"{callback_url}?{urlencode({'next': next_page})}"
    
    return oauth.auth0.authorize_redirect(
        request,
        callback_url,
        connection='google-oauth2'
    )




def auth0_callback(request, *args, **kwargs):
    try:
        token = oauth.auth0.authorize_access_token(request)
        target_group = "all-charts-access" # If user is dkv then add to this group
        group, _ = Group.objects.get_or_create(name=target_group)
        # get next page from request parameters
        next_page = request.GET.get('next')
        if not next_page:
            next_page = '/'
            
        request.session["user"] = token
        email = token.get("userinfo").get("email")
        user = User.objects.filter(email=email).first()
        if not user:
            user = User.objects.create(
                username=token.get("userinfo").get("nickname"),
                email=token.get("userinfo").get("email"),
                first_name=token.get("userinfo").get("given_name"),
                last_name=token.get("userinfo").get("family_name"),
                
            )
        if email.endswith("@dkv.global"):
            user.is_staff = True
            user.groups.add(group)
            user.save()
        login(request, user)
        response = HttpResponseRedirect(next_page)
        auth_token, created = Token.objects.get_or_create(user=user)
        response.set_cookie('auth_token', auth_token.key)
        # add token here
        return response
    
    except Exception as e:
        # Log the error to a file
        logger.error(e)
        
        # Optionally, redirect to an error page or handle the error appropriately
        return redirect('/')


