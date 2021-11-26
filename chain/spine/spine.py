from ...chain import chainIK


class Spine(chainIK.ChainIK):
    """
    Create a IK control rig system for biped spine
    """

    def __init__(self, side, name, length=6.0, segment=6):
        """
        Override: specify the direction to be world Y-up
        """
        super(Spine, self).__init__(side, name, segment, length, [0, 1, 0], 0)
        self._rtype = 'spine'
