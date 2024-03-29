import maya.cmds as cmds

from ... import util
from ...chain import chainIK
from ...constant import Side
from ...utility.rigging import joint
from ...utility.rigging import transform


class LimbIK(chainIK.ChainIK):
    """
    Create a IK control rig system for limb
    """

    def __init__(self, side, name, length, ltype=None):
        """
        Extend: specify limb type and side determines direction

        :param ltype: str. type of the limb: 'arm' or 'leg'
        """
        self._rtype = ltype

        self.direction = [0, -1, 0]
        if ltype == 'arm' and side == Side.LEFT:
            self.direction = [1, 0, 0]
        elif ltype == 'arm' and side == Side.RIGHT:
            self.direction = [-1, 0, 0]

        super(LimbIK, self).__init__(side, name, 3, length, self.direction)

    def place_controller(self):
        """
        Override: create and place root, IK pole and top controllers
        """
        # TODO: move pole vector out

        for index in range(self.segment):
            cmds.duplicate(self._shape, n=self.ctrls[index])
            cmds.group(em=1, n=self.offsets[index])
            transform.match_xform(self.offsets[index], self.jnts[index])
            cmds.parent(self.ctrls[index], self.offsets[index], r=1)
            cmds.parent(self.offsets[index], util.G_CTRL_GRP)

    def build_ik(self):
        """
        Override: build the IK controller for limb using RP solver
        """
        if self.direction == 'vertical':
            joint.set_prefer_angle(self.jnts[1], [0, 0, -1])
        else:
            joint.set_prefer_angle(self.jnts[1], [0, 0, 1])

        cmds.ikHandle(
            sj=self.jnts[0],
            ee=self.jnts[-1],
            n=self.ik, sol='ikRPsolver')

    def add_constraint(self):
        """
        Override: no stretching support
        """
        self.build_ik()

        cmds.pointConstraint(self.ctrls[-1], self.ik, mo=1)
        cmds.orientConstraint(self.ctrls[-1], self.jnts[-1], mo=1)
        cmds.poleVectorConstraint(self.ctrls[1], self.ik)

        cmds.pointConstraint(self.ctrls[0], self.jnts[0], mo=1)
        cmds.parent(self.offsets[1], self.ctrls[0])

        cmds.setAttr(self.ik+'.v', 0)
        cmds.parent(self.ik, util.G_CTRL_GRP)
