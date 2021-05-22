import maya.cmds as cmds
from utility import outliner
import base
import arm
import leg
import spine


class Biped(base.Base):
    """ This module creates a biped template rig

    The biped template consists of:
    one head
    two arms
    one spine &
    two legs
    """

    def __init__(self, side, base_name):
        """ Initialize Biped class with side and name

        :param side: str
        :param base_name: str
        """

        base.Base.__init__(self, side, base_name)
        self.metaType = 'Biped'
        self.set_locator_attr(start_pos=[0, 8.4, 0], spine_len=5.0)

        self.left_arm = arm.Arm(side='L', base_name='arm')
        self.right_arm = arm.Arm(side='R', base_name='arm')
        self.left_leg = leg.Leg(side='L', base_name='leg')
        self.right_leg = leg.Leg(side='R', base_name='leg')
        self.spine = spine.Spine(side='M', base_name='spine')
        self.neck = base.Base(side='M', base_name='neck')
        self.head = base.Base(side='M', base_name='head')
        self.tip = base.Base(side='M', base_name='tip')

    def set_locator_attr(self, start_pos=[0, 0, 0], spine_len=6.0, scale=0.2):
        self.start_pos = start_pos
        self.spine_len = spine_len
        self.scale = scale

    def build_guide(self):
        self.left_arm.set_locator_attr(start_pos=[self.start_pos[0]+2, self.start_pos[1]+self.spine_len, self.start_pos[2]])
        self.right_arm.set_locator_attr(start_pos=[self.start_pos[0]-2, self.start_pos[1]+self.spine_len, self.start_pos[2]])
        self.left_leg.set_locator_attr(start_pos=[self.start_pos[0]+1, self.start_pos[1], self.start_pos[2]])
        self.right_leg.set_locator_attr(start_pos=[self.start_pos[0]-1, self.start_pos[1], self.start_pos[2]])
        self.spine.set_locator_attr(start_pos=self.start_pos, length=self.spine_len)
        self.neck.set_locator_attr(start_pos=[self.start_pos[0], self.start_pos[1]+self.spine_len+1, self.start_pos[2]])
        self.head.set_locator_attr(start_pos=[self.start_pos[0], self.start_pos[1]+self.spine_len+1.5, self.start_pos[2]])
        self.tip.set_locator_attr(start_pos=[self.start_pos[0], self.start_pos[1]+self.spine_len+2, self.start_pos[2]])

        self.left_arm.build_guide()
        self.right_arm.build_guide()
        self.left_leg.build_guide()
        self.right_leg.build_guide()
        self.spine.build_guide()
        self.neck.build_guide()
        self.head.build_guide()
        self.tip.build_guide()

    def construct_joint(self):
        self.left_arm.construct_joint()
        self.right_arm.construct_joint()
        self.left_leg.construct_joint()
        self.right_leg.construct_joint()
        self.spine.construct_joint()
        self.neck.construct_joint()
        self.head.construct_joint()
        self.tip.construct_joint()

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
        self.left_arm.place_controller()
        self.right_arm.place_controller()
        self.left_leg.place_controller()
        self.right_leg.place_controller()
        self.spine.place_controller()
        self.neck.place_controller()
        self.head.place_controller()
        self.tip.place_controller()

    def add_constraint(self):
        self.left_arm.add_constraint()
        self.right_arm.add_constraint()
        self.left_leg.add_constraint()
        self.right_leg.add_constraint()
        self.spine.add_constraint()
        self.neck.add_constraint()
        self.head.add_constraint()
        self.tip.add_constraint()

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
        self.left_arm.color_controller()
        self.right_arm.color_controller()
        self.left_leg.color_controller()
        self.right_leg.color_controller()
        self.spine.color_controller()
        self.neck.color_controller()
        self.head.color_controller()
        self.tip.color_controller()

    def delete_guide(self):
        loc = cmds.ls(self.loc_grp)
        cmds.delete(loc)


