from ...chain import chainIK


class Spine(chainIK.ChainIK):
    """
    This module creates a biped spine rig
    """

    def __init__(self, side, name, length=6.0, segment=6):
        chainIK.ChainIK.__init__(self, side, name, segment, length, direction=[0, 1, 0], is_stretch=0)

        self._rtype = 'spine'
