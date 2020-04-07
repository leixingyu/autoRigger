import maya.cmds as cmds
import base, misc
reload(misc)

class QuadSpine(base.Base):
    def __init__(self, prefix, side, id):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Spine'
        self.constructNameSpace(self.metaType)
        self.setLocAttr(startPos=[0, 6, -3])

    def setCtrlShape(self):
        sphere = cmds.createNode('implicitSphere')
        sphereCtrl = cmds.rename(cmds.listRelatives(sphere, p=True), 'Master_tempShape')
        cmds.scale(0.3, 0.3, 0.3, sphereCtrl)

        ctrlShape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=8, name='Spine_tempShape')
        cmds.scale(1, 1, 1, ctrlShape)

    def setLocAttr(self, startPos=[0, 0, 0], length=6.0, segment=7, scale=0.4):
        self.startPos = startPos
        self.interval = length / (segment-1)
        self.segment = segment
        self.scale = scale

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)

        for i in range(self.segment):
            spine = cmds.spaceLocator(n=self.locName+str(i))
            # root locator of spine parent to the spine group
            if i is 0:
                cmds.parent(spine, grp, relative=True)
                cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], spine, absolute=True)
                cmds.scale(self.scale, self.scale, self.scale, spine)
            # spine locator parent to the previous locator
            else:
                cmds.parent(spine, self.locName+str(i-1), relative=True)
                cmds.move(0, 0, self.interval, spine, relative=True)  # move spine locator along +z axis

        self.colorLoc()
        cmds.parent(grp, self.locGrp)
        return grp

    def constructJnt(self):
        spines = cmds.ls('%s*' % self.locName, transforms=True)
        cmds.select(clear=True)

        for i, loc in enumerate(spines):
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=locPos, name=self.jntName+str(i))
            cmds.setAttr(jnt+'.radius', self.scale)
            self.topSpine = jnt  # needs to be accessed later for parenting front leg

        self.rootSpine = self.jntName+'0'  # needs to be accessed later for parenting back leg
        cmds.parent(self.rootSpine, self.jntGrp)
        misc.orientJnt(self.rootSpine)

        return self.rootSpine

    def placeCtrl(self):
        self.setCtrlShape()

        rootPos = cmds.xform(self.jntName+'0', q=True, t=True, ws=True)
        rootRot = cmds.xform(self.jntName+'0', q=True, ro=True, ws=True)
        topPos = cmds.xform(self.jntName+str(self.segment-1), q=True, t=True, ws=True)
        topRot = cmds.xform(self.jntName+str(self.segment-1), q=True, ro=True, ws=True)

        # master ctrl is positioned on top of root ctrl
        self.masterCtrl = cmds.duplicate('Master_tempShape', name=self.ctrlName+'_master')[0]  # master ctrl needs to be acessed outside
        masterCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetGrpName+'_master')
        cmds.move(rootPos[0], rootPos[1]+2, rootPos[2], masterCtrlOffset)
        cmds.parent(self.masterCtrl, masterCtrlOffset, relative=True)

        # root ctrl is positioned at the root joint
        self.rootCtrl = cmds.duplicate('Spine_tempShape', name=self.ctrlName+'_root')[0]  # root ctrl needs to be accessed outside for parenting
        rootCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetGrpName+'_root')
        cmds.move(rootPos[0], rootPos[1], rootPos[2], rootCtrlOffset)
        cmds.rotate(rootRot[0], rootRot[1], rootRot[2], rootCtrlOffset)
        cmds.parent(self.rootCtrl, rootCtrlOffset, relative=True)

        # top ctrl is positioned at the top joint
        self.topCtrl = cmds.duplicate('Spine_tempShape', name=self.ctrlName+'_top')[0]  # top ctrl needs to be accessed outside for parenting
        topCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetGrpName+'_top')
        cmds.move(topPos[0], topPos[1], topPos[2], topCtrlOffset)
        cmds.rotate(topRot[0], topRot[1], topRot[2], topCtrlOffset)
        cmds.parent(self.topCtrl, topCtrlOffset, relative=True)
        
        # mid ctrl is positioned at the middle joint / or middle two joint
        if self.segment % 2 != 0:
            midPos = cmds.xform(self.jntName+str((self.segment-1)/2), q=True, t=True, ws=True)
            midRot = cmds.xform(self.jntName+str((self.segment-1)/2), q=True, ro=True, ws=True)
            midCtrl = cmds.duplicate('Spine_tempShape', name=self.ctrlName+'_mid')[0]
    
            midCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetGrpName+'_mid')
            cmds.move(midPos[0], midPos[1], midPos[2], midCtrlOffset)
            cmds.rotate(midRot[0], midRot[1], midRot[2], midCtrlOffset)
            cmds.parent(midCtrl, midCtrlOffset, relative=True)
        else:
            midUpperPos = cmds.xform(self.jntName+str((self.segment+1) / 2), q=True, t=True, ws=True)
            midUpperRot = cmds.xform(self.jntName+str((self.segment+1) / 2), q=True, ro=True, ws=True)
            midLowerPos = cmds.xform(self.jntName+str((self.segment-1) / 2), q=True, t=True, ws=True)
            midLowerRot = cmds.xform(self.jntName+str((self.segment-1) / 2), q=True, ro=True, ws=True)
            midPos = [(midUpperPos[0]+midLowerPos[0])/2, (midUpperPos[1]+midLowerPos[1])/2, (midUpperPos[2]+midLowerPos[2])/2]
            midRot = [(midUpperRot[0]+midLowerRot[0])/2, (midUpperRot[1]+midLowerRot[1])/2, (midUpperRot[2]+midLowerRot[2])/2]
            midCtrl = cmds.duplicate('Spine_tempShape', name=self.ctrlName+'_mid')[0]

            midCtrlOffset = cmds.group(em=True, name=self.ctrlOffsetGrpName+'_mid')
            cmds.move(midPos[0], midPos[1], midPos[2], midCtrlOffset)
            cmds.rotate(midRot[0], midRot[1], midRot[2], midCtrlOffset)
            cmds.parent(midCtrl, midCtrlOffset, relative=True)

        misc.batchParent([midCtrlOffset, rootCtrlOffset, topCtrlOffset], self.masterCtrl)
        cmds.parent(masterCtrlOffset, self.ctrlGrp)
        self.deleteShape()
        return self.masterCtrl

    def buildIK(self):
        # use ik auto create curve with spans of 2 (5 cvs), exclude the root joint
        self.backIK = cmds.ikHandle(startJoint=self.jntName+'1', endEffector=self.jntName+str(self.segment-1), name=self.prefix+'_backIK'+self.name, createCurve=True,
                               parentCurve=False, roc=True, solver='ikSplineSolver', simplifyCurve=True, numSpans=2)[0]
        cmds.rename('curve1', self.ctrlName+'backCurve')

        cmds.cluster(self.ctrlName+'backCurve.cv[0:1]', name=self.ctrlName+'cluster_root')
        cmds.cluster(self.ctrlName+'backCurve.cv[2]', name=self.ctrlName+'cluster_mid')
        cmds.cluster(self.ctrlName+'backCurve.cv[3:4]', name=self.ctrlName+'cluster_top')

        cmds.setAttr(self.backIK+'.visibility', 0)  # hide ik
        cmds.parent(self.backIK, self.ctrlGrp)

    def addConstraint(self):
        # each ik control is the parent of spine clusters
        self.buildIK()
        for i in ['root', 'mid', 'top']:
            spineCluster = cmds.ls('%scluster_%sHandle' % (self.ctrlName, i))
            spineCtrl = cmds.ls('%s_%s' % (self.ctrlName, i))
            cmds.parent(spineCluster, spineCtrl)

        # middle control is driven by the top and root control
        midCtrl = cmds.ls(self.ctrlName+'_mid')[0]
        cmds.pointConstraint(self.topCtrl, self.rootCtrl, midCtrl)
        cmds.parentConstraint(self.rootCtrl, self.jntName+'0')

        '''scaling of the spine'''
        curve = cmds.ls(self.ctrlName+'backCurve')[0]
        arclen = cmds.arclen(curve, constructionHistory=True)
        cmds.rename(arclen, self.ctrlName+'backCurveInfo')
        cmds.parent(curve, self.ctrlGrp)
        cmds.setAttr(curve+'.visibility', 0)

        # create curve length node and multiply node
        initLen = cmds.getAttr(self.ctrlName+'backCurveInfo.arcLength')
        stretchNode = cmds.shadingNode('multiplyDivide', asUtility=True, name=self.ctrlName+'Stretch')
        cmds.setAttr(stretchNode+'.operation', 2)
        cmds.setAttr(stretchNode+'.input2X', initLen)
        cmds.connectAttr(self.ctrlName+'backCurveInfo.arcLength', stretchNode+'.input1X')
        for i in range(self.segment):
            cmds.connectAttr(stretchNode+'.outputX', self.jntName+str(i)+'.scaleX')

        # enable advance twist control
        cmds.setAttr(self.backIK+'.dTwistControlEnable', 1)
        cmds.setAttr(self.backIK+'.dWorldUpType', 4)
        cmds.connectAttr(self.rootCtrl+'.worldMatrix[0]', self.backIK+'.dWorldUpMatrix', f=True)
        cmds.connectAttr(self.topCtrl+'.worldMatrix[0]', self.backIK+'.dWorldUpMatrixEnd', f=True)

    def lockCtrl(self):
        ctrls = cmds.ls(self.ctrlName+'*', transforms=True)
        for ctrl in ctrls:
            for transform in 's':
                for axis in 'xyz':
                    cmds.setAttr(ctrl+'.'+transform+axis, l=True, k=0)


