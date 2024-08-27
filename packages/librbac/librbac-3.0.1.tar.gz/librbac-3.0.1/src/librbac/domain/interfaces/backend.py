from abc import ABCMeta
from abc import abstractmethod
from typing import TYPE_CHECKING
from typing import Any


if TYPE_CHECKING:
    from librbac.domain.permissions import CollectedPermissions
    from librbac.domain.permissions import Permission
    from librbac.domain.permissions import TUser


class AbstractBackend(metaclass=ABCMeta):
    """Абстрактный бэкенд контроля доступа."""

    @abstractmethod
    def __init__(self, collected_permissions: 'CollectedPermissions'):
        ...

    @abstractmethod
    def has_access(self, context: Any, request: Any, user: 'TUser') -> bool:
        """Проверяет наличие у пользователя доступа (с учётом правил)."""
        ...

    @abstractmethod
    def has_perm(self, user: 'TUser', permission: 'Permission') -> bool:
        """Проверяет наличие у пользователя разрешения (без учёта правил)."""
        ...
