from ...chain import chainIK


class Spine(chainIK.ChainIK):
    """
    Create a IK control rig system for biped spine
    """

    def __init__(self, side, name, length=6.0, segment=6):
        """
        Override: specify the direction to be world Y-up
        """
        chainIK.ChainIK.__init__(
            self,
            side,
            name,
            segment,
            length,
            direction=[0, 1, 0],
            is_stretch=0)

        self._rtype = 'spine'
