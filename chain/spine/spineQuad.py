from ...chain import chainIK


class SpineQuad(chainIK.ChainIK):
    """
    Create a IK control rig system for quadruped spine
    """

    def __init__(self, side, name, length=6.0, segment=6):
        """
        Override: specify the direction to be world Z-forward
        """
        super(SpineQuad, self).__init__(side, name, segment, length, [0, 0, 1], 0)

        self._rtype = 'qspine'
