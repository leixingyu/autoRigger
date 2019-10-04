import maya.cmds as cmds
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
        limbRoot = cmds.spaceLocator(n=self.locName+self.limbNameSpace[0])
        cmds.parent(limbRoot, grp, relative=True)
        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], limbRoot, relative=True)
        cmds.scale(self.scale, self.scale, self.scale, limbRoot)

        # middle
        limbMid = cmds.spaceLocator(n=self.locName+self.limbNameSpace[1])
        cmds.parent(limbMid, limbRoot, relative=True)
        cmds.move(self.interval*sideFactor*hFactor, -self.interval*vFactor, 0, limbMid, relative=True)  # move limb joint along +x axis

        # top
        limbTop = cmds.spaceLocator(n=self.locName+self.limbNameSpace[2])
        cmds.parent(limbTop, limbMid, relative=True)
        cmds.move(self.interval * sideFactor * hFactor, -self.interval * vFactor, 0, limbTop, relative=True)  # move limb joint along +x axis

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
        return cmds.ls(self.rootJntName)

    def placeCtrl(self):
        self.setCtrlShape()

        # getting locators' position
        rootPos = cmds.xform(self.rootJntName, q=True, t=True, ws=True)
        midPos = cmds.xform(self.midJntName, q=True, t=True, ws=True)
        topPos = cmds.xform(self.topJntName, q=True, t=True, ws=True)

        '''FK Setup'''
        # placing ctrls to the locators' position
        rootFkCtrl = cmds.duplicate('LimbFK_tempShape', name=self.rootCtrlName+'FK')[0]
        cmds.move(rootPos[0], rootPos[1], rootPos[2], rootFkCtrl, absolute=True)
        if self.vertical:  # rotate ctrl if vertical
            cmds.rotate(0, 0, 90, rootFkCtrl)
        cmds.makeIdentity(rootFkCtrl, apply=True, t=1, r=1, s=1)

        midFkCtrl = cmds.duplicate('LimbFK_tempShape', name=self.midCtrlName+'FK')[0]
        cmds.move(midPos[0], midPos[1], midPos[2], midFkCtrl, absolute=True)
        if self.vertical:
            cmds.rotate(0, 0, 90, midFkCtrl)
        cmds.makeIdentity(midFkCtrl, apply=True, t=1, r=1, s=1)

        topFkCtrl = cmds.duplicate('LimbFK_tempShape', name=self.topCtrlName+'FK')[0]
        cmds.move(topPos[0], topPos[1], topPos[2], topFkCtrl, absolute=True)
        if self.vertical:
            cmds.rotate(0, 0, 90, topFkCtrl)
        cmds.makeIdentity(topFkCtrl, apply=True, t=1, r=1, s=1)

        # for non-Tpose
        '''
        fkOffsetGrp = cmds.group(em=True, name=self.ctrlOffsetGrpName+self.limbNameSpace[0]+'FK')
        cmds.move(rootPos[0], rootPos[1], rootPos[2], fkOffsetGrp, absolute=True)
        cmds.parent(fkCtrl, fkOffsetGrp, absolute=True)
        '''

        cmds.parent(topFkCtrl, midFkCtrl)
        cmds.parent(midFkCtrl, rootFkCtrl)

        '''IK Setup'''
        ikCtrl = cmds.duplicate('LimbIK_tempShape', name=self.ctrlName+'IK')[0]
        cmds.move(topPos[0], topPos[1], topPos[2], ikCtrl, absolute=True)
        if self.vertical: cmds.rotate(0, 0, 90, ikCtrl)
        cmds.makeIdentity(ikCtrl, apply=True, t=1, r=1, s=1)

        poleVCtrl = cmds.duplicate('LimbIKPole_tempShape', name=self.ctrlName+'PoleVector')
        if self.vertical: cmds.move(midPos[0], midPos[1], midPos[2]+3, poleVCtrl, absolute=True)
        elif self.horizontal:
            cmds.move(midPos[0], midPos[1], midPos[2]-3, poleVCtrl, absolute=True)
            cmds.rotate(0, 180, 0, poleVCtrl, relative=True)
        cmds.makeIdentity(ikCtrl, apply=True, t=1, r=1, s=1)

        '''IK/FK Switch Setup'''
        switchCtrl = cmds.duplicate('Switch_tempShape', name=self.ctrlName+'IKFK_Switch')[0]
        if self.vertical: cmds.move(rootPos[0], rootPos[1], rootPos[2], switchCtrl, absolute=True)
        elif self.horizontal:
            cmds.move(rootPos[0], rootPos[1], rootPos[2], switchCtrl, absolute=True)
            cmds.rotate(0, 0, 90, switchCtrl, relative=True)
        cmds.addAttr(switchCtrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=True)
        cmds.makeIdentity(switchCtrl, apply=True, t=1, r=1, s=1)

        self.deleteShape()
        cmds.parent(switchCtrl, self.ctrlGrp)

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
            cmds.rotate(40, 0, 0, self.midJntName+'IK', relative=True)
            cmds.joint(self.midJntName+'IK', edit=True, ch=True, setPreferredAngles=True)
            cmds.rotate(-40, 0, 0, self.midJntName+'IK', relative=True)
        else:
            if self.side == 'L':
                cmds.rotate(0, 20, 0, self.midJntName+'IK', relative=True)
                cmds.joint(self.midJntName+'IK', edit=True, ch=True, setPreferredAngles=True)
                cmds.rotate(0, -20, 0, self.midJntName+'IK', relative=True)
            elif self.side == 'R':
                cmds.rotate(0, -20, 0, self.midJntName+'IK', relative=True)
                cmds.joint(self.midJntName+'IK', edit=True, ch=True, setPreferredAngles=True)
                cmds.rotate(0, 20, 0, self.midJntName+'IK', relative=True)
        ikHandle = cmds.ikHandle(startJoint=self.rootJntName+'IK', endEffector=self.topJntName+'IK', name=self.prefix+'_IK'+self.name, solver='ikRPsolver')[0]

        cmds.pointConstraint(self.ctrlName+'IK', ikHandle, mo=True)
        cmds.orientConstraint(self.ctrlName+'IK', self.topJntName+'IK', mo=True)
        cmds.poleVectorConstraint(self.ctrlName+'PoleVector', ikHandle)

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
        cmds.pointConstraint(self.ctrlName+'IKFK_Switch', self.rootJntName+'FK')
        cmds.pointConstraint(self.ctrlName+'IKFK_Switch', self.rootJntName+'IK')

        misc.batchParent([self.ctrlName+'IK', self.ctrlName+'PoleVector', self.rootCtrlName+'FK', self.prefix+'_IK'+self.name], self.ctrlName+'IKFK_Switch')

        # set visibility
        cmds.setAttr(self.rootJntName+'FK.visibility', 0)
        cmds.setAttr(self.rootJntName+'IK.visibility', 0)
        cmds.setAttr(ikHandle+'.visibility', 0)
