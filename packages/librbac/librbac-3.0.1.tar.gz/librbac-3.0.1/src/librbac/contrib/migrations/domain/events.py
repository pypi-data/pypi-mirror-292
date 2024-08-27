from typing import TYPE_CHECKING

from explicit.messagebus.events import Event
from pydantic import Field
from pydantic import conlist

from librbac.domain.events import PermissionDTO


if TYPE_CHECKING:
    from dataclasses import dataclass  # noqa
else:
    from pydantic.dataclasses import dataclass  # noqa


@dataclass
class PermissionsReplaced(Event):
    """Разрешения были заменены."""
    replacements: conlist(PermissionDTO, min_items=1) = Field(default_factory=list)
    replaces: conlist(PermissionDTO, min_items=1) = Field(default_factory=list)


@dataclass
class PermissionMarkedObsolete(Event):
    """Разрешение было помечено как устаревшее."""
    permission: PermissionDTO = Field()
