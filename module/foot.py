import maya.cmds as cmds

from autoRigger.base import bone
from autoRigger import util
from utility.setup import outliner
from utility.rigging import nurbs


class Foot(bone.Bone):
    """ This module creates a foot rig """
    
    def __init__(self, side, name, interval=0.5, height=0.4):
        """ Initialize Foot class with side and name
        
        :param side: str
        :param name: str
        """
        bone.Bone.__init__(self, side, name)
        self._rtype = 'foot'

        self.interval = interval
        self.height = height
        self.scale = 0.2

    def create_namespace(self):
        self.base_name = '{}_{}_{}'.format(self._rtype, self._side, self._name)

        self.locs.append('{}_loc'.format(self.base_name))
        self.jnts.append('{}_jnt'.format(self.base_name))
        self.ctrls.append('{}_ctrl'.format(self.base_name))
        self.offsets.append('{}_offset'.format(self.base_name))

        self.ankle_loc = '{}{}_loc'.format(self.base_name, 'ankle')
        self.ball_loc = '{}{}_loc'.format(self.base_name, 'ball')
        self.toe_loc = '{}{}_loc'.format(self.base_name, 'toe')
        self.inner_loc = '{}{}_loc'.format(self.base_name, 'inner')
        self.outer_loc = '{}{}_loc'.format(self.base_name, 'outer')
        self.heel_loc = '{}{}_loc'.format(self.base_name, 'heel')

        self.ankle_jnt = '{}{}_jnt'.format(self.base_name, 'ankle')
        self.ball_jnt = '{}{}_jnt'.format(self.base_name, 'ball')
        self.toe_jnt = '{}{}_jnt'.format(self.base_name, 'toe')
        self.inner_jnt = '{}{}_jnt'.format(self.base_name, 'inner')
        self.outer_jnt = '{}{}_jnt'.format(self.base_name, 'outer')
        self.heel_jnt = '{}{}_jnt'.format(self.base_name, 'heel')

        self.rev_ankle_jnt = '{}{}_jnt'.format(self.base_name, 'reverseankle')
        self.rev_ball_jnt = '{}{}_jnt'.format(self.base_name, 'reverseball')
        self.rev_toe_jnt = '{}{}_jnt'.format(self.base_name, 'reversetoe')

        self.fk_ankle_jnt = '{}{}_jnt'.format(self.base_name, 'fkankle')
        self.fk_ball_jnt = '{}{}_jnt'.format(self.base_name, 'fkball')
        self.fk_toe_jnt = '{}{}_jnt'.format(self.base_name, 'fktoe')

        self.fk_ctrl = '{}{}_ctrl'.format(self.base_name, 'fk')
        self.switch_ctrl = '{}{}_ctrl'.format(self.base_name, 'switch')

    def set_controller_shape(self):
        self._shape = list(range(3))

        self._shape[0] = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name=self.namer.tmp)[0]

        self._shape[1] = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name=self.namer.tmp)[0]
        cmds.rotate(0, 90, 0, self._shape[1], relative=1)
        cmds.scale(0.4, 0.4, 0.4, self._shape[1])

        self._shape[2] = nurbs.make_curve_by_text(text='FK/IK', name=self.namer.tmp)
        cmds.rotate(-90, 0, 0, self._shape[2], relative=1)

    def create_locator(self):
        # Result Foot
        cmds.spaceLocator(n=self.ankle_loc)
        cmds.scale(self.scale, self.scale, self.scale, self.ankle_loc)

        cmds.spaceLocator(n=self.ball_loc)
        cmds.parent(self.ball_loc, self.ankle_loc, relative=1)
        cmds.move(0, -self.height, self.interval, self.ball_loc, relative=1)

        cmds.spaceLocator(n=self.toe_loc)
        cmds.parent(self.toe_loc, self.ball_loc, relative=1)
        cmds.move(0, 0, 2 * self.interval, self.toe_loc, relative=1)

        # Reverse Foot Setup
        cmds.spaceLocator(n=self.inner_loc)
        cmds.parent(self.inner_loc, self.ball_loc, relative=1)
        if self._side == 'L':
            cmds.move(-self.interval, 0, 0, self.inner_loc, relative=1)
        else: 
            cmds.move(self.interval, 0, 0, self.inner_loc, relative=1)

        cmds.spaceLocator(n=self.outer_loc)
        cmds.parent(self.outer_loc, self.ball_loc, relative=1)
        if self._side == 'L':
            cmds.move(self.interval, 0, 0, self.outer_loc, relative=1)
        else: 
            cmds.move(-self.interval, 0, 0, self.outer_loc, relative=1)

        cmds.spaceLocator(n=self.heel_loc)
        cmds.parent(self.heel_loc, self.ball_loc, relative=1)
        cmds.move(0, 0, -1.5 * self.interval, self.heel_loc, relative=1)

        # Cleanup
        cmds.parent(self.ankle_loc, util.G_LOC_GRP)

    def create_joint(self):
        # Result Foot
        cmds.select(clear=1)

        ankle_pos = cmds.xform(self.ankle_loc, q=1, t=1, ws=1)
        ball_pos = cmds.xform(self.ball_loc, q=1, t=1, ws=1)
        toe_pos = cmds.xform(self.toe_loc, q=1, t=1, ws=1)

        cmds.joint(p=ankle_pos, name=self.ankle_jnt)
        cmds.joint(p=ball_pos, name=self.ball_jnt)
        cmds.joint(p=toe_pos, name=self.toe_jnt)

        # Reverse Foot
        cmds.select(clear=1)

        inner_pos = cmds.xform(self.inner_loc, q=1, t=1, ws=1)
        outer_pos = cmds.xform(self.outer_loc, q=1, t=1, ws=1)
        heel_pos = cmds.xform(self.heel_loc, q=1, t=1, ws=1)

        cmds.joint(p=inner_pos, name=self.inner_jnt)
        cmds.joint(p=outer_pos, name=self.outer_jnt)
        cmds.joint(p=heel_pos, name=self.heel_jnt)
        cmds.joint(p=toe_pos, name=self.rev_toe_jnt)
        cmds.joint(p=ball_pos, name=self.rev_ball_jnt)
        cmds.joint(p=ankle_pos, name=self.rev_ankle_jnt)

        cmds.setAttr(self.inner_jnt+'.visibility', 0)

        # FK Foot
        cmds.select(clear=1)
        cmds.joint(p=ankle_pos, name=self.fk_ankle_jnt)
        cmds.joint(p=ball_pos, name=self.fk_ball_jnt)
        cmds.joint(p=toe_pos, name=self.fk_toe_jnt)
        cmds.setAttr(self.fk_ankle_jnt+'.visibility', 0)

        # Cleanup
        outliner.batch_parent([self.fk_ankle_jnt, self.inner_jnt, self.ankle_jnt], util.G_JNT_GRP)

    def place_controller(self):
        # IK Setup

        cmds.duplicate(self._shape[0], name=self.ctrls[0])
        cmds.addAttr(self.ctrls[0], longName='foot_Roll', attributeType='double', defaultValue=0, minValue=-10, maxValue=40, keyable=1)
        cmds.addAttr(self.ctrls[0], longName='foot_Bank', attributeType='double', defaultValue=0, minValue=-20, maxValue=20, keyable=1)

        foot_pos = cmds.xform(self.ball_jnt, q=1, t=1, ws=1)
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2]+1, self.ctrls[0])
        cmds.makeIdentity(self.ctrls[0], apply=1, t=1, r=1, s=1)

        heel_loc = cmds.xform(self.heel_jnt, q=1, t=1, ws=1)
        cmds.move(heel_loc[0], heel_loc[1], heel_loc[2], '{}.scalePivot'.format(self.ctrls[0]), '{}.rotatePivot'.format(self.ctrls[0]), absolute=1)

        # FK Setup
        cmds.duplicate(self._shape[1], name=self.fk_ctrl)
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2], self.fk_ctrl)
        cmds.makeIdentity(self.fk_ctrl, apply=1, t=1, r=1, s=1)

        # IK/FK Switch Setup
        cmds.duplicate(self._shape[2], name=self.switch_ctrl)
        if self._side == "L":
            cmds.move(foot_pos[0]+2, foot_pos[1], foot_pos[2], self.switch_ctrl)

        elif self._side == "R":
            cmds.move(foot_pos[0]-3, foot_pos[1], foot_pos[2], self.switch_ctrl)

        cmds.scale(0.5, 0.5, 0.5, self.switch_ctrl)
        cmds.addAttr(self.switch_ctrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=1)
        cmds.makeIdentity(self.switch_ctrl, apply=1, t=1, r=1, s=1)

        # Cleanup
        outliner.batch_parent([self.switch_ctrl, self.ctrls[0], self.fk_ctrl], util.G_CTRL_GRP)

    def add_constraint(self):
        # FK Setup
        cmds.orientConstraint(self.fk_ctrl, self.fk_ball_jnt, mo=1)
        cmds.pointConstraint(self.fk_ankle_jnt, self.ankle_jnt)
        cmds.orientConstraint(self.fk_ankle_jnt, self.ankle_jnt, mo=1)
        cmds.orientConstraint(self.fk_ball_jnt, self.ball_jnt)
        cmds.orientConstraint(self.fk_toe_jnt, self.toe_jnt)

        # IK Setup
        cmds.parentConstraint(self.ctrls[0], self.inner_jnt, sr='z', mo=1)
        cmds.orientConstraint(self.rev_ball_jnt, self.ankle_jnt, mo=1)
        cmds.orientConstraint(self.rev_toe_jnt, self.ball_jnt, mo=1)
        cmds.pointConstraint(self.rev_ankle_jnt, self.ankle_jnt, mo=1)

        # Foot Roll
        cmds.setDrivenKeyframe(self.heel_jnt+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.heel_jnt+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=-10, value=-25)

        cmds.setDrivenKeyframe(self.rev_ball_jnt+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.rev_ball_jnt+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=20, value=25)

        cmds.setDrivenKeyframe(self.rev_toe_jnt+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=20, value=0)
        cmds.setDrivenKeyframe(self.rev_toe_jnt+'.rotateX', currentDriver=self.ctrls[0]+'.foot_Roll', driverValue=40, value=25)

        # Foot Bank
        cmds.setDrivenKeyframe(self.inner_jnt+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.outer_jnt+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=0, value=0)
        if self._side == 'R':
            cmds.setDrivenKeyframe(self.inner_jnt+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=-20, value=-30)
            cmds.setDrivenKeyframe(self.outer_jnt+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=20, value=30)
        else:
            cmds.setDrivenKeyframe(self.inner_jnt+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=-20, value=30)
            cmds.setDrivenKeyframe(self.outer_jnt+'.rotateZ', currentDriver=self.ctrls[0]+'.foot_Bank', driverValue=20, value=-30)

        # Result Foot Setup
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ankle_jnt, self.rev_ball_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ankle_jnt, self.rev_ball_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W1'.format(self.ankle_jnt, self.rev_ankle_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W1'.format(self.ankle_jnt, self.rev_ankle_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=0)

        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W0'.format(self.ankle_jnt, self.fk_ankle_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W0'.format(self.ankle_jnt, self.fk_ankle_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ankle_jnt, self.fk_ankle_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ankle_jnt, self.fk_ankle_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=1)

        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ball_jnt, self.fk_ball_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ball_jnt, self.fk_ball_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ball_jnt, self.rev_toe_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ball_jnt, self.rev_toe_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=0)

        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.toe_jnt, self.fk_toe_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.toe_jnt, self.fk_toe_jnt), currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=1)

        # IK/FK Switch Setup

        # switch will follow ankle movement
        cmds.parentConstraint(self.ankle_jnt, self.switch_ctrl, mo=1)

        cmds.setDrivenKeyframe(self.ctrls[0]+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ctrls[0]+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.fk_ctrl+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.fk_ctrl+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=1)
