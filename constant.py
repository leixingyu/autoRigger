import os

from enum import Enum, IntEnum, unique


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(PROJECT_ROOT, 'ui')
ICON_DIR = os.path.join(UI_DIR, 'icon')


@unique
class Side(Enum):
    LEFT = 'l'
    RIGHT = 'r'
    MIDDLE = 'm'


@unique
class RigType(IntEnum):
    BIPED = 0
    QUADRUPED = 1
    CHAIN = 2
    CUSTOM = 3
