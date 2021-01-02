import maya.cmds as cmds
import maya.OpenMaya as om
import base
from utility import joint, outliner


class Limb(base.Base):
    def __init__(self, side, id, type='Null'):
        base.Base.__init__(self, side, id)
        self.metaType = 'Limb'
        self.setArmLeg(type)
        self.createNaming()
        self.createSecondaryNaming()
        self.setLocAttr([0, 0, 0], 2)

    def setArmLeg(self, type):
        self.limbType = ['Root', 'Middle', 'Top']
        if type == 'Arm':
            self.limbType = ['shoulder', 'elbow', 'wrist']
            self.direction = 'Horizontal'
        elif type == 'Leg':
            self.limbType = ['clavicle', 'knee', 'ankle']
            self.direction = 'Vertical'

    def createSecondaryNaming(self):
        self.locList, self.jntList, self.ikJntList, self.fkJntList, self.ctrlList, self.fkCtrlList, self.fkOffsetList = ([] for i in range(7))  # ik has different ctrl name
        for type in self.limbType:
            self.locList.append     ('{}{}_loc'.format(self.name, type))
            self.jntList.append     ('{}{}_jnt'.format(self.name, type))
            self.ikJntList.append   ('{}{}_ik_jnt'.format(self.name, type))
            self.fkJntList.append   ('{}{}_fk_jnt'.format(self.name, type))
            self.ctrlList.append    ('{}{}_ctrl'.format(self.name, type))
            self.fkCtrlList.append  ('{}{}_fk_ctrl'.format(self.name, type))
            self.fkOffsetList.append('{}{}_fk_offset'.format(self.name, type))

        self.ikCtrlName =   '{}_ik_ctrl'.format(self.name)
        self.ikPoleName =   '{}_ikpole_ctrl'.format(self.name)
        self.ikOffsetName = '{}_ik_offset'.format(self.name)

    def setLocAttr(self, startPos=[0, 0, 0], interval=2, scale=0.4):
        self.startPos = startPos
        self.interval = interval
        self.scale = scale

    def setCtrlShape(self):
        limbFKShape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='LimbFK_tempShape')
        #cmds.scale(0.2, 0.2, 0.2, limbFKShape)

        limbIKShape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='LimbIK_tempShape')

        limbIKPoleShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='LimbIKPole_tempShape')
        selection = cmds.select('LimbIKPole_tempShape.cv[6]', 'LimbIKPole_tempShape.cv[0]')
        cmds.scale(0.5, 0.5, 0.5, selection)
        cmds.move(-0.5, 0, 0, selection)
        cmds.rotate(0, 90, 0, limbIKPoleShape)

        arrowPtList = [[2.0, 0.0, 2.0], [2.0, 0.0, 1.0], [3.0, 0.0, 1.0], [3.0, 0.0, 2.0], [5.0, 0.0, 0.0], [3.0, 0.0, -2.0], [3.0, 0.0, -1.0], [2.0, 0.0, -1.0],
                       [2.0, 0.0, -2.0], [1.0, 0.0, -2.0], [1.0, 0.0, -3.0], [2.0, 0.0, -3.0], [0.0, 0.0, -5.0], [-2.0, 0.0, -3.0], [-1.0, 0.0, -3.0], [-1.0, 0.0, -2.0],
                       [-2.0, 0.0, -2.0], [-2.0, 0.0, -1.0], [-3.0, 0.0, -1.0], [-3.0, 0.0, -2.0], [-5.0, 0.0, 0.0], [-3.0, 0.0, 2.0], [-3.0, 0.0, 1.0], [-2.0, 0.0, 1.0],
                       [-2.0, 0.0, 2.0], [-1.0, 0.0, 2.0], [-1.0, 0.0, 3.0], [-2.0, 0.0, 3.0], [0.0, 0.0, 5.0], [2.0, 0.0, 3.0], [1.0, 0.0, 3.0], [1.0, 0.0, 2.0], [2.0, 0.0, 2.0]]
        switchShape = cmds.curve(p=arrowPtList, degree=1, name='Switch_tempShape')
        cmds.scale(0.3, 0.3, 0.3, switchShape)

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        sideFactor, hFactor, vFactor = 1, 1, 0
        if self.side == 'R':             sideFactor = -1
        if self.direction == 'Vertical': hFactor, vFactor = 0, 1

        #--- Root ---#
        limbRoot = cmds.spaceLocator(n=self.locList[0])
        cmds.parent(limbRoot, grp, relative=True)
        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], limbRoot, relative=True)
        cmds.scale(self.scale, self.scale, self.scale, limbRoot)

        #--- Middle ---#
        limbMid = cmds.spaceLocator(n=self.locList[1])
        cmds.parent(limbMid, limbRoot, relative=True)
        cmds.move(self.interval*sideFactor*hFactor, -self.interval*vFactor, 0, limbMid, relative=True)  # move limb joint along +x axis

        #--- Top ---#
        limbTop = cmds.spaceLocator(n=self.locList[2])
        cmds.parent(limbTop, limbMid, relative=True)
        cmds.move(self.interval*sideFactor*hFactor, -self.interval*vFactor, 0, limbTop, relative=True)  # move limb joint along +x axis

        #--- Cleanup ---#
        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        #--- Result joint ---#
        cmds.select(clear=True)
        for i, type in enumerate(self.limbType):
            loc = cmds.ls(self.locList[i], transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntList[i])
            cmds.setAttr(jnt+'.radius', 1)

        #--- FK Joint ---#
        cmds.select(clear=True)
        for i, type in enumerate(self.limbType):
            loc = cmds.ls(self.locList[i], transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            fkJnt = cmds.joint(p=locPos, name=self.fkJntList[i])
            cmds.setAttr(fkJnt+'.radius', 1)

        #--- IK Joint ---#
        cmds.select(clear=True)
        for i, type in enumerate(self.limbType):
            loc = cmds.ls(self.locList[i], transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            ikJnt = cmds.joint(p=locPos, name=self.ikJntList[i])
            cmds.setAttr(ikJnt+'.radius', 1)

        #--- Cleanup ---#
        outliner.batch_parent([self.jntList[0], self.ikJntList[0], self.fkJntList[0]], self.jntGrp)
        joint.orient_joint([self.jntList[0], self.ikJntList[0], self.fkJntList[0]])
        return cmds.ls(self.jntList[0])

    def placeCtrl(self):
        self.setCtrlShape()
        rootPos, midPos, topPos = [cmds.xform(self.jntList[i], q=True, t=True, ws=True) for i in range(len(self.limbType))]
        rootRot, midRot, topRot = [cmds.xform(self.jntList[i], q=True, ro=True, ws=True) for i in range(len(self.limbType))]

        #--- FK Setup ---#
        rootFkCtrl = cmds.duplicate('LimbFK_tempShape', name=self.fkCtrlList[0])[0]
        cmds.move(rootPos[0], rootPos[1], rootPos[2], rootFkCtrl, absolute=True)
        #if self.direction == 'Vertical': cmds.rotate(0, 0, 90, rootFkCtrl)
            
        rootOffset = cmds.group(em=True, name=self.fkOffsetList[0])
        cmds.move(rootPos[0], rootPos[1], rootPos[2], rootOffset)
        cmds.parent(rootFkCtrl, rootOffset)
        cmds.rotate(rootRot[0], rootRot[1], rootRot[2], rootOffset)
        cmds.makeIdentity(rootFkCtrl, apply=True, t=1, r=1, s=1)

        midFkCtrl = cmds.duplicate('LimbFK_tempShape', name=self.fkCtrlList[1])[0]
        cmds.move(midPos[0], midPos[1], midPos[2], midFkCtrl, absolute=True)
        #if self.direction == 'Vertical': cmds.rotate(0, 0, 90, midFkCtrl)
            
        midOffset = cmds.group(em=True, name=self.fkOffsetList[1])
        cmds.move(midPos[0], midPos[1], midPos[2], midOffset)
        cmds.parent(midFkCtrl, midOffset)
        cmds.rotate(midRot[0], midRot[1], midRot[2], midOffset)
        cmds.makeIdentity(midFkCtrl, apply=True, t=1, r=1, s=1)

        topFkCtrl = cmds.duplicate('LimbFK_tempShape', name=self.fkCtrlList[2])[0]
        cmds.move(topPos[0], topPos[1], topPos[2], topFkCtrl, absolute=True)
        #if self.direction == 'Vertical': cmds.rotate(0, 0, 90, topFkCtrl)

        topOffset = cmds.group(em=True, name=self.fkOffsetList[2])
        cmds.move(topPos[0], topPos[1], topPos[2], topOffset)
        cmds.parent(topFkCtrl, topOffset)
        cmds.rotate(topRot[0], topRot[1], topRot[2], topOffset)
        cmds.makeIdentity(topFkCtrl, apply=True, t=1, r=1, s=1)

        cmds.parent(topOffset, midFkCtrl)
        cmds.parent(midOffset, rootFkCtrl)

        #--- IK Setup ---#
        ikCtrl = cmds.duplicate('LimbIK_tempShape', name=self.ikCtrlName)[0]
        cmds.move(topPos[0], topPos[1], topPos[2], ikCtrl, absolute=True)
        #if self.direction == 'Vertical': cmds.rotate(0, 0, 90, ikCtrl)

        offsetGrp = cmds.group(em=True, name=self.ikOffsetName)
        cmds.move(topPos[0], topPos[1], topPos[2], offsetGrp)
        cmds.parent(ikCtrl, offsetGrp)
        cmds.rotate(topRot[0], topRot[1], topRot[2], offsetGrp)
        cmds.makeIdentity(ikCtrl, apply=True, t=1, r=1, s=1)

        poleCtrl = cmds.duplicate('LimbIKPole_tempShape', name=self.ikPoleName)
        if self.direction == 'Vertical':
            cmds.move(midPos[0], midPos[1], midPos[2]+3, poleCtrl, absolute=True)
        elif self.direction == 'Horizontal':
            cmds.move(midPos[0], midPos[1], midPos[2]-3, poleCtrl, absolute=True)
            cmds.rotate(0, 180, 0, poleCtrl, relative=True)
        cmds.makeIdentity(poleCtrl, apply=True, t=1, r=1, s=1)

        #--- IK/FK Switch Setup ---#
        self.switchCtrl = cmds.duplicate('Switch_tempShape', name='{}_switch_ctrl'.format(self.name))[0]
        #if self.direction == 'Vertical':
        #    cmds.move(rootPos[0], rootPos[1], rootPos[2], self.switchCtrl, absolute=True)
        #elif self.direction == 'Horizontal':
        cmds.move(rootPos[0], rootPos[1], rootPos[2], self.switchCtrl, absolute=True)
        cmds.rotate(0, 0, 90, self.switchCtrl, relative=True)
        cmds.addAttr(self.switchCtrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=True)

        offsetGrp = cmds.group(em=True, name='{}_switch_offset'.format(self.name))
        cmds.move(rootPos[0], rootPos[1], rootPos[2], offsetGrp)
        cmds.parent(self.switchCtrl, offsetGrp)
        cmds.rotate(rootRot[0], rootRot[1], rootRot[2], offsetGrp)
        cmds.makeIdentity(self.switchCtrl, apply=True, t=1, r=1, s=1)

        #--- Cleanup ---#
        self.deleteShape()
        cmds.parent(offsetGrp, self.ctrlGrp)

    def addConstraint(self):
        #--- Result Joint + IK/FK Switch ---#
        for i, type in enumerate(self.limbType):
            if i == 0:
                cmds.parentConstraint(self.ikJntList[i], self.fkJntList[i], self.jntList[i])
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jntList[i], self.ikJntList[i]), currentDriver='{}.FK_IK'.format(self.switchCtrl), driverValue=1, value=1)
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jntList[i], self.fkJntList[i]), currentDriver='{}.FK_IK'.format(self.switchCtrl), driverValue=1, value=0)
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jntList[i], self.ikJntList[i]), currentDriver='{}.FK_IK'.format(self.switchCtrl), driverValue=0, value=0)
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jntList[i], self.fkJntList[i]), currentDriver='{}.FK_IK'.format(self.switchCtrl), driverValue=0, value=1)
            else:
                cmds.orientConstraint(self.ikJntList[i], self.fkJntList[i], self.jntList[i])
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jntList[i], self.ikJntList[i]), currentDriver='{}.FK_IK'.format(self.switchCtrl), driverValue=1, value=1)
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.jntList[i], self.fkJntList[i]), currentDriver='{}.FK_IK'.format(self.switchCtrl), driverValue=1, value=0)
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jntList[i], self.ikJntList[i]), currentDriver='{}.FK_IK'.format(self.switchCtrl), driverValue=0, value=0)
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.jntList[i], self.fkJntList[i]), currentDriver='{}.FK_IK'.format(self.switchCtrl), driverValue=0, value=1)

        for i, type in enumerate(self.limbType):
            cmds.setDrivenKeyframe(self.fkCtrlList[i]+'.visibility', currentDriver=self.switchCtrl+'.FK_IK', driverValue=0, value=1)
            cmds.setDrivenKeyframe(self.fkCtrlList[i]+'.visibility', currentDriver=self.switchCtrl+'.FK_IK', driverValue=1, value=0)

        cmds.setDrivenKeyframe(self.ikCtrlName+'.visibility', currentDriver=self.switchCtrl+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ikCtrlName+'.visibility', currentDriver=self.switchCtrl+'.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.ikPoleName+'.visibility', currentDriver=self.switchCtrl+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ikPoleName+'.visibility', currentDriver=self.switchCtrl+'.FK_IK', driverValue=0, value=0)

        #--- FK Setup ---#
        for i, type in enumerate(self.limbType): cmds.orientConstraint(self.fkCtrlList[i], self.fkJntList[i], mo=True)
        cmds.setAttr(self.fkJntList[0]+'.visibility', 0)

        #--- IK Setup ---#
        # Set Preferred Angles #
        middleIkJnt = self.ikJntList[1]
        if self.direction == 'Vertical':
            cmds.rotate(0, 0, -20, middleIkJnt, relative=True)
            cmds.joint(middleIkJnt, edit=True, ch=True, setPreferredAngles=True)
            cmds.rotate(0, 0, 20, middleIkJnt, relative=True)
        else:
            if self.side == 'L':
                cmds.rotate(0, 0, 20, middleIkJnt, relative=True)
                cmds.joint(middleIkJnt, edit=True, ch=True, setPreferredAngles=True)
                cmds.rotate(0, 0, -20, middleIkJnt, relative=True)
            elif self.side == 'R':
                cmds.rotate(0, 0, 20, middleIkJnt, relative=True)
                cmds.joint(middleIkJnt, edit=True, ch=True, setPreferredAngles=True)
                cmds.rotate(0, 0, -20, middleIkJnt, relative=True)
        cmds.setAttr(self.ikJntList[0]+'.visibility', 0)

        # IK Handle #
        ikHandle = cmds.ikHandle(startJoint=self.ikJntList[0], endEffector=self.ikJntList[-1], name='{}_ikhandle'.format(self.name), solver='ikRPsolver')[0]
        cmds.pointConstraint(self.ikCtrlName, ikHandle, mo=True)
        cmds.orientConstraint(self.ikCtrlName, self.ikJntList[-1], mo=True)
        cmds.poleVectorConstraint(self.ikPoleName, ikHandle)
        cmds.aimConstraint(middleIkJnt, self.ikPoleName, mo=True)
        cmds.setAttr(ikHandle+'.visibility', 0)

        #--- Cleanup ---#
        cmds.pointConstraint(self.switchCtrl, self.ikJntList[0], mo=True)
        cmds.pointConstraint(self.switchCtrl, self.fkJntList[0], mo=True)
        outliner.batch_parent([self.ikOffsetName, self.ikPoleName, self.fkOffsetList[0], ikHandle], self.switchCtrl)

    def lockCtrl(self):
        fkMidCtrl = cmds.ls(self.fkCtrlList[1], transforms=True)[0]
        if self.direction == 'Horizontal':
            cmds.setAttr(fkMidCtrl+'.rz', l=True, k=0)
            cmds.setAttr(fkMidCtrl+'.rx', l=True, k=0)
        else:
            cmds.setAttr(fkMidCtrl+'.rz', l=True, k=0)
            cmds.setAttr(fkMidCtrl+'.ry', l=True, k=0)

    def ikSnap(self):
        """ Snap IK joint to FK joint"""
        fkRootPos = cmds.xform(self.fkJntList[0], ws=True, q=True, t=True)
        fkMidPos = cmds.xform(self.fkJntList[1], ws=True, q=True, t=True)
        fkTopPos = cmds.xform(self.fkJntList[-1], ws=True, q=True, t=True)
        fkTopRot = cmds.xform(self.fkJntList[-1], ws=True, q=True, ro=True)

        fkRootVec = om.MVector(fkRootPos[0], fkRootPos[1], fkRootPos[2])
        fkMidVec = om.MVector(fkMidPos[0], fkMidPos[1], fkMidPos[2])
        fkTopVec = om.MVector(fkTopPos[0], fkTopPos[1], fkTopPos[2])

        midPointVec = (fkRootVec + fkTopVec) / 2
        poleDir = fkMidVec - midPointVec
        polePos = fkMidVec + poleDir

        ikCtrlPos = cmds.xform(self.ikCtrlName, ws=True, q=True, sp=True)
        pvCtrlPos = cmds.xform(self.ikPoleName, ws=True, q=True, sp=True)

        cmds.rotate(fkTopRot[0], fkTopRot[1], fkTopRot[2], self.ikCtrlName)
        cmds.move(fkTopPos[0]-ikCtrlPos[0], fkTopPos[1]-ikCtrlPos[1], fkTopPos[2]-ikCtrlPos[2], self.ikCtrlName, relative=True)
        cmds.move(polePos[0]-pvCtrlPos[0], polePos[1]-pvCtrlPos[1], polePos[2]-pvCtrlPos[2], self.ikPoleName, relative=True)

    def fkSnap(self):
        """ Snap FK joint to IK joint"""
        ikRootRot = cmds.xform(self.ikJntList[0], os=True, q=True, ro=True)
        ikMidRot = cmds.xform(self.ikJntList[1], os=True, q=True, ro=True)
        ikTopRot = cmds.xform(self.ikJntList[-1], os=True, q=True, ro=True)

        cmds.rotate(ikRootRot[0], ikRootRot[1], ikRootRot[2], self.fkCtrlList[0])
        cmds.rotate(ikMidRot[0], ikMidRot[1], ikMidRot[2], self.fkCtrlList[1])
        cmds.rotate(ikTopRot[0], ikTopRot[1], ikTopRot[2], self.fkCtrlList[-1])
