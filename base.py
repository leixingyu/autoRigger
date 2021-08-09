import maya.cmds as cmds
from utility import joint
from . import rig


class Base(rig.Bone):
    """ This module creates a single joint rig """

    def __init__(self, side='M', base_name='idPlaceHolder', start_pos=[0, 0, 0], scale=0.2):
        """ Initialize Base class with side and name

        :param side: str, 'M', 'L' or 'R'
        :param base_name: str
        """
        rig.Bone.__init__(self, side, base_name)

        self.meta_type = 'Base'
        self.ctrl_scale = 1

        self.start_pos = start_pos
        self.scale = scale

        self.initial_setup()

    def set_controller_shape(self):
        # Base controller shape
        circle_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Base_tempShape')[0]

        # Global Scale
        cmds.scale(self.ctrl_scale, self.ctrl_scale, self.ctrl_scale, circle_shape, relative=1)

    def create_locator(self):
        """ Create the rig guides for placement purpose """

        self.loc = cmds.spaceLocator(n=self.loc_name)
        grp = cmds.group(em=1, name=self.loc_grp_name)

        cmds.move(self.start_pos[0], self.start_pos[1], self.start_pos[2], self.loc, relative=1)
        cmds.scale(self.scale, self.scale, self.scale, self.loc)

        cmds.parent(self.loc, grp)
        cmds.parent(grp, self.loc_global_grp)

        return grp

    def create_joint(self):
        """ Create the rig joints based on the guide's transform """

        cmds.select(clear=1)
        locPos = cmds.xform(self.loc_name, q=1, t=1, ws=1)

        self.jnt = cmds.joint(p=locPos, name=self.jnt_name)
        cmds.setAttr(self.jnt + '.radius', 1)

        cmds.parent(self.jnt, self.jnt_global_grp)
        joint.orient_joint(self.jnt)
        return self.jnt

    def place_controller(self):
        """ Duplicate controller shapes and
        place them based on guide's and joint's transform """

        self.ctrl = cmds.duplicate('Base_tempShape', name=self.ctrl_name)[0]
        jntPos = cmds.xform(self.jnt, q=1, t=1, ws=1)
        locRot = cmds.xform(self.loc, q=1, ro=1, ws=1)

        # use offset group to clear out rotation on ctrl
        self.ctrl_offset_grp = cmds.group(em=1, name=self.ctrl_offset_grp_name)
        cmds.move(jntPos[0], jntPos[1], jntPos[2], self.ctrl_offset_grp)
        cmds.rotate(locRot[0], locRot[1], locRot[2], self.ctrl_offset_grp)

        # ctrl has transform relative to offset group, which is 0
        cmds.parent(self.ctrl, self.ctrl_offset_grp, relative=1)
        cmds.parent(self.ctrl_offset_grp, self.ctrl_global_grp)

    def add_constraint(self):
        """ Add all necessary constraints for the controller """

        cmds.parentConstraint(self.ctrl, self.jnt)





