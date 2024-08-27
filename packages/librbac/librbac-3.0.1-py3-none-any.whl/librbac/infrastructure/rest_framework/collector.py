from abc import ABCMeta
from contextlib import suppress
from importlib import import_module
from itertools import chain
from typing import TYPE_CHECKING
from typing import Generator
from typing import Iterable
from typing import final

from django.apps import apps
from django.conf import settings

from librbac.domain.interfaces.collector import AbstractPermissionsCollector
from librbac.domain.permissions import PermissionGroup
from librbac.domain.permissions import PermissionMetadata
from librbac.domain.permissions import PermissionMetadataMapping
from librbac.domain.permissions import PermissionRuleMapping
from librbac.domain.permissions import PermissionsGraph

from .domain import DRFCollectedPermissions
from .domain import ViewSetRegistry
from .viewsets import RBACMixin


if TYPE_CHECKING:
    from types import ModuleType


class BaseAppsPermissionsCollector(AbstractPermissionsCollector, metaclass=ABCMeta):

    """Базовый разрешений из зарегистрированных django приложений."""

    _msg_perm_not_found = 'Разрешение не зарегистрировано: "{}"'
    _msg_perm_not_found_plural = 'Разрешения не зарегистрированы: "{}"'
    _msg_perm_group_not_defined = 'Не определён раздел для разрешения: "{}"'
    _msg_perm_group_already_defined = 'Группа разрешений "{}" уже закреплена за другим разделом системы'
    _processed_groups: dict[PermissionGroup, str]

    def __init__(self):
        super().__init__()
        self._processed_groups = {}

    def get_apps_permission_modules(self) -> Generator['ModuleType', None, None]:
        """Возвращает модули permissions из приложений системы."""
        for app_config in apps.get_app_configs():
            with suppress(ModuleNotFoundError):
                yield import_module('.permissions', app_config.name)

    def _collect_permissions(
        self,
        permissions_module: 'ModuleType',
        permissions_graph: PermissionsGraph,
    ):
        """Сбор разрешений системы и их взаимоотношений."""

        module_permissions = getattr(permissions_module, 'permissions', ())
        module_dependencies = getattr(permissions_module, 'dependencies', {})

        processed_permissions = set()

        if callable(module_dependencies):
            module_dependencies = module_dependencies()

        for permission, _ in module_permissions:
            dependencies = module_dependencies.get(permission)
            processed_permissions.add(permission)

            permissions_graph.register_permission(permission, dependencies)

        not_yet_registered_permissions = set(module_dependencies).difference(processed_permissions)
        assert not not_yet_registered_permissions, self._msg_perm_not_found.format(
            '; '.join(str(i) for i in not_yet_registered_permissions)
        )

    def _collect_metadata(
        self,
        permissions_module: 'ModuleType',
        permissions_graph: PermissionsGraph,
        permissions_metadata_mapping: PermissionMetadataMapping
    ):
        """Сбор метаданных разрешений системы."""

        partitions = getattr(permissions_module, 'partitions', {})
        group_partition_mapping = {group: partition for partition, groups in partitions.items() for group in groups}

        for permission, title in getattr(permissions_module, 'permissions', ()):

            perm_group = PermissionGroup(permission.namespace, permission.resource)
            if perm_group in self._processed_groups:
                assert self._processed_groups[perm_group] == group_partition_mapping[perm_group], (
                    self._msg_perm_group_already_defined.format(perm_group)
                )
            else:
                self._processed_groups[perm_group] = group_partition_mapping[perm_group]

            assert permission in permissions_graph, self._msg_perm_not_found.format(permission)
            assert perm_group in group_partition_mapping, self._msg_perm_group_not_defined.format(permission)
            permissions_metadata_mapping[permission] = PermissionMetadata(
                title=title,
                partition_title=group_partition_mapping[perm_group],
            )

    def _collect_rules(
        self,
        permissions_module: 'ModuleType',
        permissions_graph: PermissionsGraph,
        permissions_rules_mapping: PermissionRuleMapping
    ):
        """Сбор обработчиков правил для разрешений системы."""

        for permission, rules in getattr(permissions_module, 'rules', {}).items():
            assert permission in permissions_graph, (self._msg_perm_not_found.format(permission))

            if not isinstance(rules, Iterable):
                rules = (rules,)
            for handler in rules:
                assert callable(handler), handler
                permissions_rules_mapping[permission] = rules


@final
class AppsPermissionsCollector(BaseAppsPermissionsCollector):
    """Сборщик разрешений из зарегистрированных django приложений."""

    _msg_unrequired_permission = 'Разрешения не востребованы: {}'

    def _collect_permission_module_viewsets(self, permissions_module: 'ModuleType', viewset_registry: ViewSetRegistry):
        """Сбор данных о представлениях и требуемых разрешениях."""
        module_viewsets = getattr(permissions_module, 'viewset_permission_mapping', {})
        for viewset, perm_map in module_viewsets.items():
            viewset_registry.add_permission_mapping(viewset, perm_map)

    def _collect_urlpatterns_viewsets(self, viewset_registry: ViewSetRegistry):
        """Сбор данных о разрешениях представлений, зарегистрированных в роутере."""
        urlpatterns = import_module(settings.ROOT_URLCONF).urlpatterns
        for viewset in self._get_rbac_viewsets(urlpatterns):
            viewset_registry.add_permission_mapping(viewset, viewset.perm_map)

    def _validate_unrequired(self, permissions_graph: PermissionsGraph, viewset_registry: ViewSetRegistry):
        viewsets_permissions = set(chain.from_iterable(chain.from_iterable(perm_map.values()) for _, perm_map in viewset_registry))
        graph_permissions = set(p for p, _ in permissions_graph)
        difference = graph_permissions.difference(viewsets_permissions)

        assert not difference, self._msg_unrequired_permission.format(', '.join((str(p) for p in difference)))

    def _get_rbac_viewsets(
        self,
        urlpatterns,
        viewsets=None
    ) -> set[type['RBACMixin']]:
        """Находит и возвращает все ViewSet'ы системы."""
        viewsets = viewsets if viewsets is not None else set()

        for pattern in urlpatterns:
            if hasattr(pattern, 'url_patterns'):
                self._get_rbac_viewsets(pattern.url_patterns, viewsets)
            else:
                if cls := getattr(pattern.callback, 'cls', None):
                    if not issubclass(cls, RBACMixin):
                        continue
                    viewsets.add(cls)

        return viewsets

    def collect(self) -> DRFCollectedPermissions:
        permissions_graph = PermissionsGraph()
        permission_metadata_mapping = PermissionMetadataMapping()
        permission_rule_mapping = PermissionRuleMapping()
        viewset_registry = ViewSetRegistry()

        # сборка разрешений и регистрация использующих их представлений в .permissions модулях приложений
        for module in self.get_apps_permission_modules():
            self._collect_permissions(module, permissions_graph)
            self._collect_metadata(module, permissions_graph, permission_metadata_mapping)
            self._collect_rules(module, permissions_graph, permission_rule_mapping)
            self._collect_permission_module_viewsets(module, viewset_registry)

        # регистрация представлений, в которых напрямую определены требуемы разрешения
        self._collect_urlpatterns_viewsets(viewset_registry)

        self._validate_unrequired(permissions_graph, viewset_registry)

        return DRFCollectedPermissions(
            graph=permissions_graph,
            metadata_mapping=permission_metadata_mapping,
            rule_mapping=permission_rule_mapping,
            viewset_registry=viewset_registry
        )
