from abc import ABCMeta
from abc import abstractmethod

from librbac.domain.permissions import CollectedPermissions


class AbstractPermissionsPublisher(metaclass=ABCMeta):
    """Абстрактный издатель событий о разрешениях.

    Область ответственности: передача сведений о собранных разрешениях в сервисную или локальную шину.
    """

    @abstractmethod
    def publish(self, collected_permissions: CollectedPermissions):
        ...
