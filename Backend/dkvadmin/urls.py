from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from dkvadmin.views import (home_redirect, login_page, logout_view, 
                            auth0_callback, login_with_google)

# Swagger schema view setup
schema_view = get_schema_view(
    openapi.Info(
        title="Your API Documentation",
        default_version='v1',
        description="API documentation for your Django project",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin-backend/', admin.site.urls),
    path('login/', login_page, name='login'),
    path('api/auth0_callback/', auth0_callback, name='callback'),
    path('login-auth0/', login_with_google, name='auth0-login'),
    path('logout/', logout_view, name='logout'),
    path('api/', include("core.urls")),
    path('api/', include("diagrams.urls")),
    path('statistics', TemplateView.as_view(template_name="stats.html")),
    path('', home_redirect, name='home'),

    # Swagger UI
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)