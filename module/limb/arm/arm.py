import maya.cmds as cmds

from autoRigger.module import hand
from autoRigger.module.limb import limb
from autoRigger.module.base import bone
from autoRigger import util


class Arm(bone.Bone):
    """ This module creates an Arm rig with a limb and a hand"""

    def __init__(self, side, name, distance=2, interval=0.5, gap=2):
        """  Initialize Arm class with side and base_name

        :param side: str
        :param name: str
        """

        self._rtype = 'arm'

        self.distance = distance
        self.interval = interval
        self.gap = gap
        self.scale = 0.2

        bone.Bone.__init__(self, side, name)

        self.limb = limb.Limb(side=self._side, name=name, ltype='arm', interval=self.distance)

        self.hand = None
        if self._side == 'l':
            self.hand = hand.Hand(side=self._side, name=name, interval=self.interval, distance=self.gap)
        elif self._side == 'r':
            self.hand = hand.Hand(side=self._side, name=name, interval=self.interval, distance=self.gap)

    def create_locator(self):
        # Limb
        self.limb.create_locator()

        # Hand
        self.hand.create_locator()

        # move hand based on side
        if self._side == 'l':
            util.move(self.hand.wrist.loc, pos=[2 * self.distance+self.gap, 0, 0])
        elif self._side == 'r':
            util.move(self.hand.wrist.loc, pos=[-2 * self.distance-self.gap, 0, 0])

        cmds.parent(self.hand.wrist.loc, self.limb.locs[-1])

    def set_controller_shape(self):
        self.limb.set_controller_shape()
        self.hand.set_controller_shape()

    def create_joint(self):
        self.limb.create_joint()
        self.hand.create_joint()

    def place_controller(self):
        self.limb.place_controller()
        self.hand.place_controller()

    def add_constraint(self):
        self.limb.add_constraint()
        self.hand.add_constraint()
        cmds.parentConstraint(self.limb.jnts[-1], self.hand.wrist.ctrl, mo=1)

    def lock_controller(self):
        self.limb.lock_controller()

    def color_controller(self):
        self.limb.color_controller()
        self.hand.color_controller()

    def delete_guide(self):
        limb_grp = cmds.ls(self.limb.loc_grp)
        cmds.delete(limb_grp)
        hand_grp = cmds.ls(self.hand.loc_grp)
        cmds.delete(hand_grp)
