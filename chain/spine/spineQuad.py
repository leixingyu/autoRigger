from ...chain import chainIK


class SpineQuad(chainIK.ChainIK):
    """
    This module creates a biped spine rig
    """

    def __init__(self, side, name, length=6.0, segment=6):
        chainIK.ChainIK.__init__(self, side, name, segment, length, direction=[0, 0, 1], is_stretch=0)

        self._rtype = 'qspine'
