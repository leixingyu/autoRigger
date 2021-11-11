import maya.cmds as cmds

from . import chain
from autoRigger import util
from autoRigger.base import bone
from utility.datatype import vector


class ChainIK(chain.Chain):
    """
    Abstract IK type Chain module
    """

    def __init__(self, side, name, segment, length, direction, is_stretch=1):
        chain.Chain.__init__(self, side, name, segment)

        self.is_stretch = is_stretch

        self.clusters = list()
        self.ik_curve = None
        self.ik = None

        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(direction).normalize()

    @bone.update_base_name
    def create_namespace(self):
        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base_name, index))
            self.jnts.append('{}{}ik_jnt'.format(self.base_name, index))
            self.ctrls.append('{}{}ik_ctrl'.format(self.base_name, index))
            self.offsets.append(
                '{}{}ik_offset'.format(self.base_name, index))
            self.clusters.append('{}{}_cluster'.format(self.base_name, index))

        self.ik_curve = '{}ik_curve'.format(self.base_name)
        self.ik = '{}_ik'.format(self.base_name)

    def set_shape(self):
        sphere = cmds.createNode('implicitSphere')
        self._shape = cmds.rename(cmds.listRelatives(sphere, p=1), self.namer.tmp)

    def build_ik(self):
        curve_points = list()
        for index, jnt in enumerate(self.jnts):
            pos = cmds.xform(jnt, q=1, t=1, ws=1)
            curve_points.append(pos)

        cmds.curve(p=curve_points, name=self.ik_curve)
        cmds.setAttr(self.ik_curve+'.visibility', 0)
        # turning off inherit transform avoid curve move/scale twice as much
        cmds.inheritTransform(self.ik_curve, off=1)
        cmds.parent(self.ik_curve, util.G_CTRL_GRP)

        cvs = cmds.ls(self.ik_curve+'.cv[0:]', fl=1)
        for index, cv in enumerate(cvs):
            cluster = cmds.cluster(cv, name=self.clusters[index])[-1]
            cmds.setAttr(cluster+'.visibility', 0)

        cmds.ikHandle(startJoint=self.jnts[0],
                      endEffector=self.jnts[self.segment-1],
                      name=self.ik, curve=self.ik_curve, createCurve=False,
                      parentCurve=1, roc=1, solver='ikSplineSolver')

        cmds.setAttr(self.ik+'.visibility', 0)
        cmds.parent(self.ik, util.G_CTRL_GRP)

    def add_constraint(self):
        self.build_ik()

        for index, cluster in enumerate(self.clusters):
            cmds.parent(cluster+'Handle', self.ctrls[index])

        # enable advance twist control
        cmds.setAttr(self.ik+'.dTwistControlEnable', 1)
        cmds.setAttr(self.ik+'.dWorldUpType', 4)
        cmds.connectAttr(self.ctrls[0]+'.worldMatrix[0]', self.ik+'.dWorldUpMatrix', f=1)
        cmds.connectAttr(self.ctrls[-1]+'.worldMatrix[0]', self.ik+'.dWorldUpMatrixEnd', f=1)

        if self.is_stretch:
            # mid cluster weighting
            for index, offset in enumerate(self.offsets):
                if self.ctrls[index] not in [self.ctrls[0], self.ctrls[-1]]:
                    weight = (1.00 / (self.segment-1)) * index
                    cmds.pointConstraint(self.ctrls[-1], offset, w=weight, mo=1)
                    cmds.pointConstraint(self.ctrls[0], offset, w=1-weight, mo=1)

            # scaling of the spine
            arc_len = cmds.arclen(self.ik_curve, constructionHistory=1)
            cmds.rename(arc_len, self.ik_curve+'Info')
            cmds.parent(self.ik_curve, util.G_CTRL_GRP)
            cmds.setAttr(self.ik_curve+'.visibility', 0)

            # create curve length node and multiply node
            init_len = cmds.getAttr(self.ik_curve+'Info.arcLength')
            stretch_node = cmds.shadingNode('multiplyDivide', asUtility=1, name=self.ctrls[0]+'Stretch')
            cmds.setAttr(stretch_node+'.operation', 2)
            cmds.setAttr(stretch_node+'.input2X', init_len)
            cmds.connectAttr(self.ik_curve+'Info.arcLength', stretch_node+'.input1X')

            for i in range(self.segment):
                cmds.connectAttr(stretch_node+'.outputX', self.jnts[i]+'.scaleX')
