from ..chain import chainFKIK


class Tail(chainFKIK.ChainFKIK):
    """
    Create a Tail rig system with FK/IK controls
    """

    def __init__(self, side, name, segment=6, length=4.0, direction=[0, -1, 0]):
        """
        Extend: specify rig type
        """
        super(Tail, self).__init__(side, name, segment, length, direction)
        # self._rtype = 'tail'
