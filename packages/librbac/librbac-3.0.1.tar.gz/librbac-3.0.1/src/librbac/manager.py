from typing import TYPE_CHECKING
from typing import Any

from librbac.domain.interfaces.backend import AbstractBackend
from librbac.domain.interfaces.collector import AbstractPermissionsCollector
from librbac.domain.interfaces.publisher import AbstractPermissionsPublisher
from librbac.domain.permissions import CollectedPermissions
import librbac


if TYPE_CHECKING:
    from librbac.domain.permissions import TUser
from librbac.domain.permissions import Permission


class RBACManager:

    """Менеджер системы контроля доступа RBAC.

    Область ответственности — оркестрация процессов
      * Сборки разрешений из системы.
      * Отправки разрешений в хранилище.
      * Предоставление API проверки доступа к ресурсу.
    """

    _collected_permissions: CollectedPermissions

    _backend: AbstractBackend
    _publisher: AbstractPermissionsPublisher

    def __init__(
        self,
        collector_cls: type[AbstractPermissionsCollector],
        backend_cls: type[AbstractBackend],
        publisher: AbstractPermissionsPublisher,
    ):

        self._collected_permissions = collector_cls().collect()
        self._backend = backend_cls(collected_permissions=self._collected_permissions)
        self._publisher = publisher

    @classmethod
    def bootstrap(
        cls,
        collector_cls: type[AbstractPermissionsCollector],
        backend_cls: type[AbstractBackend],
        publisher: AbstractPermissionsPublisher,
    ):
        """Инициализация модуля контроля доступа."""
        assert issubclass(collector_cls, AbstractPermissionsCollector)
        assert issubclass(backend_cls, AbstractBackend)
        assert isinstance(publisher, AbstractPermissionsPublisher)

        if hasattr(librbac, 'rbac'):
            return

        librbac.rbac = cls(
            collector_cls=collector_cls,
            backend_cls=backend_cls,
            publisher=publisher
        )

    @property
    def permissions(self) -> CollectedPermissions:
        return self._collected_permissions

    def get_permission_dependencies(self, permission: 'Permission') -> set[Permission]:
        """Возвращает все разрешения, от которых зависит данное разрешение."""
        return self._collected_permissions.graph.get_dependencies(permission=permission)

    def get_permission_dependents(self, permission: 'Permission') -> set[Permission]:
        """Возвращает все разрешения, которые зависят от данного разрешения."""
        return self._collected_permissions.graph.get_dependents(permission=permission)

    def publish_permissions(self):
        """Выполняет передачу разрешений в хранилище."""

        self._publisher.publish(self._collected_permissions)

    def has_access(self, context: Any, request: Any, user: 'TUser') -> bool:
        """Проверяет наличие у пользователя доступа (с учётом правил)."""
        return self._backend.has_access(context, request, user)

    def has_perm(self, user: 'TUser', permission: 'Permission') -> bool:
        """Проверяет наличие у пользователя разрешения (без учёта правил)."""
        return self._backend.has_perm(user, permission)
