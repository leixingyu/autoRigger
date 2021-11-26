from ...chain import chainFK
from ...constant import Side


class LimbFK(chainFK.ChainFK):
    """
    Create a FK control rig system for limb
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

        chainFK.ChainFK.__init__(
            self,
            side,
            name,
            segment=3,
            length=length,
            direction=self.direction)
