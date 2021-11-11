import maya.cmds as cmds

from autoRigger import util
from autoRigger.module import foot
from autoRigger.base import bone
from autoRigger.chain.limb import limbFKIK


class Leg(bone.Bone):
    """
    Biped leg rig module with a limb and a foot
    """

    def __init__(self, side, name, distance=8, interval=0.5, height=0.4):
        bone.Bone.__init__(self, side, name)
        self._rtype = 'leg'

        self.distance = distance
        self.interval = interval
        self.height = height

        self.limb = limbFKIK.LimbFKIK(side=self._side, name=name, ltype='leg', length=self.distance)
        self.foot = foot.Foot(side=self._side, name=name, interval=self.interval, height=self.height)

        self._components = [self.limb, self.foot]

    def create_locator(self):
        super(Leg, self).create_locator()

        util.move(self.foot.locs[0], [0, -self.distance, 0])
        cmds.parent(self.foot.locs[0], self.limb.locs[-1])

    def add_constraint(self):
        super(Leg, self).add_constraint()

        # Connect foot and limb
        # IK constraint #
        cmds.parentConstraint(self.foot.rev_jnts[0], self.limb.ik_chain.ctrls[-1], mo=1)
        cmds.setAttr(self.limb.ik_chain.ctrls[-1]+'.visibility', 0)

        # FK constraint #
        cmds.parentConstraint(self.limb.jnts[-1], self.foot.fk_jnts[0], mo=1)
        cmds.parent(self.foot.ctrls[1], self.limb.fk_chain.ctrls[-1])

        # IK/FK switch #
        cmds.setDrivenKeyframe(self.limb.ctrls[0]+'.FK_IK', currentDriver=self.foot.ctrls[2]+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.limb.ctrls[0]+'.FK_IK', currentDriver=self.foot.ctrls[2]+'.FK_IK', driverValue=0, value=0)

        # Sub controller visibility and channel hide #
        cmds.setDrivenKeyframe(self.limb.ik_chain.ctrls[-1]+'.visibility', currentDriver=self.limb.ctrls[0]+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.limb.ik_chain.ctrls[-1]+'.visibility', currentDriver=self.limb.ctrls[0]+'.FK_IK', driverValue=0, value=0)
        cmds.setAttr(self.limb.ctrls[0]+'.FK_IK', l=1, k=0)
