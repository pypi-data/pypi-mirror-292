# Общая библиотека контроля доступа для микросервисов

## Подключение
#### settings.py:

```python
INSTALLED_APPS = [
    # другие приложение
    'testapp.core',
    'librbac',                         # для management команды rbac
    'librbac.contrib.migrations',      # для поддержки миграций
]

# Опционально. 
# Подойдёт любая имплементация, где `request.user` поддерживает `librbac.domain.permissions.UserProtocol` 
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'oidc_auth.authentication.JSONWebTokenAuthentication',
    ),
}

OIDC_AUTH = {
    # URL сервиса аутентификации, необходимо указать своё значение
    'OIDC_ENDPOINT': 'http://testserver/oauth',
    
    # Функция преобразующая токен в объект пользователя. Указать как есть.
    'OIDC_RESOLVE_USER_FUNCTION': 'librbac.contrib.oidc.auth.get_user_from_token',
    
    # Заголовок в котором хранится токен. Указать как есть.
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',

    # The Claims Options can now be defined by a static string.
    # ref: https://docs.authlib.org/en/latest/jose/jwt.html#jwt-payload-claims-validation
    # The old OIDC_AUDIENCES option is removed in favor of this new option.
    # `aud` is only required, when you set it as an essential claim.
    'OIDC_CLAIMS_OPTIONS': {
        'iss': {
            'essential': True,
        }
    },
}
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
```    


#### testapp/&#95;&#95;init__.py:
```python
from typing import TYPE_CHECKING

from explicit.contrib.messagebus.event_registry import Registry


if TYPE_CHECKING:
    from explicit.messagebus.messagebus import MessageBus  # noqa


default_app_config = f'{__package__}.apps.AppConfig'


bus: 'MessageBus'

event_registry = Registry()
```



#### testapp/apps.py:

```python
from django.apps.config import AppConfig as AppConfigBase


class AppConfig(AppConfigBase):
    name = __package__

    _rbac_permissions_topic = 'test.rbac.permission'

    def _bootstrap(self):
        """Предоставление общей шины ядра."""
        ...

    def _setup_rbac(self):
        from librbac.infrastructure.rest_framework.collector import (
            AppsPermissionsCollector)
        from librbac.infrastructure.rest_framework.backend import (
            RestFrameworkBackend)
        from librbac.infrastructure.explicit.publisher import (
            ServiceBusPublisher)
        from librbac.manager import RBACManager
        from testapp.core.adapters.messaging import adapter

        RBACManager.bootstrap(
            collector_cls=AppsPermissionsCollector,
            backend_cls=RestFrameworkBackend,
            publisher=ServiceBusPublisher(adapter=adapter, topic=self._rbac_permissions_topic),
            # или если нужно отправлять события в локальную шину
            # publisher=LocalBusPermissionsPublisher(bus=bus),
        )

    # Опционально, если нужны миграции
    def _setup_rbac_migrations(self):
        from librbac.contrib.migrations import config
        from testapp import core
        from testapp.core.adapters import messaging

        class Config(config.IConfig):
            bus = core.bus
            adapter = messaging.adapter
            rbac_topic_permission = self._rbac_permissions_topic

        config.migrations_config = Config()

    def ready(self):
        self._bootstrap()
        self._setup_rbac()
        self._setup_rbac_migrations()

```

#### testapp/rest/persons/permissions/rules.py
```python
from testapp.core.persons.models import Person


def is_own_person(
    context: 'GenericViewSet',
    request: 'Request',
    user: 'UserProtocol',
):
    """Проверка отношения пользователя к ФЛ."""
    person_id = context.get_rbac_rule_data()

    user_id = user.pk
    return Person.objects.filter(id=person_id, user_id=user_id).exists()

```


#### testapp/rest/persons/permissions/&#95;&#95;init__.py

```python

from librbac.domain.permissions import PermissionGroup, Permission

from . import rules

PERM_NAMESPACE_TEST = 'test'

PERM_RESOURCE__PERSON = 'person'
PERM__PERSON__READ = Permission(
    # (namespace, resource, action, scope)
    PERM_NAMESPACE_TEST, PERM_RESOURCE__PERSON, 'read'
)
PERM__PERSON__WRITE_OWN = Permission(
    PERM_NAMESPACE_TEST, PERM_RESOURCE__PERSON, 'write', 'own'
)
# Описание разрешений
# -----------------------------------------------------------------------------
permissions = (
    (PERM__PERSON__READ, 'Просмотр ФЛ'),
    (PERM__PERSON__WRITE_OWN, 'Редактирование своего ФЛ'),
)

dependencies = {
    PERM__PERSON__WRITE_OWN: {
        PERM__PERSON__READ,
    },
}
# Описание связей разделов и групп разрешений
# -----------------------------------------------------------------------------
partitions = {
    'Администрирование': (
        PermissionGroup(PERM_NAMESPACE_TEST, PERM_RESOURCE__PERSON),
    ),
}
# Описание правил доступа
# -----------------------------------------------------------------------------
rules = {
    PERM__PERSON__WRITE_OWN: (rules.is_own_person,),
}

# Сопоставление представлений с разрешениями (взаимоисключающее с RBACMixin)
# -----------------------------------------------------------------------------
viewset_permission_mapping = {
    'testapp.rest.persons.views.PersonViewSet': dict(
        create=(PERM__PERSON__WRITE_OWN,),
        partial_update=(PERM__PERSON__WRITE_OWN,),
        destroy=(PERM__PERSON__WRITE_OWN,),
        retrieve=(PERM__PERSON__READ,),
        list=(PERM__PERSON__READ,),
    )
}

```


#### testapp/views.py
```python
from rest_framework.viewsets import ModelViewSet

from librbac.infrastructure.django.rest_framework.viewsets import RBACMixin

from .permissions import PERM__PERSON__READ
from .permissions import PERM__PERSON__WRITE


class PersonViewSet(RBACMixin, ModelViewSet):
    
    # сопоставление действий с разрешениями (взаимоисключающее с permissions.viewset_permission_mapping)
    perm_map = dict(
        create=(PERM__PERSON__WRITE,),
        partial_update=(PERM__PERSON__WRITE,),
        destroy=(PERM__PERSON__WRITE,),
        retrieve=(PERM__PERSON__READ,),
        list=(PERM__PERSON__READ,),
    )

    ...
```

## Миграции разрешений
[Описание](./src/librbac/contrib/migrations/README.md) в модуле миграций

## Запуск тестов
    $ tox
