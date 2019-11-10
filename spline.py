import maya.cmds as cmds
import base

class Spline(base.Base):
    def __init__(self, prefix, side, id):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Spline'

        self.constructNameSpace(self.metaType)

        '''default locator attribute'''
        self.setLocAttr()

    def setCtrlShape(self):
        globalShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='SplineGlobal_tempShape')
        cmds.scale(2, 2, 2, globalShape)

        splineShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Spline_tempShape')
        selectionTip = cmds.select('Spline_tempShape.cv[5]')
        cmds.move(0, 0, 1.5, selectionTip, relative=True)
        selectionEdge = cmds.select('Spline_tempShape.cv[4]', 'Spline_tempShape.cv[6]')
        cmds.scale(0.25, 0.25, 0.25, selectionEdge, relative=True)
        cmds.move(0, 0, 0.75, relative=True)
        cmds.rotate(0, 0, 90, splineShape)
        cmds.scale(0.5, 0.5, 0.5, splineShape)

    def setLocAttr(self, startPos=[0, 0, 0], length=6.0, segment=6, scale=0.5):
        self.startPos = startPos
        self.interval = length/(segment-1)
        self.segment = segment
        self.scale = scale

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        for i in range(self.segment):
            spline = cmds.spaceLocator(n=self.locName+str(i))
            # root locator of spline parent to the spline group
            if i is 0:
                cmds.parent(spline, grp, relative=True)
                cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], spline, absolute=True)
                cmds.scale(self.scale, self.scale, self.scale, spline)
            # spline locator parent to the previous locator
            else:
                cmds.parent(spline, self.locName+str(i-1), relative=True)
                cmds.move(0, self.interval, 0, spline, relative=True)  # move spline locator along +y axis

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        spline = cmds.ls('%s*' % self.locName, transforms=True)
        cmds.select(clear=True)

        for i, loc in enumerate(spline):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntName+str(i))
            cmds.setAttr(jnt + '.radius', self.scale)
            self.topSpine = jnt

        self.rootSpine = self.jntName+'0'
        cmds.parent(self.rootSpine, self.jntGrp)
        return self.rootSpine
    
    def placeCtrl(self):
        self.setCtrlShape()
        grp = cmds.group(em=True, name=self.ctrlGrpName)
        splines = cmds.ls('%s*' % self.jntName, transforms=True)
        
        for i, spline in enumerate(splines):
            splinePos = cmds.xform(spline, q=True, t=True, ws=True)
            splineCtrl = cmds.duplicate('Spline_tempShape', name=self.ctrlName+str(i))[0]
            if i == 0:
                self.globalCtrl = cmds.duplicate('SplineGlobal_tempShape', name=self.ctrlName)[0]
                cmds.move(splinePos[0], splinePos[1], splinePos[2], self.globalCtrl)
                cmds.makeIdentity(self.globalCtrl, apply=True, t=1, r=1, s=1)
                cmds.parent(splineCtrl, self.globalCtrl, relative=True)
            elif i != 0:
                cmds.parent(splineCtrl, self.ctrlName+str(i-1))
            cmds.move(splinePos[0], splinePos[1], splinePos[2]-5, splineCtrl)
            cmds.move(splinePos[0], splinePos[1], splinePos[2], splineCtrl+'.scalePivot', splineCtrl+'.rotatePivot', absolute=True)
            cmds.makeIdentity(splineCtrl, apply=True, t=1, r=1, s=1)

            # parent line shape under curve transform (combine curve)
            line = cmds.curve(degree=1, point=[(splinePos[0], splinePos[1], splinePos[2]), (splinePos[0], splinePos[1], splinePos[2]-5)], name=self.ctrlName+'line'+str(i))
            lineShape = cmds.listRelatives(line, shapes=True)
            cmds.parent(lineShape, splineCtrl, relative=True, shape=True)
            cmds.delete(line)

        cmds.parent(self.ctrlName, grp)
        self.deleteShape()
        cmds.parent(grp, self.ctrlGrp)
        return grp

    def buildIK(self):
        curvePoints = []
        allSplines = cmds.ls(self.jntName+'*', transforms=True)

        for i, spline in enumerate(allSplines):
            splinePos = cmds.xform(spline, q=True, t=True, ws=True)
            curvePoints.append(splinePos)

        splineCurve = cmds.curve(p=curvePoints, name=self.ctrlName+'splineCurve')
        cmds.setAttr(splineCurve+'.visibility', 0)  # hide splineCurve
        cmds.inheritTransform(splineCurve, off=True)  # turning off inherit transform avoid curve move/scale twice as much

        CVs = cmds.ls(self.ctrlName+'splineCurve.cv[0:]', fl=True)
        for i, cv in enumerate(CVs):
            cluster = cmds.cluster(cv, name=self.ctrlName+'cluster_'+str(i))[-1]
            if i != 0:
                cmds.parent(cluster, self.ctrlName+'cluster_%sHandle' % str(i-1), relative=False)
            else:
                cmds.parent(cluster, self.ctrlGrp)
            cmds.setAttr(cluster+'.visibility', 0)  # hide clusters

        splineIK = cmds.ikHandle(startJoint=self.jntName+'0', endEffector=self.jntName+str(self.segment-1), name=self.prefix+'_SplineIK'+self.name, curve=splineCurve, createCurve=False, parentCurve=True, roc=True, solver='ikSplineSolver')[0]
        cmds.setAttr(splineIK+'.visibility', 0)  # hide ik
        cmds.parent(splineIK, self.ctrlGrp)

    def addConstraint(self):
        self.buildIK()
        for i in range(0, self.segment):
            splineCluster = cmds.ls(self.ctrlName+'cluster_%sHandle' % str(i))
            splineCtrl = cmds.ls(self.ctrlName+str(i))
            cmds.pointConstraint(splineCtrl, splineCluster)
            if i == self.segment-1:
                self.topCtrl = cmds.ls(self.ctrlName+str(i))[0]
                cmds.connectAttr(self.topCtrl+'.rotateY', self.prefix+'_SplineIK'+self.name+'.twist')

    def lockCtrl(self):
        ctrls = cmds.ls(self.ctrlName+'*', transforms=True)
        for ctrl in ctrls:
            for transform in 'ts':
                for axis in 'xyz':
                    cmds.setAttr(ctrl+'.'+transform+axis, l=True, k=0)


