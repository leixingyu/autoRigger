import maya.cmds as cmds
import base

class Head(base.Base):
    def __init__(self, id, side='NA'):
        base.Base.__init__(self, side, id)
        self.metaType = 'Face'

        self.constructNameSpace(self.metaType)
        self.set_locator_attr()
        
    def set_locator_attr(self, startPos=[0, 0, 0], distance=0.1, scale=0.1):
        self.startPos = startPos
        self.distance = distance
        self.scale = scale
    
    def build_guide(self):
        self.eyeLocators()
        #self.lipLocators()
        #self.addLocators()
        #self.groupLocators()
    
    def eyeLocators(self):
        if cmds.objExists('L_Eye') and cmds.objExists('R_Eye'):
            leftPos = cmds.xform('L_Eye.rotatePivot', q=True, t=True, ws=True)
            rightPos = cmds.xform('R_Eye.rotatePivot', q=True, t=True, ws=True)
            self.startPos = [(leftPos[0]+rightPos[0])/2,
                             (leftPos[1]+rightPos[1])/2,
                             (leftPos[2]+rightPos[2])/2]
        else: cmds.confirmDialog(title="Eyes missing", message="The eyes could not be found", button=['OK'])

        sideMult = 1
        scaleFac = self.scale
        for side in 'LR':
            eyeUpLidCurve = [(0, 0, 0), (0.5*scaleFac*sideMult, 0.2*scaleFac, 0), (1*scaleFac*sideMult, 0.4*scaleFac, 0), (1.5*scaleFac*sideMult, 0.2*scaleFac, 0), (2*scaleFac*sideMult, 0, 0)]
            eyeLowLidCurve = [(0, 0, 0), (0.5*scaleFac*sideMult, -0.2*scaleFac, 0), (1*scaleFac*sideMult, -0.4*scaleFac, 0), (1.5*scaleFac*sideMult, -0.2*scaleFac, 0), (2*scaleFac*sideMult, 0, 0)]
            eyeBrowCurve = [(0, 0, 0), (0.5*scaleFac*sideMult, 0.2*scaleFac, 0), (1*scaleFac*sideMult, 0.3*scaleFac, 0), (1.5*scaleFac*sideMult, 0.2*scaleFac, 0), (2*scaleFac*sideMult, 0, 0)]

            eyeCenterLoc = cmds.spaceLocator(n='Loc_Face_'+side+'_EyeCenter')
            cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], eyeCenterLoc)

            eyeAimLoc = cmds.spaceLocator(n='Loc_Face_'+side+'_EyeAim')
            cmds.move(self.startPos[0], self.startPos[1], self.startPos[2]+10*scaleFac, eyeAimLoc)

            upperLid = cmds.curve(p=eyeUpLidCurve, n="CV_%s_UpperEyeLid" % side)
            cmds.scale(2.5, 2.5, 2.5, upperLid)
            cmds.move(self.startPos[0]-2.2*scaleFac*sideMult, self.startPos[1], self.startPos[2]+6*scaleFac, upperLid)

            lowerLid = cmds.curve(p=eyeLowLidCurve, n="CV_%s_LowerEyeLid" % side)
            cmds.scale(2.5, 2.5, 2.5, lowerLid)
            cmds.move(self.startPos[0]-2.2*scaleFac*sideMult, self.startPos[1]-1.5*scaleFac, self.startPos[2]+6*scaleFac, lowerLid)

            eyeBrow = cmds.curve(p=eyeBrowCurve, n="CV_%s_EyeBrow" % side)
            cmds.scale(4, 3, 2.5, eyeBrow)
            cmds.move(self.startPos[0]-3.5*scaleFac*sideMult, self.startPos[1]+2.5*scaleFac, self.startPos[2]+8*scaleFac, eyeBrow)

            foreHeadBrow = cmds.curve(p=eyeBrowCurve, n="CV_%s_ForeHeadBrow" % side)
            cmds.scale(5, 4, 2.5, foreHeadBrow)
            cmds.move(self.startPos[0]-3.5*scaleFac*sideMult, self.startPos[1]+7*scaleFac, self.startPos[2]+8*scaleFac, foreHeadBrow)

            cheekLoc = cmds.spaceLocator(name='Loc_Face_%s_Cheek' % side)
            cmds.move(self.startPos[0]+4*scaleFac*sideMult, self.startPos[1]-6*scaleFac, self.startPos[2]+7*scaleFac, cheekLoc)

            sideMult = -1
    
            #jawLoc = cmds.spaceLocator(n='Loc_Face_Jaw')
            #cmds.move(0, 317*scaleFac, 21*scaleFac, jawLoc)
    
    def lipLocators(self):
        if cmds.objExists('Loc_Face_Jaw'):
            sideMult = 1
            scaleFac = self.scale
    
            jawLoc = cmds.xform("Loc_Face_Jaw", q=True, t=True, ws=True)
    
            for side in 'LR':
                upperLipCurve = [(0, 0.2*scaleFac, 0), (1*scaleFac*sideMult, 0.2*scaleFac, 0), (2*scaleFac*sideMult, 0.2*scaleFac, 0), (3*scaleFac*sideMult, -0.2*scaleFac, 0)]
                lowerLipCurve = [(0, -0.2*scaleFac, 0), (1*scaleFac*sideMult, -0.2*scaleFac, 0), (2*scaleFac*sideMult, -0.2*scaleFac, 0), (3*scaleFac*sideMult, 0.2*scaleFac, 0)]
    
                upperLip = cmds.curve(p=upperLipCurve, n="CV_%s_UpperLip" % side)
                cmds.scale(2, 3, 3, upperLip)
                cmds.move(jawLoc[0], jawLoc[1]+8.5*scaleFac, jawLoc[2]+1*scaleFac, upperLip)
    
                lowerLip = cmds.curve(p=lowerLipCurve, n="CV_%s_LowerLip" % side)
                cmds.scale(2, 3, 3, lowerLip)
                cmds.move(jawLoc[0], jawLoc[1]+6*scaleFac, jawLoc[2]+1*scaleFac, lowerLip)
    
                smileMuscleCurve = [(0, 0, 0), (0.4*scaleFac*sideMult, -0.5*scaleFac, 0), (1*scaleFac*sideMult, -1.5*scaleFac, 0), (1.2*scaleFac*sideMult, -2.1*scaleFac, 0), (1.3*scaleFac*sideMult, -3*scaleFac, 0)]
    
                smileMuscle = cmds.curve(p=smileMuscleCurve, n="CV_%s_Smile" % side)
                cmds.scale(3, 3, 3, smileMuscle)
                cmds.move(jawLoc[0]+4.5*sideMult*scaleFac, jawLoc[1]+18*scaleFac, jawLoc[2], smileMuscle)
                sideMult = -1
        else:
            cmds.confirmDialog(title="Jaw Locator missing", message="Need Jaw Locator", button=['OK'])
    
    def addLocators(self):
        headLoc = cmds.spaceLocator(n='Loc_Face_Head')
        cmds.move(0, 371*self.distance, 8*self.distance, headLoc)
    
        centerLoc = cmds.spaceLocator(n='Loc_Face_Center')
        cmds.move(0, 336*self.distance, -3.5*self.distance, centerLoc)
    
        jawEndLoc = cmds.spaceLocator(n='Loc_Face_JawEnd')
        cmds.move(0, 325*self.distance, 0, jawEndLoc)
    
        curves = cmds.ls("CV_*")
        for curve in curves:
            cvs = cmds.ls(curve+'.cv[0:]', fl=True)
            for i, cv in enumerate(cvs):
                temp = cv.split('CV_')[1].split('.cv')[0]
    
                faceCluster = cmds.cluster(cv, cv, n="cluster_%s_%s" % (temp, str(i)))
                if cv == 'CV_R_UpperLip.cv[0]' or cv == 'CV_R_LowerLip.cv[0]':
                    pass
                else:
                    faceLoc = cmds.spaceLocator(name='Loc_Face_%s_%s' % (temp, str(i)))
                    clusterPos = cmds.xform(faceCluster[1]+'.rotatePivot', q=True, t=True, ws=True)
                    cmds.move(clusterPos[0], clusterPos[1], clusterPos[2], faceLoc)
                    cmds.scale(0.2, 0.2, 0.2, faceLoc)
    
                if faceCluster[1] == 'cluster_R_UpperLip_0Handle':
                    cmds.parent(faceCluster[1], 'Loc_Face_L_UpperLip_0')
                elif faceCluster[1] == 'cluster_R_LowerLip_0Handle':
                    cmds.parent(faceCluster[1], 'Loc_Face_L_LowerLip_0')
                else:
                    cmds.parent(faceCluster[1], faceLoc)
    
    def groupLocators(self):
        locs = cmds.ls('Loc_Face_*', transforms=True)
        locGrp = cmds.group(em=True, name='FaceLoc_Grp')
        cmds.parent(locs, locGrp)
    
        crvs = cmds.ls('CV_*', transforms=True)
        crvGrp = cmds.group(em=True, name='FaceCV_Grp')
        cmds.parent(crvs, crvGrp)
    
    def construct_joint(self):
        jointGrp = cmds.group(em=True, name='Joint_Grp')
        allLocs = cmds.ls('Loc_Face_*', transforms=True)
        for loc in allLocs:
            locPos = cmds.xform(loc, q=True, t=True, ws=True)
            cmds.select(clear=True)
            name = loc.split('Loc_Face_')[1]
            jnt = cmds.joint(p=locPos, name='Jnt_Face_'+name)
            cmds.parent(jnt, jointGrp)

        self.parentJoint()
    
    def parentJoint(self):
        leftEyeLidJnt = cmds.ls('Jnt_Face_L*EyeLid*')
        rightEyeLidJnt = cmds.ls('Jnt_Face_R*EyeLid*')
        smileJnt = cmds.ls('Jnt_Face*Smile*')
        foreHeadJnt = cmds.ls('Jnt_Face*ForeHeadBrow*')
        eyeBrowJnt = cmds.ls('Jnt_Face*EyeBrow*')
        lipJnt = cmds.ls('Jnt_Face*Lip*')
        eyeCenterJnt = cmds.ls('Jnt_Face*EyeCenter')
        cheekJnt = cmds.ls('Jnt_Face*Cheek')
    
        for jnt in leftEyeLidJnt:
            cmds.parent(jnt, 'Jnt*L_EyeCenter')
    
        for jnt in rightEyeLidJnt:
            cmds.parent(jnt, 'Jnt*R_EyeCenter')
    
        for jnt in smileJnt+foreHeadJnt+eyeBrowJnt+lipJnt+eyeCenterJnt+cheekJnt:
            cmds.parent(jnt, 'Jnt_Face_Center')
    
        cmds.parent('Jnt_Face_Jaw', 'Jnt_Face_JawEnd')
        cmds.parent('Jnt_Face_JawEnd', 'Jnt_Face_Center')
        cmds.parent('Jnt_Face_Head', 'Jnt_Face_Center')
    
    def place_controller(self):
        ctrlGrp = cmds.group(em=True, name='FaceCtrl_Grp')
        for side in ['L', 'R']:
            allJnts = cmds.ls('Jnt_Face_%s*' % side)
            for jnt in allJnts:
                ctrl = cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), radius=0.07, s=6, name='Ctrl_Face_%s' % jnt.split('Jnt_Face_')[1])
                ctrlOffsetGrp = cmds.group(em=True, n='CtrlOffset_Face_%s' % jnt.split('Jnt_Face_')[1])
                jntPos = cmds.xform(jnt, q=True, t=True, ws=True)
    
                cmds.move(jntPos[0], jntPos[1], jntPos[2], ctrl)
                cmds.move(jntPos[0], jntPos[1], jntPos[2], ctrlOffsetGrp)
                cmds.parent(cmds.ls(ctrl, transforms=True), ctrlOffsetGrp)
                cmds.parent(ctrlOffsetGrp, ctrlGrp)
    
            # Advance controller
            # Mouth Corner
            cornerEndPos = cmds.xform('Jnt_Face_%s_Smile_4' % side, q=True, t=True, ws=True)
            cornerStartPos = cmds.xform('Jnt_Face_%s_UpperLip_3' % side, q=True, t=True, ws=True)
            cornerCtrl = cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), radius=0.1, s=6, n='Ctrl_Face_%s_MouthCorner' % side)
            cmds.move((cornerStartPos[0]+cornerEndPos[0])/2, (cornerStartPos[1]+cornerEndPos[1])/2, (cornerStartPos[2]+cornerEndPos[2])/2, cornerCtrl)
            cmds.parent(cmds.ls(cornerCtrl, transforms=True), ctrlGrp)
    
            # Cheek Advance
            cheekPos = cmds.xform('Jnt_Face_%s_Cheek' % side, q=True, t=True, ws=True)
            smilePos = cmds.xform('Jnt_Face_%s_Smile_1' % side, q=True, t=True, ws=True)
            cheekAdCtrl = cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), radius=0.1, s=6, n='Ctrl_Face_%s_SecondCheek' % side)
            cmds.move((cheekPos[0] + smilePos[0]) / 2, (cheekPos[1] + smilePos[1]) / 2, (cheekPos[2] + smilePos[2]) / 2, cheekAdCtrl)
            cmds.parent(cmds.ls(cheekAdCtrl, transforms=True), ctrlGrp)
    
        jawPos = cmds.xform('Jnt_Face_Jaw', q=True, t=True, ws=True)
        jawEndPos = cmds.xform('Jnt_Face_JawEnd', q=True, t=True, ws=True)
        jawCtrl = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=0.12, s=6, n='Ctrl_Face_Jaw')[0]
        cmds.move(jawPos[0], jawPos[1], jawPos[2], jawCtrl)
        cmds.move(jawEndPos[0], jawEndPos[1], jawEndPos[2], jawCtrl+'.rotatePivot')
        cmds.move(jawEndPos[0], jawEndPos[1], jawEndPos[2], jawCtrl + '.scalePivot')
        cmds.parent(jawCtrl, ctrlGrp)
    
    def add_constraint(self):
        self.connectNode()

        filteredCtrl = []
        allCtrls = cmds.ls('Ctrl_Face*', transforms=True)
        for ctrl in allCtrls:
            if 'EyeLid' in ctrl or 'Jaw' in ctrl:
                name = ctrl.split('Ctrl_Face')[1]
                jnt = cmds.ls('Jnt_Face' + name)
                cmds.parentConstraint(ctrl, jnt, mo=True)
            elif 'EyeAim' in ctrl:
                pass
            elif 'MouthCorner' in ctrl:
                pass
            elif 'Second' in ctrl:
                pass
            elif 'EyeCenter' in ctrl:
                pass
            else:
                filteredCtrl.append(ctrl)
        for ctrl in filteredCtrl:
            name = ctrl.split('Ctrl_Face')[1]
            jnt = cmds.ls('Jnt_Face' + name)
            cmds.pointConstraint(ctrl, jnt)

        self.lock_controller()

    def connectNode(self):
        allctrls = cmds.ls("Ctrl_Face*", transforms=True)
        for ctrl in allctrls:
            cmds.makeIdentity(ctrl, apply=True, t=1, s=1, r=1)
        allctrloffsets = cmds.ls("CtrlOffset_Face*", transforms=True)

        for side in 'LR':
            eyeLidCtrl = cmds.ls('Ctrl_Face_%s_*EyeLid*' % side, transforms=True)
            eyeCenterPos = cmds.xform('Jnt_Face_%s_EyeCenter' % side, q=True, t=True, ws=True)
            for ctrl in eyeLidCtrl:
                cmds.move(eyeCenterPos[0], eyeCenterPos[1], eyeCenterPos[2], ctrl+'.scalePivot')
                cmds.move(eyeCenterPos[0], eyeCenterPos[1], eyeCenterPos[2], ctrl+'.rotatePivot')

        for i, ctrl in enumerate(allctrloffsets):
            cmds.makeIdentity(ctrl, apply=True, t=1, s=1, r=1)
            # Lip part advance control
            if 'Lip' in ctrl:
                value = ctrl.split('Lip_')[-1]
                multNode = cmds.shadingNode('multiplyDivide', asUtility=True, n='Node_Face_Influence'+str(i))
                for axis in 'XYZ':
                    cmds.setAttr(multNode+'.input2'+axis, 0.2 * int(value))
                cmds.setAttr(multNode+'.operation', 1)
                if value is '0':
                    pass
                else:
                    if '_L_' in ctrl:
                        cmds.connectAttr('Ctrl_Face_L_MouthCorner.translate', multNode+'.input1')
                    elif '_R_' in ctrl:
                        cmds.connectAttr('Ctrl_Face_R_MouthCorner.translate', multNode+'.input1')
                    cmds.connectAttr(multNode+'.output', ctrl+'.translate')
            if 'Smile' in ctrl:
                value = ctrl.split('_Smile_')[-1]
                addNode = cmds.shadingNode('plusMinusAverage', asUtility=True, n='Node_Smile_Distribution'+str(i))
                cmds.setAttr(addNode+'.operation', 1)
                multCornerNode = cmds.shadingNode('multiplyDivide', asUtility=True, n='Node_Smile_Corner_Influence'+str(i))
                cmds.setAttr(multCornerNode+'.operation', 1)
                for axis in 'XYZ':
                    cmds.setAttr(multCornerNode+'.input2'+axis, 0.15 * int(value))
                multCheekNode = cmds.shadingNode('multiplyDivide', asUtility=True, n='Node_Smile_Cheek_Influence'+str(i))
                cmds.setAttr(multCheekNode+'.operation', 1)
                for axis in 'XYZ':
                    cmds.setAttr(multCheekNode+'.input2'+axis, 0.15 * (4-int(value)))

                if '_L_' in ctrl:
                    cmds.connectAttr('Ctrl_Face_L_MouthCorner.translate', multCornerNode+'.input1')
                    cmds.connectAttr('Ctrl_Face_L_SecondCheek.translate', multCheekNode+'.input1')
                else:
                    cmds.connectAttr('Ctrl_Face_R_MouthCorner.translate', multCornerNode+'.input1')
                    cmds.connectAttr('Ctrl_Face_R_SecondCheek.translate', multCheekNode+'.input1')
                cmds.connectAttr(multCornerNode+'.output', addNode+'.input3D[0]')
                cmds.connectAttr(multCheekNode+'.output', addNode+'.input3D[1]')
                cmds.connectAttr(addNode+'.output3D', ctrl+'.translate')
            if '_Cheek' in ctrl:
                multNode = cmds.shadingNode('multiplyDivide', asUtility=True, n='Node_Cheek_Influence'+str(i))
                cmds.setAttr(multNode+'.operation', 1)
                for axis in 'XYZ':
                    cmds.setAttr(multNode+'.input2'+axis, 0.7)
                if '_L_' in ctrl:
                    cmds.connectAttr('Ctrl_Face_L_SecondCheek.translate', multNode+'.input1')
                elif '_R_' in ctrl:
                    cmds.connectAttr('Ctrl_Face_R_SecondCheek.translate', multNode+'.input1')
                cmds.connectAttr(multNode+'.output', ctrl+'.translate')

    def colorController(self):
        allCtrls = cmds.ls('Ctrl_Face_*')
        for ctrl in allCtrls:
            cmds.setAttr(ctrl+'.overrideEnabled', 1)
            cmds.setAttr(ctrl+'.overrideColor', 17)
        for side in 'LR':
            if side is 'L':
                controllers = cmds.ls('Ctrl_Face_L*')
                for ctrl in controllers:
                    if 'Ctrl_Face_L_LowerLip_0' in ctrl or 'Ctrl_Face_L_UpperLip_0' in ctrl:
                        pass
                    else:
                        cmds.setAttr(ctrl+'.overrideColor', 6)

            elif side is 'R':
                controllers = cmds.ls('Ctrl_Face_R*')
                for ctrl in controllers:
                    cmds.setAttr(ctrl+'.overrideColor', 13)

    def lock_controller(self):
        allCtrls = cmds.ls('Ctrl_Face_*', transforms=True)
        for ctrl in allCtrls:
            cmds.setAttr(ctrl+'.visibility', k=0, l=1)
            for axis in 'xyz':
                cmds.setAttr(ctrl+'.s'+axis, k=0, l=1)
            if 'Ctrl_Face_Jaw' in ctrl:
                for axis in 'xyz':
                    cmds.setAttr(ctrl+'.t'+axis, k=0, l=1)
                for axis in 'yz':
                    cmds.setAttr(ctrl+'.r'+axis, k=0, l=1)
            elif 'EyeLid' in ctrl:
                print(ctrl)
                for axis in 'xyz':
                    cmds.setAttr(ctrl+'.t'+axis, k=0, l=1)
            else:
                for axis in 'xyz':
                    cmds.setAttr(ctrl+'.r'+axis, k=0, l=1)
    
    def delete_guide(self):
        cmds.delete('FaceCV_Grp', 'FaceLoc_Grp')

    '''Utility methods'''
    #############################################################

    def mirror(self):
        rLocs = cmds.ls('Loc_Face_R_*', transforms=True)

        lLocs = cmds.ls('Loc_Face_L_*', transforms=True)
        lLocs.remove('Loc_Face_L_UpperLip_0')
        lLocs.remove('Loc_Face_L_LowerLip_0')

        for i, loc in enumerate(lLocs):
            pos = cmds.xform(loc, q=True, t=True, ws=True)
            cmds.move(-pos[0], pos[1], pos[2], rLocs[i])

    def ConnectWBody(self):
        neckJnt = cmds.ls('Rig_Neck')
        old_HeadJnt = cmds.ls('Rig_Head')
        cmds.delete(old_HeadJnt)
        new_HeadJnt = cmds.ls('Jnt_Face_Center')
        cmds.parent(new_HeadJnt, neckJnt)

        neckCtrl = cmds.ls('Ctrl_Neck')
        faceCtrls = cmds.ls('FaceCtrl_Grp')
        cmds.parent(faceCtrls, neckCtrl)