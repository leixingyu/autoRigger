import maya.cmds as cmds
import base
import hand
import limb


class Arm(base.Base):
    """ This module creates an Arm rig with a limb and a hand"""

    def __init__(self, side, base_name):
        """  Initialize Arm class with side and base_name

        :param side: str
        :param base_name: str
        """

        base.Base.__init__(self, side, base_name)
        self.meta_type = 'Arm'
        self.assign_naming()
        self.set_locator_attr(start_pos=[0, 10, 0])
        self.limb = limb.Limb(side=self.side, base_name=base_name, limb_type='Arm')
        self.hand = hand.Hand(side=self.side, base_name=base_name)

    def set_locator_attr(self, start_pos=[0, 0, 0], distance=2, interval=0.5, gap=2, scale=0.2):
        self.start_pos = start_pos
        self.distance = distance
        self.interval = interval
        self.gap = gap
        self.scale = scale

    def build_guide(self):
        # Limb
        self.limb.set_locator_attr(start_pos=self.start_pos, interval=self.distance)
        self.limb.build_guide()

        # Hand
        if self.side == 'L':
            self.hand.set_locator_attr(start_pos=[self.start_pos[0] + 2 * self.distance + self.gap, self.start_pos[1], self.start_pos[2]], interval=self.interval, distance=self.gap)
        elif self.side == 'R':
            self.hand.set_locator_attr(start_pos=[self.start_pos[0] - 2 * self.distance - self.gap, self.start_pos[1], self.start_pos[2]], interval=self.interval, distance=self.gap)
        wrist_loc = self.hand.build_guide()

        # parent wrist to the tip of limb
        cmds.parent(wrist_loc, self.limb.loc_list[-1])

    def construct_joint(self):
        self.limb.construct_joint()
        self.hand.construct_joint()

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
