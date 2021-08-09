import maya.cmds as cmds
from . import rig, hand, limb


class Arm(rig.Bone):
    """ This module creates an Arm rig with a limb and a hand"""

    def __init__(self, side, base_name, start_pos=[0, 10, 0], distance=2, interval=0.5, gap=2):
        """  Initialize Arm class with side and base_name

        :param side: str
        :param base_name: str
        """

        rig.Bone.__init__(self, side, base_name)
        self.meta_type = 'Arm'
        self.start_pos = start_pos
        self.distance = distance
        self.interval = interval
        self.gap = gap
        self.scale = 0.2

        self.initial_setup()

        self.limb = limb.Limb(
            side=self.side,
            base_name=base_name,
            limb_type='Arm',
            start_pos=self.start_pos,
            interval=self.distance
        )

        self.hand = None
        if self.side == 'L':
            self.hand = hand.Hand(
                side=self.side,
                base_name=base_name,
                start_pos=[self.start_pos[0]+2 * self.distance+self.gap,
                           self.start_pos[1], self.start_pos[2]],
                interval=self.interval,
                distance=self.gap
            )
        elif self.side == 'R':
            self.hand = hand.Hand(
                side=self.side,
                base_name=base_name,
                start_pos=[self.start_pos[0]-2 * self.distance-self.gap,
                           self.start_pos[1], self.start_pos[2]],
                interval=self.interval,
                distance=self.gap
            )

    def create_locator(self):
        # Limb
        self.limb.create_locator()

        # Hand
        wrist_loc = self.hand.create_locator()

        # parent wrist to the tip of limb
        cmds.parent(wrist_loc, self.limb.loc_list[-1])

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
        cmds.parentConstraint(self.limb.jnt_list[-1], self.hand.wrist.jnt_name, mo=1)

    def lock_controller(self):
        self.limb.lock_controller()

    def color_controller(self):
        self.limb.color_controller()
        self.hand.color_controller()

    def delete_guide(self):
        limb_grp = cmds.ls(self.limb.loc_grp_name)
        cmds.delete(limb_grp)
        hand_grp = cmds.ls(self.hand.loc_grp_name)
        cmds.delete(hand_grp)
