import os

from enum import Enum, IntEnum, unique


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(PROJECT_ROOT, 'ui')
ICON_DIR = os.path.join(UI_DIR, 'icon')

# custom attribute short name long name mapping to be added on controllers
ATTRS = {
    # quad foot
    'flx': 'flex',
    'swv': 'swivel',
    'tap': 'tap',
    'tip': 'tip',
    'wr': 'wrist',
    # biped foot
    'fr': 'foot_roll',
    'fb': 'foot_bank',
    # fk ik switch
    'sw': 'FK_IK'
}


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


@unique
class Direction(Enum):
    Y_POSITIVE = [0, 1, 0]
    Y_NEGATIVE = [0, -1, 0]
    X_POSITIVE = [1, 0, 0]
    X_NEGATIVE = [-1, 0, 0]
    Z_POSITIVE = [0, 0, 1]
    Z_NEGATIVE = [0, 0, -1]

