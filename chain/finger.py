from ..base import base
from ..chain import chainFK
from ..constant import Side


class FingerItem(base.BaseItem):
    def __init__(self, name='biped-finger'):
        super(FingerItem, self).__init__(name)

    def build_guide(self, side, base_name):
        self._obj = Finger(side, base_name)
        self._obj.build_guide()


class Finger(chainFK.ChainFK):
    """
    Create a finger rig system with FK controls
    """

    def __init__(self, side, name, segment=4, length=2.0, direction=[-1, 0, 0]):
        """
        Extend: specify scale, rig type, and direction (determined by side)
        """
        if side == Side.LEFT:
            direction = [1, 0, 0]

        super(Finger, self).__init__(side, name, segment, length, direction)
        self._rtype = 'finger'
        self._scale = 0.4
