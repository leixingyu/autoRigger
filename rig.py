import maya.cmds as cmds


class Bone(object):
    """ Abstract class for joint """

    def __init__(self, side, base_name):
        """ Initialize Base class with side and name

        :param side: str, 'M', 'L' or 'R'
        :param base_name: str
        """

        self.side = side
        self.base_name = base_name

        self.meta_type = 'Abstract'

    def initial_setup(self):
        # all initial setup

        self.assign_naming()
        self.assign_secondary_naming()
        self.create_outliner_grp()

    def assign_naming(self):
        """ Create primary naming convention """

        self.loc_global_grp = '_Locators'
        self.ctrl_global_grp = '_Controllers'
        self.jnt_global_grp = '_Joints'
        self.mesh_global_grp = '_Meshes'

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

        for grp in [self.loc_global_grp, self.ctrl_global_grp, self.jnt_global_grp, self.mesh_global_grp]:
            if not cmds.ls(grp):
                cmds.group(em=1, name=grp)

    @staticmethod
    def set_controller_shape():
        """ Setting up controller curve shapes as templates """

        pass

    def set_locator_attr(self):
        """ Setup Locator initial position and size as guide """

        pass

    def create_locator(self):
        """ Create the rig guides for placement purpose """

        pass

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

    def create_joint(self):
        """ Create the rig joints based on the guide's transform """

        pass

    def place_controller(self):
        """ Duplicate controller shapes and
        place them based on guide's and joint's transform """

        pass

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

    def add_constraint(self):
        """ Add all necessary constraints for the controller """

        pass

    def delete_guide(self):
        """ Delete all locator guides to de-clutter the scene """

        grp = cmds.ls(self.loc_grp_name)
        cmds.delete(grp)

    @staticmethod
    def delete_shape():
        """ Delete control template shape to de-clutter the scene """

        shapes = cmds.ls('*_tempShape*')
        cmds.delete(shapes)

    def lock_controller(self):
        """ Not exposing specific channels of controllers """

        pass

    def build_guide(self):
        """ Create the entire rig guide setup """

        self.set_locator_attr()
        self.create_locator()
        self.color_locator()

    def build_rig(self):
        """ Build the full rig based on the guide, without skinning """

        self.create_joint()
        self.set_controller_shape()
        self.place_controller()

        self.delete_guide()
        self.delete_shape()

        self.color_controller()
        self.add_constraint()

        # clean ups
        self.lock_controller()
