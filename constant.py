from enum import Enum, IntEnum, unique


@unique
class Side(Enum):
    LEFT = 'l'
    RIGHT = 'r'
    MIDDLE = 'm'


@unique
class RigComponents(Enum):
    BASE = 'base'
    FINGER = 'biped-finger'
    HAND = 'biped-hand'
    LIMB = 'limb'
    ARM = 'biped-arm'
    FOOT = 'biped-foot'
    LEG = 'biped-leg'
    HEAD = 'biped-head'
    SPINE = 'biped-spine'
    BIPED = 'biped'
    LEG_FRONT = 'quad-front'
    LEG_BACK = 'quad-hind'
    SPINE_QUAD = 'quad-spine'
    TAIL = 'quad-tail'
    QUAD = 'quad'

    CHAIN_IK = 'chain-ik'
    CHAIN_FK = 'chain-fk'
    CHAIN_EP = 'chain-ep'
    CHAIN_FKIK = 'chain-fkik'


@unique
class RigType(IntEnum):
    BIPED = 0
    QUADRUPED = 1
    CHAIN = 2
    CUSTOM = 3
