import maya.cmds as cmds

from utility.algorithm import strGenerator
from autoRigger import util


TMP_PREFIX = 'tmp_'


class Bone(object):
    """ Abstract class for joint """

    namer = strGenerator.StrGenerator(TMP_PREFIX, 8)

    def __init__(self, side, name):
        """ Initialize Base class with side and name

        :param side: str. 'm', 'l' or 'r'
        :param name: str
        """

        util.create_outliner_grp()

        self._side = side
        self._name = name
        self._rtype = None

        self._shape = None

        self.base_name = None
        self.locs = list()
        self.jnts = list()
        self.ctrls = list()
        self.offsets = list()

    def create_namespace(self):
        """ Create naming convention for complex module """
        self.base_name = '{}_{}_{}'.format(self._rtype, self._side, self._name)

        self.locs.append('{}_loc'.format(self.base_name))
        self.jnts.append('{}_jnt'.format(self.base_name))
        self.ctrls.append('{}_ctrl'.format(self.base_name))
        self.offsets.append('{}_offset'.format(self.base_name))

    def set_controller_shape(self):
        """ Setting up controller curve shapes as templates """

        pass

    def set_locator_attr(self):
        """ Setup Locator initial position and size as guide """

        pass

    def create_locator(self):
        """ Create the rig guides for placement purpose """

        pass

    def color_locator(self):
        """
        Color-code the guide locators based on left, right, middle side
        """

        locs = cmds.ls('{}*_loc'.format(self.base_name))
        for loc in locs:
            if cmds.nodeType(loc) in ['transform']:
                cmds.setAttr(loc + '.overrideEnabled', 1)
                if self._side == 'l':
                    cmds.setAttr(loc + '.overrideColor', 6)
                elif self._side == 'r':
                    cmds.setAttr(loc + '.overrideColor', 13)
                else:
                    cmds.setAttr(loc + '.overrideColor', 17)

    def create_joint(self):
        """ Create the rig joints based on the guide's transform """

        pass

    def place_controller(self):
        """
        Duplicate controller shapes and
        place them based on guide's and joint's transform
        """

        pass

    def color_controller(self):
        """
        Colorize the controller based on left, right, middle side
        """

        ctrls = cmds.ls('{}*_ctrl'.format(self.base_name))
        for ctrl in ctrls:
            if cmds.nodeType(ctrl) in ['nurbsCurve', 'transform']:
                cmds.setAttr(ctrl + '.overrideEnabled', 1)
                if self._side == 'l':
                    cmds.setAttr(ctrl + '.overrideColor', 6)
                elif self._side == 'r':
                    cmds.setAttr(ctrl + '.overrideColor', 13)
                else:
                    cmds.setAttr(ctrl + '.overrideColor', 17)

    def add_constraint(self):
        """ Add all necessary constraints for the controller """

        pass

    def delete_guide(self):
        """ Delete all locator guides to de-clutter the scene """

        grp = cmds.ls('*_loc')
        cmds.delete(grp)

    @staticmethod
    def delete_shape():
        """ Delete control template shape to de-clutter the scene """

        shapes = cmds.ls('{}*'.format(TMP_PREFIX))
        cmds.delete(shapes)

    def lock_controller(self):
        """ Not exposing specific channels of controllers """

        pass

    def build_guide(self):
        """
        Create the entire rig guide setup
        """
        self.create_namespace()
        self.set_locator_attr()
        self.create_locator()
        self.color_locator()

    def build_rig(self):
        """
        Build the full rig based on the guide, without skinning
        """

        self.create_joint()
        self.set_controller_shape()
        self.place_controller()

        self.delete_guide()
        self.delete_shape()

        self.color_controller()
        self.add_constraint()

        # clean ups
        self.lock_controller()
