import maya.cmds as cmds

from autoRigger import util
from . import chain

from utility.algorithm import vector
reload(vector)


class ChainIK(chain.Chain):

    def __init__(self, side, name, length=4.0, segment=6, direction=[0, 1, 0]):
        self.clusters = list()
        self.ik_curve = None
        self.ik = None

        chain.Chain.__init__(self, side, name, length, segment, direction)

    def assign_secondary_naming(self):
        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base_name, index))
            self.jnts.append('{}{}ik_jnt'.format(self.base_name, index))
            self.ctrls.append('{}{}ik_ctrl'.format(self.base_name, index))
            self.offsets.append(
                '{}{}ik_offset'.format(self.base_name, index))
            self.clusters.append('{}{}_cluster'.format(self.base_name, index))

        self.ik_curve = '{}ik_curve'.format(self.base_name)
        self.ik = '{}_ik'.format(self.base_name)

    def set_controller_shape(self):
        sphere = cmds.createNode('implicitSphere')
        # ik ctrl shape
        self._shape = cmds.rename(cmds.listRelatives(sphere, p=1), self.namer.tmp)

    def build_ik(self):
        curve_points = []
        for index, jnt in enumerate(self.jnts):
            pos = cmds.xform(jnt, q=1, t=1, ws=1)
            curve_points.append(pos)

        curve = cmds.curve(p=curve_points, name=self.ik_curve)
        cmds.setAttr(curve+'.visibility', 0)
        # turning off inherit transform avoid curve move/scale twice as much
        cmds.inheritTransform(curve, off=1)

        cvs = cmds.ls(self.ik_curve+'.cv[0:]', fl=1)
        for index, cv in enumerate(cvs):
            cluster = cmds.cluster(cv, name=self.clusters[index])[-1]
            cmds.setAttr(cluster+'.visibility', 0)

        cmds.ikHandle(startJoint=self.jnts[0],
                      endEffector=self.jnts[self.segment-1],
                      name=self.ik, curve=curve, createCurve=False,
                      parentCurve=1, roc=1, solver='ikSplineSolver')
        cmds.setAttr(self.ik+'.visibility', 0)
        cmds.parent(self.ik, util.G_CTRL_GRP)

    def add_constraint(self):
        self.build_ik()
        for index in range(self.segment):
            cluster = cmds.ls('{}Handle'.format(self.clusters[index]))
            cmds.parent(cluster, self.ctrls[index])

