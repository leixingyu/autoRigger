from ...chain import chain, chainFKIK
from ...chain.limb import limbIK, limbFK
from ...constant import Side
from ...utility.datatype import vector


class LimbFKIK(chainFKIK.ChainFKIK):
    """
    Abstract FK/IK limb rig
    """

    def __init__(self, side, name, length, ltype='null'):
        self._rtype = ltype

        self.direction = [0, -1, 0]
        if ltype == 'arm' and side == Side.LEFT:
            self.direction = [1, 0, 0]
        elif ltype == 'arm' and side == Side.RIGHT:
            self.direction = [-1, 0, 0]

        chain.Chain.__init__(self, side, name, segment=3)
        self.ik_chain = limbIK.LimbIK(side, name, length)
        self.fk_chain = limbFK.LimbFK(side, name, length)

        # master controller location
        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(self.direction).normalize()
