import maya.cmds as cmds


from .. import util, shape
from ..base import bone
from ..utility.rigging import transform


class Base(bone.Bone):
    """
    Create the rig system for a single joint
    """

    def __init__(self, side, name):
        """
        Extend: specify rig type
        """
        super(Base, self).__init__(side, name)
        self._rtype = 'base'

    def set_shape(self):
        """
        Override: use a circle as controller
        """
        self._shape = shape.make_circle(self._scale)

    def create_locator(self):
        """
        Override: create a single locator
        """
        cmds.spaceLocator(n=self.locs[0])
        util.uniform_scale(self.locs[0], self._scale)
        cmds.parent(self.locs[0], util.G_LOC_GRP)

    def create_joint(self):
        """
        Override: create a single joint
        """
        cmds.select(clear=1)

        cmds.joint(n=self.jnts[0])
        util.uniform_scale(self.jnts[0], self._scale)

        transform.match_xform(self.jnts[0], self.locs[0])
        cmds.parent(self.jnts[0], util.G_JNT_GRP)

    def place_controller(self):
        """
        Override: create a controller parented by an offset group
        """
        cmds.duplicate(self._shape, n=self.ctrls[0])
        cmds.group(em=1, n=self.offsets[0])

        transform.clear_xform(self.ctrls[0], self.offsets[0], self.jnts[0])
        cmds.parent(self.offsets[0], util.G_CTRL_GRP)

    def add_constraint(self):
        """
        Override: connect controller and joint
        """
        cmds.parentConstraint(self.ctrls[0], self.jnts[0])
