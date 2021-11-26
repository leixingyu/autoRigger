from . import legQuad


class LegFront(legQuad.LegQuad):
    """
    Create a rig system for quadruped front leg
    """

    def __init__(self, side, name, distance=1.5, height=0.2):
        """
        Override: specify rig type
        """
        super(LegFront, self).__init__(side, name, distance, height, 1)
        self._rtype = 'front'
