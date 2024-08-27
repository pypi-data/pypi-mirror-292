from typing import Iterable
from typing import TypedDict


class TokenPermissionDict(TypedDict):

    """Структура разрешения передаваемого в составе токена."""

    resource_set_id: str
    """Объект доступа, например `auth:role`"""
    scopes: Iterable[str]
    """Операции на которые пользователю выдан доступ, например `read`"""
    exp: int
    """Временная метка после которой набор прав должен быть обновлён"""
