from abc import ABC
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from explicit.kafka.adapters.messaging import Adapter
    from explicit.messagebus import MessageBus


class IConfig(ABC):
    """Конфигурация для компонентов librbac использующих explicit."""

    bus: 'MessageBus'
    """Внутренняя шина сервиса."""

    adapter: 'Adapter'
    """Адаптер к kafka"""

    rbac_topic_permission: str
    """Топик событий о разрешениях"""



migrations_config: IConfig
