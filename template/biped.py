import maya.cmds as cmds

from autoRigger import util
from autoRigger.base import base, bone
from autoRigger.chain.spine import spine
from autoRigger.chain.limb.arm import arm
from autoRigger.chain.limb.leg import leg


class Biped(bone.Bone):
    """
    This module creates a biped template rig consisting of
    one head, two arms, one spine & two legs
    """

    def __init__(self, side, name, spine_len=5.0):
        bone.Bone.__init__(self, side, name)
        self._rtype = 'biped'

        self.pos = [0, 8.4, 0]
        self.spine_len = spine_len
        self.scale = 0.2

        self.left_arm = arm.Arm(side='l', name='arm')
        self.right_arm = arm.Arm(side='r', name='arm')

        self.left_leg = leg.Leg(side='l', name='leg')
        self.right_leg = leg.Leg(side='r', name='leg')
        self.spine = spine.Spine(side='m', name='spine', length=self.spine_len)
        self.neck = base.Base(side='m', name='neck')
        self.head = base.Base(side='m', name='head')
        self.tip = base.Base(side='m', name='tip')

        self.rig_components = [
            self.left_arm,
            self.right_arm,
            self.left_leg,
            self.right_leg,
            self.spine,
            self.neck,
            self.head,
            self.tip
        ]

    def create_namespace(self):
        for rig_component in self.rig_components:
            rig_component.create_namespace()

    def create_locator(self):
        for rig_component in self.rig_components:
            rig_component.create_locator()

        self.move_locator()

    def color_locator(self):
        for rig_component in self.rig_components:
            rig_component.color_locator()

    def move_locator(self):
        util.move(self.left_arm.limb.locs[0], pos=[self.pos[0]+2, self.pos[1]+self.spine_len, self.pos[2]])
        util.move(self.right_arm.limb.locs[0], pos=[self.pos[0]-2, self.pos[1]+self.spine_len, self.pos[2]])

        util.move(self.left_leg.limb.locs[0], pos=[self.pos[0]+1, self.pos[1], self.pos[2]])
        util.move(self.right_leg.limb.locs[0], pos=[self.pos[0]-1, self.pos[1], self.pos[2]])

        util.move(self.spine.locs[0], pos=self.pos)

        util.move(self.neck.locs[0], pos=[self.pos[0], self.pos[1]+self.spine_len+1, self.pos[2]])
        util.move(self.head.locs[0], pos=[self.pos[0], self.pos[1]+self.spine_len+1.5, self.pos[2]])
        util.move(self.tip.locs[0], pos=[self.pos[0], self.pos[1]+self.spine_len+2, self.pos[2]])

    def set_controller_shape(self):
        for rig_component in self.rig_components:
            rig_component.set_controller_shape()

    def create_joint(self):
        for rig_component in self.rig_components:
            rig_component.create_joint()

        # Leg root to spine root
        cmds.parent(self.left_leg.limb.jnts[0], self.spine.jnts[0])
        cmds.parent(self.right_leg.limb.jnts[0], self.spine.jnts[0])

        # Arm root spine root
        cmds.parent(self.left_arm.limb.jnts[0], self.spine.jnts[-1])
        cmds.parent(self.right_arm.limb.jnts[0], self.spine.jnts[-1])

        # Neck to spine tip, head to neck
        cmds.parent(self.neck.jnts[0], self.spine.jnts[-1])
        cmds.parent(self.head.jnts[0], self.neck.jnts[0])
        cmds.parent(self.tip.jnts[0], self.head.jnts[0])

    def place_controller(self):
        for rig_component in self.rig_components:
            rig_component.place_controller()

    def add_constraint(self):
        for rig_component in self.rig_components:
            rig_component.add_constraint()

        # Leg driven by root spine control #
        cmds.parent(self.left_leg.limb.offsets[0], self.spine.ctrls[0])
        cmds.parent(self.right_leg.limb.offsets[0], self.spine.ctrls[0])

        # Arm driven by top spine control #
        cmds.parent(self.left_arm.limb.offsets[0], self.spine.ctrls[-1])
        cmds.parent(self.right_arm.limb.offsets[0], self.spine.ctrls[-1])

        # Neck to Head chain #
        cmds.parent(self.tip.offsets[0], self.head.offsets[0])
        cmds.parent(self.head.offsets[0], self.neck.offsets[0])
        cmds.parent(self.neck.offsets[0], self.spine.ctrls[-1])

    def color_controller(self):
        for rig_component in self.rig_components:
            rig_component.color_controller()

    def delete_guide(self):
        for rig_component in self.rig_components:
            rig_component.delete_guide()
