import maya.cmds as cmds
from utility import outliner
from . import base, rig, arm, leg, spine


class Biped(rig.Bone):
    """ This module creates a biped template rig

    The biped template consists of:
    one head
    two arms
    one spine &
    two legs
    """

    def __init__(self, side, name, rig_type='Biped', pos=[0, 8.4, 0], spine_len=5.0):
        """ Initialize Biped class with side and name

        :param side: str
        :param name: str
        """
        self.pos = pos
        self.spine_len = spine_len
        self.scale = 0.2

        self.left_arm = arm.Arm(side='L', name='arm', pos=[self.pos[0]+2, self.pos[1]+self.spine_len, self.pos[2]])
        self.right_arm = arm.Arm(side='R', name='arm', pos=[self.pos[0]-2, self.pos[1]+self.spine_len, self.pos[2]])
        self.left_leg = leg.Leg(side='L', name='leg', pos=[self.pos[0]+1, self.pos[1], self.pos[2]])
        self.right_leg = leg.Leg(side='R', name='leg', pos=[self.pos[0]-1, self.pos[1], self.pos[2]])
        self.spine = spine.Spine(side='M', name='spine', pos=self.pos, length=self.spine_len)
        self.neck = base.Base(side='M', name='neck', pos=[self.pos[0], self.pos[1]+self.spine_len+1, self.pos[2]])
        self.head = base.Base(side='M', name='head', pos=[self.pos[0], self.pos[1]+self.spine_len+1.5, self.pos[2]])
        self.tip = base.Base(side='M', name='tip', pos=[self.pos[0], self.pos[1]+self.spine_len+2, self.pos[2]])

        self.rig_components = [self.left_arm, self.right_arm, self.left_leg, self.right_leg, self.spine, self.neck, self.head, self.tip]

        rig.Bone.__init__(self, side, name, rig_type)

    def create_locator(self):
        for rig_component in self.rig_components:
            rig_component.create_locator()

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
        cmds.parent(self.neck.jnt, top_spine_jnt)
        cmds.parent(self.head.jnt, self.neck.jnt)
        cmds.parent(self.tip.jnt, self.head.jnt)

    def place_controller(self):
        for rig_component in self.rig_components:
            rig_component.place_controller()

    def add_constraint(self):
        for rig_component in self.rig_components:
            rig_component.add_constraint()

        # Connect
        # Leg driven by root spine control #
        cmds.parent(self.left_leg.limb.switch_offset, self.spine.global_ctrl)
        cmds.parent(self.right_leg.limb.switch_offset, self.spine.global_ctrl)

        # Arm driven by top spine control #
        cmds.parent(self.left_arm.limb.switch_offset, self.spine.ctrls[-1])
        cmds.parent(self.right_arm.limb.switch_offset, self.spine.ctrls[-1])

        # Neck to Head chain #
        cmds.parent(self.tip.ctrl_offset, self.head.ctrl_offset)
        cmds.parent(self.head.ctrl_offset, self.neck.ctrl_offset)
        cmds.parent(self.neck.ctrl_offset, self.spine.ctrls[-1])

    def color_controller(self):
        for rig_component in self.rig_components:
            rig_component.color_controller()

    def delete_guide(self):
        loc = cmds.ls(self.loc_global_grp)
        cmds.delete(loc)
