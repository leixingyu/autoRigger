import maya.cmds as cmds
import base, util

class Tail(base.Base):
    def __init__(self, prefix, side, id):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Tail'
        self.constructNameSpace(self.metaType)
        self.setLocAttr(startPos=[0, 6, -4])

    def setCtrlShape(self):
        sphere = cmds.createNode('implicitSphere')
        sphereCtrl = cmds.rename(cmds.listRelatives(sphere, p=True), 'Tailik_tempShape')
        cmds.scale(0.2, 0.2, 0.2, sphereCtrl)

        ctrlShape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=8, name='Tailfk_tempShape')
        cmds.scale(0.3, 0.3, 0.3, ctrlShape)

    def setLocAttr(self, startPos=[0, 0, 0], length=4.0, segment=6, scale=0.4):
        self.startPos = startPos
        self.interval = length / (segment-1)
        self.segment = segment
        self.scale = scale

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        for i in range(self.segment):
            tail = cmds.spaceLocator(n=self.locName+str(i))
            # root locator of tail parent to the tail group
            if i is 0:
                cmds.parent(tail, grp, relative=True)
                cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], tail, absolute=True)
                cmds.scale(self.scale, self.scale, self.scale, tail)
            # tail locator parent to the previous locator
            else:
                cmds.parent(tail, self.locName+str(i-1), relative=True)
                cmds.move(0, -self.interval, 0, tail, relative=True)  # move tail locator along -y axis

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        tail = cmds.ls('%s*' % self.locName, transforms=True)
        # result jnt
        cmds.select(clear=True)
        for i, loc in enumerate(tail):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntName+'final'+str(i))
            cmds.setAttr(jnt+'.radius', self.scale)

        # ik jnt
        cmds.select(clear=True)
        for i, loc in enumerate(tail):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntName+'ik'+str(i))
            cmds.setAttr(jnt+'.radius', self.scale)

        # fk jnt
        cmds.select(clear=True)
        for i, loc in enumerate(tail):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntName+'fk'+str(i))
            cmds.setAttr(jnt+'.radius', self.scale)

        self.rootTail = self.jntName+'final0'
        rootIKTail = self.jntName+'ik0'
        rootFKTail = self.jntName+'fk0'
        cmds.setAttr(rootFKTail+'.visibility', 0)
        cmds.setAttr(rootIKTail+'.visibility', 0)
        misc.batchParent([self.rootTail, rootFKTail, rootIKTail], self.jntGrp)
        misc.orientJnt([self.rootTail, rootIKTail, rootFKTail])
        return self.rootTail

    def placeCtrl(self):
        self.setCtrlShape()
        
        self.masterCtrl = cmds.duplicate('Tailik_tempShape', name=self.ctrlName+'master')[0]
        tailPos = cmds.xform(self.jntName+'final0', q=True, t=True, ws=True)
        cmds.move(tailPos[0], tailPos[1], tailPos[2]-1, self.masterCtrl)
        cmds.addAttr(self.masterCtrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=True)
        
        tails = cmds.ls('%sfinal*' % self.jntName, transforms=True)
        for type in ['fk', 'ik']:
            first = True
            for i, tail in enumerate(tails):
                tailPos = cmds.xform(tail, q=True, t=True, ws=True)
                tailRot = cmds.xform(tail, q=True, ro=True, ws=True)
                tailCtrl = cmds.duplicate('Tail%s_tempShape' % type, name=self.ctrlName+type+str(i))[0]

                tailCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetGrpName+type+str(i))
                cmds.move(tailPos[0], tailPos[1], tailPos[2], tailCtrlOffset)
                cmds.rotate(tailRot[0], tailRot[1], tailRot[2], tailCtrlOffset)
                cmds.parent(tailCtrl, tailCtrlOffset, relative=True)
                if not first:
                    cmds.parent(tailCtrlOffset, self.ctrlName+type+str(i-1))
                else:
                    cmds.parent(tailCtrlOffset, self.masterCtrl)
                    first = False

        cmds.parent(self.masterCtrl, self.ctrlGrp)
        self.deleteShape()
        return self.masterCtrl

    def buildIK(self):
        curvePoints = []
        all = cmds.ls(self.jntName+'ik*', transforms=True)

        for i, tail in enumerate(all):
            tailPos = cmds.xform(tail, q=True, t=True, ws=True)
            curvePoints.append(tailPos)

        tailCurve = cmds.curve(p=curvePoints, name=self.ctrlName+'tailCurve')
        cmds.setAttr(tailCurve+'.visibility', 0)  # hide tailCurve
        cmds.inheritTransform(tailCurve, off=True)  # turning off inherit transform avoid curve move/scale twice as much

        CVs = cmds.ls(self.ctrlName+'tailCurve.cv[0:]', fl=True)
        for i, cv in enumerate(CVs):
            cluster = cmds.cluster(cv, name=self.ctrlName+'cluster_'+str(i))[-1]
            cmds.setAttr(cluster+'.visibility', 0)  # hide clusters

        tailIK = cmds.ikHandle(startJoint=self.jntName+'ik0', endEffector=self.jntName+'ik'+str(self.segment-1), name=self.prefix+'_tailIK'+self.name, curve=tailCurve, createCurve=False,
                      parentCurve=True, roc=True, solver='ikSplineSolver')[0]
        cmds.setAttr(tailIK+'.visibility', 0)  # hide ik
        cmds.parent(tailIK, self.ctrlGrp)

    def buildFK(self):
        # format this way for systematic purpose
        pass

    def addConstraint(self):
        self.buildIK()
        for i in range(self.segment):
            tailCluster = cmds.ls('%scluster_%sHandle' % (self.ctrlName, str(i)))
            tailCtrl = cmds.ls(self.ctrlName+'ik'+str(i))
            cmds.parent(tailCluster, tailCtrl)

        self.buildFK()
        all = cmds.ls(self.jntName+'fk*', transforms=True)
        for i, tailJnt in enumerate(all):
            tailCtrl = cmds.ls(self.ctrlName+'fk'+str(i))
            cmds.parentConstraint(tailCtrl, tailJnt)

        # ik fk to result jnt
        for i in range(self.segment):
            ikTail = cmds.ls(self.jntName+'ik'+str(i))
            fkTail = cmds.ls(self.jntName+'fk'+str(i))
            finalTail = cmds.ls(self.jntName+'final'+str(i))
            cmds.parentConstraint(ikTail, fkTail, finalTail)

        # ik fk switch
        for i in range(self.segment):
            cmds.setDrivenKeyframe('%s%s%s_parentConstraint1.%s%s%s%s' % (self.jntName, 'final', str(i), self.jntName, 'ik', str(i), 'W0'), currentDriver=self.masterCtrl+'.FK_IK', driverValue=1, value=1)
            cmds.setDrivenKeyframe('%s%s%s_parentConstraint1.%s%s%s%s' % (self.jntName, 'final', str(i), self.jntName, 'fk', str(i), 'W1'), currentDriver=self.masterCtrl+'.FK_IK', driverValue=1, value=0)
            cmds.setDrivenKeyframe('%s%s%s_parentConstraint1.%s%s%s%s' % (self.jntName, 'final', str(i), self.jntName, 'ik', str(i), 'W0'), currentDriver=self.masterCtrl+'.FK_IK', driverValue=0, value=0)
            cmds.setDrivenKeyframe('%s%s%s_parentConstraint1.%s%s%s%s' % (self.jntName, 'final', str(i), self.jntName, 'fk', str(i), 'W1'), currentDriver=self.masterCtrl+'.FK_IK', driverValue=0, value=1)
    
            cmds.setDrivenKeyframe(self.ctrlName+'ik'+str(i)+'.visibility', currentDriver=self.masterCtrl+'.FK_IK', driverValue=1, value=1)
            cmds.setDrivenKeyframe(self.ctrlName+'ik'+str(i)+'.visibility', currentDriver=self.masterCtrl+'.FK_IK', driverValue=0, value=0)
            cmds.setDrivenKeyframe(self.ctrlName+'fk'+str(i)+'.visibility', currentDriver=self.masterCtrl+'.FK_IK', driverValue=0, value=1)
            cmds.setDrivenKeyframe(self.ctrlName+'fk'+str(i)+'.visibility', currentDriver=self.masterCtrl+'.FK_IK', driverValue=1, value=0)


    def lockCtrl(self):
        ctrls = cmds.ls(self.ctrlName+'*', transforms=True)
        for ctrl in ctrls:
            for transform in 's':
                for axis in 'xyz':
                    cmds.setAttr(ctrl+'.'+transform+axis, l=True, k=0)


