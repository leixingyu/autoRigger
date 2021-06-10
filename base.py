import maya.cmds as cmds
from utility import joint


class Base(object):
    """ This module creates a single joint rig """

    def __init__(self, side='M', base_name='idPlaceHolder'):
        """ Initialize Base class with side and name

        :param side: str, 'M', 'L' or 'R'
        :param base_name: str
        """

        self.side = side
        self.base_name = base_name
        self.meta_type = 'Base'
        self.assign_naming()
        self.create_outliner_grp()
        self.set_locator_attr()

    def assign_naming(self):
        """ Create primary naming convention """

        self.loc_grp = '_Locators'
        self.ctrl_grp = '_Controllers'
        self.jnt_grp = '_Joints'
        self.mesh_grp = '_Meshes'

        self.name = '{}_{}_{}'.format(self.meta_type, self.side, self.base_name)

        self.loc_name = '{}_loc'.format(self.name)
        self.loc_grp_name = '{}_locGrp'.format(self.name)
        self.jnt_name = '{}_jnt'.format(self.name)
        self.jnt_grp_name = '{}_jntGrp'.format(self.name)
        self.ctrl_name = '{}_ctrl'.format(self.name)
        self.ctrl_grp_name = '{}_ctrlGrp'.format(self.name)
        self.ctrl_offset_grp_name = '{}_offset'.format(self.name)

    def assign_secondary_naming(self):
        """ Create secondary naming convention for complex module """

        pass

    def create_outliner_grp(self):
        """ Create different groups in the outliner """

        for grp in [self.loc_grp, self.ctrl_grp, self.jnt_grp, self.mesh_grp]:
            if not cmds.ls(grp):
                cmds.group(em=1, name=grp)

    @staticmethod
    def set_controller_shape():
        """ Setting up controller curve shapes as templates """

        pass

    def set_locator_attr(self, start_pos=[0, 0, 0], scale=0.2):
        """ Setup Locator initial position and size as guide

        :param start_pos: vector 3 list
        :param scale: float
        """

        self.start_pos = start_pos
        self.scale = scale

    def build_guide(self):
        """ Create the rig guides for placement purpose """

        self.loc = cmds.spaceLocator(n=self.loc_name)
        grp = cmds.group(em=1, name=self.loc_grp_name)

        cmds.move(self.start_pos[0], self.start_pos[1], self.start_pos[2], self.loc, relative=1)
        cmds.scale(self.scale, self.scale, self.scale, self.loc)

        cmds.parent(self.loc, grp)
        cmds.parent(grp, self.loc_grp)

        self.color_locator()
        return grp

    def color_locator(self):
        """ Color-code the guide locators based on left, right, middle side """

        locs = cmds.ls('{}*_loc'.format(self.name))
        for loc in locs:
            if cmds.nodeType(loc) in ['transform']:
                cmds.setAttr(loc + '.overrideEnabled', 1)
                if self.side == 'L':
                    cmds.setAttr(loc + '.overrideColor', 6)
                elif self.side == 'R':
                    cmds.setAttr(loc + '.overrideColor', 13)
                else:
                    cmds.setAttr(loc + '.overrideColor', 17)

    def construct_joint(self):
        """ Create the rig joints based on the guide's transform """

        cmds.select(clear=1)
        locPos = cmds.xform(self.loc_name, q=1, t=1, ws=1)

        self.jnt = cmds.joint(p=locPos, name=self.jnt_name)
        cmds.setAttr(self.jnt + '.radius', 1)

        cmds.parent(self.jnt, self.jnt_grp)
        joint.orient_joint(self.jnt)
        return self.jnt

    def place_controller(self):
        """ Duplicate controller shapes and
        place them based on guide's and joint's transform """

        self.ctrl = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name=self.ctrl_name)[0]
        jntPos = cmds.xform(self.jnt, q=1, t=1, ws=1)
        locRot = cmds.xform(self.loc, q=1, ro=1, ws=1)

        # use offset group to clear out rotation on ctrl
        self.ctrl_offset_grp = cmds.group(em=1, name=self.ctrl_offset_grp_name)
        cmds.move(jntPos[0], jntPos[1], jntPos[2], self.ctrl_offset_grp)
        cmds.rotate(locRot[0], locRot[1], locRot[2], self.ctrl_offset_grp)

        # ctrl has transform relative to offset group, which is 0
        cmds.parent(self.ctrl, self.ctrl_offset_grp, relative=1)
        cmds.parent(self.ctrl_offset_grp, self.ctrl_grp)

    def add_constraint(self):
        """ Add all necessary constraints for the controller """

        cmds.parentConstraint(self.ctrl, self.jnt)

    def delete_guide(self):
        """ Delete all locator guides to de-clutter the scene """

        grp = cmds.ls(self.loc_grp_name)
        cmds.delete(grp)

    @staticmethod
    def delete_shape():
        """ Delete control template shape to de-clutter the scene """

        shapes = cmds.ls('*_tempShape*')
        cmds.delete(shapes)

    def color_controller(self):
        """ Colorize the controller based on left, right, middle side """

        ctrls = cmds.ls('{}*_ctrl'.format(self.name))
        for ctrl in ctrls:
            if cmds.nodeType(ctrl) in ['nurbsCurve', 'transform']:
                cmds.setAttr(ctrl + '.overrideEnabled', 1)
                if self.side == 'L':
                    cmds.setAttr(ctrl + '.overrideColor', 6)
                elif self.side == 'R':
                    cmds.setAttr(ctrl + '.overrideColor', 13)
                else:
                    cmds.setAttr(ctrl + '.overrideColor', 17)

    def lock_controller(self):
        """ Not exposing specific channels of controllers """

        pass

    def build_rig(self):
        """ Build the full rig based on the guide, without skinning """

        self.construct_joint()
        self.place_controller()
        self.delete_guide()
        self.color_controller()
        self.add_constraint()
        self.lock_controller()




