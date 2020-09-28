import maya.cmds as cmds
import base, util

class Tail(base.Base):
    def __init__(self, side, id):
        self.segment = 6
        base.Base.__init__(self, side, id)
        self.metaType = 'Tail'
        self.createNaming()
        self.createSecondaryNaming()

    def createSecondaryNaming(self):
        self.locList, self.jntList, self.ikJntList, self.fkJntList,\
        self.fkCtrlList, self.ikCtrlList, self.fkOffsetList,\
        self.clusterList, self.ikOffsetList = ([] for i in range(9))  # ik has different ctrl name
        for i in range(self.segment):
            self.locList.append('{}{}_loc'.format(self.name, i))
            self.jntList.append('{}{}_jnt'.format(self.name, i))
            self.fkJntList.append('{}{}fk_jnt'.format(self.name, i))
            self.ikJntList.append('{}{}ik_jnt'.format(self.name, i))
            self.fkCtrlList.append('{}{}fk_ctrl'.format(self.name, i))
            self.ikCtrlList.append('{}{}ik_ctrl'.format(self.name, i))
            self.fkOffsetList.append('{}{}fk_offset'.format(self.name, i))
            self.ikOffsetList.append('{}{}ik_offset'.format(self.name, i))
            self.clusterList.append('{}{}_cluster'.format(self.name, i))

        self.masterCtrl = '{}master_ctrl'.format(self.name)
        self.ikCurve = '{}ik_curve'.format(self.name)
        self.tailIK = '{}_ik'.format(self.name)

    def setCtrlShape(self):
        sphere = cmds.createNode('implicitSphere')
        sphereCtrl = cmds.rename(cmds.listRelatives(sphere, p=True), 'TailIK_tempShape')
        cmds.scale(0.2, 0.2, 0.2, sphereCtrl)

        ctrlShape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=8, name='TailFK_tempShape')
        cmds.scale(0.3, 0.3, 0.3, ctrlShape)

    def setLocAttr(self, startPos=[0, 6, -4], length=4.0, scale=0.4):
        self.startPos = startPos
        self.interval = length / (self.segment-1)
        self.scale = scale

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        for i in range(self.segment):
            tail = cmds.spaceLocator(n=self.locList[i])
            # root locator of tail parent to the tail group
            if i is 0:
                cmds.parent(tail, grp, relative=True)
                cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], tail, absolute=True)
                cmds.scale(self.scale, self.scale, self.scale, tail)
            # tail locator parent to the previous locator
            else:
                cmds.parent(tail, self.locList[i-1], relative=True)
                cmds.move(0, -self.interval, 0, tail, relative=True)  # move tail locator along -y axis

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        # result jnt
        cmds.select(clear=True)
        for i, loc in enumerate(self.locList):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntList[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        # ik jnt
        cmds.select(clear=True)
        for i, loc in enumerate(self.locList):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.ikJntList[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        # fk jnt
        cmds.select(clear=True)
        for i, loc in enumerate(self.locList):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.fkJntList[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        #--- Cleanup ---#
        cmds.setAttr(self.fkJntList[0]+'.visibility', 0)
        cmds.setAttr(self.ikJntList[0]+'.visibility', 0)
        util.batchParent([self.jntList[0], self.fkJntList[0], self.ikJntList[0]], self.jntGrp)
        util.orientJnt([self.jntList[0], self.fkJntList[0], self.ikJntList[0]])
        return self.jntList[0]

    def placeCtrl(self):
        self.setCtrlShape()

        #--- Master control ---#
        cmds.duplicate('TailIK_tempShape', name=self.masterCtrl)
        tailPos = cmds.xform(self.jntList[0], q=True, t=True, ws=True)
        cmds.move(tailPos[0], tailPos[1], tailPos[2]-1, self.masterCtrl)
        cmds.addAttr(self.masterCtrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=True)

        #--- IK and FK control has the same setup ---#
        for i in range(self.segment):
            cmds.duplicate('TailIK_tempShape', name=self.ikCtrlList[i])
            cmds.group(em=True, name=self.ikOffsetList[i])
            cmds.duplicate('TailFK_tempShape', name=self.fkCtrlList[i])
            cmds.group(em=True, name=self.fkOffsetList[i])

        for i, tail in enumerate(self.jntList):
            tailPos = cmds.xform(tail, q=True, t=True, ws=True)
            tailRot = cmds.xform(tail, q=True, ro=True, ws=True)
            cmds.move(tailPos[0], tailPos[1], tailPos[2], self.ikOffsetList[i])
            cmds.rotate(tailRot[0], tailRot[1], tailRot[2], self.ikOffsetList[i])
            cmds.move(tailPos[0], tailPos[1], tailPos[2], self.fkOffsetList[i])
            cmds.rotate(tailRot[0], tailRot[1], tailRot[2], self.fkOffsetList[i])
        for i in range(self.segment):
            cmds.parent(self.ikCtrlList[i], self.ikOffsetList[i], relative=True)
            cmds.parent(self.fkCtrlList[i], self.fkOffsetList[i], relative=True)
            if i != 0:
                cmds.parent(self.ikOffsetList[i], self.ikCtrlList[i-1])
                cmds.parent(self.fkOffsetList[i], self.fkCtrlList[i-1])
            else:
                util.batchParent([self.ikOffsetList[i], self.fkOffsetList[i]], self.masterCtrl)

        #--- Cleanup ---#
        cmds.parent(self.masterCtrl, self.ctrlGrp)
        self.deleteShape()
        return self.masterCtrl

    def buildIK(self):
        curvePoints = []
        for i, tail in enumerate(self.ikJntList):
            tailPos = cmds.xform(tail, q=True, t=True, ws=True)
            curvePoints.append(tailPos)

        tailCurve = cmds.curve(p=curvePoints, name=self.ikCurve)
        cmds.setAttr(tailCurve+'.visibility', 0)  # hide tailCurve
        cmds.inheritTransform(tailCurve, off=True)  # turning off inherit transform avoid curve move/scale twice as much

        cvs = cmds.ls(self.ikCurve+'.cv[0:]', fl=True)
        for i, cv in enumerate(cvs):
            cluster = cmds.cluster(cv, name=self.clusterList[i])[-1]
            cmds.setAttr(cluster+'.visibility', 0)  # hide clusters

        cmds.ikHandle(startJoint=self.ikJntList[0], endEffector=self.ikJntList[self.segment-1], name=self.tailIK, curve=tailCurve, createCurve=False,
                      parentCurve=True, roc=True, solver='ikSplineSolver')
        cmds.setAttr(self.tailIK+'.visibility', 0)  # hide ik
        cmds.parent(self.tailIK, self.ctrlGrp)

    def buildFK(self):
        pass

    def addConstraint(self):
        self.buildIK()
        for i in range(self.segment):
            tailCluster = cmds.ls('{}Handle'.format(self.clusterList[i]))
            tailCtrl = cmds.ls(self.ikCtrlList[i])
            cmds.parent(tailCluster, tailCtrl)

        self.buildFK()
        for i, tailJnt in enumerate(self.fkJntList):
            tailCtrl = cmds.ls(self.fkCtrlList[i])
            cmds.parentConstraint(tailCtrl, tailJnt)

        # ik fk to result jnt
        for i in range(self.segment):
            ikTail = cmds.ls(self.ikJntList[i])
            fkTail = cmds.ls(self.fkJntList[i])
            finalTail = cmds.ls(self.jntList[i])
            cmds.parentConstraint(ikTail, fkTail, finalTail)

        # ik fk switch
        for i in range(self.segment):
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jntList[i], self.ikJntList[i]), currentDriver=self.masterCtrl+'.FK_IK', driverValue=1, value=1)
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jntList[i], self.fkJntList[i]), currentDriver=self.masterCtrl+'.FK_IK', driverValue=1, value=0)
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jntList[i], self.ikJntList[i]), currentDriver=self.masterCtrl+'.FK_IK', driverValue=0, value=0)
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jntList[i], self.fkJntList[i]), currentDriver=self.masterCtrl+'.FK_IK', driverValue=0, value=1)
    
            cmds.setDrivenKeyframe(self.ikCtrlList[i]+'.visibility', currentDriver=self.masterCtrl+'.FK_IK', driverValue=1, value=1)
            cmds.setDrivenKeyframe(self.ikCtrlList[i]+'.visibility', currentDriver=self.masterCtrl+'.FK_IK', driverValue=0, value=0)
            cmds.setDrivenKeyframe(self.fkCtrlList[i]+'.visibility', currentDriver=self.masterCtrl+'.FK_IK', driverValue=0, value=1)
            cmds.setDrivenKeyframe(self.fkCtrlList[i]+'.visibility', currentDriver=self.masterCtrl+'.FK_IK', driverValue=1, value=0)

    def lockCtrl(self):
        for ctrl in self.fkCtrlList+self.ikCtrlList+[self.masterCtrl]:
            for transform in 's':
                for axis in 'xyz':
                    cmds.setAttr('{}.{}{}'.format(ctrl, transform, axis), l=True, k=0)


