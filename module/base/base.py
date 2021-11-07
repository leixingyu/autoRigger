import maya.cmds as cmds

from autoRigger.module.base import bone
from autoRigger import util
from utility.rigging import joint


class Base(bone.Bone):
    """ This module creates a single joint rig """

    def __init__(self, side, name):
        """ Initialize Base class with side and name

        :param side: str, 'M', 'L' or 'R'
        :param name: str
        """
        bone.Bone.__init__(self, side, name)

        self._rtype = 'base'
        self.scale = 0.2

    def set_controller_shape(self):
        # Base controller shape
        self._shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name=self.namer.tmp)[0]

    def create_locator(self):
        """ Create the rig guides for placement purpose """

        cmds.spaceLocator(n=self.locs[0])
        cmds.scale(self.scale, self.scale, self.scale, self.locs[0])
        cmds.parent(self.locs[0], util.G_LOC_GRP)

        return self.locs[0]

    def create_joint(self):
        """ Create the rig joints based on the guide's transform """

        cmds.select(clear=1)
        loc_pos = cmds.xform(self.locs[0], q=1, t=1, ws=1)

        cmds.joint(p=loc_pos, name=self.jnts[0])

        cmds.parent(self.jnts[0], util.G_JNT_GRP)
        joint.orient_joint(self.jnts[0])
        return self.jnts[0]

    def place_controller(self):
        """
        Duplicate controller shapes and
        place them based on guide's and joint's transform
        """

        # TODO: use nurbs clear transform on this
        cmds.duplicate(self._shape, name=self.ctrls[0])

        # used to clear out ctrl transform offset
        cmds.group(em=1, name=self.offsets[0])
        util.match_xform(self.offsets[0], self.jnts[0])

        # ctrl has transform relative to offset group, which is 0
        cmds.parent(self.ctrls[0], self.offsets[0], relative=1)
        cmds.parent(self.offsets[0], util.G_CTRL_GRP)

    def add_constraint(self):
        """ Add all necessary constraints for the controller """

        cmds.parentConstraint(self.ctrls[0], self.jnts[0])
