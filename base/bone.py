from functools import wraps

import maya.cmds as cmds

from .. import util
from ..constant import Side
from ..utility.useful import strGenerator
from ..utility.datatype import color
from ..utility.rigging import transform


TMP_PREFIX = 'tmp_'
Yellow = color.ColorRGB.yellow()
Blue = color.ColorRGB.blue()
Red = color.ColorRGB.red()


def update_base_name(func):
    """
    Update the base name attribute in the rig comp
    """
    @wraps(func)
    def wrap(self):
        self.base = '{}_{}_{}'.format(
            self._rtype, self._side.value, self._name)
        func(self)
    return wrap


class Bone(object):
    """
    Abstract class for creating rig control system, without the skinning

    The two fundamental steps are:
    1. build_guide: create guide locators for placement
    2. build_rig: create joints and controller following the guide

    # Attribute:
    namer. a string generator for temporary naming
    """

    namer = strGenerator.StrGenerator(TMP_PREFIX, 8)

    def __init__(self, side, name):
        """
        Initialization

        :param side: Side enum. the side where the rig lays on
        :param name: str. name of the rig
        """
        super(Bone, self).__init__()
        util.create_outliner_grp()

        self._side = side
        self._name = name
        self._rtype = None
        self._scale = 1

        # components and controller shape
        self._comps = list()
        self._shape = None

        # naming related instance vars
        self.base = None
        self.locs = list()
        self.jnts = list()
        self.ctrls = list()
        self.offsets = list()

    @update_base_name
    def create_namespace(self):
        """
        Create naming conventions for the current rig type
        """
        if self._comps:
            for c in self._comps:
                c.create_namespace()

        self.locs.append('{}_loc'.format(self.base))
        self.jnts.append('{}_jnt'.format(self.base))
        self.ctrls.append('{}_ctrl'.format(self.base))
        self.offsets.append('{}_offset'.format(self.base))

    def set_shape(self):
        """
        Set up controller shape with nurbs curve
        """
        if self._comps:
            for c in self._comps:
                c.set_shape()

    def create_locator(self):
        """
        Create the rig guides using locators for placement purpose
        """
        if self._comps:
            for c in self._comps:
                c.create_locator()

    def color_locator(self):
        """
        Color-code the guide locators based on rig side
        """
        if self._comps:
            for c in self._comps:
                c.color_locator()

        for loc in self.locs:
            try:
                if self._side == Side.LEFT:
                    transform.colorize_rgb_normalized(
                        loc,
                        Blue.r_normalized,
                        Blue.g_normalized,
                        Blue.b_normalized
                    )
                elif self._side == Side.RIGHT:
                    transform.colorize_rgb_normalized(
                        loc,
                        Red.r_normalized,
                        Red.g_normalized,
                        Red.b_normalized
                    )
                else:
                    transform.colorize_rgb_normalized(
                        loc,
                        Yellow.r_normalized,
                        Yellow.g_normalized,
                        Yellow.b_normalized
                    )
            except RuntimeError:
                # some locators have namespace created but doesn't exists
                pass

    def create_joint(self):
        """
        Create the rig joints based on the guide locators' transform
        """
        if self._comps:
            for c in self._comps:
                c.create_joint()

    def place_controller(self):
        """
        Place controller (nurbs curve) based on guide's and joint's transform
        """
        if self._comps:
            for c in self._comps:
                c.place_controller()

    def color_controller(self):
        """
        Color-code the controller based on rig side
        """
        if self._comps:
            for c in self._comps:
                c.color_controller()

        for ctrl in self.ctrls:
            try:
                if self._side == Side.LEFT:
                    transform.colorize_rgb_normalized(
                        ctrl,
                        Blue.r_normalized,
                        Blue.g_normalized,
                        Blue.b_normalized
                    )
                elif self._side == Side.RIGHT:
                    transform.colorize_rgb_normalized(
                        ctrl,
                        Red.r_normalized,
                        Red.g_normalized,
                        Red.b_normalized
                    )
                else:
                    transform.colorize_rgb_normalized(
                        ctrl,
                        Yellow.r_normalized,
                        Yellow.g_normalized,
                        Yellow.b_normalized
                    )
            except RuntimeError:
                # some controllers have namespace created but doesn't exist
                pass

    def add_constraint(self):
        """
        Add all constraints for the controllers and joints in the rig system
        """
        if self._comps:
            for c in self._comps:
                c.add_constraint()

    def delete_guide(self):
        """
        Delete all locator guides to de-clutter the scene
        """
        if self._comps:
            for c in self._comps:
                c.delete_guide()

        try:
            cmds.delete(self.locs)
        except ValueError:
            pass

    @staticmethod
    def delete_shape():
        """
        Delete controller temp shape to de-clutter the scene
        """
        cmds.delete(cmds.ls('{}*'.format(TMP_PREFIX)))

    def lock_controller(self):
        """
        Lock and hide specific channels of the controllers
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
        Build the full rig system based on the guide
        """
        self.create_joint()
        self.set_shape()
        self.place_controller()
        self.delete_guide()
        self.delete_shape()
        self.color_controller()
        self.add_constraint()
        self.lock_controller()
