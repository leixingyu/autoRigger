import maya.cmds as cmds

from autoRigger import util
from . import chain


class ChainEP(chain.Chain):

    def __init__(self, side, name, segment, curve):

        self.clusters = list()
        self.guide_curve = None

        chain.Chain.__init__(self, side, name, segment)

        self.curve = curve

    def assign_secondary_naming(self):
        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base_name, index))
            self.jnts.append('{}{}_jnt'.format(self.base_name, index))
            self.ctrls.append('{}{}_ctrl'.format(self.base_name, index))
            self.offsets.append(
                '{}{}_offset'.format(self.base_name, index))
            self.clusters.append('{}{}_cluster'.format(self.base_name, index))

        self.guide_curve = '{}_curve'.format(self.base_name)

    def create_locator(self):
        locs = util.create_locators_on_curve(self.curve, self.segment)

        for index, loc in enumerate(locs):
            cmds.rename(loc, self.locs[index])

            if index:
                cmds.parent(self.locs[index], self.locs[index-1], absolute=1)

        cmds.parent(self.locs[0], util.G_LOC_GRP)
        return self.locs[0]

    def set_controller_shape(self):
        sphere = cmds.createNode('implicitSphere')
        self._shape = cmds.rename(cmds.listRelatives(sphere, p=1),
                                  self.namer.tmp)

    def place_controller(self):
        for index in range(self.segment):
            cmds.duplicate(self._shape, name=self.ctrls[index])
            cmds.group(em=1, name=self.offsets[index])
            util.matchXform(self.offsets[index], self.jnts[index])

            cmds.parent(self.ctrls[index], self.offsets[index], relative=1)
            cmds.parent(self.offsets[index], util.G_CTRL_GRP)
        return self.offsets[0]

    def build_curve(self):
        curve_points = []
        for index, jnt in enumerate(self.jnts):
            pos = cmds.xform(jnt, q=1, t=1, ws=1)
            curve_points.append(pos)

        cmds.curve(ep=curve_points, name=self.guide_curve)
        cmds.setAttr(self.guide_curve+'.visibility', 0)
        # turning off inherit transform avoid curve move/scale twice as much
        cmds.inheritTransform(self.guide_curve, off=1)
        cmds.parent(self.guide_curve, util.G_LOC_GRP)

        cvs = cmds.ls(self.guide_curve+'.ep[0:]', fl=1)
        for index, cv in enumerate(cvs):
            cluster = cmds.pointCurveConstraint(cv, rpo=1, w=1)[0]
            cmds.rename(cluster, self.clusters[index])
            cmds.setAttr(self.clusters[index]+'.visibility', 0)

    def add_constraint(self):
        self.build_curve()

        for index, cluster in enumerate(self.clusters):
            cmds.parent(cluster, self.ctrls[index])
            cmds.parentConstraint(self.ctrls[index], self.jnts[index])

