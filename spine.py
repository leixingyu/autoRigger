import maya.cmds as cmds
import base
from utility import joint, outliner


class Spine(base.Base):
    def __init__(self, side, id):
        base.Base.__init__(self, side, id)
        self.metaType = 'Spine'
        self.createNaming()
        self.createSecondaryNaming()

    def createSecondaryNaming(self):
        self.locList, self.jntList, self.ctrlList, self.clusterList = ([] for i in range(4))  # ik has different ctrl name
        for i in range(self.segment):
            self.locList.append('{}{}_loc'.format(self.name, i))
            self.jntList.append('{}{}_jnt'.format(self.name, i))
            self.ctrlList.append('{}{}_ctrl'.format(self.name, i))
            self.clusterList.append('{}{}_cluster'.format(self.name, i))
        self.ikCurve = '{}ik_curve'.format(self.name)
        self.ikName = '{}_ik'.format(self.name)

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
            spine = cmds.spaceLocator(n=self.locList[i])
            if i is 0:    # root locator of spine parent to the spine group
                cmds.parent(spine, grp, relative=True)
                cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], spine, absolute=True)
                cmds.scale(self.scale, self.scale, self.scale, spine)
            else:         # spine locator parent to the previous locator
                cmds.parent(spine, self.locList[i-1], relative=True)
                cmds.move(0, self.interval, 0, spine, relative=True)  # move spine locator along +y axis

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        cmds.select(clear=True)

        for i, loc in enumerate(self.locList):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntList[i])
            cmds.setAttr(jnt + '.radius', self.scale)

        cmds.parent(self.jntList[0], self.jntGrp)
        return self.jntList[0]
    
    def placeCtrl(self):
        self.setCtrlShape()
        grp = cmds.group(em=True, name=self.ctrlGrpName)
        
        for i, spine in enumerate(self.jntList):
            spinePos = cmds.xform(spine, q=True, t=True, ws=True)
            spineCtrl = cmds.duplicate('Spine_tempShape', name=self.ctrlList[i])[0]
            if i == 0:
                self.globalCtrl = cmds.duplicate('SpineGlobal_tempShape', name=self.ctrlName)[0]
                cmds.move(spinePos[0], spinePos[1], spinePos[2], self.globalCtrl)
                cmds.makeIdentity(self.globalCtrl, apply=True, t=1, r=1, s=1)
                cmds.parent(spineCtrl, self.globalCtrl, relative=True)
            elif i != 0:
                cmds.parent(spineCtrl, self.ctrlList[i-1])
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
        for i, spine in enumerate(self.jntList):
            spinePos = cmds.xform(spine, q=True, t=True, ws=True)
            curvePoints.append(spinePos)
        cmds.curve(p=curvePoints, name=self.ikCurve)
        cmds.setAttr(self.ikCurve+'.visibility', 0)
        cmds.inheritTransform(self.ikCurve, off=True)  # turning off inherit transform avoid curve move/scale twice as much

        #--- Create Spline IK ---#
        cmds.ikHandle(startJoint=self.jntList[0], endEffector=self.jntList[-1], name=self.ikName, curve=self.ikCurve, createCurve=False, parentCurve=True, roc=True, solver='ikSplineSolver')
        cmds.setAttr(self.ikName+'.visibility', 0)
        cmds.parent(self.ikName, self.ctrlGrp)

        #--- Create Cluster ---#
        cvs = cmds.ls('{}.cv[0:]'.format(self.ikCurve), fl=True)
        for i, cv in enumerate(cvs):
            cluster = cmds.cluster(cv, name=self.clusterList[i])[-1]
            if i != 0: cmds.parent(cluster, '{}Handle'.format(self.clusterList[i-1]), relative=False)
            else: cmds.parent(cluster, self.ctrlGrp)
            cmds.setAttr(cluster+'.visibility', 0)

    def addConstraint(self):
        self.buildIK()
        for i in range(0, self.segment):
            spineCluster = cmds.ls('{}Handle'.format(self.clusterList[i]))
            spineCtrl = cmds.ls(self.ctrlList[i])
            cmds.pointConstraint(spineCtrl, spineCluster)
        cmds.connectAttr(self.ctrlList[-1]+'.rotateY', '{}.twist'.format(self.ikName))

    def lockCtrl(self):
        for ctrl in self.ctrlList:
            for transform in 'ts':
                for axis in 'xyz':
                    cmds.setAttr(ctrl+'.'+transform+axis, l=True, k=0)

class SpineQuad(base.Base):
    def __init__(self, side, id):
        base.Base.__init__(self, side, id)
        self.metaType = 'Spine'
        self.createNaming()
        self.createSecondaryNaming()
        # self.setLocAttr()

    def createSecondaryNaming(self):
        self.locList, self.jntList, self.clusterList, self.ctrlList, self.ctrlOffsetList = ([] for i in range(5))  # ik has different ctrl name
        for i in range(self.segment):
            self.locList.append('{}{}_loc'.format(self.name, i))
            self.jntList.append('{}{}_jnt'.format(self.name, i))

        for name in ['root', 'mid', 'top']:
            self.ctrlList.append('{}{}_ctrl'.format(self.name, name))
            self.ctrlOffsetList.append('{}{}_offset'.format(self.name, name))
            self.clusterList.append('{}{}_cluster'.format(self.name, name))

        self.masterCtrl = '{}master_ctrl'.format(self.name, name)
        self.masterOffset = '{}master_offset'.format(self.name, name)
        self.ikCurve = '{}ik_curve'.format(self.name)
        self.ikName = '{}_ik'.format(self.name)

    def setCtrlShape(self):
        sphere = cmds.createNode('implicitSphere')
        sphereCtrl = cmds.rename(cmds.listRelatives(sphere, p=True), 'Master_tempShape')
        cmds.scale(0.3, 0.3, 0.3, sphereCtrl)

        ctrlShape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=8, name='Spine_tempShape')
        cmds.scale(1, 1, 1, ctrlShape)

    def setLocAttr(self, startPos=[0, 6, -3], length=6.0, segment=7, scale=0.4):
        self.startPos = startPos
        self.interval = length / (segment-1)
        self.segment = segment
        self.scale = scale

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        for i in range(self.segment):
            spine = cmds.spaceLocator(n=self.locList[i])
            if i is 0:
                cmds.parent(spine, grp, relative=True)
                cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], spine, absolute=True)
                cmds.scale(self.scale, self.scale, self.scale, spine)
            else:
                cmds.parent(spine, self.locList[i-1], relative=True)
                cmds.move(0, 0, self.interval, spine, relative=True)  # move spine locator along +z axis

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        cmds.select(clear=True)

        for i, loc in enumerate(self.locList):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntList[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        cmds.parent(self.jntList[0], self.jntGrp)
        joint.orient_joint(self.jntList[0])
        return self.jntList[0]

    def placeCtrl(self):
        self.setCtrlShape()

        rootPos = cmds.xform(self.jntList[0], q=True, t=True, ws=True)
        rootRot = cmds.xform(self.jntList[0], q=True, ro=True, ws=True)
        topPos = cmds.xform(self.jntList[-1], q=True, t=True, ws=True)
        topRot = cmds.xform(self.jntList[-1], q=True, ro=True, ws=True)

        # master ctrl is positioned on top of root ctrl
        cmds.duplicate('Master_tempShape', name=self.masterCtrl)
        cmds.group(em=True, name=self.masterOffset)
        cmds.move(rootPos[0], rootPos[1]+2, rootPos[2], self.masterOffset)
        cmds.parent(self.masterCtrl, self.masterOffset, relative=True)

        # root ctrl is positioned at the root joint
        cmds.duplicate('Spine_tempShape', name=self.ctrlList[0])  # root ctrl needs to be accessed outside for parenting
        cmds.group(em=True, name=self.ctrlOffsetList[0])
        cmds.move(rootPos[0], rootPos[1], rootPos[2], self.ctrlOffsetList[0])
        cmds.rotate(rootRot[0], rootRot[1], rootRot[2], self.ctrlOffsetList[0])
        cmds.parent(self.ctrlList[0], self.ctrlOffsetList[0], relative=True)

        # top ctrl is positioned at the top joint
        cmds.duplicate('Spine_tempShape', name=self.ctrlList[-1])  # top ctrl needs to be accessed outside for parenting
        cmds.group(em=True, name=self.ctrlOffsetList[-1])
        cmds.move(topPos[0], topPos[1], topPos[2], self.ctrlOffsetList[-1])
        cmds.rotate(topRot[0], topRot[1], topRot[2], self.ctrlOffsetList[-1])
        cmds.parent(self.ctrlList[-1], self.ctrlOffsetList[-1], relative=True)

        # mid ctrl is positioned at the middle joint / or middle two joint
        if self.segment % 2 != 0:
            midPos = cmds.xform(self.jntList[(self.segment-1) / 2], q=True, t=True, ws=True)
            midRot = cmds.xform(self.jntList[(self.segment-1) / 2], q=True, ro=True, ws=True)
        else:
            midUpperPos = cmds.xform(self.jntList[(self.segment+1) / 2], q=True, t=True, ws=True)
            midUpperRot = cmds.xform(self.jntList[(self.segment+1) / 2], q=True, ro=True, ws=True)
            midLowerPos = cmds.xform(self.jntList[(self.segment-1) / 2], q=True, t=True, ws=True)
            midLowerRot = cmds.xform(self.jntList[(self.segment-1) / 2], q=True, ro=True, ws=True)
            midPos = [(midUpperPos[0]+midLowerPos[0]) / 2, (midUpperPos[1]+midLowerPos[1]) / 2, (midUpperPos[2]+midLowerPos[2]) / 2]
            midRot = [(midUpperRot[0]+midLowerRot[0]) / 2, (midUpperRot[1]+midLowerRot[1]) / 2, (midUpperRot[2]+midLowerRot[2]) / 2]
        cmds.duplicate('Spine_tempShape', name=self.ctrlList[1])
        cmds.group(em=True, name=self.ctrlOffsetList[1])
        cmds.move(midPos[0], midPos[1], midPos[2], self.ctrlOffsetList[1])
        cmds.rotate(midRot[0], midRot[1], midRot[2], self.ctrlOffsetList[1])
        cmds.parent(self.ctrlList[1], self.ctrlOffsetList[1], relative=True)

        # --- Cleanup ---#
        outliner.batch_parent([self.ctrlOffsetList[0], self.ctrlOffsetList[1], self.ctrlOffsetList[-1]], self.masterCtrl)
        cmds.parent(self.masterOffset, self.ctrlGrp)
        self.deleteShape()
        return self.masterCtrl

    def buildIK(self):
        # use ik auto create curve with spans of 2 (5 cvs), exclude the root joint
        cmds.ikHandle(startJoint=self.jntList[1], endEffector=self.jntList[-1], name=self.ikName, createCurve=True,
                      parentCurve=False, roc=True, solver='ikSplineSolver', simplifyCurve=True, numSpans=2)
        cmds.rename('curve1', self.ikCurve)

        cmds.cluster(self.ikCurve+'.cv[0:1]', name=self.clusterList[0])
        cmds.cluster(self.ikCurve+'.cv[2]', name=self.clusterList[1])
        cmds.cluster(self.ikCurve+'.cv[3:4]', name=self.clusterList[-1])

        cmds.setAttr(self.ikName+'.visibility', 0)  # hide ik
        cmds.parent(self.ikName, self.ctrlGrp)

    def addConstraint(self):
        # each ik control is the parent of spine clusters
        self.buildIK()
        for i, cluster in enumerate(self.clusterList):
            spineCluster = cmds.ls('{}Handle'.format(cluster))
            spineCtrl = cmds.ls(self.ctrlList[i])
            cmds.parent(spineCluster, spineCtrl)

        # middle control is driven by the top and root control
        cmds.pointConstraint(self.ctrlList[-1], self.ctrlList[0], self.ctrlList[1])
        cmds.parentConstraint(self.ctrlList[0], self.jntList[0])

        '''scaling of the spine'''
        arclen = cmds.arclen(self.ikCurve, constructionHistory=True)
        cmds.rename(arclen, self.ikCurve+'Info')
        cmds.parent(self.ikCurve, self.ctrlGrp)
        cmds.setAttr(self.ikCurve+'.visibility', 0)

        # create curve length node and multiply node
        initLen = cmds.getAttr(self.ikCurve+'Info.arcLength')
        stretchNode = cmds.shadingNode('multiplyDivide', asUtility=True, name=self.ctrlName+'Stretch')
        cmds.setAttr(stretchNode+'.operation', 2)
        cmds.setAttr(stretchNode+'.input2X', initLen)
        cmds.connectAttr(self.ikCurve+'Info.arcLength', stretchNode+'.input1X')
        for i in range(self.segment):
            cmds.connectAttr(stretchNode+'.outputX', self.jntList[i]+'.scaleX')

        # enable advance twist control
        cmds.setAttr(self.ikName+'.dTwistControlEnable', 1)
        cmds.setAttr(self.ikName+'.dWorldUpType', 4)
        cmds.connectAttr(self.ctrlList[0]+'.worldMatrix[0]', self.ikName+'.dWorldUpMatrix', f=True)
        cmds.connectAttr(self.ctrlList[-1]+'.worldMatrix[0]', self.ikName+'.dWorldUpMatrixEnd', f=True)

    def lockCtrl(self):
        for ctrl in self.ctrlList+[self.masterCtrl]:
            for transform in 's':
                for axis in 'xyz':
                    cmds.setAttr(ctrl+'.'+transform+axis, l=True, k=0)
