from ...chain import chainIK
from ...base import base


class SpineItem(base.BaseItem):
    def __init__(self, name='biped-spine'):
        super(SpineItem, self).__init__(name)

    def build_guide(self, side, base_name):
        self._obj = Spine(side, base_name)
        self._obj.build_guide()


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
