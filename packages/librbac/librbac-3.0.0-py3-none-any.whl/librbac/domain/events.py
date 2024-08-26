from typing import TYPE_CHECKING
from typing import ForwardRef
from typing import Optional
from typing import Union

from explicit.domain.factories import DTOBase
from explicit.domain.model import Unset
from explicit.domain.model import unset
from explicit.messagebus.events import Event
from pydantic import Field
from pydantic import conlist


if TYPE_CHECKING:
    from dataclasses import dataclass  # noqa
else:
    from pydantic.dataclasses import dataclass  # noqa


class PermissionDTO(DTOBase):
    """Данные разрешения."""
    namespace: Union[str, Unset] = unset
    resource: Union[str, Unset] = unset
    action: Union[str, Unset] = unset
    scope: Optional[str] = None
    title: Union[str, Unset] = unset
    module: Union[str, Unset] = unset
    dependencies: conlist(ForwardRef('PermissionDTO'), min_items=0) = Field(default_factory=list)


@dataclass
class PermissionsCollected(Event):
    permissions: conlist(PermissionDTO, min_items=0) = Field(default_factory=list)
