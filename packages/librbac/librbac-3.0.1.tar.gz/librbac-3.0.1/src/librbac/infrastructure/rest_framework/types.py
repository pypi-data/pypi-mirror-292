from typing import Tuple

from librbac.domain.permissions import Permission


TPermMapDict = dict[str, Tuple[Permission, ...]]
"""Структура сопоставления разрешений с действиями во ViewSet'е."""
