import maya.cmds as cmds

from autoRigger.chain.spine import spine
from autoRigger.chain.limb.arm import arm
from autoRigger.chain.limb.leg import leg
from autoRigger.base import base, bone
from autoRigger import util
from utility.setup import outliner


class Biped(bone.Bone):
    """ This module creates a biped template rig

    The biped template consists of:
    one head
    two arms
    one spine &
    two legs
    """

    def __init__(self, side, name, spine_len=5.0):
        """ Initialize Biped class with side and name

        :param side: str
        :param name: str
        """

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

        bone.Bone.__init__(self, side, name)

    def create_namespace(self):
        for rig_componet in self.rig_components:
            rig_componet.create_namespace()

    def create_locator(self):
        for rig_component in self.rig_components:
            rig_component.create_locator()

        self.move_locator()

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

        # Connect
        # Leg root to spine root
        left_leg_jnt = cmds.ls(self.left_leg.limb.jnts[0])
        right_leg_jnt = cmds.ls(self.right_leg.limb.jnts[0])
        root_spine_jnt = cmds.ls(self.spine.jnts[0])
        outliner.batch_parent([left_leg_jnt, right_leg_jnt], root_spine_jnt)

        # Arm root spine root
        left_arm_jnt = cmds.ls(self.left_arm.limb.jnts[0])
        right_arm_jnt = cmds.ls(self.right_arm.limb.jnts[0])
        top_spine_jnt = cmds.ls(self.spine.jnts[-1])
        outliner.batch_parent([left_arm_jnt, right_arm_jnt], top_spine_jnt)

        # Neck to spine tip, head to neck
        cmds.parent(self.neck.jnts[0], top_spine_jnt)
        cmds.parent(self.head.jnts[0], self.neck.jnts[0])
        cmds.parent(self.tip.jnts[0], self.head.jnts[0])

    def place_controller(self):
        for rig_component in self.rig_components:
            rig_component.place_controller()

    def add_constraint(self):
        for rig_component in self.rig_components:
            rig_component.add_constraint()

        # Connect
        # Leg driven by root spine control #
        cmds.parent(self.left_leg.limb.master_offset, self.spine.ctrls[0])
        cmds.parent(self.right_leg.limb.master_offset, self.spine.ctrls[0])

        # Arm driven by top spine control #
        cmds.parent(self.left_arm.limb.master_offset, self.spine.ctrls[-1])
        cmds.parent(self.right_arm.limb.master_offset, self.spine.ctrls[-1])

        # Neck to Head chain #
        cmds.parent(self.tip.offsets[0], self.head.offsets[0])
        cmds.parent(self.head.offsets[0], self.neck.offsets[0])
        cmds.parent(self.neck.offsets[0], self.spine.ctrls[-1])

    def color_controller(self):
        for rig_component in self.rig_components:
            rig_component.color_controller()

    def delete_guide(self):
        loc = cmds.ls(util.G_LOC_GRP)
        cmds.delete(loc)
