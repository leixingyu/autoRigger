import maya.cmds as cmds

from . import chain
from autoRigger import util
from autoRigger.base import bone
from utility.algorithm import algorithm
import utility.setup.outliner


class ChainEP(chain.Chain):
    """
    Abstract EP (Edit Point) type Chain module
    """

    def __init__(self, side, name, segment, curve, cv=None):
        chain.Chain.__init__(self, side, name, segment)
        self.clusters = list()
        self.guide_curve = None

        if not cv:
            cv = self.segment

        if cv < 2:
            raise ValueError('in-sufficient control points')

        self.cvs = list()
        percentages = algorithm.get_percentages(cv)
        for p in percentages:
            integer = int(round(p*(self.segment-1)))
            self.cvs.append(integer)

        self.curve = curve

    @bone.update_base_name
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

    def set_controller_shape(self):
        sphere = cmds.createNode('implicitSphere')
        self._shape = cmds.rename(
            cmds.listRelatives(sphere, p=1),
            self.namer.tmp
        )

    def place_controller(self):
        for index in self.cvs:
            cmds.duplicate(self._shape, name=self.ctrls[index])
            cmds.group(em=1, name=self.offsets[index])

            utility.setup.outliner.match_xform(self.offsets[index], self.jnts[index])

            cmds.parent(self.ctrls[index], self.offsets[index], relative=1)
            cmds.parent(self.offsets[index], util.G_CTRL_GRP)

    def add_constraint(self):
        # smooth fall off constraint along the chain
        for i in range(len(self.cvs)-1):
            head = self.cvs[i]
            tail = self.cvs[i+1]
            for j in range(head, tail+1):
                gap = 1.00/(tail - head)
                # why not using parent constraint? because it will break things
                cmds.pointConstraint(self.ctrls[head], self.jnts[j], w=1-((j-head) * gap), mo=1)
                cmds.pointConstraint(self.ctrls[tail], self.jnts[j], w=(j-head) * gap, mo=1)
                cmds.orientConstraint(self.ctrls[head], self.jnts[j], w=1-((j-head) * gap), mo=1)
                cmds.orientConstraint(self.ctrls[tail], self.jnts[j], w=(j-head) * gap, mo=1)
