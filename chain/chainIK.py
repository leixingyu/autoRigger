import os

import maya.cmds as cmds
from Qt import QtWidgets, QtGui, _loadUi

from . import chain
from .. import util, shape
from ..base import bone, base
from ..constant import UI_DIR
from ..utility.datatype import vector


class ChainIKItem(base.BaseItem):
    def __init__(self, name='chain-ik'):
        super(ChainIKItem, self).__init__(name)
        self.extra_ui = 'chain.ui'
        self.init_extra()

    def build_guide(self, *args, **kwargs):
        """Override"""
        self._obj = ChainIK(*args, **kwargs)
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


class ChainIK(chain.Chain):
    """
    Create a IK control rig system for a chain-like joints
    """

    def __init__(self, side, name, segment, length, direction, is_stretch=0):
        """
        Extend: specify length and direction of the chain
        and whether it allows for stretching

        :param length: float. total length of rig chain
        :param direction: vector.Vector. world direction from root to top node
        :param is_stretch: bool. allow stretching for the rig
        """
        super(ChainIK, self).__init__(side, name, segment)

        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(direction).normalize()
        self.is_stretch = is_stretch

        self.clusters = list()
        self.ik_curve = None
        self.ik = None

    @bone.update_base_name
    def create_namespace(self):
        """
        Override: create segment based naming and IK names
        """
        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base, index))
            self.jnts.append('{}{}ik_jnt'.format(self.base, index))
            self.ctrls.append('{}{}ik_ctrl'.format(self.base, index))
            self.offsets.append(
                '{}{}ik_offset'.format(self.base, index))
            self.clusters.append('{}{}_cluster'.format(self.base, index))

        self.ik_curve = '{}ik_curve'.format(self.base)
        self.ik = '{}_ik'.format(self.base)

    def set_shape(self):
        """
        Override: set controller shape as sphere
        """
        self._shape = shape.make_sphere(self._scale)

    def build_ik(self):
        """
        Build the IK controller
        """
        curve_points = list()
        for index, jnt in enumerate(self.jnts):
            pos = cmds.xform(jnt, q=1, t=1, ws=1)
            curve_points.append(pos)

        cmds.curve(p=curve_points, n=self.ik_curve)
        cmds.setAttr(self.ik_curve+'.v', 0)

        # inherit transform will cause curve move/scale twice as much
        cmds.inheritTransform(self.ik_curve, off=1)
        cmds.parent(self.ik_curve, util.G_CTRL_GRP)

        cvs = cmds.ls(self.ik_curve+'.cv[0:]', fl=1)
        for index, cv in enumerate(cvs):
            cluster = cmds.cluster(cv, n=self.clusters[index])[-1]
            cmds.setAttr(cluster+'.v', 0)

        cmds.ikHandle(sj=self.jnts[0],
                      ee=self.jnts[self.segment-1],
                      n=self.ik, c=self.ik_curve, ccv=False,
                      pcv=1, roc=1, sol='ikSplineSolver')

        cmds.setAttr(self.ik+'.v', 0)
        cmds.parent(self.ik, util.G_CTRL_GRP)

    def add_constraint(self):
        """
        Override: constraint joints with corresponding controllers
        add IK system and stretch node network
        """
        self.build_ik()

        for index, cluster in enumerate(self.clusters):
            cmds.parent(cluster+'Handle', self.ctrls[index])

        # enable advance twist control
        cmds.setAttr(self.ik+'.dTwistControlEnable', 1)
        cmds.setAttr(self.ik+'.dWorldUpType', 4)
        cmds.connectAttr(
            self.ctrls[0]+'.worldMatrix[0]',
            self.ik+'.dWorldUpMatrix', f=1)
        cmds.connectAttr(
            self.ctrls[-1]+'.worldMatrix[0]',
            self.ik+'.dWorldUpMatrixEnd', f=1)

        if not self.is_stretch:
            return

        self.add_stretch()

    def add_stretch(self):
        """
        Add node network for joint stretch ability
        :return:
        """
        # FIXME: cycle evaluation when stretching

        # mid cluster weighting
        for index, offset in enumerate(self.offsets):
            if self.ctrls[index] not in [self.ctrls[0], self.ctrls[-1]]:
                weight = (1.00 / (self.segment-1)) * index
                cmds.pointConstraint(self.ctrls[-1], offset, w=weight, mo=1)
                cmds.pointConstraint(self.ctrls[0], offset, w=1-weight, mo=1)

        # scaling of the spine
        arc_len = cmds.arclen(self.ik_curve, constructionHistory=1)
        ik_info = self.ik_curve + '_info'
        cmds.rename(arc_len, ik_info)
        cmds.parent(self.ik_curve, util.G_CTRL_GRP)
        cmds.setAttr(self.ik_curve+'.v', 0)

        # create curve length node and multiply node
        init_len = cmds.getAttr('{}.arcLength'.format(ik_info))
        stretch_node = cmds.shadingNode(
            'multiplyDivide',
            asUtility=1,
            n=self.ctrls[0]+'Stretch')
        cmds.setAttr(stretch_node+'.operation', 2)
        cmds.setAttr(stretch_node+'.i2x', init_len)
        cmds.connectAttr('{}.arcLength'.format(ik_info), stretch_node+'.i1x')

        for i in range(self.segment):
            cmds.connectAttr(stretch_node+'.ox', self.jnts[i]+'.sx')
