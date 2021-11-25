from ...constant import Side
from ...chain import chainFK


class LimbFK(chainFK.ChainFK):
    """
    Abstract FK limb rig
    """

    def __init__(self, side, name, length, ltype='null'):
        self._rtype = ltype

        self.direction = [0, -1, 0]
        if ltype == 'arm' and side == Side.LEFT:
            self.direction = [1, 0, 0]
        elif ltype == 'arm' and side == Side.RIGHT:
            self.direction = [-1, 0, 0]

        chainFK.ChainFK.__init__(
            self,
            side,
            name,
            segment=3,
            length=length,
            direction=self.direction)
