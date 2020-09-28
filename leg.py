import maya.cmds as cmds
import util, base, foot, limb

class Leg(base.Base):
    def __init__(self, side, id):
        base.Base.__init__(self, side, id)
        self.metaType = 'Leg'
        self.createNaming()
        self.setLocAttr(startPos=[0, 8.4, 0])
        self.limb = limb.Limb(side=self.side, id=id, type='Leg')
        self.foot = foot.Foot(side=self.side, id=id)

    def setLocAttr(self, startPos=[0, 0, 0], distance=4, interval=0.5, height=0.4, scale=0.2):
        self.startPos = startPos
        self.distance = distance
        self.interval = interval
        self.height = height
        self.scale = scale

    def buildGuide(self):
        #--- Limb ---#
        self.limb.setLocAttr(startPos=self.startPos, interval=self.distance)
        self.limb.buildGuide()

        #--- Foot ---#
        self.foot.setLocAttr(startPos=[self.startPos[0], self.startPos[1]-2*self.distance, self.startPos[2]],
                             interval=self.interval, height=self.height)
        footGrp = self.foot.buildGuide()

        #--- Connect ---#
        cmds.parent(footGrp, self.limb.locList[-1])

    def constructJnt(self):
        self.limb.constructJnt()
        self.foot.constructJnt()

    def placeCtrl(self):
        self.limb.placeCtrl()
        self.foot.placeCtrl()

    def addConstraint(self):
        self.limb.addConstraint()
        self.foot.addConstraint()

        #--- Connect ---#
        # IK constraint #
        cmds.parentConstraint(self.foot.revAnkleJntName, self.limb.ikCtrlName, mo=True)
        cmds.setAttr(self.limb.ikCtrlName+'.visibility', 0)

        # FK constraint #
        cmds.parentConstraint(self.limb.jntList[-1], self.foot.fkAnkleJntName, mo=True)
        cmds.parent(self.foot.fkCtrlName, self.limb.fkCtrlList[-1])

        # IK/FK switch #
        cmds.setDrivenKeyframe(self.limb.switchCtrl+'.FK_IK', currentDriver=self.foot.switchCtrlName+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.limb.switchCtrl+'.FK_IK', currentDriver=self.foot.switchCtrlName+'.FK_IK', driverValue=0, value=0)

        # Sub controller visibility and channel hide #
        cmds.setDrivenKeyframe(self.limb.ikCtrlName+'.visibility', currentDriver=self.limb.switchCtrl+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.limb.ikCtrlName+'.visibility', currentDriver=self.limb.switchCtrl+'.FK_IK', driverValue=0, value=0)
        cmds.setAttr(self.limb.switchCtrl+'.FK_IK', l=1, k=0)

    def deleteGuide(self):
        self.foot.deleteGuide()
        self.limb.deleteGuide()

    def colorCtrl(self):
        self.limb.colorCtrl()
        self.foot.colorCtrl()

class LegFront(base.Base):
    def __init__(self, side, id):
        base.Base.__init__(self, side, id)
        self.metaType = 'FrontLeg'
        self.createNaming()
        self.createSecondaryNaming()

    def createSecondaryNaming(self):
        self.locList, self.jntList, self.ctrlList, self.ctrlOffsetList = ([] for i in range(4))  # ik has different ctrl name
        self.limbType = ['shoulder', 'elbow', 'wrist', 'paw', 'toe']
        for type in self.limbType:
            self.locList.append('{}{}_loc'.format(self.name, type))
            self.jntList.append('{}{}_jnt'.format(self.name, type))
            self.ctrlList.append('{}{}_ctrl'.format(self.name, type))
            self.ctrlOffsetList.append('{}{}_offset'.format(self.name, type))

        self.legIKName = '{}leg_ik'.format(self.name)
        self.footIKName = '{}foot_ik'.format(self.name)
        self.toeIKName = '{}toe_ik'.format(self.name)

    def setLocAttr(self, startPos=[0, 5, 3], distance=1.5, height=0.2, scale=0.4):
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
        shoulder = cmds.spaceLocator(n=self.locList[0])
        cmds.parent(shoulder, grp, relative=True)
        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], shoulder, relative=True)
        cmds.scale(self.scale, self.scale, self.scale, shoulder)

        # elbow
        elbow = cmds.spaceLocator(n=self.locList[1])
        cmds.parent(elbow, shoulder, relative=True)
        cmds.move(0, -self.distance, -0.5 * self.distance, elbow, relative=True)

        # wrist
        wrist = cmds.spaceLocator(n=self.locList[2])
        cmds.parent(wrist, elbow, relative=True)
        cmds.move(0, -self.distance, 0, wrist, relative=True)

        # paw
        paw = cmds.spaceLocator(n=self.locList[3])
        cmds.parent(paw, wrist, relative=True)
        cmds.move(0, -self.distance+self.height, 0.5 * self.distance, paw, relative=True)

        # toe
        toe = cmds.spaceLocator(n=self.locList[4])
        cmds.parent(toe, paw, relative=True)
        cmds.move(0, 0, 0.5 * self.distance, toe, relative=True)

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        cmds.select(clear=True)
        for index in range(len(self.locList)):
            loc = cmds.ls(self.locList[index], transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntList[index])
            cmds.setAttr(jnt+'.radius', self.scale)

        cmds.parent(self.jntList[0], self.jntGrp)
        util.orientJnt(self.jntList[0])
        return self.jntList[0]

    def placeCtrl(self):
        self.setCtrlShape()

        # shoulder
        shoulder = cmds.ls(self.jntList[0])
        shoulderCtrl = cmds.duplicate('Shoulder_tempShape', name=self.ctrlList[0])[0]
        shoulderPos = cmds.xform(shoulder, q=True, ws=True, t=True)
        shoulderRot = cmds.xform(shoulder, q=True, ws=True, ro=True)

        shoulderCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetList[0])
        cmds.move(shoulderPos[0], shoulderPos[1], shoulderPos[2], shoulderCtrlOffset)
        cmds.rotate(shoulderRot[0], shoulderRot[1], shoulderRot[2], shoulderCtrlOffset)
        cmds.parent(shoulderCtrl, shoulderCtrlOffset, relative=True)

        # front foot
        paw = cmds.ls(self.jntList[3])
        pawCtrl = cmds.duplicate('Paw_tempShape', name=self.ctrlList[3])[0]
        pawPos = cmds.xform(paw, q=True, ws=True, t=True)
        cmds.move(pawPos[0], 0, pawPos[2], pawCtrl)
        # custom attribute for later pivot group access
        cmds.addAttr(pawCtrl, longName='Flex', attributeType='double', keyable=True)
        cmds.addAttr(pawCtrl, longName='Swivel', attributeType='double', keyable=True)
        cmds.addAttr(pawCtrl, longName='Toe_Tap', attributeType='double', keyable=True)
        cmds.addAttr(pawCtrl, longName='Toe_Tip', attributeType='double', keyable=True)
        cmds.addAttr(pawCtrl, longName='Wrist', attributeType='double', keyable=True)
        cmds.makeIdentity(pawCtrl, apply=True, t=1, r=1, s=1)

        # elbow control - aka. pole vector
        elbow = cmds.ls(self.jntList[1])
        poleCtrl = cmds.duplicate('Pole_tempShape', name=self.ctrlList[1])[0]
        poleCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetList[1])
        elbowPos = cmds.xform(elbow, q=True, ws=True, t=True)
        cmds.move(elbowPos[0], elbowPos[1], elbowPos[2]-self.distance, poleCtrlOffset)
        cmds.parent(poleCtrl, poleCtrlOffset, relative=True)
        cmds.parent(poleCtrlOffset, pawCtrl)

        util.batchParent([shoulderCtrlOffset, pawCtrl], self.ctrlGrp)
        self.deleteShape()

    def buildIK(self):
        cmds.ikHandle(startJoint=self.jntList[0], endEffector=self.jntList[2], name=self.legIKName, solver='ikRPsolver')
        cmds.ikHandle(startJoint=self.jntList[2], endEffector=self.jntList[3], name=self.footIKName, solver='ikSCsolver')
        cmds.ikHandle(startJoint=self.jntList[3], endEffector=self.jntList[4], name=self.toeIKName, solver='ikSCsolver')
        cmds.setAttr(self.legIKName+'.visibility', 0)
        cmds.setAttr(self.footIKName+'.visibility', 0)
        cmds.setAttr(self.toeIKName+'.visibility', 0)

    def addMeasurement(self):
        # length segment
        shoulderPos = cmds.xform(self.jntList[0], q=True, ws=True, t=True)
        elbowPos = cmds.xform(self.jntList[1], q=True, ws=True, t=True)
        wristPos = cmds.xform(self.jntList[2], q=True, ws=True, t=True)
        straightenLen = ((shoulderPos[0]-elbowPos[0]) ** 2+(shoulderPos[1]-elbowPos[1]) ** 2+(shoulderPos[2]-elbowPos[2]) ** 2) ** 0.5+ \
                        ((wristPos[0]-elbowPos[0]) ** 2+(wristPos[1]-elbowPos[1]) ** 2+(wristPos[2]-elbowPos[2]) ** 2) ** 0.5

        # create measurement
        measureShape = cmds.distanceDimension(sp=shoulderPos, ep=wristPos)
        locs = cmds.listConnections(measureShape)
        measureNode = cmds.listRelatives(measureShape, parent=True, type='transform')
        lengthNode = '{}length_node'.format(self.name)
        shoulderLoc = '{}shoulder_node'.format(self.name)
        elbowLoc = '{}elbow_node'.format(self.name)
        cmds.rename(measureNode, lengthNode)
        cmds.rename(locs[0], shoulderLoc)
        cmds.rename(locs[1], elbowLoc)

        stretchNode = cmds.shadingNode('multiplyDivide', asUtility=True, name='{}stretch_node'.format(self.name))
        cmds.setAttr(stretchNode+'.operation', 2)
        cmds.setAttr(stretchNode+'.input2X', straightenLen)
        cmds.connectAttr(lengthNode+'.distance', stretchNode+'.input1X')

        conditionNode = cmds.shadingNode('condition', asUtility=True, name='{}condition_node'.format(self.name))
        cmds.connectAttr(stretchNode+'.outputX', conditionNode+'.firstTerm')
        cmds.setAttr(conditionNode+'.secondTerm', 1)
        cmds.setAttr(conditionNode+'.operation', 2)  # Greater than
        cmds.connectAttr(stretchNode+'.outputX', conditionNode+'.colorIfTrueR')
        cmds.setAttr(conditionNode+'.colorIfFalseR', 1)

        cmds.connectAttr(conditionNode+'.outColorR', self.jntList[0]+'.scaleX')
        cmds.connectAttr(conditionNode+'.outColorR', self.jntList[1]+'.scaleX')

        cmds.setAttr(lengthNode+'.visibility', 0)
        cmds.setAttr(shoulderLoc+'.visibility', 0)
        cmds.setAttr(elbowLoc+'.visibility', 0)
        util.batchParent([lengthNode, shoulderLoc, elbowLoc], self.ctrlGrp)

        cmds.parentConstraint(self.ctrlList[0], shoulderLoc)
        cmds.parentConstraint(self.ctrlList[3], elbowLoc, mo=True)

    def addConstraint(self):
        self.buildIK()
        # shoulder pivot
        cmds.parentConstraint(self.ctrlList[0], self.jntList[0])

        # front foot pivot group
        toeTapPivotGrp = cmds.group(em=True, name='{}toetap_pivotGrp'.format(self.name))
        flexPivotGrp = cmds.group(em=True, name='{}flex_pivotGrp'.format(self.name))
        swivelPivotGrp = cmds.group(em=True, name='{}swivel_pivotGrp'.format(self.name))
        toeTipPivotGrp = cmds.group(em=True, name='{}toetip_pivotGrp'.format(self.name))
        wristPivotGrp = cmds.group(em=True, name='{}wrist_pivotGrp'.format(self.name))

        pawPos = cmds.xform(self.jntList[3], q=True, ws=True, t=True)
        toePos = cmds.xform(self.jntList[4], q=True, ws=True, t=True)
        wristPos = cmds.xform(self.jntList[2], q=True, ws=True, t=True)
        cmds.move(pawPos[0], pawPos[1], pawPos[2], toeTapPivotGrp)
        cmds.move(pawPos[0], pawPos[1], pawPos[2], flexPivotGrp)
        cmds.move(pawPos[0], pawPos[1], pawPos[2], swivelPivotGrp)
        cmds.move(toePos[0], toePos[1], toePos[2], toeTipPivotGrp)
        cmds.move(wristPos[0], wristPos[1], wristPos[2], wristPivotGrp)

        cmds.parent(self.toeIKName, toeTapPivotGrp)
        util.batchParent([self.legIKName, self.footIKName], flexPivotGrp)
        util.batchParent([toeTapPivotGrp, flexPivotGrp], swivelPivotGrp)
        cmds.parent(swivelPivotGrp, toeTipPivotGrp)
        cmds.parent(toeTipPivotGrp, wristPivotGrp)
        cmds.parent(wristPivotGrp, self.ctrlList[3])

        cmds.connectAttr(self.ctrlList[3]+'.Flex', flexPivotGrp+'.rotateX')
        cmds.connectAttr(self.ctrlList[3]+'.Swivel', swivelPivotGrp+'.rotateY')
        cmds.connectAttr(self.ctrlList[3]+'.Toe_Tap', toeTapPivotGrp+'.rotateX')
        cmds.connectAttr(self.ctrlList[3]+'.Toe_Tip', toeTipPivotGrp+'.rotateX')
        cmds.connectAttr(self.ctrlList[3]+'.Wrist', wristPivotGrp+'.rotateX')

        # pole vector constraint
        cmds.poleVectorConstraint(self.ctrlList[1], self.legIKName)

        # scalable
        self.addMeasurement()

class LegBack(base.Base):
    def __init__(self, side, id):
        base.Base.__init__(self, side, id)
        self.metaType = 'BackLeg'
        self.createNaming()
        self.createSecondaryNaming()

    def createSecondaryNaming(self):
        self.locList, self.jntList, self.ctrlList, self.ctrlOffsetList, self.jntHelperList = ([] for i in range(5))  # ik has different ctrl name
        self.limbType = ['hip', 'knee', 'ankle', 'paw', 'toe']
        for type in self.limbType:
            self.locList.append('{}{}_loc'.format(self.name, type))
            self.jntList.append('{}{}_jnt'.format(self.name, type))
            self.jntHelperList.append('{}{}helper_jnt'.format(self.name, type))
            self.ctrlList.append('{}{}_ctrl'.format(self.name, type))
            self.ctrlOffsetList.append('{}{}_offset'.format(self.name, type))

        self.legIKName = '{}leg_ik'.format(self.name)
        self.footIKName = '{}foot_ik'.format(self.name)
        self.toeIKName = '{}toe_ik'.format(self.name)
        self.helperIKName = '{}helper_ik'.format(self.name)

    def setLocAttr(self, startPos=[0, 5, -3], distance=1.5, height=0.2, scale=0.4):
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
        hip = cmds.spaceLocator(n=self.locList[0])
        cmds.parent(hip, grp, relative=True)
        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], hip, relative=True)
        cmds.scale(self.scale, self.scale, self.scale, hip)

        # knee
        knee = cmds.spaceLocator(n=self.locList[1])
        cmds.parent(knee, hip, relative=True)
        cmds.move(0, -self.distance, 0, knee, relative=True)

        # ankle
        ankle = cmds.spaceLocator(n=self.locList[2])
        cmds.parent(ankle, knee, relative=True)
        cmds.move(0, -self.distance, -0.5 * self.distance, ankle, relative=True)

        # foot
        foot = cmds.spaceLocator(n=self.locList[3])
        cmds.parent(foot, ankle, relative=True)
        cmds.move(0, -self.distance+self.height, 0, foot, relative=True)

        # toe
        toe = cmds.spaceLocator(n=self.locList[4])
        cmds.parent(toe, foot, relative=True)
        cmds.move(0, 0, 0.5 * self.distance, toe, relative=True)

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        # result jnt chain
        cmds.select(clear=True)
        for index in range(len(self.locList)):
            loc = cmds.ls(self.locList[index], transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntList[index])
            cmds.setAttr(jnt+'.radius', self.scale)
        util.orientJnt(self.jntList[0])
        cmds.parent(self.jntList[0], self.jntGrp)

        # helper jnt chain
        cmds.select(clear=True)
        for index in range(len(self.locList[:-1])):
            loc = cmds.ls(self.locList[index], transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntHelperList[index])
            cmds.setAttr(jnt+'.radius', 1)
        util.orientJnt(self.jntHelperList[0])
        cmds.parent(self.jntHelperList[0], self.jntGrp)
        cmds.setAttr(self.jntHelperList[0]+'.visibility', 0)

        return self.jntList[0]

    def placeCtrl(self):
        self.setCtrlShape()

        # hip
        hip = cmds.ls(self.jntList[0])
        hipCtrl = cmds.duplicate('Hip_tempShape', name=self.ctrlList[0])[0]
        hipPos = cmds.xform(hip, q=True, ws=True, t=True)
        hipRot = cmds.xform(hip, q=True, ws=True, ro=True)

        hipCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetList[0])
        cmds.move(hipPos[0], hipPos[1], hipPos[2], hipCtrlOffset)
        cmds.rotate(hipRot[0], hipRot[1], hipRot[2], hipCtrlOffset)
        cmds.parent(hipCtrl, hipCtrlOffset, relative=True)

        # back foot
        foot = cmds.ls(self.jntList[3])
        footCtrl = cmds.duplicate('Foot_tempShape', name=self.ctrlList[3])[0]
        footPos = cmds.xform(foot, q=True, ws=True, t=True)
        cmds.move(footPos[0], 0, footPos[2], footCtrl)
        cmds.makeIdentity(footCtrl, apply=True, t=1, r=1, s=1)
        # custom attribute for later pivot group access
        cmds.addAttr(footCtrl, longName='Flex', attributeType='double', keyable=True)
        cmds.addAttr(footCtrl, longName='Swivel', attributeType='double', keyable=True)
        cmds.addAttr(footCtrl, longName='Toe_Tap', attributeType='double', keyable=True)
        cmds.addAttr(footCtrl, longName='Toe_Tip', attributeType='double', keyable=True)

        # ankle control - poleVector
        ankle = cmds.ls(self.jntList[2])
        poleCtrl = cmds.duplicate('Pole_tempShape', name=self.ctrlList[2])[0]
        poleCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetList[2])
        anklePos = cmds.xform(ankle, q=True, ws=True, t=True)
        cmds.move(anklePos[0], anklePos[1], anklePos[2]+self.distance, poleCtrlOffset)
        cmds.parent(poleCtrl, poleCtrlOffset, relative=True)
        cmds.parent(poleCtrlOffset, footCtrl)

        util.batchParent([hipCtrlOffset, footCtrl], self.ctrlGrp)
        self.deleteShape()

    def buildIK(self):
        cmds.ikHandle(startJoint=self.jntList[0], endEffector=self.jntList[2], name=self.legIKName, solver='ikRPsolver')
        cmds.ikHandle(startJoint=self.jntList[2], endEffector=self.jntList[3], name=self.footIKName, solver='ikSCsolver')
        cmds.ikHandle(startJoint=self.jntList[3], endEffector=self.jntList[4], name=self.toeIKName, solver='ikSCsolver')
        cmds.ikHandle(startJoint=self.jntHelperList[0], endEffector=self.jntHelperList[3], name=self.helperIKName, solver='ikRPsolver')
        cmds.setAttr(self.legIKName+'.visibility', 0)
        cmds.setAttr(self.footIKName+'.visibility', 0)
        cmds.setAttr(self.toeIKName+'.visibility', 0)
        cmds.setAttr(self.helperIKName+'.visibility', 0)

    def addMeasurement(self):
        # length segment
        hipPos = cmds.xform(self.jntList[0], q=True, ws=True, t=True)
        kneePos = cmds.xform(self.jntList[1], q=True, ws=True, t=True)
        anklePos = cmds.xform(self.jntList[2], q=True, ws=True, t=True)
        footPos = cmds.xform(self.jntList[3], q=True, ws=True, t=True)
        straightenLen = ((kneePos[0]-anklePos[0]) ** 2+(kneePos[1]-anklePos[1]) ** 2+(kneePos[2]-anklePos[2]) ** 2) ** 0.5+ \
                        ((footPos[0]-anklePos[0]) ** 2+(footPos[1]-anklePos[1]) ** 2+(footPos[2]-anklePos[2]) ** 2) ** 0.5+ \
                        ((hipPos[0]-kneePos[0]) ** 2+(hipPos[1]-kneePos[1]) ** 2+(hipPos[2]-kneePos[2]) ** 2) ** 0.5

        # create measurement
        measureShape = cmds.distanceDimension(sp=hipPos, ep=footPos)
        locs = cmds.listConnections(measureShape)
        measureNode = cmds.listRelatives(measureShape, parent=True, type='transform')
        lengthNode = '{}length_node'.format(self.name)
        hipLoc = '{}hip_node'.format(self.name)
        ankleLoc = '{}ankle_node'.format(self.name)
        cmds.rename(measureNode, lengthNode)
        cmds.rename(locs[0], hipLoc)
        cmds.rename(locs[1], ankleLoc)

        stretchNode = cmds.shadingNode('multiplyDivide', asUtility=True, name='{}stretch_node'.format(self.name))
        cmds.setAttr(stretchNode+'.operation', 2)
        cmds.setAttr(stretchNode+'.input2X', straightenLen)
        cmds.connectAttr(lengthNode+'.distance', stretchNode+'.input1X')

        conditionNode = cmds.shadingNode('condition', asUtility=True, name='{}condition_node'.format(self.name))
        cmds.connectAttr(stretchNode+'.outputX', conditionNode+'.firstTerm')
        cmds.setAttr(conditionNode+'.secondTerm', 1)
        cmds.setAttr(conditionNode+'.operation', 2)  # Greater than
        cmds.connectAttr(stretchNode+'.outputX', conditionNode+'.colorIfTrueR')
        cmds.setAttr(conditionNode+'.colorIfFalseR', 1)

        for joint in [self.jntList[0], self.jntList[1], self.jntList[2],
                      self.jntHelperList[0], self.jntHelperList[1], self.jntHelperList[2]]:
            cmds.connectAttr(conditionNode+'.outColorR', joint+'.scaleX')

        cmds.setAttr(lengthNode+'.visibility', 0)
        cmds.setAttr(hipLoc+'.visibility', 0)
        cmds.setAttr(ankleLoc+'.visibility', 0)
        util.batchParent([lengthNode, hipLoc, ankleLoc], self.ctrlGrp)

        cmds.parentConstraint(self.ctrlList[0], hipLoc)
        cmds.parentConstraint(self.ctrlList[3], ankleLoc, mo=True)

    def addConstraint(self):
        self.buildIK()
        # shoulder pivot
        cmds.parentConstraint(self.ctrlList[0], self.jntList[0])
        cmds.parentConstraint(self.ctrlList[0], self.jntHelperList[0])

        # front foot pivot group
        toeTapPivotGrp = cmds.group(em=True, name='{}toetap_pivotGrp'.format(self.name))
        flexPivotGrp = cmds.group(em=True, name='{}flex_pivotGrp'.format(self.name))
        flexOffsetGrp = cmds.group(em=True, name='{}flex_offsetGrp'.format(self.name))
        swivelPivotGrp = cmds.group(em=True, name='{}swivel_pivotGrp'.format(self.name))
        toeTipPivotGrp = cmds.group(em=True, name='{}toetip_pivotGrp'.format(self.name))

        footPos = cmds.xform(self.jntList[3], q=True, ws=True, t=True)
        toePos = cmds.xform(self.jntList[4], q=True, ws=True, t=True)

        cmds.move(footPos[0], footPos[1], footPos[2], flexOffsetGrp)
        cmds.move(footPos[0], footPos[1], footPos[2], flexPivotGrp)
        cmds.move(footPos[0], footPos[1], footPos[2], toeTapPivotGrp)
        cmds.move(footPos[0], footPos[1], footPos[2], swivelPivotGrp)
        cmds.move(toePos[0], toePos[1], toePos[2], toeTipPivotGrp)

        util.batchParent([self.legIKName, self.footIKName], flexPivotGrp)
        cmds.parent(flexPivotGrp, flexOffsetGrp)
        cmds.parentConstraint(self.jntHelperList[3], flexOffsetGrp, mo=True)
        util.batchParent([self.toeIKName, self.helperIKName], toeTapPivotGrp)
        util.batchParent([toeTapPivotGrp, flexOffsetGrp], toeTipPivotGrp)
        cmds.parent(toeTipPivotGrp, swivelPivotGrp)
        cmds.parent(swivelPivotGrp, self.ctrlList[3])

        cmds.connectAttr(self.ctrlList[3]+'.Flex', flexPivotGrp+'.rotateX')
        cmds.connectAttr(self.ctrlList[3]+'.Swivel', swivelPivotGrp+'.rotateY')
        cmds.connectAttr(self.ctrlList[3]+'.Toe_Tap', toeTapPivotGrp+'.rotateX')
        cmds.connectAttr(self.ctrlList[3]+'.Toe_Tip', toeTipPivotGrp+'.rotateX')

        # pole vector constraint
        cmds.poleVectorConstraint(self.ctrlList[2], self.legIKName)
        cmds.poleVectorConstraint(self.ctrlList[2], self.helperIKName)
        cmds.parent(self.ctrlOffsetList[2], swivelPivotGrp)

        # scalable
        self.addMeasurement()