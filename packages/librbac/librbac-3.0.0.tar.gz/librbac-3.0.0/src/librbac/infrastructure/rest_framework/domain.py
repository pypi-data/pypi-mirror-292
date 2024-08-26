from dataclasses import dataclass
from importlib import import_module
from typing import TYPE_CHECKING

from librbac.domain.permissions import (
    CollectedPermissions as CollectedPermissionsBase)
from librbac.infrastructure.rest_framework.types import TPermMapDict


if TYPE_CHECKING:

    from librbac.domain.permissions import PermissionMetadataMapping
    from librbac.domain.permissions import PermissionRuleMapping
    from librbac.domain.permissions import PermissionsGraph
    from librbac.infrastructure.rest_framework.viewsets import RBACMixin

class ViewSetRegistry:
    """Реестр представлений и их сопоставление с требуемыми разрешениями."""

    _registry: 'dict[type[RBACMixin], TPermMapDict]'

    def __init__(self):
        self._registry = {}

    def add_permission_mapping(
        self, viewset: 'str | type[RBACMixin]',
        permission_mapping: 'TPermMapDict'
    ):
        if isinstance(viewset, str):
            module_path, class_name = viewset.rsplit(".", 1)
            module = import_module(module_path)
            viewset_cls = getattr(module, class_name)
        else:
            viewset_cls = viewset

        assert viewset_cls not in self._registry, f'Для {viewset} уже зарегистрированы разрешения'
        self._registry[viewset_cls] = permission_mapping

    def get_viewset_permissions(self, viewset_cls: 'type[RBACMixin]') -> 'TPermMapDict | None':
        return self._registry.get(viewset_cls)

    def __contains__(self, viewset_cls: 'type[RBACMixin]') -> bool:
        return viewset_cls in self._registry


@dataclass(frozen=True)
class DRFCollectedPermissions(CollectedPermissionsBase):
    """Структура собранных из системы данных о разрешениях и вьюсетах."""
    graph: 'PermissionsGraph'
    metadata_mapping: 'PermissionMetadataMapping'
    rule_mapping: 'PermissionRuleMapping'
    viewset_registry: 'ViewSetRegistry'
