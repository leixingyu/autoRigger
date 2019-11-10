import maya.cmds as cmds
import base

class Finger(base.Base):
    def __init__(self, prefix, side, id, type='Other'):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Finger'
        self.type = type

        self.constructNameSpace(self.metaType)

        '''default locator attribute'''
        self.setLocAttr()

    '''
    Create controller shape
    '''
    def setCtrlShape(self):
        # finger shape
        fingerShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=6, name='Finger_tempShape')
        cmds.select('Finger_tempShape.cv[3]', 'Finger_tempShape.cv[5]')
        cmds.scale(0.2, 0.2, 0.2, relative=True)
        cmds.select('Finger_tempShape.cv[1]', 'Finger_tempShape.cv[4]')
        cmds.move(0, 0, 1, relative=True)
        cmds.scale(0.2, 0.2, 0.4, fingerShape)
        cmds.rotate(90, 0, 0, fingerShape)

        # thumb shape
        thumbShape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='Thumb_tempShape')
        cmds.scale(0.2, 0.2, 0.2, thumbShape)

    '''
    Set Locator attribute, locator scale default to 0.2
    '''
    def setLocAttr(self, startPos=[0, 0, 0], interval=0.5, segment=4, scale=0.2):
        self.startPos = startPos
        self.interval = interval
        self.segment = segment
        self.scale = scale

    '''
    Create Finger Locator:

    start position
        |
    [locator1]-------[locator2]-------[locator3]-------[locator4]  = total segment 4 (direction default along the x axis)
                 |
              interval
    '''
    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        for i in range(self.segment):
            finger = cmds.spaceLocator(n=self.locName+str(i))
            # root locator of finger parent to the finger group
            if i is 0:
                cmds.parent(finger, grp, relative=True)
                cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], finger, absolute=True)
                cmds.scale(self.scale, self.scale, self.scale, finger)
            # finger locator parent to the previous locator
            else:
                cmds.parent(finger, self.locName+str(i-1), relative=True)
                if self.side == 'L':
                    cmds.move(self.interval, 0, 0, finger, relative=True)  # move finger locator along +x axis
                elif self.side == 'R':
                    cmds.move(-self.interval, 0, 0, finger, relative=True)  # move finger locator along -x axis

        cmds.parent(grp, self.locGrp)
        self.colorLoc()
        cmds.select(clear=True)
        return grp

    '''
    Create Finger Joint based on the locator position
    '''
    def constructJnt(self):
        finger = cmds.ls('%s*' % self.locName, transforms=True)
        cmds.select(clear=True)

        for i, loc in enumerate(finger):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntName+str(i))
            cmds.setAttr(jnt + '.radius', self.scale)

        cmds.parent(self.jntName+'0', self.jntGrp)
        return cmds.ls(self.jntName+'0')

    '''
    Create Finger Controller and Placing it on the joint position
    '''
    def placeCtrl(self):
        self.setCtrlShape()

        for i in range(self.segment-1):
            jntPos = cmds.xform(self.jntName+str(i), q=True, t=True, ws=True)
            jntRot = cmds.xform(self.locName+str(i), q=True, ro=True, ws=True)

            if self.type != 'Thumb':
                ctrl = cmds.duplicate('Finger_tempShape', name=self.ctrlName+str(i))[0]
                cmds.move(jntPos[0], jntPos[1]+1, jntPos[2], ctrl)
                cmds.move(jntPos[0], jntPos[1], jntPos[2], ctrl+'.rotatePivot', ctrl+'.scalePivot')
            else:
                ctrl = cmds.duplicate('Thumb_tempShape', name=self.ctrlName+str(i))[0]
                cmds.move(jntPos[0], jntPos[1], jntPos[2], ctrl)

            offsetGrp = cmds.group(em=True, name=self.ctrlName+str(i)+'offset')
            cmds.move(jntPos[0], jntPos[1], jntPos[2], offsetGrp)
            cmds.parent(ctrl, offsetGrp)
            cmds.rotate(jntRot[0], jntRot[1], jntRot[2], offsetGrp)
            cmds.makeIdentity(ctrl, apply=True, t=1, r=1, s=1)
            if i == 0:
                cmds.parent(offsetGrp, self.ctrlGrp)
            elif i != 0:
                cmds.parent(offsetGrp, self.ctrlName+str(i-1))

        self.deleteShape()
        return cmds.ls(self.ctrlName+str(0)+'offset')

    '''
    Build Constraint between controller and joint
    '''
    def addConstraint(self):
        for i in range(self.segment-1):
            ctrl = cmds.ls(self.ctrlName+str(i))[0]
            jnt = cmds.ls(self.jntName+str(i))
            cmds.orientConstraint(ctrl, jnt, mo=True)

    '''
    Lock attribute translate(x,y,z), scale(x,y,z), rotate(x), thumb has full transform ability
    '''
    def lockCtrl(self):
        if self.type != 'Thumb':
            ctrls = cmds.ls(self.ctrlName+'*', transforms=True)
            offsetGrp = cmds.ls('*offset')
            for ctrl in ctrls:
                if ctrl not in offsetGrp:
                    for transform in 's':
                        for axis in 'xyz':
                            cmds.setAttr(ctrl+'.'+transform+axis, l=True, k=0)
                    cmds.setAttr(ctrl+'.rx', l=1, k=0)


