import maya.cmds as cmds
import maya.OpenMaya as om
import base
import misc

class Limb(base.Base):
    def __init__(self, prefix, side, id, type='Null'):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Limb'

        self.setArmLeg(type)
        self.constructNameSpace(self.metaType)
        self.constructSecNameSpace()

        '''default locator attribute'''
        self.setLocAttr([0, 0, 0], 2)

    '''
    Identify the limb type ('Arm' or 'Leg')
    '''
    def setArmLeg(self, limb):
        self.horizontal = True
        self.vertical = False
        if limb == 'Arm':
            self.limbNameSpace = ['Shoulder', 'Elbow', 'Wrist']
        elif limb == 'Leg':
            self.limbNameSpace = ['Clavicle', 'Knee', 'Ankle']
            self.vertical = True
            self.horizontal = False
        else:
            self.limbNameSpace = ['Root', 'Middle', 'Top']

    '''
    Construct secondary namespace to further simplify naming
    '''
    def constructSecNameSpace(self):
        self.rootLocName = self.locName+self.limbNameSpace[0]
        self.midLocName = self.locName+self.limbNameSpace[1]
        self.topLocName = self.locName+self.limbNameSpace[2]
        
        self.rootJntName = self.jntName + self.limbNameSpace[0]
        self.midJntName = self.jntName + self.limbNameSpace[1]
        self.topJntName = self.jntName + self.limbNameSpace[2]

        self.rootCtrlName = self.ctrlName + self.limbNameSpace[0]
        self.midCtrlName = self.ctrlName + self.limbNameSpace[1]
        self.topCtrlName = self.ctrlName + self.limbNameSpace[2]

    '''
    Set locator attribute
    '''
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

        arrorPtList = [[2.0, 0.0, 2.0], [2.0, 0.0, 1.0], [3.0, 0.0, 1.0], [3.0, 0.0, 2.0], [5.0, 0.0, 0.0], [3.0, 0.0, -2.0], [3.0, 0.0, -1.0], [2.0, 0.0, -1.0],
                       [2.0, 0.0, -2.0], [1.0, 0.0, -2.0], [1.0, 0.0, -3.0], [2.0, 0.0, -3.0], [0.0, 0.0, -5.0], [-2.0, 0.0, -3.0], [-1.0, 0.0, -3.0], [-1.0, 0.0, -2.0],
                       [-2.0, 0.0, -2.0], [-2.0, 0.0, -1.0], [-3.0, 0.0, -1.0], [-3.0, 0.0, -2.0], [-5.0, 0.0, 0.0], [-3.0, 0.0, 2.0], [-3.0, 0.0, 1.0], [-2.0, 0.0, 1.0],
                       [-2.0, 0.0, 2.0], [-1.0, 0.0, 2.0], [-1.0, 0.0, 3.0], [-2.0, 0.0, 3.0], [0.0, 0.0, 5.0], [2.0, 0.0, 3.0], [1.0, 0.0, 3.0], [1.0, 0.0, 2.0], [2.0, 0.0, 2.0]]
        switchShape = cmds.curve(p=arrorPtList, degree=1, name='Switch_tempShape')
        cmds.scale(0.3, 0.3, 0.3, switchShape)

    '''
    Create locators
    '''
    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        sideFactor = 1
        hFactor, vFactor = 1, 0

        if self.side == 'R': sideFactor = -1
        if self.vertical == True:
            hFactor, vFactor = 0, 1

        # root
        limbRoot = cmds.spaceLocator(n=self.rootLocName)
        cmds.parent(limbRoot, grp, relative=True)
        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], limbRoot, relative=True)
        cmds.scale(self.scale, self.scale, self.scale, limbRoot)

        # middle
        limbMid = cmds.spaceLocator(n=self.midLocName)
        cmds.parent(limbMid, limbRoot, relative=True)
        cmds.move(self.interval*sideFactor*hFactor, -self.interval*vFactor, 0, limbMid, relative=True)  # move limb joint along +x axis

        # top
        limbTop = cmds.spaceLocator(n=self.topLocName)
        cmds.parent(limbTop, limbMid, relative=True)
        cmds.move(self.interval * sideFactor * hFactor, -self.interval * vFactor, 0, limbTop, relative=True)  # move limb joint along +x axis

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    '''
    Create joint based on the locators
    
    TODO: simplify this, seems redundant
    '''
    def constructJnt(self):
        # create result joint
        cmds.select(clear=True)
        for name in self.limbNameSpace:
            loc = cmds.ls(self.locName+name, transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntName+name)
            cmds.setAttr(jnt+'.radius', 1)

        # create fk joint
        cmds.select(clear=True)
        for name in self.limbNameSpace:
            loc = cmds.ls(self.locName + name, transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            fkJnt = cmds.joint(p=locPos, name=self.jntName+name+'FK')
            cmds.setAttr(fkJnt+'.radius', 1)

        # create ik joint
        cmds.select(clear=True)
        for name in self.limbNameSpace:
            loc = cmds.ls(self.locName + name, transforms=True)
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            ikJnt = cmds.joint(p=locPos, name=self.jntName+name+'IK')
            cmds.setAttr(ikJnt+'.radius', 1)

        misc.batchParent([self.rootJntName, self.rootJntName+'IK', self.rootJntName+'FK'], self.jntGrp)
        misc.orientJnt([self.rootJntName, self.rootJntName+'IK', self.rootJntName+'FK'])
        return cmds.ls(self.rootJntName)

    def placeCtrl(self):
        self.setCtrlShape()

        # getting locators' position
        rootPos = cmds.xform(self.rootJntName, q=True, t=True, ws=True)
        midPos = cmds.xform(self.midJntName, q=True, t=True, ws=True)
        topPos = cmds.xform(self.topJntName, q=True, t=True, ws=True)

        # getting locators' rotation
        rootRot = cmds.xform(self.rootLocName, q=True, ro=True, ws=True)
        midRot = cmds.xform(self.midLocName, q=True, ro=True, ws=True)
        topRot = cmds.xform(self.topLocName, q=True, ro=True, ws=True)

        '''FK Setup'''
        # placing ctrls to the locators' position
        rootFkCtrl = cmds.duplicate('LimbFK_tempShape', name=self.rootCtrlName+'FK')[0]
        cmds.move(rootPos[0], rootPos[1], rootPos[2], rootFkCtrl, absolute=True)
        if self.vertical:  # rotate ctrl if vertical
            cmds.rotate(0, 0, 90, rootFkCtrl)
            
        rootOffset = cmds.group(em=True, name=self.rootCtrlName+'FKoffset')
        cmds.move(rootPos[0], rootPos[1], rootPos[2], rootOffset)
        cmds.parent(rootFkCtrl, rootOffset)
        cmds.rotate(rootRot[0], rootRot[1], rootRot[2], rootOffset)
        cmds.makeIdentity(rootFkCtrl, apply=True, t=1, r=1, s=1)

        midFkCtrl = cmds.duplicate('LimbFK_tempShape', name=self.midCtrlName+'FK')[0]
        cmds.move(midPos[0], midPos[1], midPos[2], midFkCtrl, absolute=True)
        if self.vertical:
            cmds.rotate(0, 0, 90, midFkCtrl)
            
        midOffset = cmds.group(em=True, name=self.midCtrlName+'FKoffset')
        cmds.move(midPos[0], midPos[1], midPos[2], midOffset)
        cmds.parent(midFkCtrl, midOffset)
        cmds.rotate(midRot[0], midRot[1], midRot[2], midOffset)
        cmds.makeIdentity(midFkCtrl, apply=True, t=1, r=1, s=1)

        topFkCtrl = cmds.duplicate('LimbFK_tempShape', name=self.topCtrlName+'FK')[0]
        cmds.move(topPos[0], topPos[1], topPos[2], topFkCtrl, absolute=True)
        if self.vertical:
            cmds.rotate(0, 0, 90, topFkCtrl)

        topOffset = cmds.group(em=True, name=self.topCtrlName+'FKoffset')
        cmds.move(topPos[0], topPos[1], topPos[2], topOffset)
        cmds.parent(topFkCtrl, topOffset)
        cmds.rotate(topRot[0], topRot[1], topRot[2], topOffset)
        cmds.makeIdentity(topFkCtrl, apply=True, t=1, r=1, s=1)

        cmds.parent(topOffset, midFkCtrl)
        cmds.parent(midOffset, rootFkCtrl)

        '''IK Setup'''
        ikCtrl = cmds.duplicate('LimbIK_tempShape', name=self.ctrlName+'IK')[0]
        cmds.move(topPos[0], topPos[1], topPos[2], ikCtrl, absolute=True)
        if self.vertical: cmds.rotate(0, 0, 90, ikCtrl)

        offsetGrp = cmds.group(em=True, name=self.ctrlName+'IKoffset')
        cmds.move(topPos[0], topPos[1], topPos[2], offsetGrp)
        cmds.parent(ikCtrl, offsetGrp)
        cmds.rotate(topRot[0], topRot[1], topRot[2], offsetGrp)
        cmds.makeIdentity(ikCtrl, apply=True, t=1, r=1, s=1)

        poleVCtrl = cmds.duplicate('LimbIKPole_tempShape', name=self.ctrlName+'PoleVector')
        if self.vertical: cmds.move(midPos[0], midPos[1], midPos[2]+3, poleVCtrl, absolute=True)
        elif self.horizontal:
            cmds.move(midPos[0], midPos[1], midPos[2]-3, poleVCtrl, absolute=True)
            cmds.rotate(0, 180, 0, poleVCtrl, relative=True)
        cmds.makeIdentity(poleVCtrl, apply=True, t=1, r=1, s=1)

        '''IK/FK Switch Setup'''
        self.switchCtrl = cmds.duplicate('Switch_tempShape', name=self.ctrlName+'IKFK_Switch')[0]
        if self.vertical: cmds.move(rootPos[0], rootPos[1], rootPos[2], self.switchCtrl, absolute=True)
        elif self.horizontal:
            cmds.move(rootPos[0], rootPos[1], rootPos[2], self.switchCtrl, absolute=True)
            cmds.rotate(0, 0, 90, self.switchCtrl, relative=True)
        cmds.addAttr(self.switchCtrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=True)

        offsetGrp = cmds.group(em=True, name=self.ctrlName+'IKFK_Switchoffset')
        cmds.move(rootPos[0], rootPos[1], rootPos[2], offsetGrp)
        cmds.parent(self.switchCtrl, offsetGrp)
        cmds.rotate(rootRot[0], rootRot[1], rootRot[2], offsetGrp)
        cmds.makeIdentity(self.switchCtrl, apply=True, t=1, r=1, s=1)

        self.deleteShape()
        cmds.parent(offsetGrp, self.ctrlGrp)

    def addConstraint(self):

        '''Result Joint'''
        cmds.parentConstraint(self.rootJntName+'IK', self.rootJntName+'FK', self.rootJntName)
        cmds.orientConstraint(self.midJntName+'IK', self.midJntName+'FK', self.midJntName)
        cmds.orientConstraint(self.topJntName+'IK', self.topJntName+'FK', self.topJntName)

        cmds.setDrivenKeyframe(self.rootJntName+'_parentConstraint1.'+self.rootJntName+'IKW0', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.rootJntName+'_parentConstraint1.'+self.rootJntName+'FKW1', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.rootJntName+'_parentConstraint1.'+self.rootJntName+'IKW0', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.rootJntName+'_parentConstraint1.'+self.rootJntName+'FKW1', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=1)

        cmds.setDrivenKeyframe(self.midJntName+'_orientConstraint1.'+self.midJntName+'IKW0', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.midJntName+'_orientConstraint1.'+self.midJntName+'FKW1', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.midJntName+'_orientConstraint1.'+self.midJntName+'IKW0', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.midJntName+'_orientConstraint1.'+self.midJntName+'FKW1', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=1)

        cmds.setDrivenKeyframe(self.topJntName+'_orientConstraint1.'+self.topJntName+'IKW0', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.topJntName+'_orientConstraint1.'+self.topJntName+'FKW1', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.topJntName+'_orientConstraint1.'+self.topJntName+'IKW0', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.topJntName+'_orientConstraint1.'+self.topJntName+'FKW1', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=1)

        '''FK Setup'''
        cmds.orientConstraint(self.rootCtrlName+'FK', self.rootJntName+'FK', mo=True)
        cmds.orientConstraint(self.midCtrlName+'FK', self.midJntName+'FK', mo=True)
        cmds.orientConstraint(self.topCtrlName+'FK', self.topJntName+'FK', mo=True)

        '''IK Setup'''
        if self.vertical:
            cmds.rotate(0, 0, -20, self.midJntName+'IK', relative=True)
            cmds.joint(self.midJntName+'IK', edit=True, ch=True, setPreferredAngles=True)
            cmds.rotate(0, 0, 20, self.midJntName+'IK', relative=True)
        else:
            if self.side == 'L':
                cmds.rotate(0, 0, 20, self.midJntName+'IK', relative=True)
                cmds.joint(self.midJntName+'IK', edit=True, ch=True, setPreferredAngles=True)
                cmds.rotate(0, 0, -20, self.midJntName+'IK', relative=True)
            elif self.side == 'R':
                cmds.rotate(0, 0, 20, self.midJntName+'IK', relative=True)
                cmds.joint(self.midJntName+'IK', edit=True, ch=True, setPreferredAngles=True)
                cmds.rotate(0, 0, -20, self.midJntName+'IK', relative=True)

        # build IK
        ikHandle = cmds.ikHandle(startJoint=self.rootJntName+'IK', endEffector=self.topJntName+'IK', name=self.prefix+'_IK'+self.name, solver='ikRPsolver')[0]

        cmds.pointConstraint(self.ctrlName+'IK', ikHandle, mo=True)
        cmds.orientConstraint(self.ctrlName+'IK', self.topJntName+'IK', mo=True)
        cmds.poleVectorConstraint(self.ctrlName+'PoleVector', ikHandle)
        cmds.aimConstraint(self.midJntName+'IK', self.ctrlName+'PoleVector', mo=True)

        '''IK/FK Switch'''

        # IK visiblity
        cmds.setDrivenKeyframe(self.ctrlName+'IK.visibility', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ctrlName+'PoleVector.visibility', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ctrlName+'IK.visibility', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.ctrlName+'PoleVector.visibility', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=0)

        # FK visiblity
        cmds.setDrivenKeyframe(self.rootCtrlName+'FK.visibility', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe(self.midCtrlName+'FK.visibility', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe(self.topCtrlName+'FK.visibility', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=1)
        cmds.setDrivenKeyframe(self.rootCtrlName+'FK.visibility', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.midCtrlName+'FK.visibility', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.topCtrlName+'FK.visibility', currentDriver=self.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=0)

        '''Other constraints'''

        # parent controller
        cmds.pointConstraint(self.ctrlName+'IKFK_Switch', self.rootJntName+'FK', mo=True)
        cmds.pointConstraint(self.ctrlName+'IKFK_Switch', self.rootJntName+'IK', mo=True)

        misc.batchParent([self.ctrlName+'IKoffset', self.ctrlName+'PoleVector', self.rootCtrlName+'FKoffset', self.prefix+'_IK'+self.name], self.ctrlName+'IKFK_Switch')

        # set visibility
        cmds.setAttr(self.rootJntName+'FK.visibility', 0)
        cmds.setAttr(self.rootJntName+'IK.visibility', 0)
        cmds.setAttr(ikHandle+'.visibility', 0)

    def lockCtrl(self):
        fkMidCtrl = cmds.ls(self.midCtrlName+'FK', transforms=True)[0]
        if self.horizontal:
            cmds.setAttr(fkMidCtrl+'.rz', l=True, k=0)
            cmds.setAttr(fkMidCtrl+'.rx', l=True, k=0)
        else:
            cmds.setAttr(fkMidCtrl+'.rz', l=True, k=0)
            cmds.setAttr(fkMidCtrl+'.ry', l=True, k=0)

    '''
    Snap IK joints to FK joints
    '''
    def ikSnap(self):
        fkRootPos = cmds.xform(self.rootJntName+'FK', ws=True, q=True, t=True)
        fkMidPos = cmds.xform(self.midJntName+'FK', ws=True, q=True, t=True)
        fkTopPos = cmds.xform(self.topJntName+'FK', ws=True, q=True, t=True)
        fkTopRot = cmds.xform(self.topJntName+'FK', ws=True, q=True, ro=True)

        fkRootVec = om.MVector(fkRootPos[0], fkRootPos[1], fkRootPos[2])
        fkMidVec = om.MVector(fkMidPos[0], fkMidPos[1], fkMidPos[2])
        fkTopVec = om.MVector(fkTopPos[0], fkTopPos[1], fkTopPos[2])

        midPointVect = (fkRootVec + fkTopVec)/2
        poleDir = fkMidVec - midPointVect
        polePos = fkMidVec + poleDir

        ikCtrlPos = cmds.xform(self.ctrlName+'IK', ws=True, q=True, sp=True)
        pvCtrlPos = cmds.xform(self.ctrlName+'PoleVector', ws=True, q=True, sp=True)

        cmds.rotate(fkTopRot[0], fkTopRot[1], fkTopRot[2], self.ctrlName+'IK')
        cmds.move(fkTopPos[0]-ikCtrlPos[0], fkTopPos[1]-ikCtrlPos[1], fkTopPos[2]-ikCtrlPos[2], self.ctrlName+'IK', relative=True)
        cmds.move(polePos[0]-pvCtrlPos[0], polePos[1]-pvCtrlPos[1], polePos[2]-pvCtrlPos[2], self.ctrlName+'PoleVector', relative=True)

    '''
    Snap FK joints to IK joints
    '''
    def fkSnap(self):
        ikRootRot = cmds.xform(self.rootJntName+'IK', os=True, q=True, ro=True)
        ikMidRot = cmds.xform(self.midJntName+'IK', os=True, q=True, ro=True)
        ikTopRot = cmds.xform(self.topJntName+'IK', os=True, q=True, ro=True)

        cmds.rotate(ikRootRot[0], ikRootRot[1], ikRootRot[2], self.rootCtrlName+'FK')
        cmds.rotate(ikMidRot[0], ikMidRot[1], ikMidRot[2], self.midCtrlName+'FK')
        cmds.rotate(ikTopRot[0], ikTopRot[1], ikTopRot[2], self.topCtrlName+'FK')
