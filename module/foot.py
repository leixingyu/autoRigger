import maya.cmds as cmds

from .. import util, shape
from ..base import bone
from ..constant import Side
from ..utility.common import hierarchy


ATTRS = {
    'fr': 'foot_roll',
    'fb': 'foot_bank',
    'sw': 'FK_IK'
}


cmds.sdk = cmds.setDrivenKeyframe


class Foot(bone.Bone):
    """
    Create a reverse FK rig system for Foot
    """
    
    def __init__(self, side, name, interval=0.5, height=0.4):
        """
        Extend: specify interval and height for foot creation

        :param interval: float. horizontal distance between segments of foot
        :param height: float. vertical height of ankle to the ground
        """
        bone.Bone.__init__(self, side, name)
        self._rtype = 'foot'

        self.interval = interval
        self.height = height
        
        self.rev_jnts = list()
        self.fk_jnts = list()

    @bone.update_base_name
    def create_namespace(self):
        """
        Override: create naming for reverse, FK support
        """
        segments = ['ankle', 'ball', 'toe', 'inner', 'outer', 'heel']
        for segment in segments:
            self.locs.append('{}{}_loc'.format(self.base, segment))
            self.jnts.append('{}{}_jnt'.format(self.base, segment))
            self.rev_jnts.append('{}{}rev_jnt'.format(self.base, segment))
            self.fk_jnts.append('{}{}fk_jnt'.format(self.base, segment))

        self.ctrls.append('{}_ctrl'.format(self.base))
        self.ctrls.append('{}fk_ctrl'.format(self.base))
        self.ctrls.append('{}switch_ctrl'.format(self.base))

    def set_shape(self):
        """
        Override: setup controller shapes for foot and FK switch
        """
        self._shape = list(range(3))

        self._shape[0] = shape.make_circle(self._scale)
        self._shape[1] = shape.make_circle(self._scale)
        cmds.rotate(0, 90, 0, self._shape[1], r=1)
        self._shape[2] = shape.make_text('FK/IK', self._scale)

    def create_locator(self):
        """
        Override: create locators for result foot and reverse foot setup
        """
        # result foot
        cmds.spaceLocator(n=self.locs[0])

        cmds.spaceLocator(n=self.locs[1])
        cmds.parent(self.locs[1], self.locs[0], r=1)
        cmds.move(0, -self.height, self.interval, self.locs[1], r=1)

        cmds.spaceLocator(n=self.locs[2])
        cmds.parent(self.locs[2], self.locs[1], r=1)
        cmds.move(0, 0, 2 * self.interval, self.locs[2], r=1)

        # reverse foot setup
        cmds.spaceLocator(n=self.locs[3])
        cmds.parent(self.locs[3], self.locs[1], r=1)
        if self._side == Side.LEFT:
            cmds.move(-self.interval, 0, 0, self.locs[3], r=1)
        else: 
            cmds.move(self.interval, 0, 0, self.locs[3], r=1)

        cmds.spaceLocator(n=self.locs[4])
        cmds.parent(self.locs[4], self.locs[1], r=1)
        if self._side == Side.LEFT:
            cmds.move(self.interval, 0, 0, self.locs[4], r=1)
        else: 
            cmds.move(-self.interval, 0, 0, self.locs[4], r=1)

        cmds.spaceLocator(n=self.locs[5])
        cmds.parent(self.locs[5], self.locs[1], r=1)
        cmds.move(0, 0, -1.5 * self.interval, self.locs[5], r=1)

        cmds.parent(self.locs[0], util.G_LOC_GRP)

    def create_joint(self):
        """
        Override: create joint sets for result, reverse and FK foot
        """
        ankle_pos = cmds.xform(self.locs[0], q=1, t=1, ws=1)
        ball_pos = cmds.xform(self.locs[1], q=1, t=1, ws=1)
        toe_pos = cmds.xform(self.locs[2], q=1, t=1, ws=1)
        
        # result foot
        cmds.select(clear=1)
        cmds.joint(p=ankle_pos, n=self.jnts[0])
        cmds.joint(p=ball_pos, n=self.jnts[1])
        cmds.joint(p=toe_pos, n=self.jnts[2])

        # reverse foot
        cmds.select(clear=1)
        cmds.joint(p=cmds.xform(self.locs[3], q=1, t=1, ws=1), n=self.jnts[3])
        cmds.joint(p=cmds.xform(self.locs[4], q=1, t=1, ws=1), n=self.jnts[4])
        cmds.joint(p=cmds.xform(self.locs[5], q=1, t=1, ws=1), n=self.jnts[5])
        cmds.joint(p=toe_pos, n=self.rev_jnts[2])
        cmds.joint(p=ball_pos, n=self.rev_jnts[1])
        cmds.joint(p=ankle_pos, n=self.rev_jnts[0])
        cmds.setAttr(self.jnts[3]+'.v', 0)

        # FK foot
        cmds.select(clear=1)
        cmds.joint(p=ankle_pos, n=self.fk_jnts[0])
        cmds.joint(p=ball_pos, n=self.fk_jnts[1])
        cmds.joint(p=toe_pos, n=self.fk_jnts[2])
        cmds.setAttr(self.fk_jnts[0]+'.v', 0)

        hierarchy.batch_parent(
            [self.fk_jnts[0], self.jnts[3], self.jnts[0]],
            util.G_JNT_GRP)

    def place_controller(self):
        """
        Override: create and place controller for IK, FK, switch support
        add custom controller attribute for foot roll and foot bank
        """
        # reverse
        cmds.duplicate(self._shape[0], n=self.ctrls[0])
        cmds.addAttr(
            self.ctrls[0],
            sn='fr', ln=ATTRS['fr'], at='double',
            dv=0, min=-10, max=40,
            k=1)
        cmds.addAttr(
            self.ctrls[0],
            sn='fb', ln=ATTRS['fb'], at='double',
            dv=0, min=-20, max=20,
            k=1)

        foot_pos = cmds.xform(self.jnts[1], q=1, t=1, ws=1)
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2]+1, self.ctrls[0])
        cmds.makeIdentity(self.ctrls[0], apply=1, t=1, r=1, s=1)

        heel_loc = cmds.xform(self.jnts[5], q=1, t=1, ws=1)
        util.move_to('{}.sp'.format(self.ctrls[0]), heel_loc)
        util.move_to('{}.rp'.format(self.ctrls[0]), heel_loc)

        # FK setup
        cmds.duplicate(self._shape[1], n=self.ctrls[1])
        util.move_to(self.ctrls[1], foot_pos)
        cmds.makeIdentity(self.ctrls[1], apply=1, t=1, r=1, s=1)

        # IK/FK switch
        cmds.duplicate(self._shape[2], n=self.ctrls[2])
        if self._side == Side.LEFT:
            cmds.move(foot_pos[0]+2, foot_pos[1], foot_pos[2], self.ctrls[2])
        elif self._side == Side.RIGHT:
            cmds.move(foot_pos[0]-3, foot_pos[1], foot_pos[2], self.ctrls[2])

        cmds.addAttr(
            self.ctrls[2],
            sn='sw', ln=ATTRS['sw'], at='double',
            dv=1, min=0, max=1,
            k=1)
        cmds.makeIdentity(self.ctrls[2], apply=1, t=1, r=1, s=1)

        hierarchy.batch_parent(
            [self.ctrls[2], self.ctrls[0], self.ctrls[1]], util.G_CTRL_GRP)

    def add_constraint(self):
        """
        Override: add constraints for reverse, FK, switch support
        as well as custom behavior like foot roll and foot bank
        """
        # FK setup
        cons_p1 = cmds.pointConstraint(self.fk_jnts[0], self.jnts[0])[0]
        cons_o1 = cmds.orientConstraint(self.fk_jnts[0], self.jnts[0], mo=1)[0]
        cons_o2 = cmds.orientConstraint(self.fk_jnts[1], self.jnts[1])[0]
        cons_o3 = cmds.orientConstraint(self.fk_jnts[2], self.jnts[2])[0]
        cmds.orientConstraint(self.ctrls[1], self.fk_jnts[1], mo=1)

        # reverse
        cmds.parentConstraint(self.ctrls[0], self.jnts[3], sr='z', mo=1)
        cmds.orientConstraint(self.rev_jnts[1], self.jnts[0], mo=1)
        cmds.orientConstraint(self.rev_jnts[2], self.jnts[1], mo=1)
        cmds.pointConstraint(self.rev_jnts[0], self.jnts[0], mo=1)

        # foot roll
        cmds.sdk(self.jnts[5]+'.rx', cd=self.ctrls[0]+'.fr', dv=0, v=0)
        cmds.sdk(self.jnts[5]+'.rx', cd=self.ctrls[0]+'.fr', dv=-10, v=-25)

        cmds.sdk(self.rev_jnts[1]+'.rx', cd=self.ctrls[0]+'.fr', dv=0, v=0)
        cmds.sdk(self.rev_jnts[1]+'.rx', cd=self.ctrls[0]+'.fr', dv=20, v=25)

        cmds.sdk(self.rev_jnts[2]+'.rx', cd=self.ctrls[0]+'.fr', dv=20, v=0)
        cmds.sdk(self.rev_jnts[2]+'.rx', cd=self.ctrls[0]+'.fr', dv=40, v=25)

        # foot bank
        cmds.sdk(self.jnts[3]+'.rz', cd=self.ctrls[0]+'.fb', dv=0, v=0)
        cmds.sdk(self.jnts[4]+'.rz', cd=self.ctrls[0]+'.fb', dv=0, v=0)
        if self._side == Side.RIGHT:
            cmds.sdk(self.jnts[3]+'.rz', cd=self.ctrls[0]+'.fb', dv=-20, v=-30)
            cmds.sdk(self.jnts[4]+'.rz', cd=self.ctrls[0]+'.fb', dv=20, v=30)
        else:
            cmds.sdk(self.jnts[3]+'.rz', cd=self.ctrls[0]+'.fb', dv=-20, v=30)
            cmds.sdk(self.jnts[4]+'.rz', cd=self.ctrls[0]+'.fb', dv=20, v=-30)

        # result foot
        cmds.sdk('{}.w1'.format(cons_o1), cd=self.ctrls[2]+'.sw', dv=1, v=1)
        cmds.sdk('{}.w1'.format(cons_o1), cd=self.ctrls[2]+'.sw', dv=0, v=0)
        cmds.sdk('{}.w1'.format(cons_p1), cd=self.ctrls[2]+'.sw', dv=1, v=1)
        cmds.sdk('{}.w1'.format(cons_p1), cd=self.ctrls[2]+'.sw', dv=0, v=0)

        cmds.sdk('{}.w0'.format(cons_p1), cd=self.ctrls[2]+'.sw', dv=1, v=0)
        cmds.sdk('{}.w0'.format(cons_p1), cd=self.ctrls[2]+'.sw', dv=0, v=1)
        cmds.sdk('{}.w0'.format(cons_o1), cd=self.ctrls[2]+'.sw', dv=1, v=0)
        cmds.sdk('{}.w0'.format(cons_o1), cd=self.ctrls[2]+'.sw', dv=0, v=1)

        cmds.sdk('{}.w0'.format(cons_o2), cd=self.ctrls[2]+'.sw', dv=1, v=0)
        cmds.sdk('{}.w0'.format(cons_o2), cd=self.ctrls[2]+'.sw', dv=0, v=1)
        cmds.sdk('{}.w1'.format(cons_o2), cd=self.ctrls[2]+'.sw', dv=1, v=1)
        cmds.sdk('{}.w1'.format(cons_o2), cd=self.ctrls[2]+'.sw', dv=0, v=0)

        cmds.sdk('{}.w0'.format(cons_o3), cd=self.ctrls[2]+'.sw', dv=1, v=0)
        cmds.sdk('{}.w0'.format(cons_o3), cd=self.ctrls[2]+'.sw', dv=0, v=1)

        # IK/FK switch
        # switch will follow ankle movement
        cmds.parentConstraint(self.jnts[0], self.ctrls[2], mo=1)
        cmds.sdk(self.ctrls[0]+'.v', cd=self.ctrls[2]+'.sw', dv=1, v=1)
        cmds.sdk(self.ctrls[0]+'.v', cd=self.ctrls[2]+'.sw', dv=0, v=0)
        cmds.sdk(self.ctrls[1]+'.v', cd=self.ctrls[2]+'.sw', dv=1, v=0)
        cmds.sdk(self.ctrls[1]+'.v', cd=self.ctrls[2]+'.sw', dv=0, v=1)
