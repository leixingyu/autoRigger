import maya.cmds as cmds

from .. import util
from ..base import bone
from ..constant import Side
from ..utility.common import hierarchy
from ..utility.rigging import nurbs


class Foot(bone.Bone):
    """
    This module creates a foot rig
    """
    
    def __init__(self, side, name, interval=0.5, height=0.4):
        bone.Bone.__init__(self, side, name)
        self._rtype = 'foot'

        self.interval = interval
        self.height = height
        
        self.rev_jnts = list()
        self.fk_jnts = list()

    @bone.update_base_name
    def create_namespace(self):
        # sub-sequentially: ankle, ball, toe, inner, outer, heel
        segments = ['ankle', 'ball', 'toe', 'inner', 'outer', 'heel']
        for segment in segments:
            self.locs.append('{}{}_loc'.format(self.base_name, segment))
            self.jnts.append('{}{}_jnt'.format(self.base_name, segment))
            self.rev_jnts.append('{}{}rev_jnt'.format(self.base_name, segment))
            self.fk_jnts.append('{}{}fk_jnt'.format(self.base_name, segment))

        self.ctrls.append('{}_ctrl'.format(self.base_name))
        self.ctrls.append('{}fk_ctrl'.format(self.base_name))
        self.ctrls.append('{}switch_ctrl'.format(self.base_name))

    def set_shape(self):
        self._shape = list(range(3))

        self._shape[0] = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name=self.namer.tmp)[0]

        self._shape[1] = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name=self.namer.tmp)[0]
        cmds.rotate(0, 90, 0, self._shape[1], relative=1)

        self._shape[2] = nurbs.make_curve_by_text(text='FK/IK', name=self.namer.tmp)
        cmds.rotate(-90, 0, 0, self._shape[2], relative=1)

    def create_locator(self):
        # Result Foot
        cmds.spaceLocator(n=self.locs[0])

        cmds.spaceLocator(n=self.locs[1])
        cmds.parent(self.locs[1], self.locs[0], relative=1)
        cmds.move(0, -self.height, self.interval, self.locs[1], relative=1)

        cmds.spaceLocator(n=self.locs[2])
        cmds.parent(self.locs[2], self.locs[1], relative=1)
        cmds.move(0, 0, 2 * self.interval, self.locs[2], relative=1)

        # Reverse Foot Setup
        cmds.spaceLocator(n=self.locs[3])
        cmds.parent(self.locs[3], self.locs[1], relative=1)
        if self._side == Side.LEFT:
            cmds.move(-self.interval, 0, 0, self.locs[3], relative=1)
        else: 
            cmds.move(self.interval, 0, 0, self.locs[3], relative=1)

        cmds.spaceLocator(n=self.locs[4])
        cmds.parent(self.locs[4], self.locs[1], relative=1)
        if self._side == Side.LEFT:
            cmds.move(self.interval, 0, 0, self.locs[4], relative=1)
        else: 
            cmds.move(-self.interval, 0, 0, self.locs[4], relative=1)

        cmds.spaceLocator(n=self.locs[5])
        cmds.parent(self.locs[5], self.locs[1], relative=1)
        cmds.move(0, 0, -1.5 * self.interval, self.locs[5], relative=1)

        # Cleanup
        cmds.parent(self.locs[0], util.G_LOC_GRP)

    def create_joint(self):
        ankle_pos = cmds.xform(self.locs[0], q=1, t=1, ws=1)
        ball_pos = cmds.xform(self.locs[1], q=1, t=1, ws=1)
        toe_pos = cmds.xform(self.locs[2], q=1, t=1, ws=1)
        
        # Result Foot
        cmds.select(clear=1)
        cmds.joint(p=ankle_pos, name=self.jnts[0])
        cmds.joint(p=ball_pos, name=self.jnts[1])
        cmds.joint(p=toe_pos, name=self.jnts[2])

        # Reverse Foot
        cmds.select(clear=1)
        cmds.joint(p=cmds.xform(self.locs[3], q=1, t=1, ws=1), name=self.jnts[3])
        cmds.joint(p=cmds.xform(self.locs[4], q=1, t=1, ws=1), name=self.jnts[4])
        cmds.joint(p=cmds.xform(self.locs[5], q=1, t=1, ws=1), name=self.jnts[5])
        cmds.joint(p=toe_pos, name=self.rev_jnts[2])
        cmds.joint(p=ball_pos, name=self.rev_jnts[1])
        cmds.joint(p=ankle_pos, name=self.rev_jnts[0])
        cmds.setAttr(self.jnts[3]+'.visibility', 0)

        # FK Foot
        cmds.select(clear=1)
        cmds.joint(p=ankle_pos, name=self.fk_jnts[0])
        cmds.joint(p=ball_pos, name=self.fk_jnts[1])
        cmds.joint(p=toe_pos, name=self.fk_jnts[2])
        cmds.setAttr(self.fk_jnts[0]+'.visibility', 0)

        # Cleanup
        hierarchy.batch_parent([self.fk_jnts[0], self.jnts[3], self.jnts[0]], util.G_JNT_GRP)

    def place_controller(self):
        # IK Setup

        cmds.duplicate(self._shape[0], name=self.ctrls[0])
        cmds.addAttr(self.ctrls[0], longName='foot_Roll', attributeType='double', defaultValue=0, minValue=-10, maxValue=40, keyable=1)
        cmds.addAttr(self.ctrls[0], longName='foot_Bank', attributeType='double', defaultValue=0, minValue=-20, maxValue=20, keyable=1)

        foot_pos = cmds.xform(self.jnts[1], q=1, t=1, ws=1)
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2]+1, self.ctrls[0])
        cmds.makeIdentity(self.ctrls[0], apply=1, t=1, r=1, s=1)

        heel_loc = cmds.xform(self.jnts[5], q=1, t=1, ws=1)
        cmds.move(heel_loc[0], heel_loc[1], heel_loc[2], '{}.scalePivot'.format(self.ctrls[0]), '{}.rotatePivot'.format(self.ctrls[0]), absolute=1)

        # FK Setup
        cmds.duplicate(self._shape[1], name=self.ctrls[1])
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2], self.ctrls[1])
        cmds.makeIdentity(self.ctrls[1], apply=1, t=1, r=1, s=1)

        # IK/FK Switch Setup
        cmds.duplicate(self._shape[2], name=self.ctrls[2])
        if self._side == Side.LEFT:
            cmds.move(foot_pos[0]+2, foot_pos[1], foot_pos[2], self.ctrls[2])
        elif self._side == Side.RIGHT:
            cmds.move(foot_pos[0]-3, foot_pos[1], foot_pos[2], self.ctrls[2])

        cmds.addAttr(self.ctrls[2], longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=1)
        cmds.makeIdentity(self.ctrls[2], apply=1, t=1, r=1, s=1)

        # Cleanup
        hierarchy.batch_parent([self.ctrls[2], self.ctrls[0], self.ctrls[1]], util.G_CTRL_GRP)

    def add_constraint(self):
        # FK Setup
        cmds.orientConstraint(self.ctrls[1], self.fk_jnts[1], mo=1)
        cmds.pointConstraint(self.fk_jnts[0], self.jnts[0])
        cmds.orientConstraint(self.fk_jnts[0], self.jnts[0], mo=1)
        cmds.orientConstraint(self.fk_jnts[1], self.jnts[1])
        cmds.orientConstraint(self.fk_jnts[2], self.jnts[2])

        # IK Setup
        cmds.parentConstraint(self.ctrls[0], self.jnts[3], sr='z', mo=1)
        cmds.orientConstraint(self.rev_jnts[1], self.jnts[0], mo=1)
        cmds.orientConstraint(self.rev_jnts[2], self.jnts[1], mo=1)
        cmds.pointConstraint(self.rev_jnts[0], self.jnts[0], mo=1)

        # Foot Roll
        cmds.setDrivenKeyframe(self.jnts[5]+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.jnts[5]+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=-10, value=-25)

        cmds.setDrivenKeyframe(self.rev_jnts[1]+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.rev_jnts[1]+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=20, value=25)

        cmds.setDrivenKeyframe(self.rev_jnts[2]+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=20, value=0)
        cmds.setDrivenKeyframe(self.rev_jnts[2]+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=40, value=25)

        # Foot Bank
        cmds.setDrivenKeyframe(self.jnts[3]+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.jnts[4]+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=0, value=0)
        if self._side == Side.RIGHT:
            cmds.setDrivenKeyframe(self.jnts[3]+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=-20, value=-30)
            cmds.setDrivenKeyframe(self.jnts[4]+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=20, value=30)
        else:
            cmds.setDrivenKeyframe(self.jnts[3]+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=-20, value=30)
            cmds.setDrivenKeyframe(self.jnts[4]+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=20, value=-30)

        # Result Foot Setup
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.jnts[0], self.rev_jnts[1]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.jnts[0], self.rev_jnts[1]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W1'.format(self.jnts[0], self.rev_jnts[0]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W1'.format(self.jnts[0], self.rev_jnts[0]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=0, value=0)

        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W0'.format(self.jnts[0], self.fk_jnts[0]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W0'.format(self.jnts[0], self.fk_jnts[0]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jnts[0], self.fk_jnts[0]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jnts[0], self.fk_jnts[0]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=0, value=1)

        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jnts[1], self.fk_jnts[1]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jnts[1], self.fk_jnts[1]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.jnts[1], self.rev_jnts[2]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.jnts[1], self.rev_jnts[2]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=0, value=0)

        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jnts[2], self.fk_jnts[2]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jnts[2], self.fk_jnts[2]), currentDriver=self.ctrls[2]+'.FK_IK', driverValue=0, value=1)

        # IK/FK Switch Setup

        # switch will follow ankle movement
        cmds.parentConstraint(self.jnts[0], self.ctrls[2], mo=1)
        cmds.setDrivenKeyframe(self.ctrls[0]+'.visibility', currentDriver=self.ctrls[2]+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ctrls[0]+'.visibility', currentDriver=self.ctrls[2]+'.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.ctrls[1]+'.visibility', currentDriver=self.ctrls[2]+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.ctrls[1]+'.visibility', currentDriver=self.ctrls[2]+'.FK_IK', driverValue=0, value=1)
