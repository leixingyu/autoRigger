import maya.cmds as cmds

from ....constant import Side
from autoRigger import util
from autoRigger.module import hand
from autoRigger.base import bone
from autoRigger.chain.limb import limbFKIK


class Arm(bone.Bone):
    """
    Arm rig module with a limb and a hand
    """

    def __init__(self, side, name, distance=6, interval=0.5, gap=2):
        bone.Bone.__init__(self, side, name)
        self._rtype = 'arm'

        self.distance = distance
        self.interval = interval
        self.gap = gap

        self.limb = limbFKIK.LimbFKIK(side=self._side, name=name, ltype='arm', length=self.distance)
        self.hand = None
        if self._side == Side.LEFT:
            self.hand = hand.Hand(side=self._side, name=name, interval=self.interval, distance=self.gap)
        elif self._side == Side.RIGHT:
            self.hand = hand.Hand(side=self._side, name=name, interval=self.interval, distance=self.gap)

        self._components = [self.hand, self.limb]

    def create_locator(self):
        super(Arm, self).create_locator()

        # move hand based on side
        if self._side == Side.LEFT:
            util.move(self.hand.wrist.locs[0], pos=[self.distance+self.gap, 0, 0])
        elif self._side == Side.RIGHT:
            util.move(self.hand.wrist.locs[0], pos=[-self.distance-self.gap, 0, 0])

        cmds.parent(self.hand.wrist.locs[0], self.limb.locs[-1])

    def add_constraint(self):
        super(Arm, self).add_constraint()

        cmds.parentConstraint(self.limb.jnts[-1], self.hand.wrist.ctrls[0], mo=1)


