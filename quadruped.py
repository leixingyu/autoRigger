import maya.cmds as cmds
from . import base, rig, tail, spine, leg
from utility import outliner


class Quadruped(rig.Bone):
    """ This module creates a quadruped template rig

    The quadruped template consists of:
    one head
    two front legs
    one spine
    two back legs &
    one tail
    """

    def __init__(self, side='NA', rig_type='Quadruped', name='standard', start_pos=[0, 0, 0]):
        """ Initialize Quadruped class with side and name

        :param side: str
        :param name: str
        """

        rig.Bone.__init__(self, side, name, rig_type)

        self.left_arm  = leg.LegFront(
            side='L',
            name='standard',
            start_pos=[
                1 + start_pos[0],
                5 + start_pos[1],
                3 + start_pos[2]]
        )

        self.right_arm = leg.LegFront(side='R', name='standard', start_pos=[-1+start_pos[0], 5+start_pos[1], 3+start_pos[2]])

        self.left_leg  = leg.LegBack(side='L', name='standard', start_pos=[1+start_pos[0], 5+start_pos[1], -3+start_pos[2]])
        self.right_leg = leg.LegBack(side='R', name='standard', start_pos=[-1+start_pos[0], 5+start_pos[1], -3+start_pos[2]])

        self.spine = spine.SpineQuad(side='M', name='spine', start_pos=[start_pos[0], 6+start_pos[1], -3+start_pos[2]])
        self.tail = tail.Tail(side='M', name='tail', start_pos=[start_pos[0], 6+start_pos[1], -4+start_pos[2]])

        self.neck_root = base.Base(side='M', name='neck_root', start_pos=[start_pos[0], 6+start_pos[1]+0.5, 3+start_pos[2]+0.5])
        self.head = base.Base(side='M', name='head', start_pos=[start_pos[0], 7.5+start_pos[1], 4+start_pos[2]])
        self.tip = base.Base(side='M', name='tip', start_pos=[start_pos[0], 7.5+start_pos[1], 6+start_pos[2]])

        self.rig_components = [self.left_arm, self.right_arm, self.left_leg, self.right_leg, self.spine, self.tail, self.neck_root, self.head, self.tip]

    def create_locator(self):
        for rig_component in self.rig_components:
            rig_component.create_locator()

        cmds.rotate(90, 0, 0, self.head.loc)
        cmds.rotate(90, 0, 0, self.tip.loc)

    def set_controller_shape(self):
        for rig_component in self.rig_components:
            rig_component.set_controller_shape()

    def create_joint(self):
        left_shoulder = self.left_arm.create_joint()
        right_shoulder = self.right_arm.create_joint()
        left_hip = self.left_leg.create_joint()
        right_hip = self.right_leg.create_joint()
        spine_root = self.spine.create_joint()
        tail_root = self.tail.create_joint()

        neck_root = self.neck_root.create_joint()
        head = self.head.create_joint()
        tip = self.tip.create_joint()

        # parent leg root joints to root spline joint
        outliner.batch_parent([left_shoulder, right_shoulder], self.spine.jnts[-1])

        # parent arm root joints to top spline joint
        outliner.batch_parent([left_hip, right_hip], spine_root)

        # parent tail to spine
        cmds.parent(tail_root, spine_root)

        # parent neck, head, tip
        cmds.parent(neck_root, self.spine.jnts[-1])
        cmds.parent(head, neck_root)
        cmds.parent(tip, head)

    def place_controller(self):
        for rig_component in self.rig_components:
            rig_component.place_controller()

        cmds.addAttr(self.spine.master_ctrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=1)

    def add_constraint(self):
        for rig_component in self.rig_components:
            rig_component.add_constraint()

        # parenting the front and back leg and tail under spine ctrl
        outliner.batch_parent([self.left_arm.ctrl_offsets[0], self.right_arm.ctrl_offsets[0]], self.spine.ctrls[-1])
        outliner.batch_parent([self.left_leg.ctrl_offsets[0], self.right_leg.ctrl_offsets[0]], self.spine.ctrls[0])
        cmds.parentConstraint(self.spine.ctrls[0], self.tail.master_ctrl, mo=1)

        # hide tail ctrl and connect ik/fk switch to spine master ctrl
        cmds.connectAttr(self.spine.master_ctrl+'.FK_IK', self.tail.master_ctrl+'.FK_IK')

        # parent head up
        cmds.parent(self.neck_root.ctrl_offset, self.spine.ctrls[-1])
        cmds.parent(self.head.ctrl_offset, self.neck_root.ctrl)
        cmds.parent(self.tip.ctrl_offset, self.head.ctrl)

    def color_controller(self):
        for rig_component in self.rig_components:
            rig_component.color_controller()


    def delete_guide(self):
        loc = cmds.ls(self.loc_global_grp)
        cmds.delete(loc)
