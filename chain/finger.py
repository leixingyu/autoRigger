from ..constant import Side
from autoRigger.chain import chainFK


class Finger(chainFK.ChainFK):
    """
    Rig module for FK finger
    """

    def __init__(self, side, name, segment=4, length=2.0):
        direction = [-1, 0, 0]
        if side == Side.LEFT:
            direction = [1, 0, 0]

        chainFK.ChainFK.__init__(self, side, name, segment, length, direction)
        self._rtype = 'finger'
