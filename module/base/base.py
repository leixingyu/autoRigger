import maya.cmds as cmds

from utility.rigging import joint

from autoRigger.module.base import bone
from autoRigger import util


class Base(bone.Bone):
    """ This module creates a single joint rig """

    def __init__(self, side, name, rig_type='Base', pos=[0, 0, 0]):
        """ Initialize Base class with side and name

        :param side: str, 'M', 'L' or 'R'
        :param name: str
        """
        bone.Bone.__init__(self, side, name, rig_type)

        self.pos = pos
        self.scale = 0.2

    def set_controller_shape(self):
        # Base controller shape
        self._shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Base_tempShape')[0]

    def create_locator(self):
        """ Create the rig guides for placement purpose """

        cmds.spaceLocator(n=self.loc)

        cmds.move(self.pos[0], self.pos[1], self.pos[2], self.loc, relative=1)
        cmds.scale(self.scale, self.scale, self.scale, self.loc)

        cmds.parent(self.loc, util.G_LOC_GRP)

        return self.loc

    def create_joint(self):
        """ Create the rig joints based on the guide's transform """

        cmds.select(clear=1)
        loc_pos = cmds.xform(self.loc, q=1, t=1, ws=1)

        cmds.joint(p=loc_pos, name=self.jnt)

        cmds.parent(self.jnt, util.G_JNT_GRP)
        joint.orient_joint(self.jnt)
        return self.jnt

    def place_controller(self):
        """
        Duplicate controller shapes and
        place them based on guide's and joint's transform
        """

        # TODO: check why use locator rotation instead of joint

        cmds.duplicate(self._shape, name=self.ctrl)

        # used to clear out ctrl transform offset
        self.ctrl_offset = cmds.group(em=1, name=self.ctrl_offset)
        util.matchXform(self.ctrl_offset, self.jnt)

        # ctrl has transform relative to offset group, which is 0
        cmds.parent(self.ctrl, self.ctrl_offset, relative=1)
        cmds.parent(self.ctrl_offset, util.G_CTRL_GRP)

    def add_constraint(self):
        """ Add all necessary constraints for the controller """

        cmds.parentConstraint(self.ctrl, self.jnt)
