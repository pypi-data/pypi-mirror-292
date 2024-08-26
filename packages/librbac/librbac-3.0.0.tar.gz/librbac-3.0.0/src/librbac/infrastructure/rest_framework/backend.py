from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import final

from librbac.domain.interfaces.backend import AbstractBackend
from librbac.domain.permissions import Permission


if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.viewsets import GenericViewSet

    from librbac.domain.permissions import CollectedPermissions
    from librbac.domain.permissions import PermissionRuleMapping
    from librbac.domain.permissions import PermissionsGraph
    from librbac.domain.permissions import TUser
    from librbac.infrastructure.django.domain import DRFCollectedPermissions
    from librbac.infrastructure.django.domain import ViewSetRegistry

class BaseRestFrameworkBackend(AbstractBackend):

    """База для бэкендов контроля доступа для Rest Framework."""

    _permissions_graph: 'PermissionsGraph'
    _permission_rule_mapping: 'PermissionRuleMapping'

    def __init__(self, collected_permissions: 'CollectedPermissions'):
        super().__init__(collected_permissions)
        self._permissions_graph = collected_permissions.graph
        self._permission_rule_mapping = collected_permissions.rule_mapping

    @abstractmethod
    def _need_check_access(self, viewset: 'GenericViewSet') -> bool:
        """Возвращает True, если ``viewset`` предполагает проверку доступа."""

    def _get_user_permissions(self, user: 'TUser') -> tuple['Permission', ...]:
        """Возвращает все доступные пользователю разрешения."""
        return getattr(user, 'rbac_permissions', ())

    @abstractmethod
    def _get_viewset_permissions(
        self,
        viewset: 'GenericViewSet | RBACMixin'
    ) -> tuple[Permission, ...]:
        """Возвращает имена разрешений ViewSet'а."""

    def _check_permission(
        self,
        permission: 'Permission',
        viewset: 'GenericViewSet | RBACMixin',
        request: 'Request',
        user: 'TUser',
    ) -> bool | None:
        """Проверяет возможность предоставления доступа.

        Если для указанного разрешения определены правила, то выполняет их проверку.
        """
        if permission in self._permission_rule_mapping:
            for handler in self._permission_rule_mapping[permission]:
                if handler(viewset, request, user):
                    result = True
                    break
            else:
                result = None
        else:
            # Для разрешения не определено правил, значит достаточно
            # только наличия у пользователя разрешения как такового.
            result = True

        return result

    def has_access(self, context: 'GenericViewSet', request: 'Request', user: 'TUser') -> bool:
        if not self._need_check_access(context):
            return True

        return any(
            self._check_permission(permission, context, request, user)
            for permission in self._get_user_permissions(user)
            if permission in self._get_viewset_permissions(context)
        )

    def has_perm(self, user: 'TUser', permission: Permission) -> bool:
        return permission in self._get_user_permissions(user)


@final
class RestFrameworkBackend(BaseRestFrameworkBackend):
    """Бэкенд контроля доступа специфичный для Rest Framework."""

    _viewset_registry: 'ViewSetRegistry'

    def __init__(self, collected_permissions: 'DRFCollectedPermissions'):
        super().__init__(collected_permissions)
        self._viewset_registry = collected_permissions.viewset_registry

    def _need_check_access(self, viewset: 'GenericViewSet') -> bool:
        """Возвращает True, если ``viewset`` предполагает проверку доступа."""
        result = False
        if perm_map := self._viewset_registry.get_viewset_permissions(type(viewset)):
            result = viewset.action in perm_map
        return result

    def _get_viewset_permissions(
        self,
        viewset: 'GenericViewSet'
    ) -> tuple['Permission', ...]:
        """Возвращает имена разрешений ViewSet'а."""

        return self._viewset_registry.get_viewset_permissions(type(viewset)).get(viewset.action, ())
