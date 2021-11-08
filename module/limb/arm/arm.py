import maya.cmds as cmds

from autoRigger.module import hand
from autoRigger.module.chain import limbFKIK
from autoRigger.module.base import bone
from autoRigger import util


class Arm(bone.Bone):
    """ This module creates an Arm rig with a limb and a hand"""

    def __init__(self, side, name, distance=6, interval=0.5, gap=2):
        """  Initialize Arm class with side and base_name

        :param side: str
        :param name: str
        """
        bone.Bone.__init__(self, side, name)
        self._rtype = 'arm'

        self.distance = distance

        self.interval = interval
        self.gap = gap
        self.scale = 0.2

        self.limb = limbFKIK.LimbFKIK(side=self._side, name=name, ltype='arm', length=self.distance)

        self.hand = None
        if self._side == 'l':
            self.hand = hand.Hand(side=self._side, name=name, interval=self.interval, distance=self.gap)
        elif self._side == 'r':
            self.hand = hand.Hand(side=self._side, name=name, interval=self.interval, distance=self.gap)

    def create_namespace(self):
        self.limb.create_namespace()
        self.hand.create_namespace()

    def create_locator(self):
        # Limb
        self.limb.create_locator()

        # Hand
        self.hand.create_locator()

        # move hand based on side
        if self._side == 'l':
            util.move(self.hand.wrist.locs[0], pos=[self.distance+self.gap, 0, 0])
        elif self._side == 'r':
            util.move(self.hand.wrist.locs[0], pos=[-self.distance-self.gap, 0, 0])

        cmds.parent(self.hand.wrist.locs[0], self.limb.locs[-1])

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
        cmds.parentConstraint(self.limb.jnts[-1], self.hand.wrist.ctrls[0], mo=1)

    def lock_controller(self):
        self.limb.lock_controller()

    def color_controller(self):
        self.limb.color_controller()
        self.hand.color_controller()

