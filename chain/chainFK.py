import os

import maya.cmds as cmds
from Qt import QtWidgets, QtGui, _loadUi

from . import chain
from ..base import base, bone
from ..constant import UI_DIR
from ..utility.datatype import vector


class ChainFKItem(base.BaseItem):
    def __init__(self, name='chain-fk'):
        super(ChainFKItem, self).__init__(name)
        self.extra_ui = 'chain.ui'
        self.init_extra()

    def build_guide(self, *args, **kwargs):
        """Override"""
        self._obj = ChainFK(*args, **kwargs)
        self._obj.build_guide()

    def init_extra(self):
        """Override"""
        self.extra_widget = QtWidgets.QWidget()
        _loadUi(os.path.join(UI_DIR, self.extra_ui), self.extra_widget)

    def parse_extra(self):
        seg = self.widget.ui_seg_sbox.value()
        length = self.widget.ui_len_sbox.value()
        direction = self.widget.ui_dir_cbox.currentText()

        return [seg, length, direction]


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
