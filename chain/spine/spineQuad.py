from ...chain import chainIK


class SpineQuad(chainIK.ChainIK):
    """
    Create a IK control rig system for quadruped spine
    """

    def __init__(self, side, name, length=6.0, segment=6):
        """
        Override: specify the direction to be world Z-forward
        """
        chainIK.ChainIK.__init__(
            self,
            side,
            name,
            segment,
            length,
            direction=[0, 0, 1],
            is_stretch=0)

        self._rtype = 'qspine'
