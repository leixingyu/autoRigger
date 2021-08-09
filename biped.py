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

    def __init__(self, side, base_name, start_pos=[0, 8.4, 0], spine_len=5.0):
        """ Initialize Biped class with side and name

        :param side: str
        :param base_name: str
        """

        rig.Bone.__init__(self, side, base_name)
        self.meta_type = 'Biped'

        self.start_pos = start_pos
        self.spine_len = spine_len
        self.scale = 0.2

        self.initial_setup()

        self.left_arm = arm.Arm(side='L', base_name='arm', start_pos=[self.start_pos[0]+2, self.start_pos[1]+self.spine_len, self.start_pos[2]])
        self.right_arm = arm.Arm(side='R', base_name='arm', start_pos=[self.start_pos[0]-2, self.start_pos[1]+self.spine_len, self.start_pos[2]])
        self.left_leg = leg.Leg(side='L', base_name='leg', start_pos=[self.start_pos[0]+1, self.start_pos[1], self.start_pos[2]])
        self.right_leg = leg.Leg(side='R', base_name='leg', start_pos=[self.start_pos[0]-1, self.start_pos[1], self.start_pos[2]])
        self.spine = spine.Spine(side='M', base_name='spine', start_pos=self.start_pos, length=self.spine_len)
        self.neck = base.Base(side='M', base_name='neck', start_pos=[self.start_pos[0], self.start_pos[1]+self.spine_len+1, self.start_pos[2]])
        self.head = base.Base(side='M', base_name='head', start_pos=[self.start_pos[0], self.start_pos[1]+self.spine_len+1.5, self.start_pos[2]])
        self.tip = base.Base(side='M', base_name='tip', start_pos=[self.start_pos[0], self.start_pos[1]+self.spine_len+2, self.start_pos[2]])

        self.rig_components = [self.left_arm, self.right_arm, self.left_leg, self.right_leg, self.spine, self.neck, self.head, self.tip]

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
        left_leg_jnt = cmds.ls(self.left_leg.limb.jnt_list[0])
        right_leg_jnt = cmds.ls(self.right_leg.limb.jnt_list[0])
        root_spine_jnt = cmds.ls(self.spine.jnt_list[0])
        outliner.batch_parent([left_leg_jnt, right_leg_jnt], root_spine_jnt)

        # Arm root spine root
        left_arm_jnt = cmds.ls(self.left_arm.limb.jnt_list[0])
        right_arm_jnt = cmds.ls(self.right_arm.limb.jnt_list[0])
        top_spine_jnt = cmds.ls(self.spine.jnt_list[-1])
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
        cmds.parent(self.left_leg.limb.switch_offset_grp, self.spine.global_ctrl)
        cmds.parent(self.right_leg.limb.switch_offset_grp, self.spine.global_ctrl)

        # Arm driven by top spine control #
        cmds.parent(self.left_arm.limb.switch_offset_grp, self.spine.ctrl_list[-1])
        cmds.parent(self.right_arm.limb.switch_offset_grp, self.spine.ctrl_list[-1])

        # Neck to Head chain #
        cmds.parent(self.tip.ctrl_offset_grp, self.head.ctrl_offset_grp)
        cmds.parent(self.head.ctrl_offset_grp, self.neck.ctrl_offset_grp)
        cmds.parent(self.neck.ctrl_offset_grp, self.spine.ctrl_list[-1])

    def color_controller(self):
        for rig_component in self.rig_components:
            rig_component.color_controller()

    def delete_guide(self):
        loc = cmds.ls(self.loc_global_grp)
        cmds.delete(loc)


