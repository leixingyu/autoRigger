import maya.cmds as cmds
from . import base
from utility import outliner, other


class Foot(base.Base):
    """ This module creates a foot rig """
    
    def __init__(self, side, base_name):
        """ Initialize Foot class with side and name
        
        :param side: str
        :param base_name: str
        """
        
        base.Base.__init__(self, side, base_name)
        self.meta_type = 'Foot'
        self.assign_naming()
        self.assign_secondary_naming()

    def assign_secondary_naming(self):
        self.ankle_loc_name = '{}{}_loc'.format(self.name, 'ankle')
        self.ball_loc_name  = '{}{}_loc'.format(self.name, 'ball')
        self.toe_loc_name   = '{}{}_loc'.format(self.name, 'toe')
        self.inner_loc_name = '{}{}_loc'.format(self.name, 'inner')
        self.outer_loc_name = '{}{}_loc'.format(self.name, 'outer')
        self.heel_loc_name  = '{}{}_loc'.format(self.name, 'heel')

        self.ankle_jnt_name = '{}{}_jnt'.format(self.name, 'ankle')
        self.ball_jnt_name  = '{}{}_jnt'.format(self.name, 'ball')
        self.toe_jnt_name   = '{}{}_jnt'.format(self.name, 'toe')
        self.inner_jnt_name = '{}{}_jnt'.format(self.name, 'inner')
        self.outer_jnt_name = '{}{}_jnt'.format(self.name, 'outer')
        self.heel_jnt_name  = '{}{}_jnt'.format(self.name, 'heel')

        self.rev_ankle_jnt_name = '{}{}_jnt'.format(self.name, 'reverseankle')
        self.rev_ball_jnt_name  = '{}{}_jnt'.format(self.name, 'reverseball')
        self.rev_toe_jnt_name   = '{}{}_jnt'.format(self.name, 'reversetoe')

        self.fk_ankle_jnt_name = '{}{}_jnt'.format(self.name, 'fkankle')
        self.fk_ball_jnt_name  = '{}{}_jnt'.format(self.name, 'fkball')
        self.fk_toe_jnt_name   = '{}{}_jnt'.format(self.name, 'fktoe')

        self.fk_ctrl_name     = '{}{}_ctrl'.format(self.name, 'fk')
        self.switch_ctrl_name = '{}{}_ctrl'.format(self.name, 'switch')

    def set_locator_attr(self, start_pos=[0, 0, 0], interval=0.5, height=0.4, scale=0.2):
        self.start_pos = start_pos
        self.interval = interval
        self.height = height
        self.scale = scale

    @staticmethod
    def set_controller_shape():
        foot_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Foot_tempShape')[0]
        selection = cmds.select('Foot_tempShape.cv[0:2]')
        cmds.move(0, 0, -1.5, selection, relative=1)
        # cmds.scale(1.8, 1.8, 1.8, foot_shape)

        foot_fk_shape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='FootFK_tempShape')
        cmds.rotate(0, 90, 0, foot_fk_shape, relative=1)
        cmds.scale(0.4, 0.4, 0.4, foot_fk_shape)

        foot_switch_shape = other.make_curve_by_text(text='FK/IK', name='FootSwitch_tempShape')
        cmds.rotate(-90, 0, 0, foot_switch_shape, relative=1)

    def build_guide(self):
        grp = cmds.group(em=1, n=self.loc_grp_name)

        # Result Foot
        ankle = cmds.spaceLocator(n=self.ankle_loc_name)
        cmds.move(self.start_pos[0], self.start_pos[1], self.start_pos[2], ankle, absolute=1)
        cmds.scale(self.scale, self.scale, self.scale, ankle)

        ball = cmds.spaceLocator(n=self.ball_loc_name)
        cmds.parent(ball, ankle, relative=1)
        cmds.move(0, -self.height, self.interval, ball, relative=1)

        toe = cmds.spaceLocator(n=self.toe_loc_name)
        cmds.parent(toe, ball, relative=1)
        cmds.move(0, 0, 2*self.interval, toe, relative=1)

        # Reverse Foot
        inner = cmds.spaceLocator(n=self.inner_loc_name)
        cmds.parent(inner, ball, relative=1)
        if self.side == 'L': 
            cmds.move( -self.interval, 0, 0, inner, relative=1)
        else: 
            cmds.move(self.interval, 0, 0, inner, relative=1)

        outer = cmds.spaceLocator(n=self.outer_loc_name)
        cmds.parent(outer, ball, relative=1)
        if self.side is 'L': 
            cmds.move(self.interval, 0, 0, outer, relative=1)
        else: 
            cmds.move(-self.interval, 0, 0, outer, relative=1)

        heel = cmds.spaceLocator(n=self.heel_loc_name)
        cmds.parent(heel, ball, relative=1)
        cmds.move(0, 0, -1.5*self.interval, heel, relative=1)

        # Cleanup
        self.color_locator()
        cmds.parent(ankle, grp)
        cmds.parent(grp, self.loc_grp)
        return grp
        
    def construct_joint(self):
        # Result Foot
        ankle = cmds.ls(self.ankle_loc_name)
        cmds.select(clear=1)
        ankle_pos = cmds.xform(ankle, q=1, t=1, ws=1)
        ankle_jnt = cmds.joint(p=ankle_pos, name=self.ankle_jnt_name)

        ball = cmds.ls(self.ball_loc_name)
        ball_pos = cmds.xform(ball, q=1, t=1, ws=1)
        ball_jnt = cmds.joint(p=ball_pos, name=self.ball_jnt_name)

        toe = cmds.ls(self.toe_loc_name)
        toe_pos = cmds.xform(toe, q=1, t=1, ws=1)
        toe_jnt = cmds.joint(p=toe_pos, name=self.toe_jnt_name)

        # Reverse Foot
        inner = cmds.ls(self.inner_loc_name)
        cmds.select(clear=1)
        inner_pos = cmds.xform(inner, q=1, t=1, ws=1)
        inner_jnt = cmds.joint(p=inner_pos, name=self.inner_jnt_name)

        outer = cmds.ls(self.outer_loc_name)
        outer_pos = cmds.xform(outer, q=1, t=1, ws=1)
        outer_jnt = cmds.joint(p=outer_pos, name=self.outer_jnt_name)

        heel = cmds.ls(self.heel_loc_name)
        heel_pos = cmds.xform(heel, q=1, t=1, ws=1)
        heel_jnt = cmds.joint(p=heel_pos, name=self.heel_jnt_name)

        reverse_toe_jnt = cmds.joint(p=toe_pos, radius=0.8, name=self.rev_toe_jnt_name)
        reverse_ball_jnt = cmds.joint(p=ball_pos, radius=0.8, name=self.rev_ball_jnt_name)
        reverse_ankle_jnt = cmds.joint(p=ankle_pos, radius=0.8, name=self.rev_ankle_jnt_name)

        cmds.setAttr(inner_jnt+'.visibility', 0)

        # FK Foot
        cmds.select(clear=1)
        ankle_jnt_fk = cmds.joint(p=ankle_pos, name=self.fk_ankle_jnt_name)
        ball_jnt_fk = cmds.joint(p=ball_pos, name=self.fk_ball_jnt_name)
        toe_jnt_fk = cmds.joint(p=toe_pos, name=self.fk_toe_jnt_name)
        cmds.setAttr(ankle_jnt_fk+'.visibility', 0)

        # Cleanup
        outliner.batch_parent([ankle_jnt_fk, inner_jnt, ankle_jnt], self.jnt_grp)

    def place_controller(self):
        self.set_controller_shape()

        # IK Setup
        foot_ctrl = cmds.duplicate('Foot_tempShape', name=self.ctrl_name)[0]
        cmds.addAttr(foot_ctrl, longName='foot_Roll', attributeType='double', defaultValue=0, minValue=-10, maxValue=40, keyable=1)
        cmds.addAttr(foot_ctrl, longName='foot_Bank', attributeType='double', defaultValue=0, minValue=-20, maxValue=20, keyable=1)

        foot_pos = cmds.xform(self.ball_jnt_name, q=1, t=1, ws=1)
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2]+1, foot_ctrl)
        cmds.makeIdentity(foot_ctrl, apply=1, t=1, r=1, s=1)

        heel_loc = cmds.xform(self.heel_jnt_name, q=1, t=1, ws=1)
        cmds.move(heel_loc[0], heel_loc[1], heel_loc[2], '%s.scalePivot' % foot_ctrl, '%s.rotatePivot' % foot_ctrl, absolute=1)

        # FK Setup
        foot_fk_ctrl = cmds.duplicate('FootFK_tempShape', name=self.fk_ctrl_name)[0]
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2], foot_fk_ctrl)
        cmds.makeIdentity(foot_fk_ctrl, apply=1, t=1, r=1, s=1)

        # IK/FK Switch Setup
        switch = cmds.duplicate('FootSwitch_tempShape', name=self.switch_ctrl_name)[0]
        if self.side == "L":   cmds.move(foot_pos[0]+2, foot_pos[1], foot_pos[2], switch)
        elif self.side == "R": cmds.move(foot_pos[0]-3, foot_pos[1], foot_pos[2], switch)
        cmds.scale(0.5, 0.5, 0.5, switch)
        cmds.addAttr(switch, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=1)
        cmds.makeIdentity(switch, apply=1, t=1, r=1, s=1)

        # Cleanup
        outliner.batch_parent([switch, foot_ctrl, foot_fk_ctrl], self.ctrl_grp)
        self.delete_shape()

    def add_constraint(self):
        # FK Setup
        cmds.orientConstraint(self.fk_ctrl_name, self.fk_ball_jnt_name, mo=1)
        cmds.pointConstraint(self.fk_ankle_jnt_name, self.ankle_jnt_name)
        cmds.orientConstraint(self.fk_ankle_jnt_name, self.ankle_jnt_name, mo=1)
        cmds.orientConstraint(self.fk_ball_jnt_name, self.ball_jnt_name)
        cmds.orientConstraint(self.fk_toe_jnt_name, self.toe_jnt_name)

        # IK Setup
        cmds.parentConstraint(self.ctrl_name, self.inner_jnt_name, sr='z', mo=1)
        cmds.orientConstraint(self.rev_ball_jnt_name, self.ankle_jnt_name, mo=1)
        cmds.orientConstraint(self.rev_toe_jnt_name, self.ball_jnt_name, mo=1)
        cmds.pointConstraint(self.rev_ankle_jnt_name, self.ankle_jnt_name, mo=1)

        # Foot Roll
        cmds.setDrivenKeyframe(self.heel_jnt_name+'.rotateX', currentDriver=self.ctrl_name+'.foot_Roll', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.heel_jnt_name+'.rotateX', currentDriver=self.ctrl_name+'.foot_Roll', driverValue=-10, value=-25)

        cmds.setDrivenKeyframe(self.rev_ball_jnt_name+'.rotateX', currentDriver=self.ctrl_name+'.foot_Roll', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.rev_ball_jnt_name+'.rotateX', currentDriver=self.ctrl_name+'.foot_Roll', driverValue=20, value=25)

        cmds.setDrivenKeyframe(self.rev_toe_jnt_name+'.rotateX', currentDriver=self.ctrl_name+'.foot_Roll', driverValue=20, value=0)
        cmds.setDrivenKeyframe(self.rev_toe_jnt_name+'.rotateX', currentDriver=self.ctrl_name+'.foot_Roll', driverValue=40, value=25)

        # Foot Bank
        cmds.setDrivenKeyframe(self.inner_jnt_name+'.rotateZ', currentDriver=self.ctrl_name+'.foot_Bank', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.outer_jnt_name+'.rotateZ', currentDriver=self.ctrl_name+'.foot_Bank', driverValue=0, value=0)
        if self.side == 'R':
            cmds.setDrivenKeyframe(self.inner_jnt_name+'.rotateZ', currentDriver=self.ctrl_name+'.foot_Bank', driverValue=-20, value=-30)
            cmds.setDrivenKeyframe(self.outer_jnt_name+'.rotateZ', currentDriver=self.ctrl_name+'.foot_Bank', driverValue=20, value=30)
        else:
            cmds.setDrivenKeyframe(self.inner_jnt_name+'.rotateZ', currentDriver=self.ctrl_name+'.foot_Bank', driverValue=-20, value=30)
            cmds.setDrivenKeyframe(self.outer_jnt_name+'.rotateZ', currentDriver=self.ctrl_name+'.foot_Bank', driverValue=20, value=-30)

        # Result Foot Setup
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ankle_jnt_name, self.rev_ball_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ankle_jnt_name, self.rev_ball_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W1'.format(self.ankle_jnt_name, self.rev_ankle_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W1'.format(self.ankle_jnt_name, self.rev_ankle_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=0, value=0)

        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W0'.format(self.ankle_jnt_name, self.fk_ankle_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W0'.format(self.ankle_jnt_name, self.fk_ankle_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ankle_jnt_name, self.fk_ankle_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ankle_jnt_name, self.fk_ankle_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=0, value=1)

        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ball_jnt_name, self.fk_ball_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ball_jnt_name, self.fk_ball_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ball_jnt_name, self.rev_toe_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ball_jnt_name, self.rev_toe_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=0, value=0)

        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.toe_jnt_name, self.fk_toe_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.toe_jnt_name, self.fk_toe_jnt_name), currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=0, value=1)

        # IK/FK Switch Setup

        # switch will follow ankle movement
        cmds.parentConstraint(self.ankle_jnt_name, self.switch_ctrl_name, mo=1)

        cmds.setDrivenKeyframe(self.ctrl_name+'.visibility', currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ctrl_name+'.visibility', currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.fk_ctrl_name+'.visibility', currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.fk_ctrl_name+'.visibility', currentDriver=self.switch_ctrl_name+'.FK_IK', driverValue=0, value=1)
