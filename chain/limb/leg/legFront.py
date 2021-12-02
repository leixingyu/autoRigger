from . import legQuad
from ....base import base


class LegFrontItem(base.BaseItem):
    def __init__(self, name='quad-front'):
        super(LegFrontItem, self).__init__(name)

    def build_guide(self, side, base_name):
        self._obj = LegFront(side, base_name)
        self._obj.build_guide()


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
