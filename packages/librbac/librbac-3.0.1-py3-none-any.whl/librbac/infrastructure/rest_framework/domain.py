from dataclasses import dataclass
from importlib import import_module
from itertools import chain
from typing import TYPE_CHECKING
from typing import Iterator

from rest_framework.routers import SimpleRouter

from librbac.domain.permissions import (
    CollectedPermissions as CollectedPermissionsBase)
from librbac.infrastructure.rest_framework.types import TPermMapDict


if TYPE_CHECKING:
    from rest_framework.viewsets import GenericViewSet

    from librbac.domain.permissions import PermissionMetadataMapping
    from librbac.domain.permissions import PermissionRuleMapping
    from librbac.domain.permissions import PermissionsGraph


class ViewSetRegistrationError(Exception):
    """Возбуждается, если сопоставление представления с разрешением не может быть зарегистрировано."""

    message: str

    def __init__(self, message: str):
        self.message = message

class ViewSetRegistry:
    """Реестр представлений и их сопоставление с требуемыми разрешениями."""

    _registry: 'dict[type[GenericViewSet], TPermMapDict]'

    _msg_action_does_not_exist = (
        'Невозможно зарегистрировать разрешения для представления "{}". '
        'Указанные действия отсутствуют в представлении: {}'
    )
    _msg_already_registered = 'Для представления "{}" уже зарегистрированы разрешения'

    def __init__(self):
        self._registry = {}

    def _get_viewset_path(self, viewset: 'GenericViewSet') -> str:
        return f'{viewset.__module__}.{viewset.__qualname__}'

    def _validate_actions(self, viewset: 'GenericViewSet', permission_mapping: 'TPermMapDict') -> None:
        """Проверяет, что указанные action'ы существуют в представлении."""
        viewset_actions = chain.from_iterable(i.mapping.values() for i in SimpleRouter().get_routes(viewset))
        difference = set(permission_mapping).difference(viewset_actions)
        if difference:
            raise ViewSetRegistrationError(
                self._msg_action_does_not_exist.format(
                    self._get_viewset_path(viewset), ', '.join(difference)
                )
            )

    def add_permission_mapping(
        self, viewset: 'str | type[GenericViewSet]',
        permission_mapping: 'TPermMapDict'
    ):
        if isinstance(viewset, str):
            module_path, class_name = viewset.rsplit(".", 1)
            module = import_module(module_path)
            viewset_cls = getattr(module, class_name)
        else:
            viewset_cls = viewset

        if viewset_cls in self._registry:
            raise ViewSetRegistrationError(
                message=self._msg_already_registered.format(self._get_viewset_path(viewset_cls))
            )

        self._validate_actions(viewset_cls, permission_mapping)

        self._registry[viewset_cls] = permission_mapping

    def get_viewset_permissions(self, viewset_cls: 'type[GenericViewSet]') -> 'TPermMapDict | None':
        return self._registry.get(viewset_cls)

    def __contains__(self, viewset_cls: 'type[GenericViewSet]') -> bool:
        return viewset_cls in self._registry

    def __iter__(self) -> Iterator[tuple[type['GenericViewSet'], 'TPermMapDict']]:
        for viewset_cls in self._registry:
            yield viewset_cls, self.get_viewset_permissions(viewset_cls)


@dataclass(frozen=True)
class DRFCollectedPermissions(CollectedPermissionsBase):
    """Структура собранных из системы данных о разрешениях и представлениях."""
    graph: 'PermissionsGraph'
    metadata_mapping: 'PermissionMetadataMapping'
    rule_mapping: 'PermissionRuleMapping'
    viewset_registry: 'ViewSetRegistry'
