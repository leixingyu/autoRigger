import maya.cmds as cmds

from .... import util
from ....base import bone
from ....chain.limb import limbFKIK
from ....constant import Side
from ....module import hand


class Arm(bone.Bone):
    """
    Create a FK/IK control rig system for arm

    Uses the combination of LimbFKIK and Hand modules
    """

    def __init__(self, side, name, distance=6, interval=0.5, gap=2):
        """
        Extend: specify distance, interval and gap for connection

        :param distance: float. length of the limb
        :param interval: float. interval for Hand module
        :param gap: float. gap for Hand module
        """
        super(Arm, self).__init__(side, name)
        self._rtype = 'arm'

        self.distance = distance
        self.interval = interval
        self.gap = gap

        self.limb = limbFKIK.LimbFKIK(
            self._side, name, ltype='arm', length=self.distance)

        self.hand = None
        if self._side == Side.LEFT:
            self.hand = hand.Hand(
                self._side, name, interval=self.interval, distance=self.gap)
        elif self._side == Side.RIGHT:
            self.hand = hand.Hand(
                self._side, name, interval=self.interval, distance=self.gap)

        self._comps = [self.hand, self.limb]

    def create_locator(self):
        """
        Extend: move hand and parent it with top of the limb
        """
        super(Arm, self).create_locator()

        if self._side == Side.LEFT:
            util.move(
                self.hand.wrist.locs[0],
                pos=[self.distance+self.gap, 0, 0])
        elif self._side == Side.RIGHT:
            util.move(
                self.hand.wrist.locs[0],
                pos=[-self.distance-self.gap, 0, 0])

        cmds.parent(self.hand.wrist.locs[0], self.limb.locs[-1])

    def add_constraint(self):
        """
        Extend: connect the hand and limb control
        """
        super(Arm, self).add_constraint()
        cmds.parentConstraint(
            self.limb.jnts[-1], self.hand.wrist.ctrls[0], mo=1)
