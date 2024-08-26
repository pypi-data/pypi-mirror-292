from django.utils.decorators import classonlymethod

from librbac.domain.permissions import Permission

from .permissions import HasAccess
from .types import TPermMapDict


class RBACMixin:

    """Примесь для ViewSet'ов требующих контроля доступа."""

    perm_map: TPermMapDict
    """Сопоставление действий и требуемых разрешений."""

    permission_classes = (
        HasAccess,
    )

    @classonlymethod
    def as_view(cls, actions=None, **initkwargs):
        assert isinstance(cls.perm_map, dict)
        assert len(cls.perm_map)
        for action, perms in cls.perm_map.items():
            assert all(isinstance(p, Permission) for p in perms)
        return super().as_view(actions=actions, **initkwargs)
