from importlib import import_module
from typing import TYPE_CHECKING
from typing import Generator
from typing import Union

from django.conf import settings


if TYPE_CHECKING:
    from rest_framework.viewsets import GenericViewSet

    from .viewsets import RBACMixin


def get_viewsets(
    urlpatterns,
    viewsets=None
) -> set[type[GenericViewSet]]:
    """Находит и возвращает все ViewSet'ы в urlpatterns."""
    viewsets = viewsets if viewsets is not None else set()
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            get_viewsets(pattern.url_patterns, viewsets=viewsets)
        else:
            if cls := getattr(pattern.callback, 'cls', None):
                if issubclass(cls, GenericViewSet):
                    viewsets.add(cls)

    return viewsets


def get_rbac_viewsets() -> Generator[Union['GenericViewSet', 'RBACMixin'], None, None]:
    """Возвращает ViewSet'ы системы, доступ к которым нужно проверять."""
    from .viewsets import RBACMixin
    urlpatterns = import_module(settings.ROOT_URLCONF).urlpatterns
    for viewset in get_viewsets(urlpatterns):
        if issubclass(viewset, RBACMixin):
            yield viewset
