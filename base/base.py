import maya.cmds as cmds


from .. import util
from ..base import bone
from ..utility.rigging import transform


class Base(bone.Bone):
    """
    This module creates a single joint rig
    """

    def __init__(self, side, name):
        bone.Bone.__init__(self, side, name)

        self._rtype = 'base'

    def set_shape(self):
        self._shape = cmds.circle(
            nr=(0, 1, 0),
            c=(0, 0, 0),
            radius=self._scale,
            s=8,
            name=self.namer.tmp)[0]

    def create_locator(self):
        cmds.spaceLocator(n=self.locs[0])
        util.uniform_scale(self.locs[0], self._scale)
        cmds.parent(self.locs[0], util.G_LOC_GRP)

    def create_joint(self):
        cmds.select(clear=1)

        cmds.joint(name=self.jnts[0])
        util.uniform_scale(self.jnts[0], self._scale)

        transform.match_xform(self.jnts[0], self.locs[0])
        cmds.parent(self.jnts[0], util.G_JNT_GRP)
        # joint.orient_joint(self.jnts[0])

    def place_controller(self):
        cmds.duplicate(self._shape, name=self.ctrls[0])
        cmds.group(em=1, name=self.offsets[0])

        transform.clear_transform(self.ctrls[0], self.offsets[0], self.jnts[0])
        cmds.parent(self.offsets[0], util.G_CTRL_GRP)

    def add_constraint(self):
        cmds.parentConstraint(self.ctrls[0], self.jnts[0])