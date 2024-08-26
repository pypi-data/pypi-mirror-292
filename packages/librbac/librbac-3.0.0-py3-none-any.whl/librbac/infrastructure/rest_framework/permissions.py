from typing import TYPE_CHECKING

from rest_framework.permissions import BasePermission


if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.viewsets import GenericViewSet


class HasAccess(BasePermission):

    def has_permission(self, request: 'Request', view: 'GenericViewSet'):
        """Проверяет наличие доступа."""
        from librbac import rbac

        return rbac.has_access(view, request, request.user)
