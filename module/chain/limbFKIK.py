from . import chain, limbFK, limbIK, chainFKIK
from utility.datatype import vector


class LimbFKIK(chainFKIK.ChainFKIK):

    def __init__(self, side, name, length, ltype='null'):

        self.ltype = ltype
        self.direction = [0, -1, 0]
        self._rtype = ltype

        if ltype == 'arm' and side == 'l':
            self.direction = [1, 0, 0]
        elif ltype == 'arm' and side == 'r':
            self.direction = [-1, 0, 0]

        self.master_ctrl = None
        chain.Chain.__init__(self, side, name, segment=3)
        self.ik_chain = limbIK.LimbIK(side, name, length)
        self.fk_chain = limbFK.LimbFK(side, name, length)

        # master controller location
        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(self.direction).normalize()
