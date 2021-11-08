import maya.cmds as cmds

from utility.setup import outliner
from autoRigger import util
from utility.rigging import joint
from . import chainIK


class LimbIK(chainIK.ChainIK):

    def __init__(self, side, name, length, ltype='null'):

        segment = 3
        self.ltype = ltype
        self.direction = [0, -1, 0]
        self._rtype = ltype

        if ltype == 'arm' and side == 'l':
            self.direction = [1, 0, 0]
        elif ltype == 'arm' and side == 'r':
            self.direction = [-1, 0, 0]

        chainIK.ChainIK.__init__(self, side, name, segment, length, self.direction)

    def place_controller(self):
        # TODO: move pole vector out

        for index in range(self.segment):
            cmds.duplicate(self._shape, name=self.ctrls[index])
            cmds.group(em=1, name=self.offsets[index])
            outliner.match_xform(self.offsets[index], self.jnts[index])
            cmds.parent(self.ctrls[index], self.offsets[index], relative=1)
            cmds.parent(self.offsets[index], util.G_CTRL_GRP)

        return self.offsets[0]

    def build_ik(self):
        if self.direction == 'vertical':
            joint.set_prefer_angle(self.jnts[1], [0, 0, -1])
        else:
            joint.set_prefer_angle(self.jnts[1], [0, 0, 1])

        # IK Handle #
        cmds.ikHandle(
            startJoint=self.jnts[0],
            endEffector=self.jnts[-1],
            name=self.ik,
            solver='ikRPsolver')

    def add_constraint(self):
        self.build_ik()

        cmds.pointConstraint(self.ctrls[-1], self.ik, mo=1)
        cmds.orientConstraint(self.ctrls[-1], self.jnts[-1], mo=1)
        cmds.poleVectorConstraint(self.ctrls[1], self.ik)

        cmds.pointConstraint(self.ctrls[0], self.jnts[0], mo=1)
        cmds.parent(self.offsets[1], self.ctrls[0])

        cmds.setAttr(self.ik+'.visibility', 0)
        cmds.parent(self.ik, util.G_CTRL_GRP)
