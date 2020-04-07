import maya.cmds as cmds
import base
import misc

class FrontLeg(base.Base):
    def __init__(self, prefix, side, id):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'FrontLeg'

        self.constructNameSpace(self.metaType)
        self.setLocAttr(startPos=[0, 5, 3])

    def setLocAttr(self, startPos=[0, 0, 0], distance=1.5, height=0.2, scale=0.4):
        self.startPos = startPos
        self.distance = distance
        self.height = height
        self.scale = scale

    def setCtrlShape(self):
        sphere = cmds.createNode('implicitSphere')
        sphereCtrl = cmds.rename(cmds.listRelatives(sphere, p=True), 'Shoulder_tempShape')
        cmds.scale(0.5, 0.5, 0.5, sphereCtrl)

        pole = cmds.createNode('implicitSphere')
        poleCtrl = cmds.rename(cmds.listRelatives(pole, p=True), 'Pole_tempShape')
        cmds.scale(0.2, 0.2, 0.2, poleCtrl)

        ctrlShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Paw_tempShape')
        cmds.scale(0.5, 0.5, 0.5, ctrlShape)

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        # shoulder
        shoulder = cmds.spaceLocator(n=self.locName+'shoulder')
        cmds.parent(shoulder, grp, relative=True)
        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], shoulder, relative=True)
        cmds.scale(self.scale, self.scale, self.scale, shoulder)

        # elbow
        elbow = cmds.spaceLocator(n=self.locName+'elbow')
        cmds.parent(elbow, shoulder, relative=True)
        cmds.move(0, -self.distance, -0.5*self.distance, elbow, relative=True)

        # wrist
        wrist = cmds.spaceLocator(n=self.locName+'wrist')
        cmds.parent(wrist, elbow, relative=True)
        cmds.move(0, -self.distance, 0, wrist, relative=True)

        # paw
        paw = cmds.spaceLocator(n=self.locName+'paw')
        cmds.parent(paw, wrist, relative=True)
        cmds.move(0, -self.distance+self.height, 0.5*self.distance, paw, relative=True)

        # toe
        toe = cmds.spaceLocator(n=self.locName+'toe')
        cmds.parent(toe, paw, relative=True)
        cmds.move(0, 0, 0.5*self.distance, toe, relative=True)

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        cmds.select(clear=True)
        jntChain = ['shoulder', 'elbow', 'wrist', 'paw', 'toe']
        for name in jntChain:
            loc = cmds.ls(self.locName+name, transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntName+name)
            cmds.setAttr(jnt+'.radius', self.scale)

        cmds.parent(self.jntName+jntChain[0], self.jntGrp)
        misc.orientJnt(self.jntName+jntChain[0])
        return self.jntName+jntChain[0]

    def placeCtrl(self):
        self.setCtrlShape()

        # shoulder
        shoulder = cmds.ls(self.jntName+'shoulder')
        self.shoulderCtrl = cmds.duplicate('Shoulder_tempShape', name=self.ctrlName+'shoulder')[0]
        shoulderPos = cmds.xform(shoulder, q=True, ws=True, t=True)
        shoulderRot = cmds.xform(shoulder, q=True, ws=True, ro=True)

        self.shoulderCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetGrpName+'shoulder')
        cmds.move(shoulderPos[0], shoulderPos[1], shoulderPos[2], self.shoulderCtrlOffset)
        cmds.rotate(shoulderRot[0], shoulderRot[1], shoulderRot[2], self.shoulderCtrlOffset)
        cmds.parent(self.shoulderCtrl, self.shoulderCtrlOffset, relative=True)

        # front foot
        paw = cmds.ls(self.jntName+'paw')
        self.pawCtrl = cmds.duplicate('Paw_tempShape', name=self.ctrlName+'paw')[0]
        pawPos = cmds.xform(paw, q=True, ws=True, t=True)
        cmds.move(pawPos[0], 0, pawPos[2], self.pawCtrl)
        # custom attribute for later pivot group access
        cmds.addAttr(self.pawCtrl, longName='Flex', attributeType='double', keyable=True)
        cmds.addAttr(self.pawCtrl, longName='Swivel', attributeType='double', keyable=True)
        cmds.addAttr(self.pawCtrl, longName='Toe_Tap', attributeType='double', keyable=True)
        cmds.addAttr(self.pawCtrl, longName='Toe_Tip', attributeType='double', keyable=True)
        cmds.addAttr(self.pawCtrl, longName='Wrist', attributeType='double', keyable=True)
        cmds.makeIdentity(self.pawCtrl, apply=True, t=1, r=1, s=1)

        # pole vector
        elbow = cmds.ls(self.jntName+'elbow')
        self.poleCtrl = cmds.duplicate('Pole_tempShape', name=self.ctrlName+'poleVector')[0]
        poleCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetGrpName+'poleVector')
        elbowPos = cmds.xform(elbow, q=True, ws=True, t=True)
        cmds.move(elbowPos[0], elbowPos[1], elbowPos[2]-self.distance, poleCtrlOffset)
        cmds.parent(self.poleCtrl, poleCtrlOffset, relative=True)
        cmds.parent(poleCtrlOffset, self.pawCtrl)
        
        misc.batchParent([self.shoulderCtrlOffset, self.pawCtrl], self.ctrlGrp)
        self.deleteShape()

    def buildIK(self):
        self.legIK = cmds.ikHandle(startJoint=self.jntName+'shoulder', endEffector=self.jntName+'wrist', name=self.prefix+'_IKLeg'+self.name, solver='ikRPsolver')[0]
        self.footIK = cmds.ikHandle(startJoint=self.jntName+'wrist', endEffector=self.jntName+'paw', name=self.prefix+'_IKFoot'+self.name, solver='ikSCsolver')[0]
        self.toeIK = cmds.ikHandle(startJoint=self.jntName+'paw', endEffector=self.jntName+'toe', name=self.prefix+'_IKToe'+self.name, solver='ikSCsolver')[0]

        cmds.setAttr(self.legIK+'.visibility', 0)
        cmds.setAttr(self.footIK+'.visibility', 0)
        cmds.setAttr(self.toeIK+'.visibility', 0)

    def addMeasurement(self):
        # length segment
        shoulderPos = cmds.xform(self.jntName+'shoulder', q=True, ws=True, t=True)
        elbowPos = cmds.xform(self.jntName+'elbow', q=True, ws=True, t=True)
        wristPos = cmds.xform(self.jntName+'wrist', q=True, ws=True, t=True)

        straightenLen = ((shoulderPos[0]-elbowPos[0])**2 + (shoulderPos[1]-elbowPos[1])**2 + (shoulderPos[2]-elbowPos[2])**2) ** 0.5 + \
                        ((wristPos[0]-elbowPos[0])**2 + (wristPos[1]-elbowPos[1])**2 + (wristPos[2]-elbowPos[2])**2) ** 0.5

        # create measurement
        measureNode = cmds.distanceDimension(sp=shoulderPos, ep=wristPos)

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

        cmds.connectAttr(conditionNode+'.outColorR', self.jntName+'elbow.scaleX')
        cmds.connectAttr(conditionNode+'.outColorR', self.jntName+'shoulder.scaleX')

        cmds.rename('distanceDimension1', self.ctrlName+'length')
        cmds.rename('locator1', self.ctrlName+'shoulderLoc')
        cmds.rename('locator2', self.ctrlName+'elbowLoc')

        cmds.setAttr(self.ctrlName+'length.visibility', 0)
        cmds.setAttr(self.ctrlName+'shoulderLoc.visibility', 0)
        cmds.setAttr(self.ctrlName+'elbowLoc.visibility', 0)
        misc.batchParent([self.ctrlName+'length', self.ctrlName+'shoulderLoc', self.ctrlName+'elbowLoc'], self.ctrlGrp)

        cmds.parentConstraint(self.shoulderCtrl, self.ctrlName+'shoulderLoc')
        cmds.parentConstraint(self.pawCtrl, self.ctrlName+'elbowLoc', mo=True)

    def addConstraint(self):
        self.buildIK()
        # shoulder pivot
        cmds.parentConstraint(self.shoulderCtrl, self.jntName+'shoulder')

        # front foot pivot group
        toeTapPivotGrp = cmds.group(em=True, name=self.ctrlGrpName+'ToeTapPivot')
        flexPivotGrp = cmds.group(em=True, name=self.ctrlGrpName+'FlexPivot')
        swivelPivotGrp = cmds.group(em=True, name=self.ctrlGrpName+'SwivelPivot')
        toeTipPivotGrp = cmds.group(em=True, name=self.ctrlGrpName+'ToeTipPivot')
        wristPivotGrp = cmds.group(em=True, name=self.ctrlGrpName+'WristPivot')

        pawPos = cmds.xform(self.jntName+'paw', q=True, ws=True, t=True)
        toePos = cmds.xform(self.jntName+'toe', q=True, ws=True, t=True)
        wristPos = cmds.xform(self.jntName+'wrist', q=True, ws=True, t=True)
        cmds.move(pawPos[0], pawPos[1], pawPos[2], toeTapPivotGrp)
        cmds.move(pawPos[0], pawPos[1], pawPos[2], flexPivotGrp)
        cmds.move(pawPos[0], pawPos[1], pawPos[2], swivelPivotGrp)
        cmds.move(toePos[0], toePos[1], toePos[2], toeTipPivotGrp)
        cmds.move(wristPos[0], wristPos[1], wristPos[2], wristPivotGrp)

        cmds.parent(self.toeIK, toeTapPivotGrp)
        misc.batchParent([self.legIK, self.footIK], flexPivotGrp)
        misc.batchParent([toeTapPivotGrp, flexPivotGrp], swivelPivotGrp)
        cmds.parent(swivelPivotGrp, toeTipPivotGrp)
        cmds.parent(toeTipPivotGrp, wristPivotGrp)
        cmds.parent(wristPivotGrp, self.pawCtrl)

        cmds.connectAttr(self.pawCtrl+'.Flex', flexPivotGrp+'.rotateX')
        cmds.connectAttr(self.pawCtrl+'.Swivel', swivelPivotGrp+'.rotateY')
        cmds.connectAttr(self.pawCtrl+'.Toe_Tap', toeTapPivotGrp+'.rotateX')
        cmds.connectAttr(self.pawCtrl+'.Toe_Tip', toeTipPivotGrp+'.rotateX')
        cmds.connectAttr(self.pawCtrl+'.Wrist', wristPivotGrp+'.rotateX')

        # pole vector constraint
        cmds.poleVectorConstraint(self.poleCtrl, self.legIK)

        # scalable
        self.addMeasurement()


