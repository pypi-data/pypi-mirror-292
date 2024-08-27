from typing import TYPE_CHECKING

from librbac.domain.events import PermissionDTO
from librbac.domain.events import PermissionsCollected
from librbac.domain.interfaces.publisher import AbstractPermissionsPublisher
from librbac.domain.permissions import CollectedPermissions


if TYPE_CHECKING:
    from typing import TYPE_CHECKING

    from explicit.adapters.messaging import AbstractAdapter
    from explicit.messagebus import MessageBus

    from librbac.domain.permissions import CollectedPermissions
    from librbac.domain.permissions import Permission
    from librbac.domain.permissions import PermissionMetadataMapping

class EventBuilder:

    """Сборщик события PermissionsCollected."""

    @classmethod
    def _build_permission_dto(
        cls,
        metadata_mapping: 'PermissionMetadataMapping',
        permission: 'Permission',
        dependencies: set['Permission'] | None = None,
    ) -> PermissionDTO:
        dependencies = dependencies or set()
        return PermissionDTO(
            namespace=permission.namespace,
            resource=permission.resource,
            action=permission.action,
            scope=permission.scope,
            title=metadata_mapping[permission].title,
            module=metadata_mapping[permission].partition_title,
            dependencies=[
                cls._build_permission_dto(
                    metadata_mapping,
                    dependency,
                )
                for dependency in dependencies
            ]
        )

    @classmethod
    def build_event(cls, collected_permissions: CollectedPermissions) -> PermissionsCollected:
        """Собирает событие."""
        return PermissionsCollected(
            permissions=[
                cls._build_permission_dto(
                    collected_permissions.metadata_mapping,
                    permission,
                    dependencies,
                ) for permission, dependencies in collected_permissions.graph
            ]
        )


class LocalBusPermissionsPublisher(AbstractPermissionsPublisher):
    """Издатель событий о разрешениях в локальную шину.

    Требует регистрации в системе обработчика события `librbac.domain.events.PermissionsCollected`.
    """

    _bus: 'MessageBus'

    def __init__(self, bus: 'MessageBus'):
        self._bus = bus

    def publish(self, collected_permissions: CollectedPermissions):
        self._bus.handle(EventBuilder.build_event(collected_permissions))


class ServiceBusPublisher(AbstractPermissionsPublisher):

    """Издатель событий о разрешениях в сервисную шину."""

    _adapter: 'AbstractAdapter'
    _topic: str

    def __init__(self, adapter: 'AbstractAdapter', topic: str):
        self._adapter = adapter
        self._topic = topic

    def publish(self, collected_permissions: 'CollectedPermissions'):
        event = EventBuilder.build_event(collected_permissions)

        self._adapter.publish(self._topic, event.dump())

