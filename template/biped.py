import maya.cmds as cmds

from .. import util
from ..base import base, bone
from ..chain.limb.arm import arm
from ..chain.limb.leg import leg
from ..chain.spine import spine
from ..constant import Side


class Biped(bone.Bone):
    """
    Create a control rig system for biped character

    Consists of two Arms, two Legs, one Spine, three Base for neck,
    head and head tip
    """

    def __init__(self, side, name):
        """
        Override: initialize with multiple rig components
        """
        super(Biped, self).__init__(side, name)
        self._rtype = 'biped'

        self.pos = [0, 8.4, 0]
        self.s_len = 5

        self.l_arm = arm.Arm(Side.LEFT, 'arm')
        self.r_arm = arm.Arm(Side.RIGHT, 'arm')

        self.l_leg = leg.Leg(Side.LEFT, 'leg')
        self.r_leg = leg.Leg(Side.RIGHT, 'leg')
        self.spine = spine.Spine(Side.MIDDLE, 'spine', length=self.s_len)
        self.neck = base.Base(Side.MIDDLE, 'neck')
        self.head = base.Base(Side.MIDDLE, 'head')
        self.tip = base.Base(Side.MIDDLE, 'tip')

        self._comps = [
            self.l_arm,
            self.r_arm,
            self.l_leg,
            self.r_leg,
            self.spine,
            self.neck,
            self.head,
            self.tip
        ]

    def create_locator(self):
        """
        Extend: create and then move all locators
        """
        super(Biped, self).create_locator()
        self.move_locator()

    def move_locator(self):
        """
        Move all the roots of locators accordingly
        """
        util.move(self.l_arm.limb.locs[0],
                  pos=[self.pos[0]+2, self.pos[1]+self.s_len, self.pos[2]])
        util.move(self.r_arm.limb.locs[0],
                  pos=[self.pos[0]-2, self.pos[1]+self.s_len, self.pos[2]])

        util.move(self.l_leg.limb.locs[0],
                  pos=[self.pos[0]+1, self.pos[1], self.pos[2]])
        util.move(self.r_leg.limb.locs[0],
                  pos=[self.pos[0]-1, self.pos[1], self.pos[2]])

        util.move(self.spine.locs[0], pos=self.pos)

        util.move(self.neck.locs[0],
                  pos=[self.pos[0], self.pos[1]+self.s_len+1, self.pos[2]])
        util.move(self.head.locs[0],
                  pos=[self.pos[0], self.pos[1]+self.s_len+1.5, self.pos[2]])
        util.move(self.tip.locs[0],
                  pos=[self.pos[0], self.pos[1]+self.s_len+2, self.pos[2]])

    def create_joint(self):
        """
        Create all the joints from all the rig components
        """
        super(Biped, self).create_joint()

        # leg root to spine root
        cmds.parent(self.l_leg.limb.jnts[0], self.spine.jnts[0])
        cmds.parent(self.r_leg.limb.jnts[0], self.spine.jnts[0])

        # arm root to spine top
        cmds.parent(self.l_arm.limb.jnts[0], self.spine.jnts[-1])
        cmds.parent(self.r_arm.limb.jnts[0], self.spine.jnts[-1])

        # neck to spine top, head to neck
        cmds.parent(self.neck.jnts[0], self.spine.jnts[-1])
        cmds.parent(self.head.jnts[0], self.neck.jnts[0])
        cmds.parent(self.tip.jnts[0], self.head.jnts[0])

    def add_constraint(self):
        """
        Add constraints to connect all the rig components
        """
        super(Biped, self).add_constraint()

        # leg driven by root spine control #
        cmds.parent(self.l_leg.limb.offsets[0], self.spine.ctrls[0])
        cmds.parent(self.r_leg.limb.offsets[0], self.spine.ctrls[0])

        # arm driven by top spine control #
        cmds.parent(self.l_arm.limb.offsets[0], self.spine.ctrls[-1])
        cmds.parent(self.r_arm.limb.offsets[0], self.spine.ctrls[-1])

        # neck to head chain #
        cmds.parent(self.tip.offsets[0], self.head.offsets[0])
        cmds.parent(self.head.offsets[0], self.neck.offsets[0])
        cmds.parent(self.neck.offsets[0], self.spine.ctrls[-1])
