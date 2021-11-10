from functools import wraps

import maya.cmds as cmds

from .. import util
from ..constant import Side
from utility.algorithm import strGenerator
from utility.datatype import color
from utility.rigging import transform


TMP_PREFIX = 'tmp_'
Yellow = color.ColorRGB.yellow()
Blue = color.ColorRGB.blue()
Red = color.ColorRGB.red()


def update_base_name(func):
    """
    Update the base name attribute in the rig component
    """
    @wraps(func)
    def wrap(self):
        self.base_name = '{}_{}_{}'.format(self._rtype, self._side.value, self._name)
        func(self)
    return wrap


class Bone(object):
    """
    Abstract class for joint creation
    The two fundamental steps are:
    1. build_guide: create guide locators for placement
    2. build_rig: create joints and controller following the guide
    """

    namer = strGenerator.StrGenerator(TMP_PREFIX, 8)

    def __init__(self, side, name):
        """
        Initialize Base class with side and name

        :param side: str. Side.MIDDLE, Side.LEFT or Side.RIGHT
        :param name: str. name of the bone rig
        """
        util.create_outliner_grp()

        self._components = list()

        self._side = side
        self._name = name
        self._rtype = None
        self._scale = 1

        self._shape = None

        self.base_name = None
        self.locs = list()
        self.jnts = list()
        self.ctrls = list()
        self.offsets = list()

    @update_base_name
    def create_namespace(self):
        """
        Create naming conventions for the current rig type
        """
        self.locs.append('{}_loc'.format(self.base_name))
        self.jnts.append('{}_jnt'.format(self.base_name))
        self.ctrls.append('{}_ctrl'.format(self.base_name))
        self.offsets.append('{}_offset'.format(self.base_name))

    def set_controller_shape(self):
        """
        Set up controller curve shapes
        """
        pass

    def create_locator(self):
        """
        Create the rig guides for placement purpose
        """
        pass

    def color_locator(self):
        """
        Color-code the guide locators based on left, right, middle side
        """
        for loc in self.locs:
            try:
                if self._side == Side.LEFT:
                    transform.colorize_rgb_normalized(loc, Blue.r, Blue.g, Blue.b)
                elif self._side == Side.RIGHT:
                    transform.colorize_rgb_normalized(loc, Red.r, Red.g, Red.b)
                else:
                    transform.colorize_rgb_normalized(loc, Yellow.r, Yellow.g, Yellow.b)
            except RuntimeError:
                # some locators have namespace created but doesn't exists
                pass

    def create_joint(self):
        """
        Create the rig joints based on the guide's transform
        """
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
        for ctrl in self.ctrls:
            try:
                if self._side == Side.LEFT:
                    transform.colorize_rgb_normalized(ctrl, Blue.r, Blue.g, Blue.b)
                elif self._side == Side.RIGHT:
                    transform.colorize_rgb_normalized(ctrl, Red.r, Red.g, Red.b)
                else:
                    transform.colorize_rgb_normalized(ctrl, Yellow.r, Yellow.g, Yellow.b)
            except RuntimeError:
                # some controllers have namespace created but doesn't exist
                pass

    def add_constraint(self):
        """
        Add all necessary constraints for the controller
        """
        pass

    def delete_guide(self):
        """
        Delete all locator guides to de-clutter the scene
        """
        try:
            cmds.delete(self.locs)
        except ValueError:
            pass

    @staticmethod
    def delete_shape():
        """
        Delete control template shape to de-clutter the scene
        """
        cmds.delete(cmds.ls('{}*'.format(TMP_PREFIX)))

    def lock_controller(self):
        """
        Not exposing specific channels of controllers
        """
        pass

    def build_guide(self):
        """
        Create the entire rig guide setup
        """
        self.create_namespace()
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
