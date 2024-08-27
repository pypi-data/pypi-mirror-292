from collections import defaultdict
from dataclasses import dataclass
from typing import Any
from typing import Iterator
from typing import Mapping
from typing import NamedTuple
from typing import Optional
from typing import Protocol
from typing import TypeVar


class PermissionGroup(NamedTuple):

    """Структура группы разрешений."""

    namespace: str
    resource: str


class Permission(NamedTuple):

    """Структура разрешения."""

    namespace: str
    resource: str
    action: str
    scope: Optional[str] = None

    def __str__(self):
        scope = f':{self.scope}' if self.scope else ''
        return f'{self.namespace}.{self.resource}.{self.action}{scope}'


class UserProtocol(Protocol):
    """Протокол "Объект пользователя"."""
    rbac_permissions: tuple['Permission', ...]


TUser = TypeVar('TUser', bound=UserProtocol)


class RuleProtocol(Protocol):
    """Протокол 'Правило для проверки доступа'."""
    def __call__(
        self,
        context: Any,
        request: Any,
        user: 'TUser',
    ) -> bool:
        """Проверка доступа."""


TRule = TypeVar('TRule', bound=RuleProtocol)


class PermissionsGraph:
    """Структура системных разрешений.

    Предназначена для хранения отношений между разрешениями.
    """

    def __init__(self):
        # сопоставление разрешение с его прямыми зависимостями
        self._graph: dict[Permission, set[Permission]] = defaultdict(set)
        # сопоставление разрешения с напрямую зависящими от него разрешениями
        self._reverse_graph = defaultdict(set)

    def __contains__(self, permission: Permission):
        assert isinstance(permission, Permission)
        return permission in self._graph

    def __iter__(self) -> Iterator[tuple[Permission, set[Permission]]]:
        """Итератор кортежей (Разрешение, Множество вложенных разрешений)."""
        for permission in self._graph:
            yield permission, self.get_dependencies(permission)

    def _register_reverse(self, permission: Permission, dependent: Permission):
        """Регистрирует обратную зависимость."""
        self._reverse_graph[permission].add(dependent)

    def register_permission(self, permission: Permission, dependencies: set[Permission] | None = None):
        """Регистрирует зависимости разрешения."""
        assert isinstance(permission, Permission)

        dependencies = dependencies or set()
        self._graph[permission].update(dependencies)
        for dependency in dependencies:
            self._register_reverse(dependency, permission)
            self.register_permission(dependency)

    def get_dependencies(self, permission: Permission) -> set[Permission]:
        """Возвращает все разрешения, от которых зависит данное разрешение."""
        assert isinstance(permission, Permission)
        result = set()
        for dependency in self._graph[permission]:
            result.add(dependency)
            result.update(self.get_dependencies(dependency))
        return result

    def get_dependents(self, permission: Permission) -> set[Permission]:
        """Возвращает все разрешения, которые зависят от данного разрешения."""
        assert isinstance(permission, Permission)
        result = set()
        for dependent in self._reverse_graph[permission]:
            result.add(dependent)
            result.update(self.get_dependents(dependent))
        return result


class PermissionMetadata(NamedTuple):
    """Структура метаданных разрешения."""
    title: str
    partition_title: str


class PermissionMetadataMapping(Mapping):
    """Сопоставление разрешений с метаданными."""

    def __init__(self):
        self._mapping = {}

    def __getitem__(self, __key: Permission):
        assert isinstance(__key, Permission)
        return self._mapping[__key]

    def __len__(self):
        return len(self._mapping)

    def __iter__(self):
        return iter(self._mapping)

    def __setitem__(self, __key: Permission, __value: PermissionMetadata):
        assert isinstance(__key, Permission)
        assert isinstance(__value, PermissionMetadata)
        assert Permission not in self._mapping
        self._mapping[__key] = __value


class PermissionRuleMapping(Mapping):
    """Сопоставление разрешений с правилами доступа."""
    def __init__(self):
        self._mapping = {}

    def __getitem__(self, __key: Permission):
        assert isinstance(__key, Permission)
        return self._mapping[__key]

    def __len__(self):
        return len(self._mapping)

    def __iter__(self):
        return iter(self._mapping)

    def __setitem__(self, __key: Permission, __value: TRule | tuple[TRule, ...]):
        assert isinstance(__key, Permission)
        assert Permission not in self._mapping
        self._mapping[__key] = __value


@dataclass(frozen=True)
class CollectedPermissions:
    """Структура собранных из системы данных о разрешениях."""
    graph: PermissionsGraph
    metadata_mapping: PermissionMetadataMapping
    rule_mapping: PermissionRuleMapping
