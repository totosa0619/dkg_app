from .settings import *

MIDDLEWARE = [
                 "corsheaders.middleware.CorsMiddleware",
             ] + MIDDLEWARE
# INSTALLED_APPS += ["corsheaders"]
STATICFILES_DIRS = []
ALLOWED_HOSTS += ['127.0.0.1', 'localhost']
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

LOGGING = {}

