import maya.cmds as cmds
from utility.rigging import joint
from . import rig


class Base(rig.Bone):
    """ This module creates a single joint rig """

    def __init__(self, side, name, rig_type='Base', pos=[0, 0, 0], scale=0.2):
        """ Initialize Base class with side and name

        :param side: str, 'M', 'L' or 'R'
        :param name: str
        """
        rig.Bone.__init__(self, side, name, rig_type)
        self.ctrl_scale = 1

        self.pos = pos
        self.scale = scale

    def set_controller_shape(self):
        # Base controller shape
        circle_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Base_tempShape')[0]

        # Global Scale
        cmds.scale(self.ctrl_scale, self.ctrl_scale, self.ctrl_scale, circle_shape, relative=1)

    def create_locator(self):
        """ Create the rig guides for placement purpose """

        cmds.spaceLocator(n=self.loc)
        grp = cmds.group(em=1, name=self.loc_grp)

        cmds.move(self.pos[0], self.pos[1], self.pos[2], self.loc, relative=1)
        cmds.scale(self.scale, self.scale, self.scale, self.loc)

        cmds.parent(self.loc, grp)
        cmds.parent(grp, self.loc_global_grp)

        return grp

    def create_joint(self):
        """ Create the rig joints based on the guide's transform """

        cmds.select(clear=1)
        loc_pos = cmds.xform(self.loc, q=1, t=1, ws=1)

        cmds.joint(p=loc_pos, name=self.jnt)
        cmds.setAttr(self.jnt+'.radius', 1)

        cmds.parent(self.jnt, self.jnt_global_grp)
        joint.orient_joint(self.jnt)
        return self.jnt

    def place_controller(self):
        """ Duplicate controller shapes and
        place them based on guide's and joint's transform """

        cmds.duplicate('Base_tempShape', name=self.ctrl)
        jnt_pos = cmds.xform(self.jnt, q=1, t=1, ws=1)
        loc_rot = cmds.xform(self.loc, q=1, ro=1, ws=1)

        # use offset group to clear out rotation on ctrl
        self.ctrl_offset = cmds.group(em=1, name=self.ctrl_offset)
        cmds.move(jnt_pos[0], jnt_pos[1], jnt_pos[2], self.ctrl_offset)
        cmds.rotate(loc_rot[0], loc_rot[1], loc_rot[2], self.ctrl_offset)

        # ctrl has transform relative to offset group, which is 0
        cmds.parent(self.ctrl, self.ctrl_offset, relative=1)
        cmds.parent(self.ctrl_offset, self.ctrl_global_grp)

    def add_constraint(self):
        """ Add all necessary constraints for the controller """

        cmds.parentConstraint(self.ctrl, self.jnt)
