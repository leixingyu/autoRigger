import maya.cmds as cmds

from autoRigger import util
from autoRigger.chain.spine import spineQuad
from autoRigger.chain import tail
from autoRigger.chain.limb.leg import legFront
from autoRigger.chain.limb.leg import legBack
from autoRigger.base import base, bone
from utility.setup import outliner


class Quadruped(bone.Bone):
    """ This module creates a quadruped template rig

    The quadruped template consists of:
    one head
    two front legs
    one spine
    two back legs &
    one tail
    """

    def __init__(self, side='na', name='standard'):
        """ Initialize Quadruped class with side and name

        :param side: str
        :param name: str
        """
        bone.Bone.__init__(self, side, name)

        self._rtype = 'quad'

        self.left_arm = legFront.LegFront(side='l', name='standard')
        self.right_arm = legFront.LegFront(side='r', name='standard')

        self.left_leg = legBack.LegBack(side='l', name='standard')
        self.right_leg = legBack.LegBack(side='r', name='standard')

        self.spine = spineQuad.SpineQuad(side='m', name='spine')
        self.tail = tail.Tail(side='m', name='tail')

        self.neck = base.Base(side='m', name='neck')
        self.head = base.Base(side='m', name='head')
        self.tip = base.Base(side='m', name='tip')

        self.rig_components = [
            self.left_arm,
            self.right_arm,
            self.left_leg,
            self.right_leg,
            self.spine,
            self.tail,
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

    def move_locator(self):
        pos = [0, 0, 0]

        util.move(self.left_arm.locs[0], pos=[1 + pos[0], 5 + pos[1], 3 + pos[2]])
        util.move(self.right_arm.locs[0], pos=[-1+pos[0], 5+pos[1], 3+pos[2]])
        util.move(self.left_leg.locs[0], pos=[1+pos[0], 5+pos[1], -3+pos[2]])
        util.move(self.right_leg.locs[0], pos=[-1+pos[0], 5+pos[1], -3+pos[2]])

        util.move(self.spine.locs[0], pos=[pos[0], 6+pos[1], -3+pos[2]])
        util.move(self.tail.locs[0], pos=[pos[0], 6+pos[1], -4+pos[2]])

        util.move(self.neck.locs[0], pos=[pos[0], 6+pos[1]+0.5, 3+pos[2]+0.5])
        util.move(self.head.locs[0], pos=[pos[0], 7.5+pos[1], 4+pos[2]])
        util.move(self.tip.locs[0], pos=[pos[0], 7.5+pos[1], 6+pos[2]])

        cmds.rotate(90, 0, 0, self.head.locs[0])
        cmds.rotate(90, 0, 0, self.tip.locs[0])

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

        neck_root = self.neck.create_joint()
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
        outliner.batch_parent([self.left_arm.offsets[0], self.right_arm.offsets[0]], self.spine.ctrls[-1])
        outliner.batch_parent([self.left_leg.offsets[0], self.right_leg.offsets[0]], self.spine.ctrls[0])
        cmds.parentConstraint(self.spine.ctrls[0], self.tail.master_ctrl, mo=1)

        # hide tail ctrl and connect ik/fk switch to spine master ctrl
        cmds.connectAttr(self.spine.master_ctrl+'.FK_IK', self.tail.master_ctrl+'.FK_IK')

        # parent head up
        cmds.parent(self.neck.offsets[0], self.spine.ctrls[-1])
        cmds.parent(self.head.offsets[0], self.neck.ctrls[0])
        cmds.parent(self.tip.offsets[0], self.head.ctrls[0])

    def color_controller(self):
        for rig_component in self.rig_components:
            rig_component.color_controller()

    def delete_guide(self):
        loc = cmds.ls(util.G_LOC_GRP)
        cmds.delete(loc)
