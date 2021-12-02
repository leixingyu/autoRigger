from ...chain import chainFKIK
from ...chain.limb import limbIK, limbFK
from ...constant import Side
from ...base import base
from ...utility.datatype import vector


class LimbFKIKItem(base.BaseItem):
    def __init__(self, name='limb'):
        super(LimbFKIKItem, self).__init__(name)

    def build_guide(self, side, base_name):
        self._obj = LimbFKIK(side, base_name)
        self._obj.build_guide()


class LimbFKIK(chainFKIK.ChainFKIK):
    """
    Create a FK/IK control rig system for limb
    """

    def __init__(self, side, name, length, ltype=None):
        """
        Extend: specify limb type and side determines direction

        :param ltype: str. type of the limb: 'arm' or 'leg'
        """
        self._rtype = ltype

        self.direction = [0, -1, 0]
        if ltype == 'arm' and side == Side.LEFT:
            self.direction = [1, 0, 0]
        elif ltype == 'arm' and side == Side.RIGHT:
            self.direction = [-1, 0, 0]

        super(LimbFKIK, self).__init__(side, name, 3, length, self.direction, 0)
        self.ik_chain = limbIK.LimbIK(side, name, length)
        self.fk_chain = limbFK.LimbFK(side, name, length)

        # master controller location
        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(self.direction).normalize()
