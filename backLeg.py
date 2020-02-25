import maya.cmds as cmds
import base
import misc


class BackLeg(base.Base):
    def __init__(self, prefix, side, id):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'BackLeg'

        self.constructNameSpace(self.metaType)
        self.setLocAttr(startPos=[0, 5, -3])

    def setLocAttr(self, startPos=[0, 0, 0], distance=1.5, height=0.2, scale=0.4):
        self.startPos = startPos
        self.distance = distance
        self.height = height
        self.scale = scale

    def setCtrlShape(self):
        sphere = cmds.createNode('implicitSphere')
        sphereCtrl = cmds.rename(cmds.listRelatives(sphere, p=True), 'Hip_tempShape')
        cmds.scale(0.5, 0.5, 0.5, sphereCtrl)

        pole = cmds.createNode('implicitSphere')
        poleCtrl = cmds.rename(cmds.listRelatives(pole, p=True), 'Pole_tempShape')
        cmds.scale(0.2, 0.2, 0.2, poleCtrl)

        ctrlShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Foot_tempShape')
        cmds.scale(0.5, 0.5, 0.5, ctrlShape)

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        # hip
        hip = cmds.spaceLocator(n=self.locName+'hip')
        cmds.parent(hip, grp, relative=True)
        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], hip, relative=True)
        cmds.scale(self.scale, self.scale, self.scale, hip)

        # knee
        knee = cmds.spaceLocator(n=self.locName+'knee')
        cmds.parent(knee, hip, relative=True)
        cmds.move(0, -self.distance, 0, knee, relative=True)

        # ankle
        ankle = cmds.spaceLocator(n=self.locName+'ankle')
        cmds.parent(ankle, knee, relative=True)
        cmds.move(0, -self.distance, -0.5 * self.distance, ankle, relative=True)

        # foot
        foot = cmds.spaceLocator(n=self.locName+'foot')
        cmds.parent(foot, ankle, relative=True)
        cmds.move(0, -self.distance+self.height, 0, foot, relative=True)

        # toe
        toe = cmds.spaceLocator(n=self.locName+'toe')
        cmds.parent(toe, foot, relative=True)
        cmds.move(0, 0, 0.5 * self.distance, toe, relative=True)

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        # result jnt chain
        cmds.select(clear=True)
        jntChain = ['hip', 'knee', 'ankle', 'foot', 'toe']
        for name in jntChain:
            loc = cmds.ls(self.locName+name, transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntName+name)
            cmds.setAttr(jnt+'.radius', self.scale)
        misc.orientJnt(self.jntName+jntChain[0])
        cmds.parent(self.jntName+jntChain[0], self.jntGrp)

        # helper jnt chain
        cmds.select(clear=True)
        for name in jntChain[:4]:
            loc = cmds.ls(self.locName+name, transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntName+name+'helper')
            cmds.setAttr(jnt+'.radius', 1)
        misc.orientJnt(self.jntName+jntChain[0]+'helper')
        cmds.parent(self.jntName+jntChain[0]+'helper', self.jntGrp)
        cmds.setAttr(self.jntName+jntChain[0]+'helper.visibility', 0)

        return self.jntName+jntChain[0]

    def placeCtrl(self):
        self.setCtrlShape()

        # hip
        hip = cmds.ls(self.jntName+'hip')
        self.hipCtrl = cmds.duplicate('Hip_tempShape', name=self.ctrlName+'hip')[0]
        hipPos = cmds.xform(hip, q=True, ws=True, t=True)
        hipRot = cmds.xform(hip, q=True, ws=True, ro=True)

        hipCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetGrpName+'hip')
        cmds.move(hipPos[0], hipPos[1], hipPos[2], hipCtrlOffset)
        cmds.rotate(hipRot[0], hipRot[1], hipRot[2], hipCtrlOffset)
        cmds.parent(self.hipCtrl, hipCtrlOffset, relative=True)

        # back foot
        foot = cmds.ls(self.jntName+'foot')
        self.footCtrl = cmds.duplicate('Foot_tempShape', name=self.ctrlName+'foot')[0]
        footPos = cmds.xform(foot, q=True, ws=True, t=True)
        cmds.move(footPos[0], 0, footPos[2], self.footCtrl)
        # custom attribute for later pivot group access
        cmds.addAttr(self.footCtrl, longName='Flex', attributeType='double', keyable=True)
        cmds.addAttr(self.footCtrl, longName='Swivel', attributeType='double', keyable=True)
        cmds.addAttr(self.footCtrl, longName='Toe_Tap', attributeType='double', keyable=True)
        cmds.addAttr(self.footCtrl, longName='Toe_Tip', attributeType='double', keyable=True)

        # pole vector
        ankle = cmds.ls(self.jntName+'ankle')
        self.poleCtrl = cmds.duplicate('Pole_tempShape', name=self.ctrlName+'poleVector')[0]
        anklePos = cmds.xform(ankle, q=True, ws=True, t=True)
        cmds.move(anklePos[0], anklePos[1], anklePos[2]+self.distance, self.poleCtrl)
        cmds.makeIdentity(self.poleCtrl, apply=True, t=1, r=1, s=1)
        cmds.parent(self.poleCtrl, self.footCtrl)

        misc.batchParent([hipCtrlOffset, self.footCtrl], self.ctrlGrp)
        self.deleteShape()

    def buildIK(self):
        # result jnt chain IK
        self.legIK = cmds.ikHandle(startJoint=self.jntName+'hip', endEffector=self.jntName+'ankle', name=self.prefix+'_IKLeg'+self.name, solver='ikRPsolver')[0]
        self.footIK = cmds.ikHandle(startJoint=self.jntName+'ankle', endEffector=self.jntName+'foot', name=self.prefix+'_IKFoot'+self.name, solver='ikSCsolver')[0]
        self.toeIK = cmds.ikHandle(startJoint=self.jntName+'foot', endEffector=self.jntName+'toe', name=self.prefix+'_IKToe'+self.name, solver='ikSCsolver')[0]
        
        # helper jnt chain IK
        self.helperIK = cmds.ikHandle(startJoint=self.jntName+'hiphelper', endEffector=self.jntName+'foothelper', name=self.prefix+'_IKHelper'+self.name, solver='ikRPsolver')[0]

        cmds.setAttr(self.legIK+'.visibility', 0)
        cmds.setAttr(self.footIK+'.visibility', 0)
        cmds.setAttr(self.toeIK+'.visibility', 0)
        cmds.setAttr(self.helperIK+'.visibility', 0)

    def addMeasurement(self):
        # length segment
        hipPos = cmds.xform(self.jntName+'hip', q=True, ws=True, t=True)
        kneePos = cmds.xform(self.jntName+'knee', q=True, ws=True, t=True)
        anklePos = cmds.xform(self.jntName+'ankle', q=True, ws=True, t=True)
        footPos = cmds.xform(self.jntName+'foot', q=True, ws=True, t=True)

        straightenLen = ((kneePos[0]-anklePos[0]) ** 2+(kneePos[1]-anklePos[1]) ** 2+(kneePos[2]-anklePos[2]) ** 2) ** 0.5 + \
                        ((footPos[0]-anklePos[0]) ** 2+(footPos[1]-anklePos[1]) ** 2+(footPos[2]-anklePos[2]) ** 2) ** 0.5 + \
                        ((hipPos[0]-kneePos[0]) ** 2+(hipPos[1]-kneePos[1]) ** 2+(hipPos[2]-kneePos[2]) ** 2) ** 0.5
        
        # create measurement
        measureNode = cmds.distanceDimension(sp=hipPos, ep=footPos)

        stretchNode = cmds.shadingNode('multiplyDivide', asUtility=True, name=self.ctrlName+'Stretch')
        cmds.setAttr(stretchNode+'.operation', 2)
        cmds.setAttr(stretchNode+'.input2X', straightenLen)
        cmds.connectAttr(measureNode+'.distance', stretchNode+'.input1X')

        conditionNode = cmds.shadingNode('condition', asUtility=True, name=self.ctrlName+'Condition')
        cmds.connectAttr(stretchNode+'.outputX', conditionNode+'.firstTerm')
        cmds.setAttr(conditionNode+'.secondTerm', 1)
        cmds.setAttr(conditionNode+'.operation', 2)  # Greater than
        cmds.connectAttr(stretchNode+'.outputX', conditionNode+'.colorIfTrueR')
        cmds.setAttr(conditionNode+'.colorIfFalseR', 1)

        cmds.connectAttr(conditionNode+'.outColorR', self.jntName+'ankle.scaleX')
        cmds.connectAttr(conditionNode+'.outColorR', self.jntName+'knee.scaleX')
        cmds.connectAttr(conditionNode+'.outColorR', self.jntName+'hip.scaleX')
        cmds.connectAttr(conditionNode+'.outColorR', self.jntName+'anklehelper.scaleX')
        cmds.connectAttr(conditionNode+'.outColorR', self.jntName+'kneehelper.scaleX')
        cmds.connectAttr(conditionNode+'.outColorR', self.jntName+'hiphelper.scaleX')

        cmds.rename('distanceDimension1', self.ctrlName+'length')
        cmds.rename('locator1', self.ctrlName+'hipLoc')
        cmds.rename('locator2', self.ctrlName+'ankleLoc')
        cmds.setAttr(self.ctrlName+'length.visibility', 0)
        cmds.setAttr(self.ctrlName+'ankleLoc.visibility', 0)
        cmds.setAttr(self.ctrlName+'hipLoc.visibility', 0)
        misc.batchParent([self.ctrlName+'length', self.ctrlName+'hipLoc', self.ctrlName+'ankleLoc'], self.ctrlGrp)

        cmds.parentConstraint(self.hipCtrl, self.ctrlName+'hipLoc')
        cmds.parentConstraint(self.footCtrl, self.ctrlName+'ankleLoc', mo=True)

    def addConstraint(self):
        self.buildIK()
        # shoulder pivot
        cmds.parentConstraint(self.hipCtrl, self.jntName+'hip')
        cmds.parentConstraint(self.hipCtrl, self.jntName+'hiphelper')

        # front foot pivot group
        flexOffsetGrp = cmds.group(em=True, name=self.ctrlOffsetGrpName+'Flex')
        flexPivotGrp = cmds.group(em=True, name=self.ctrlGrpName+'FlexPivot')
        toeTapPivotGrp = cmds.group(em=True, name=self.ctrlGrpName+'ToeTapPivot')
        swivelPivotGrp = cmds.group(em=True, name=self.ctrlGrpName+'SwivelPivot')
        toeTipPivotGrp = cmds.group(em=True, name=self.ctrlGrpName+'ToeTipPivot')

        footPos = cmds.xform(self.jntName+'foot', q=True, ws=True, t=True)
        toePos = cmds.xform(self.jntName+'toe', q=True, ws=True, t=True)

        cmds.move(footPos[0], footPos[1], footPos[2], flexOffsetGrp)
        cmds.move(footPos[0], footPos[1], footPos[2], flexPivotGrp)
        cmds.move(footPos[0], footPos[1], footPos[2], toeTapPivotGrp)
        cmds.move(footPos[0], footPos[1], footPos[2], swivelPivotGrp)
        cmds.move(toePos[0], toePos[1], toePos[2], toeTipPivotGrp)

        misc.batchParent([self.legIK, self.footIK], flexPivotGrp)
        cmds.parent(flexPivotGrp, flexOffsetGrp)
        cmds.parentConstraint(self.jntName+'foothelper', flexOffsetGrp, mo=True)
        misc.batchParent([self.toeIK, self.helperIK], toeTapPivotGrp)
        misc.batchParent([toeTapPivotGrp, flexOffsetGrp], toeTipPivotGrp)
        cmds.parent(toeTipPivotGrp, swivelPivotGrp)
        cmds.parent(swivelPivotGrp, self.footCtrl)

        cmds.connectAttr(self.footCtrl+'.Flex', flexPivotGrp+'.rotateX')
        cmds.connectAttr(self.footCtrl+'.Swivel', swivelPivotGrp+'.rotateY')
        cmds.connectAttr(self.footCtrl+'.Toe_Tap', toeTapPivotGrp+'.rotateX')
        cmds.connectAttr(self.footCtrl+'.Toe_Tip', toeTipPivotGrp+'.rotateX')

        # pole vector constraint
        cmds.poleVectorConstraint(self.poleCtrl, self.legIK)
        cmds.poleVectorConstraint(self.poleCtrl, self.helperIK)
        cmds.parent(self.poleCtrl, swivelPivotGrp)

        # scalable
        self.addMeasurement()


