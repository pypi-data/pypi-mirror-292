from abc import ABCMeta
from abc import abstractmethod

from librbac.domain.permissions import CollectedPermissions


class AbstractPermissionsCollector(metaclass=ABCMeta):

    """Абстрактный сборщик разрешений из системы."""

    @abstractmethod
    def collect(self) -> CollectedPermissions:
        """Выполняет сборку разрешений из системы."""
