import maya.cmds as cmds
import base, util

class Foot(base.Base):
    def __init__(self, side, id):
        base.Base.__init__(self, side, id)
        self.metaType = 'Foot'
        self.createNaming()
        self.createSecondaryNaming()
        self.setLocAttr()

    def createSecondaryNaming(self):
        self.ankleLocName = '{}{}_loc'.format(self.name, 'ankle')
        self.ballLocName  = '{}{}_loc'.format(self.name, 'ball')
        self.toeLocName   = '{}{}_loc'.format(self.name, 'toe')
        self.innerLocName = '{}{}_loc'.format(self.name, 'inner')
        self.outerLocName = '{}{}_loc'.format(self.name, 'outer')
        self.heelLocName  = '{}{}_loc'.format(self.name, 'heel')

        self.ankleJntName = '{}{}_jnt'.format(self.name, 'ankle')
        self.ballJntName  = '{}{}_jnt'.format(self.name, 'ball')
        self.toeJntName   = '{}{}_jnt'.format(self.name, 'toe')
        self.innerJntName = '{}{}_jnt'.format(self.name, 'inner')
        self.outerJntName = '{}{}_jnt'.format(self.name, 'outer')
        self.heelJntName  = '{}{}_jnt'.format(self.name, 'heel')

        self.revAnkleJntName = '{}{}_jnt'.format(self.name, 'reverseankle')
        self.revBallJntName  = '{}{}_jnt'.format(self.name, 'reverseball')
        self.revToeJntName   = '{}{}_jnt'.format(self.name, 'reversetoe')

        self.fkAnkleJntName = '{}{}_jnt'.format(self.name, 'fkankle')
        self.fkBallJntName  = '{}{}_jnt'.format(self.name, 'fkball')
        self.fkToeJntName   = '{}{}_jnt'.format(self.name, 'fktoe')

        self.fkCtrlName     = '{}{}_ctrl'.format(self.name, 'fk')
        self.switchCtrlName = '{}{}_ctrl'.format(self.name, 'switch')

    def setLocAttr(self, startPos=[0, 0, 0], interval=0.5, height=0.4, scale=0.2):
        self.startPos = startPos
        self.interval = interval
        self.height = height
        self.scale = scale

    def setCtrlShape(self):
        footShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Foot_tempShape')[0]
        selection = cmds.select('Foot_tempShape.cv[0:2]')
        cmds.move(0, 0, -1.5, selection, relative=True)
        #cmds.scale(1.8, 1.8, 1.8, footShape)

        footFKShape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='FootFK_tempShape')
        cmds.rotate(0, 90, 0, footFKShape, relative=True)
        cmds.scale(0.4, 0.4, 0.4, footFKShape)

        footSwitchShape = util.makeTextCurve(string='FK/IK', name='FootSwitch_tempShape')
        cmds.rotate(-90, 0, 0, footSwitchShape, relative=True)

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        #--- Result Foot ---#
        ankle = cmds.spaceLocator(n=self.ankleLocName)
        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], ankle, absolute=True)
        cmds.scale(self.scale, self.scale, self.scale, ankle)

        ball = cmds.spaceLocator(n=self.ballLocName)
        cmds.parent(ball, ankle, relative=True)
        cmds.move(0, -self.height, self.interval, ball, relative=True)

        toe = cmds.spaceLocator(n=self.toeLocName)
        cmds.parent(toe, ball, relative=True)
        cmds.move(0, 0, 2*self.interval, toe, relative=True)

        #--- Reverse Foot ---#
        inner = cmds.spaceLocator(n=self.innerLocName)
        cmds.parent(inner, ball, relative=True)
        if self.side == 'L': cmds.move( -self.interval, 0, 0, inner, relative=True)
        else: cmds.move(self.interval, 0, 0, inner, relative=True)

        outer = cmds.spaceLocator(n=self.outerLocName)
        cmds.parent(outer, ball, relative=True)
        if self.side is 'L': cmds.move(self.interval, 0, 0, outer, relative=True)
        else: cmds.move(-self.interval, 0, 0, outer, relative=True)

        heel = cmds.spaceLocator(n=self.heelLocName)
        cmds.parent(heel, ball, relative=True)
        cmds.move(0, 0, -1.5*self.interval, heel, relative=True)

        #--- Cleanup ---#
        self.colorLoc()
        cmds.parent(ankle, grp)
        cmds.parent(grp, self.locGrp)
        return grp
        
    def constructJnt(self):
        #--- Result Foot Joint ---#
        ankle = cmds.ls(self.ankleLocName)
        cmds.select(clear=True)
        anklePos = cmds.xform(ankle, q=True, t=True, ws=True)
        ankleJnt = cmds.joint(p=anklePos, name=self.ankleJntName)

        ball = cmds.ls(self.ballLocName)
        ballPos = cmds.xform(ball, q=True, t=True, ws=True)
        ballJnt = cmds.joint(p=ballPos, name=self.ballJntName)

        toe = cmds.ls(self.toeLocName)
        toePos = cmds.xform(toe, q=True, t=True, ws=True)
        toeJnt = cmds.joint(p=toePos, name=self.toeJntName)

        #--- Reverse Foot Joint ---#
        inner = cmds.ls(self.innerLocName)
        cmds.select(clear=True)
        innerPos = cmds.xform(inner, q=True, t=True, ws=True)
        innerJoint = cmds.joint(p=innerPos, name=self.innerJntName)

        outer = cmds.ls(self.outerLocName)
        outerPos = cmds.xform(outer, q=True, t=True, ws=True)
        outerJoint = cmds.joint(p=outerPos, name=self.outerJntName)

        heel = cmds.ls(self.heelLocName)
        heelPos = cmds.xform(heel, q=True, t=True, ws=True)
        heelJoint = cmds.joint(p=heelPos, name=self.heelJntName)

        reverseToeJoint = cmds.joint(p=toePos, radius=0.8, name=self.revToeJntName)
        reverseBallJoint = cmds.joint(p=ballPos, radius=0.8, name=self.revBallJntName)
        reverseAnkleJoint = cmds.joint(p=anklePos, radius=0.8, name=self.revAnkleJntName)

        cmds.setAttr(innerJoint+'.visibility', 0)

        #--- FK Foot Joint ---#
        cmds.select(clear=True)
        ankleJntFK = cmds.joint(p=anklePos, name=self.fkAnkleJntName)
        ballJntFK = cmds.joint(p=ballPos, name=self.fkBallJntName)
        toeJntFK = cmds.joint(p=toePos, name=self.fkToeJntName)
        cmds.setAttr(ankleJntFK+'.visibility', 0)

        #--- Cleanup ---#
        util.batchParent([ankleJntFK, innerJoint, ankleJnt], self.jntGrp)

    def placeCtrl(self):
        self.setCtrlShape()

        #--- IK Setup ---#
        footCtrl = cmds.duplicate('Foot_tempShape', name=self.ctrlName)[0]
        cmds.addAttr(footCtrl, longName='foot_Roll', attributeType='double', defaultValue=0, minValue=-10, maxValue=40, keyable=True)
        cmds.addAttr(footCtrl, longName='foot_Bank', attributeType='double', defaultValue=0, minValue=-20, maxValue=20, keyable=True)

        footPos = cmds.xform(self.ballJntName, q=True, t=True, ws=True)
        cmds.move(footPos[0], footPos[1], footPos[2]+1, footCtrl)
        cmds.makeIdentity(footCtrl, apply=True, t=1, r=1, s=1)

        heelLoc = cmds.xform(self.heelJntName, q=True, t=True, ws=True)
        cmds.move(heelLoc[0], heelLoc[1], heelLoc[2], '%s.scalePivot' % footCtrl, '%s.rotatePivot' % footCtrl, absolute=True)

        #--- FK Setup ---#
        footFKCtrl = cmds.duplicate('FootFK_tempShape', name=self.fkCtrlName)[0]
        cmds.move(footPos[0], footPos[1], footPos[2], footFKCtrl)
        cmds.makeIdentity(footFKCtrl, apply=True, t=1, r=1, s=1)

        #--- IK/FK Switch Setup ---#
        switch = cmds.duplicate('FootSwitch_tempShape', name=self.switchCtrlName)[0]
        if self.side == "L":   cmds.move(footPos[0]+2, footPos[1], footPos[2], switch)
        elif self.side == "R": cmds.move(footPos[0]-3, footPos[1], footPos[2], switch)
        cmds.scale(0.5, 0.5, 0.5, switch)
        cmds.addAttr(switch, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=True)
        cmds.makeIdentity(switch, apply=True, t=1, r=1, s=1)

        #--- Cleanup ---#
        util.batchParent([switch, footCtrl, footFKCtrl], self.ctrlGrp)
        self.deleteShape()

    def addConstraint(self):
        #--- FK Setup ---#
        cmds.orientConstraint(self.fkCtrlName, self.fkBallJntName, mo=True)
        cmds.pointConstraint(self.fkAnkleJntName, self.ankleJntName)
        cmds.orientConstraint(self.fkAnkleJntName, self.ankleJntName, mo=True)
        cmds.orientConstraint(self.fkBallJntName, self.ballJntName)
        cmds.orientConstraint(self.fkToeJntName, self.toeJntName)

        #--- IK Setup ---#
        cmds.parentConstraint(self.ctrlName, self.innerJntName, sr='z', mo=True)
        cmds.orientConstraint(self.revBallJntName, self.ankleJntName, mo=True)
        cmds.orientConstraint(self.revToeJntName, self.ballJntName, mo=True)
        cmds.pointConstraint(self.revAnkleJntName, self.ankleJntName, mo=True)

        # Foot Roll
        cmds.setDrivenKeyframe(self.heelJntName+'.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.heelJntName+'.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=-10, value=-25)

        cmds.setDrivenKeyframe(self.revBallJntName+'.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.revBallJntName+'.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=20, value=25)

        cmds.setDrivenKeyframe(self.revToeJntName+'.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=20, value=0)
        cmds.setDrivenKeyframe(self.revToeJntName+'.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=40, value=25)

        # Foot Bank
        cmds.setDrivenKeyframe(self.innerJntName+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.outerJntName+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=0, value=0)
        if self.side == 'R':
            cmds.setDrivenKeyframe(self.innerJntName+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=-20, value=-30)
            cmds.setDrivenKeyframe(self.outerJntName+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=20, value=30)
        else:
            cmds.setDrivenKeyframe(self.innerJntName+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=-20, value=30)
            cmds.setDrivenKeyframe(self.outerJntName+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=20, value=-30)

        #--- Result Foot Setup ---#
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ankleJntName, self.revBallJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ankleJntName, self.revBallJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W1'.format(self.ankleJntName, self.revAnkleJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W1'.format(self.ankleJntName, self.revAnkleJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=0, value=0)

        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W0'.format(self.ankleJntName, self.fkAnkleJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_pointConstraint1.{}W0'.format(self.ankleJntName, self.fkAnkleJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ankleJntName, self.fkAnkleJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ankleJntName, self.fkAnkleJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=0, value=1)

        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ballJntName, self.fkBallJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.ballJntName, self.fkBallJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ballJntName, self.revToeJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.ballJntName, self.revToeJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=0, value=0)

        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.toeJntName, self.fkToeJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.toeJntName, self.fkToeJntName), currentDriver=self.switchCtrlName+'.FK_IK', driverValue=0, value=1)

        #--- IK/FK Switch Setup ---#
        cmds.parentConstraint(self.ankleJntName, self.switchCtrlName, mo=True)          # switch will follow ankle movement

        cmds.setDrivenKeyframe(self.ctrlName+'.visibility', currentDriver=self.switchCtrlName+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ctrlName+'.visibility', currentDriver=self.switchCtrlName+'.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.fkCtrlName+'.visibility', currentDriver=self.switchCtrlName+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.fkCtrlName+'.visibility', currentDriver=self.switchCtrlName+'.FK_IK', driverValue=0, value=1)
