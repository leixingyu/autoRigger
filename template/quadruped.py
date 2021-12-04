import maya.cmds as cmds

from .. import util
from ..base import base, bone
from ..chain import tail
from ..chain.limb.leg import legFront
from ..chain.limb.leg import legBack
from ..chain.spine import spineQuad
from ..constant import Side, ATTRS
from ..utility.common import hierarchy


class QuadrupedItem(base.BaseItem):
    def __init__(self, name='quad'):
        super(QuadrupedItem, self).__init__(name)

    def build_guide(self, side, base_name):
        self._obj = Quadruped(side, base_name)
        self._obj.build_guide()


class Quadruped(bone.Bone):
    """
    Create a control rig system for quadruped character

    Consists of two LegFront, two LegBack, one SpineQuad, three Base for neck,
    head and head tip
    """

    def __init__(self, side, name='standard'):
        """
        Override: initialize with multiple rig components
        """
        super(Quadruped, self).__init__(side, name)
        self._rtype = 'quad'

        self.l_arm = legFront.LegFront(Side.LEFT, 'standard')
        self.r_arm = legFront.LegFront(Side.RIGHT, 'standard')

        self.l_leg = legBack.LegBack(Side.LEFT, 'standard')
        self.r_leg = legBack.LegBack(Side.RIGHT, 'standard')

        self.spine = spineQuad.SpineQuad(Side.MIDDLE, 'spine')
        self.tail = tail.Tail(Side.MIDDLE, 'tail')

        self.neck = base.Base(Side.MIDDLE, 'neck')
        self.head = base.Base(Side.MIDDLE, 'head')
        self.tip = base.Base(Side.MIDDLE, 'tip')

        self._comps = [
            self.l_arm,
            self.r_arm,
            self.l_leg,
            self.r_leg,
            self.spine,
            self.tail,
            self.neck,
            self.head,
            self.tip
        ]

    def create_locator(self):
        """
        Extend: create and then move all locators
        """
        super(Quadruped, self).create_locator()
        self.move_locator()

    def move_locator(self):
        """
        Move all the roots of locators accordingly
        """
        pos = [0, 0, 0]

        util.move(self.l_arm.locs[0], pos=[1+pos[0], 5+pos[1], 3+pos[2]])
        util.move(self.r_arm.locs[0], pos=[-1+pos[0], 5+pos[1], 3+pos[2]])
        util.move(self.l_leg.locs[0], pos=[1+pos[0], 5+pos[1], -3+pos[2]])
        util.move(self.r_leg.locs[0], pos=[-1+pos[0], 5+pos[1], -3+pos[2]])

        util.move(self.spine.locs[0], pos=[pos[0], 6+pos[1], -3+pos[2]])
        util.move(self.tail.locs[0], pos=[pos[0], 6+pos[1], -4+pos[2]])

        util.move(self.neck.locs[0], pos=[pos[0], 6.5+pos[1], 3.5+pos[2]])
        util.move(self.head.locs[0], pos=[pos[0], 7.5+pos[1], 4+pos[2]])
        util.move(self.tip.locs[0], pos=[pos[0], 7.5+pos[1], 6+pos[2]])

        cmds.rotate(90, 0, 0, self.head.locs[0])
        cmds.rotate(90, 0, 0, self.tip.locs[0])

    def create_joint(self):
        """
        Create all the joints from all the rig components
        """
        super(Quadruped, self).create_joint()

        # parent leg root joints to root spline joint
        hierarchy.batch_parent(
            [self.l_arm.jnts[0], self.r_arm.jnts[0]],
            self.spine.jnts[-1])

        # parent arm root joints to top spline joint
        hierarchy.batch_parent(
            [self.l_leg.jnts[0], self.r_leg.jnts[0]],
            self.spine.jnts[0])

        # parent tail to spine
        cmds.parent(self.tail.jnts[0], self.spine.jnts[0])

        # parent neck, head, tip
        cmds.parent(self.neck.jnts[0], self.spine.jnts[-1])
        cmds.parent(self.head.jnts[0], self.neck.jnts[0])
        cmds.parent(self.tip.jnts[0], self.head.jnts[0])

    def place_controller(self):
        """
        Create and place all the joints from all the rig components
        add switch controller for spine root to tail connection
        """
        super(Quadruped, self).place_controller()
        cmds.addAttr(
            self.spine.ctrls[0],
            sn='sw', ln=ATTRS['sw'], at='double',
            dv=1, min=0, max=1,
            k=1)

    def add_constraint(self):
        """
        Add constraints to connect all the rig components
        """
        super(Quadruped, self).add_constraint()

        # parenting the front and back leg and tail under spine ctrl
        hierarchy.batch_parent(
            [self.l_arm.offsets[0], self.r_arm.offsets[0]],
            self.spine.ctrls[-1])
        hierarchy.batch_parent(
            [self.l_leg.offsets[0], self.r_leg.offsets[0]],
            self.spine.ctrls[0])
        cmds.parentConstraint(self.spine.ctrls[0], self.tail.ctrls[0], mo=1)

        # hide tail ctrl and connect ik/fk switch to spine master ctrl
        cmds.connectAttr(self.spine.ctrls[0]+'.sw', self.tail.ctrls[0]+'.sw')

        # parent head up
        cmds.parent(self.neck.offsets[0], self.spine.ctrls[-1])
        cmds.parent(self.head.offsets[0], self.neck.ctrls[0])
        cmds.parent(self.tip.offsets[0], self.head.ctrls[0])
