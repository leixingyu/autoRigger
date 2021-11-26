import maya.cmds as cmds

from .. import util
from ..base import base
from ..utility.rigging import joint, transform


class Chain(base.Base):
    """
    Abstract class for creating chain-like rig system
    such as finger, spine, tail and more
    """

    def __init__(self, side, name, segment):
        """
        Extend: specify rig type and add more instance var for convenience

        :param segment: int. number of joints on the chain
        """
        super(Chain, self).__init__(side, name)
        self._rtype = 'chain'

        self.segment = segment
        self.interval = None
        self.dir = None
        self.curve = None

    def create_locator(self):
        """
        Override: create a single chain-like locator
        parented in hierarchical order
        """
        for index in range(self.segment):
            cmds.spaceLocator(n=self.locs[index])
            if not index:
                util.uniform_scale(self.locs[index], self._scale)
            else:
                cmds.parent(self.locs[index], self.locs[index-1], r=1)
                distance = (self.interval * self.dir).as_list
                util.move(self.locs[index], distance)
        cmds.parent(self.locs[0], util.G_LOC_GRP)

    def place_controller(self):
        """
        Override: create and place controllers parented in hierarchical order
        """
        for index in range(self.segment):
            cmds.duplicate(self._shape, n=self.ctrls[index])
            cmds.rotate(0, 0, 90, self.ctrls[index])
            cmds.group(em=1, n=self.offsets[index])
            transform.clear_xform(
                self.ctrls[index],
                self.offsets[index],
                self.jnts[index]
            )
            if index:
                cmds.parent(self.offsets[index], self.ctrls[index-1])

        cmds.parent(self.offsets[0], util.G_CTRL_GRP)

    def create_joint(self):
        """
        Override: create a single joint chain
        """
        cmds.select(clear=1)
        for index in range(self.segment):
            cmds.joint(n=self.jnts[index])
            transform.match_xform(self.jnts[index], self.locs[index])
            util.uniform_scale(self.jnts[index], self._scale)

        cmds.parent(self.jnts[0], util.G_JNT_GRP)
        joint.orient_joint(self.jnts[0])
