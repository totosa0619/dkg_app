from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class IsAuthenticatedOrReadOnly(IsAuthenticated):
    SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']

    def has_permission(self, request, view):
        if (request.method in self.SAFE_METHODS or
                request.user and
                request.user.is_authenticated):
            return True
        return False


class IsAdminUserOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        if request.method in self.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_superuser) or bool(request.user and request.user.is_staff) 