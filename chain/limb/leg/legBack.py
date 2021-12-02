from . import legQuad
from ....base import base


class LegBackItem(base.BaseItem):
    def __init__(self, name='quad-hind'):
        super(LegBackItem, self).__init__(name)

    def build_guide(self, side, base_name):
        self._obj = LegBack(side, base_name)
        self._obj.build_guide()


class LegBack(legQuad.LegQuad):
    """
    Create a rig system for quadruped back/hind leg
    """

    def __init__(self, side, name, distance=1.5, height=0.2):
        """
        Override: specify rig type
        """
        super(LegBack, self).__init__(side, name, distance, height, 0)
        self._rtype = 'back'
