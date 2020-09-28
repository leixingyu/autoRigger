import maya.cmds as cmds
import base

class Finger(base.Base):
    def __init__(self, side, id, type='Other'):
        base.Base.__init__(self, side, id)
        self.metaType = 'Finger'
        self.segment = 4
        self.type = type
        self.createNaming()
        self.createSecondaryNaming()

    def createSecondaryNaming(self):
        self.locList, self.jntList, self.ctrlList, self.ctrlOffsetList = ([] for i in range(4))  # ik has different ctrl name
        for i in range(self.segment):
            self.locList.append('{}{}_loc'.format(self.name, i))
            self.jntList.append('{}{}_jnt'.format(self.name, i))
            self.ctrlList.append('{}{}_ctrl'.format(self.name, i))
            self.ctrlOffsetList.append('{}{}_offset'.format(self.name, i))

    def setCtrlShape(self):
        #--- Finger Shape ---#
        fingerShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=6, name='Finger_tempShape')
        cmds.select('Finger_tempShape.cv[3]', 'Finger_tempShape.cv[5]')
        cmds.scale(0.2, 0.2, 0.2, relative=True)
        cmds.select('Finger_tempShape.cv[1]', 'Finger_tempShape.cv[4]')
        cmds.move(0, 0, 1, relative=True)
        cmds.scale(0.2, 0.2, 0.4, fingerShape)
        cmds.rotate(90, 0, 0, fingerShape)

        #--- Thumb Shape ---#
        thumbShape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='Thumb_tempShape')
        cmds.scale(0.2, 0.2, 0.2, thumbShape)

    def setLocAttr(self, startPos=[0, 0, 0], interval=0.5, scale=0.2):
        self.startPos = startPos
        self.interval = interval
        self.scale = scale

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        for i in range(self.segment):
            finger = cmds.spaceLocator(n=self.locList[i])
            if i is 0:  # root locator of finger parent to the locator group
                cmds.parent(finger, grp, relative=True)
                cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], finger, absolute=True)
                cmds.scale(self.scale, self.scale, self.scale, finger)
            else:  # non-root locator parent to the previous locator
                cmds.parent(finger, self.locList[i-1], relative=True)
                if self.side == 'L': cmds.move(self.interval, 0, 0, finger, relative=True)  # move finger locator along +x axis
                elif self.side == 'R': cmds.move(-self.interval, 0, 0, finger, relative=True)  # move finger locator along -x axis

        cmds.parent(grp, self.locGrp)
        self.colorLoc()
        cmds.select(clear=True)
        return grp

    def constructJnt(self):
        cmds.select(clear=True)
        for i, loc in enumerate(self.locList):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntList[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        cmds.parent(self.jntList[0], self.jntGrp)
        return cmds.ls(self.jntList[0])

    def placeCtrl(self):
        self.setCtrlShape()

        for i in range(self.segment-1):
            jntPos = cmds.xform(self.jntList[i], q=True, t=True, ws=True)
            jntRot = cmds.xform(self.jntList[i], q=True, ro=True, ws=True)

            if self.type != 'Thumb':
                ctrl = cmds.duplicate('Finger_tempShape', name=self.ctrlList[i])[0]
                cmds.move(jntPos[0], jntPos[1]+1, jntPos[2], ctrl)
                cmds.move(jntPos[0], jntPos[1], jntPos[2], ctrl+'.rotatePivot', ctrl+'.scalePivot')
            else:
                ctrl = cmds.duplicate('Thumb_tempShape', name=self.ctrlList[i])[0]
                cmds.move(jntPos[0], jntPos[1], jntPos[2], ctrl)

            offsetGrp = cmds.group(em=True, name=self.ctrlOffsetList[i])
            cmds.move(jntPos[0], jntPos[1], jntPos[2], offsetGrp)
            cmds.parent(ctrl, offsetGrp)
            cmds.rotate(jntRot[0], jntRot[1], jntRot[2], offsetGrp)
            cmds.makeIdentity(ctrl, apply=True, t=1, r=1, s=1)

            if i == 0:
                cmds.parent(offsetGrp, self.ctrlGrp)
            elif i != 0:
                cmds.parent(offsetGrp, self.ctrlList[i-1])

        self.deleteShape()
        return cmds.ls(self.ctrlOffsetList[0])

    def addConstraint(self):
        for i in range(self.segment-1):
            ctrl = cmds.ls(self.ctrlList[i])[0]
            jnt  = cmds.ls(self.jntList[i])
            cmds.orientConstraint(ctrl, jnt, mo=True)

    def lockCtrl(self):
        if self.type != 'Thumb':
            for ctrl in self.ctrlList:
                if ctrl not in self.ctrlOffsetList:
                    for transform in 's':
                        for axis in 'xyz':
                            cmds.setAttr('{}.{}{}'.format(ctrl, transform, axis), l=True, k=0)
                    cmds.setAttr(ctrl+'.rx', l=1, k=0)