from rest_framework.permissions import BasePermission
from autentificacion.models import Usuario

USER_SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH')
SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS')
PROJECT_SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS', 'PUT', 'PATCH', 'DELETE')


def isAdminUserOrAnonymousUser(user):
    if user.is_anonymous:
        return False
    return user.tipo == 'A'


class IsSuperAdminOrIsSelfProfile(BasePermission):
    def has_permission(self, request, view):
        usuario = Usuario.objects.get(pk=view.kwargs['pk'])
        return request.user.is_superuser or usuario.id == request.user.id

    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser or obj.id == request.user.id


class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return isAdminUserOrAnonymousUser(request.user)

    def has_object_permission(self, request, view, obj):
        return isAdminUserOrAnonymousUser(request.user)
