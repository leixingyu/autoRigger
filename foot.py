import maya.cmds as cmds
import base
import misc

class Foot(base.Base):
    def __init__(self, prefix, side, id):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Foot'

        self.constructNameSpace(self.metaType)

        '''default locator attribute'''
        self.setLocAttr()

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

        footSwitchShape = misc.makeTextCurve(string='FK/IK', name='FootSwitch_tempShape')
        cmds.rotate(-90, 0, 0, footSwitchShape, relative=True)

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        '''Result Foot'''
        ankle = cmds.spaceLocator(n=self.locName+'ankle')
        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], ankle, absolute=True)
        cmds.scale(self.scale, self.scale, self.scale, ankle)

        ball = cmds.spaceLocator(n=self.locName+'ball')
        cmds.parent(ball, ankle, relative=True)
        cmds.move(0, -self.height, self.interval, ball, relative=True)

        toe = cmds.spaceLocator(n=self.locName+'toe')
        cmds.parent(toe, ball, relative=True)
        cmds.move(0, 0, 2*self.interval, toe, relative=True)

        '''Reverse Foot'''
        inner = cmds.spaceLocator(n=self.locName+'inner')
        cmds.parent(inner, ball, relative=True)
        if self.side == 'L': cmds.move( -self.interval, 0, 0, inner, relative=True)
        else: cmds.move(self.interval, 0, 0, inner, relative=True)

        outer = cmds.spaceLocator(n=self.locName+'outer')
        cmds.parent(outer, ball, relative=True)
        if self.side is 'L': cmds.move(self.interval, 0, 0, outer, relative=True)
        else: cmds.move(-self.interval, 0, 0, outer, relative=True)

        heel = cmds.spaceLocator(n=self.locName+'heel')
        cmds.parent(heel, ball, relative=True)
        cmds.move(0, 0, -1.5*self.interval, heel, relative=True)

        self.colorLoc()
        cmds.parent(ankle, grp)
        cmds.parent(grp, self.locGrp)
        return grp
        
    def constructJnt(self):
        '''Result Foot'''
        ankle = cmds.ls(self.locName+'ankle')
        cmds.select(clear=True)
        anklePos = cmds.xform(ankle, q=True, t=True, ws=True)
        ankleJnt = cmds.joint(p=anklePos, name=self.jntName+'ankle')

        ball = cmds.ls(self.locName+'ball')
        ballPos = cmds.xform(ball, q=True, t=True, ws=True)
        ballJnt = cmds.joint(p=ballPos, name=self.jntName+'ball')

        toe = cmds.ls(self.locName+'toe')
        toePos = cmds.xform(toe, q=True, t=True, ws=True)
        toeJnt = cmds.joint(p=toePos, name=self.jntName+'toe')

        '''Reverse Foot'''
        inner = cmds.ls(self.locName+'inner')
        cmds.select(clear=True)
        innerPos = cmds.xform(inner, q=True, t=True, ws=True)
        innerJoint = cmds.joint(p=innerPos, name=self.jntName+'inner')

        outer = cmds.ls(self.locName+'outer')
        outerPos = cmds.xform(outer, q=True, t=True, ws=True)
        outerJoint = cmds.joint(p=outerPos, name=self.jntName+'outer')

        heel = cmds.ls(self.locName+'heel')
        heelPos = cmds.xform(heel, q=True, t=True, ws=True)
        heelJoint = cmds.joint(p=heelPos, name=self.jntName+'heel')

        reverseToeJoint = cmds.joint(p=toePos, radius=0.8, name=self.jntName+'reverseToe')
        reverseBallJoint = cmds.joint(p=ballPos, radius=0.8, name=self.jntName+'reverseBall')
        reverseAnkleJoint = cmds.joint(p=anklePos, radius=0.8, name=self.jntName+'reverseAnkle')

        '''FK Foot'''
        cmds.select(clear=True)
        ankleJntFK = cmds.joint(p=anklePos, name=self.jntName+'ankleFK')
        ballJntFK = cmds.joint(p=ballPos, name=self.jntName+'ballFK')
        toeJntFK = cmds.joint(p=toePos, name=self.jntName+'toeFK')

        cmds.setAttr(ankleJntFK+'.visibility', 0)
        cmds.setAttr(innerJoint+'.visibility', 0)
        misc.batchParent([ankleJntFK, innerJoint, ankleJnt], self.jntGrp)

    def placeCtrl(self):
        self.setCtrlShape()

        '''IK Foot'''
        footCtrl = cmds.duplicate('Foot_tempShape', name=self.ctrlName)[0]
        cmds.addAttr(footCtrl, longName='foot_Roll', attributeType='double', defaultValue=0, minValue=-10, maxValue=40, keyable=True)
        cmds.addAttr(footCtrl, longName='foot_Bank', attributeType='double', defaultValue=0, minValue=-20, maxValue=20, keyable=True)

        footPos = cmds.xform(self.jntName+'ball', q=True, t=True, ws=True)
        cmds.move(footPos[0], footPos[1], footPos[2]+1, footCtrl)
        cmds.makeIdentity(footCtrl, apply=True, t=1, r=1, s=1)

        heelLoc = cmds.xform(self.jntName+'heel', q=True, t=True, ws=True)
        cmds.move(heelLoc[0], heelLoc[1], heelLoc[2], '%s.scalePivot' % footCtrl, '%s.rotatePivot' % footCtrl, absolute=True)

        '''FK Foot'''
        footFKCtrl = cmds.duplicate('FootFK_tempShape', name=self.ctrlName+'FK')[0]
        cmds.move(footPos[0], footPos[1], footPos[2], footFKCtrl)
        cmds.makeIdentity(footFKCtrl, apply=True, t=1, r=1, s=1)

        '''Switch'''
        switch = cmds.duplicate('FootSwitch_tempShape', name=self.ctrlName+'Switch')[0]
        cmds.move(footPos[0], footPos[1], footPos[2]+3, switch)
        cmds.addAttr(switch, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=True)
        cmds.makeIdentity(switch, apply=True, t=1, r=1, s=1)

        misc.batchParent([switch, footCtrl, footFKCtrl], self.ctrlGrp)
        self.deleteShape()

    def addConstraint(self):
        '''FK Foot'''
        cmds.orientConstraint(self.ctrlName+'FK', self.jntName+'ballFK', mo=True)

        cmds.pointConstraint(self.jntName+'ankleFK', self.jntName+'ankle')
        cmds.orientConstraint(self.jntName+'ankleFK', self.jntName+'ankle', mo=True)
        cmds.orientConstraint(self.jntName+'ballFK', self.jntName+'ball')
        cmds.orientConstraint(self.jntName+'toeFK', self.jntName+'toe')

        '''IK Foot'''
        # Foot Constraint
        innerJnt = cmds.ls(self.jntName+'inner')[0]
        outerJnt = cmds.ls(self.jntName+'outer')[0]
        reverseBall = cmds.ls(self.jntName+'reverseBall')[0]
        reverseToe = cmds.ls(self.jntName+'reverseToe')[0]

        cmds.parentConstraint(self.ctrlName, innerJnt, sr='z', mo=True)

        cmds.orientConstraint(reverseBall, self.jntName+'ankle', mo=True)
        cmds.orientConstraint(reverseToe, self.jntName+'ball', mo=True)
        cmds.pointConstraint(self.jntName+'reverseAnkle', self.jntName+'ankle', mo=True)

        # Set Foot Roll
        cmds.setDrivenKeyframe(self.jntName+'heel.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.jntName+'heel.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=-10, value=-25)

        cmds.setDrivenKeyframe(reverseBall+'.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=0, value=0)
        cmds.setDrivenKeyframe(reverseBall+'.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=20, value=25)

        cmds.setDrivenKeyframe(reverseToe+'.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=20, value=0)
        cmds.setDrivenKeyframe(reverseToe+'.rotateX', currentDriver=self.ctrlName+'.foot_Roll', driverValue=40, value=25)

        # Set Foot Bank
        cmds.setDrivenKeyframe(innerJnt+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=0, value=0)
        cmds.setDrivenKeyframe(outerJnt+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=0, value=0)
        if self.side == 'R':
            cmds.setDrivenKeyframe(innerJnt+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=-20, value=-30)
            cmds.setDrivenKeyframe(outerJnt+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=20, value=30)
        else:
            cmds.setDrivenKeyframe(innerJnt+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=-20, value=30)
            cmds.setDrivenKeyframe(outerJnt+'.rotateZ', currentDriver=self.ctrlName+'.foot_Bank', driverValue=20, value=-30)

        '''Result Foot'''
        cmds.setDrivenKeyframe(self.jntName+'ankle_orientConstraint1.'+self.jntName+'reverseBallW1', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.jntName+'ankle_orientConstraint1.'+self.jntName+'reverseBallW1', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.jntName+'ankle_pointConstraint1.'+self.jntName+'reverseAnkleW1', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.jntName+'ankle_pointConstraint1.'+self.jntName+'reverseAnkleW1', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=0, value=0)

        cmds.setDrivenKeyframe(self.jntName+'ankle_pointConstraint1.'+self.jntName+'ankleFKW0', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.jntName+'ankle_pointConstraint1.'+self.jntName+'ankleFKW0', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe(self.jntName+'ankle_orientConstraint1.'+self.jntName+'ankleFKW0', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.jntName+'ankle_orientConstraint1.'+self.jntName+'ankleFKW0', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=0, value=1)

        cmds.setDrivenKeyframe(self.jntName+'ball_orientConstraint1.'+self.jntName+'ballFKW0', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.jntName+'ball_orientConstraint1.'+self.jntName+'ballFKW0', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe(self.jntName+'ball_orientConstraint1.'+self.jntName+'reverseToeW1', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.jntName+'ball_orientConstraint1.'+self.jntName+'reverseToeW1', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=0, value=0)

        cmds.setDrivenKeyframe(self.jntName+'toe_orientConstraint1.'+self.jntName+'toeFKW0', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.jntName+'toe_orientConstraint1.'+self.jntName+'toeFKW0', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=0, value=1)

        '''IK/FK Switch'''
        # IK visiblity
        cmds.setDrivenKeyframe(self.ctrlName+'.visibility', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ctrlName+'.visibility', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=0, value=0)

        # FK visiblity
        cmds.setDrivenKeyframe(self.ctrlName+'FK.visibility', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.ctrlName+'FK.visibility', currentDriver=self.ctrlName+'Switch.FK_IK', driverValue=0, value=1)
