import os

import maya.cmds as cmds
from Qt import QtWidgets, QtGui, _loadUi

from . import chain
from ..base import base, bone
from ..constant import UI_DIR
from ..utility.datatype import vector


class ChainFKItem(chain.ChainItem):
    def __init__(self, name='chain-fk'):
        super(ChainFKItem, self).__init__(name)

    def build_guide(self, *args, **kwargs):
        """Override"""
        self._obj = ChainFK(*args, **kwargs)
        self._obj.build_guide()


class ChainFK(chain.Chain):
    """
    Create a FK control rig system for a chain-like joints
    """

    def __init__(self, side, name, segment, length, direction):
        """
        Extend: specify length and direction of the chain

        :param length: float. total length of rig chain
        :param direction: vector.Vector. world direction from root to top node
        """
        super(ChainFK, self).__init__(side, name, segment)

        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(direction).normalize()

    @bone.update_base_name
    def create_namespace(self):
        """
        Override: create segment based naming
        """
        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base, index))
            self.jnts.append('{}{}fk_jnt'.format(self.base, index))
            self.ctrls.append('{}{}fk_ctrl'.format(self.base, index))
            self.offsets.append(
                '{}{}fk_offset'.format(self.base, index))

    def add_constraint(self):
        """
        Override: constraint joints with corresponding controllers
        """
        for index, jnt in enumerate(self.jnts):
            cmds.parentConstraint(self.ctrls[index], jnt)
