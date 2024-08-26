# Модуль поддержки миграций разрешений для общей библиотеки контроля доступа.

## Подключение
settings.py:
```python

INSTALLED_APPS = [
    # другие приложения
    'librbac',
    'librbac.contrib.migrations',
]
```


На стороне источника разрешений/миграций

testapp/apps.py:
```python

from django.apps.config import AppConfig as AppConfigBase

from librbac.contrib.migrations.domain.events import PermissionsReplaced
from librbac.contrib.migrations.domain.events import PermissionMarkedObsolete
from librbac.contrib.migrations.config import IConfig 

class AppConfig(AppConfigBase):

    name = __package__
    
    def _setup_rbac_migrations(self):
        from testapp import core
        from testapp.core.adapters import messaging
        from librbac.contrib.migrations import config

        class Config(config.IConfig):
            bus = core.bus
            adapter = messaging.adapter
            rbac_topic_permission = 'test.rbac.permissions'
        
        config.migrations_config = Config()
    
    def _register_event_handlers(self):
        """Регистрация обработчиков событий."""
    from testapp.core import bus
    # обработчик с публикацией событий в сервисную шину
    from librbac.contrib.migrations.services.handlers import publish_to_adapter

    for event, handler in (
        (PermissionsReplaced, publish_to_adapter),
        (PermissionMarkedObsolete, publish_to_adapter),
    ):
        bus.add_event_handler(event, handler)

    def ready(self):
        ...
        self._setup_rbac_migrations()
        self._register_event_handlers()

```

На принимающей стороне 

testapp/apps.py:
```python

from django.apps.config import AppConfig as AppConfigBase

from librbac.contrib.migrations.domain.events import PermissionsReplaced
from librbac.contrib.migrations.domain.events import PermissionMarkedObsolete

class AppConfig(AppConfigBase):

    name = __package__

    def _register_events(self):
        from librbac.contrib.migrations.config import migrations_config
        from testapp import core
        
        core.event_registry.register(
            migrations_config.rbac_topic_permission,
            PermissionMarkedObsolete,
            PermissionsReplaced,
        )

    def _register_event_handlers(self):
        """Регистрация обработчиков событий."""
        from testapp.core import bus
        from testapp.core.services.handlers import (
            on_permission_marked_obsolete,
            on_permission_replaced,
        )
        bus.add_event_handler(PermissionsReplaced, on_permission_replaced)
        bus.add_event_handler(PermissionMarkedObsolete, on_permission_marked_obsolete)

    def ready(self):
        ...
        self._register_events()
        self._register_event_handlers()
```


testapp/permissions/migrations/0001_initial.json
```json
{
  "description":  "Описание миграции.",
  "replaced": [
    {
      "replacements": [
        {
          "namespace": "test",
          "resource": "person",
          "action": "write",
          "scope": "own",
          "title": "Редактирование своего ФЛ",
          "module": "Администрирование"
        }
      ],
      "replaces": [
        {
          "namespace": "test",
          "resource": "person",
          "action": "write",
          "title": "Редактирование ФЛ",
          "module": "Администрирование"
        }
      ]
    }
  ],
  "obsolete": [
    {
      "namespace": "test",
      "resource": "person",
      "action": "delete",
      "title": "Удаление ФЛ",
      "module": "Администрирование"
    }
  ]
}
```
