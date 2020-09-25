import maya.cmds as cmds
import base

class Spine(base.Base):
    def __init__(self, side, id):
        base.Base.__init__(self, side, id)
        self.metaType = 'Spine'
        self.createNaming()
        self.setLocAttr()

    def setCtrlShape(self):
        globalShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='SpineGlobal_tempShape')
        cmds.scale(2, 2, 2, globalShape)

        spineShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Spine_tempShape')
        selectionTip = cmds.select('Spine_tempShape.cv[5]')
        cmds.move(0, 0, 1.5, selectionTip, relative=True)
        selectionEdge = cmds.select('Spine_tempShape.cv[4]', 'Spine_tempShape.cv[6]')
        cmds.scale(0.25, 0.25, 0.25, selectionEdge, relative=True)
        cmds.move(0, 0, 0.75, relative=True)
        cmds.rotate(0, 0, 90, spineShape)
        cmds.scale(0.5, 0.5, 0.5, spineShape)

    def setLocAttr(self, startPos=[0, 0, 0], length=6.0, segment=6, scale=0.5):
        self.startPos = startPos
        self.interval = length/(segment-1)
        self.segment = segment
        self.scale = scale

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        for i in range(self.segment):
            spine = cmds.spaceLocator(n='{}{}_loc'.format(self.name, i))
            if i is 0:    # root locator of spine parent to the spine group
                cmds.parent(spine, grp, relative=True)
                cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], spine, absolute=True)
                cmds.scale(self.scale, self.scale, self.scale, spine)
            else:         # spine locator parent to the previous locator
                cmds.parent(spine, '{}{}_loc'.format(self.name, i-1), relative=True)
                cmds.move(0, self.interval, 0, spine, relative=True)  # move spine locator along +y axis

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        spines = cmds.ls('{}*_loc'.format(self.name), transforms=True)
        cmds.select(clear=True)

        for i, loc in enumerate(spines):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name='{}{}_jnt'.format(self.name, i))
            cmds.setAttr(jnt + '.radius', self.scale)
            self.topSpine = jnt

        self.rootSpine = '{}{}_jnt'.format(self.name, 0)
        cmds.parent(self.rootSpine, self.jntGrp)
        return self.rootSpine
    
    def placeCtrl(self):
        self.setCtrlShape()
        grp = cmds.group(em=True, name=self.ctrlGrpName)
        spines = cmds.ls('{}*_jnt'.format(self.name), transforms=True)
        
        for i, spine in enumerate(spines):
            spinePos = cmds.xform(spine, q=True, t=True, ws=True)
            spineCtrl = cmds.duplicate('Spine_tempShape', name='{}{}_ctrl'.format(self.name, i))[0]
            if i == 0:
                self.globalCtrl = cmds.duplicate('SpineGlobal_tempShape', name=self.ctrlName)[0]
                cmds.move(spinePos[0], spinePos[1], spinePos[2], self.globalCtrl)
                cmds.makeIdentity(self.globalCtrl, apply=True, t=1, r=1, s=1)
                cmds.parent(spineCtrl, self.globalCtrl, relative=True)
            elif i != 0:
                cmds.parent(spineCtrl, '{}{}_ctrl'.format(self.name, i-1))

            cmds.move(spinePos[0], spinePos[1], spinePos[2]-5, spineCtrl)
            cmds.move(spinePos[0], spinePos[1], spinePos[2], spineCtrl+'.scalePivot', spineCtrl+'.rotatePivot', absolute=True)
            cmds.makeIdentity(spineCtrl, apply=True, t=1, r=1, s=1)

            # parent line shape under curve transform (combine curve shape) #
            line = cmds.curve(degree=1, point=[(spinePos[0], spinePos[1], spinePos[2]), (spinePos[0], spinePos[1], spinePos[2]-5)], name='{}line{}_ctrl'.format(self.name, i))
            lineShape = cmds.listRelatives(line, shapes=True)
            cmds.parent(lineShape, spineCtrl, relative=True, shape=True)
            cmds.delete(line)

        cmds.parent(self.ctrlName, grp)
        self.deleteShape()
        cmds.parent(grp, self.ctrlGrp)
        return grp

    def buildIK(self):
        #--- Create Spine Curve ---#
        curvePoints = []
        spines = cmds.ls('{}*_jnt'.format(self.name), transforms=True)
        for i, spine in enumerate(spines):
            spinePos = cmds.xform(spine, q=True, t=True, ws=True)
            curvePoints.append(spinePos)
        spineCurve = cmds.curve(p=curvePoints, name='{}*_curve'.format(self.name))
        cmds.setAttr(spineCurve+'.visibility', 0)
        cmds.inheritTransform(spineCurve, off=True)  # turning off inherit transform avoid curve move/scale twice as much

        #--- Create Sline IK ---#
        splineIK = cmds.ikHandle(startJoint='{}{}_jnt'.format(self.name, 0),
                                endEffector='{}{}_jnt'.format(self.name, self.segment-1),
                                name='{}_ik'.format(self.name), curve=spineCurve, createCurve=False, parentCurve=True, roc=True, solver='ikSplineSolver')[0]
        cmds.setAttr(splineIK+'.visibility', 0)
        cmds.parent(splineIK, self.ctrlGrp)

        #--- Create Cluster ---#
        cvs = cmds.ls('{}*_curve.cv[0:]'.format(self.name), fl=True)
        for i, cv in enumerate(cvs):
            cluster = cmds.cluster(cv, name='{}{}_cluster'.format(self.name, i))[-1]
            if i != 0:
                cmds.parent(cluster, '{}{}_clusterHandle'.format(self.name, i-1), relative=False)
            else:
                cmds.parent(cluster, self.ctrlGrp)
            cmds.setAttr(cluster+'.visibility', 0)

    def addConstraint(self):
        self.buildIK()
        for i in range(0, self.segment):
            spineCluster = cmds.ls('{}{}_clusterHandle'.format(self.name, i))
            spineCtrl = cmds.ls('{}{}_ctrl'.format(self.name, i))
            cmds.pointConstraint(spineCtrl, spineCluster)
            if i == self.segment-1:
                self.topCtrl = cmds.ls('{}{}_ctrl'.format(self.name, i))[0]
                cmds.connectAttr(self.topCtrl+'.rotateY', '{}_ik.twist'.format(self.name))

    def lockCtrl(self):
        ctrls = cmds.ls('{}?_ctrl'.format(self.name), transforms=True)
        for ctrl in ctrls:
            for transform in 'ts':
                for axis in 'xyz':
                    cmds.setAttr(ctrl+'.'+transform+axis, l=True, k=0)


