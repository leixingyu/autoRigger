import maya.cmds as cmds
import base
import tail
import spine
import leg
from utility import outliner


class Quadruped(base.Base):
    """ This module creates a quadruped template rig

    The quadruped template consists of:
    one head
    two front legs
    one spine
    two back legs &
    one tail
    """

    def __init__(self, side='NA', base_name='standard'):
        """ Initialize Quadruped class with side and name

        :param side: str
        :param base_name: str
        """

        base.Base.__init__(self, side, base_name)
        self.metaType = 'Quadruped'
        self.assign_naming()

    def set_locator_attr(self, start_pos=[0, 0, 0]):
        self.left_arm  = leg.LegFront(side='L', base_name='standard')
        self.right_arm = leg.LegFront(side='R', base_name='standard')

        self.left_leg  = leg.LegBack(side='L', base_name='standard')
        self.right_leg = leg.LegBack(side='R', base_name='standard')

        self.spine = spine.SpineQuad(side='M', base_name='spine')
        self.tail = tail.Tail(side='M', base_name='tip')

        self.neck_root = base.Base(side='M', base_name='neck_root')
        self.head = base.Base(side='M', base_name='head')
        self.tip = base.Base(side='M', base_name='tip')

        self.left_arm.set_locator_attr(start_pos=[1+start_pos[0], 5+start_pos[1], 3+start_pos[2]])
        self.right_arm.set_locator_attr(start_pos=[-1+start_pos[0], 5+start_pos[1], 3+start_pos[2]])
        self.left_leg.set_locator_attr(start_pos=[1+start_pos[0], 5+start_pos[1], -3+start_pos[2]])
        self.right_leg.set_locator_attr(start_pos=[-1+start_pos[0], 5+start_pos[1], -3+start_pos[2]])
        self.spine.set_locator_attr(start_pos=[start_pos[0], 6+start_pos[1], -3+start_pos[2]])
        self.tail.set_locator_attr(start_pos=[start_pos[0], 6+start_pos[1], -4+start_pos[2]])
        self.neck_root.set_locator_attr(start_pos=[start_pos[0], 6+start_pos[1]+0.5, 3+start_pos[2]+0.5])
        self.head.set_locator_attr(start_pos=[start_pos[0], 7.5+start_pos[1], 4+start_pos[2]])
        self.tip.set_locator_attr(start_pos=[start_pos[0], 7.5+start_pos[1], 6+start_pos[2]])

    def build_guide(self):
        self.spine.build_guide()
        self.left_arm.build_guide()
        self.right_arm.build_guide()
        self.left_leg.build_guide()
        self.right_leg.build_guide()
        self.tail.build_guide()
        self.neck_root.build_guide()
        self.head.build_guide()
        self.tip.build_guide()

        cmds.rotate(90, 0, 0, self.head.loc)
        cmds.rotate(90, 0, 0, self.tip.loc)

    def construct_joint(self):
        left_shoulder = self.left_arm.construct_joint()
        right_shoulder = self.right_arm.construct_joint()
        left_hip = self.left_leg.construct_joint()
        right_hip = self.right_leg.construct_joint()
        spine_root = self.spine.construct_joint()
        tail_root = self.tail.construct_joint()

        neck_root = self.neck_root.construct_joint()
        head = self.head.construct_joint()
        tip = self.tip.construct_joint()

        # parent leg root joints to root spline joint
        outliner.batch_parent([left_shoulder, right_shoulder], self.spine.jnt_list[-1])

        # parent arm root joints to top spline joint
        outliner.batch_parent([left_hip, right_hip], spine_root)

        # parent tail to spine
        cmds.parent(tail_root, spine_root)

        # parent neck, head, tip
        cmds.parent(neck_root, self.spine.jnt_list[-1])
        cmds.parent(head, neck_root)
        cmds.parent(tip, head)

    def place_controller(self):
        self.left_arm.place_controller()
        self.right_arm.place_controller()
        self.left_leg.place_controller()
        self.right_leg.place_controller()
        self.spine.place_controller()
        self.tail.place_controller()

        self.neck_root.place_controller()
        self.head.place_controller()
        self.tip.place_controller()

        cmds.addAttr(self.spine.master_ctrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=True)

    def add_constraint(self):
        self.left_arm.add_constraint()
        self.right_arm.add_constraint()
        self.left_leg.add_constraint()
        self.right_leg.add_constraint()

        self.tail.add_constraint()
        self.neck_root.add_constraint()
        self.head.add_constraint()
        self.tip.add_constraint()
        self.spine.add_constraint()

        # parenting the front and back leg and tail under spine ctrl
        outliner.batch_parent([self.left_arm.ctrl_offset_list[0], self.right_arm.ctrl_offset_list[0]], self.spine.ctrl_list[-1])
        outliner.batch_parent([self.left_leg.ctrl_offset_list[0], self.right_leg.ctrl_offset_list[0]], self.spine.ctrl_list[0])
        cmds.parentConstraint(self.spine.ctrl_list[0], self.tail.master_ctrl, mo=True)

        # hide tail ctrl and connect ik/fk switch to spine master ctrl
        cmds.connectAttr(self.spine.master_ctrl+'.FK_IK', self.tail.master_ctrl+'.FK_IK')

        # parent head up
        cmds.parent(self.neck_root.ctrl_offset_grp, self.spine.ctrl_list[-1])
        cmds.parent(self.head.ctrl_offset_grp, self.neck_root.ctrl)
        cmds.parent(self.tip.ctrl_offset_grp, self.head.ctrl)

    def color_controller(self):
        self.left_arm.color_controller()
        self.right_arm.color_controller()
        self.left_leg.color_controller()
        self.right_leg.color_controller()
        self.spine.color_controller()
        self.tail.color_controller()
        self.neck_root.color_controller()
        self.head.color_controller()
        self.tip.color_controller()

    def delete_guide(self):
        loc = cmds.ls(self.loc_grp)
        cmds.delete(loc)
