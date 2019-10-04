import maya.cmds as cmds

# Create IKs
def createIK():
    for side in 'LR':
        # Arm IK
        if not cmds.objExists('RigIK_%s_ForeArm' % side):
            cmds.ikHandle(startJoint='RigIK_%s_Shoulder' % side, endEffector='RigIK_%s_Wrist' % side, name='%s_Arm_IK' % side, solver='ikRPsolver')
        else:
            cmds.ikHandle(startJoint='RigIK_%s_Shoulder' % side, endEffector='RigIK_%s_ForeArm' % side, name='%s_Arm_IK' % side, solver='ikRPsolver')
            wristPos = cmds.xform('RigIK_%s_Wrist' % side, q=True, t=True, ws=True)
            ikHandle = cmds.ikHandle('%s_Arm_IK' % side, query=True, endEffector=True)
            cmds.move(wristPos[0], wristPos[1], wristPos[2], '%s.scalePivot' % ikHandle, '%s.rotatePivot' % ikHandle, absolute=True)
        # Leg IK
        cmds.ikHandle(startJoint='Rig_%s_Pelvis' % side, endEffector='Rig_%s_Ankle' % side, name='%s_Leg_IK' % side, solver='ikRPsolver')

    # Spine IK
    spines = []
    curvePoints = []
    root = cmds.ls('Rig_Root')
    rootPos = cmds.xform(root, q=True, t=True, ws=True)
    curvePoints.append(rootPos)

    allSpines = cmds.ls('Rig_Spine_*')
    for spine in allSpines:
        if not cmds.ls(spine, type='shape'):
            spines.append(spine)
    for i, spine in enumerate(spines, start=1):
        spinePos = cmds.xform(spine, q=True, t=True, ws=True)
        curvePoints.append(spinePos)

    spineCount = len(allSpines)
    spineCurve = cmds.curve(p=curvePoints, name='spineCurve')
    cmds.inheritTransform(spineCurve, off=True)  # turning off inherit transform avoid curve move/scale twice as much

    CVs = cmds.ls('spineCurve.cv[0:]',fl=True)
    for i, cv in enumerate(CVs):
        if i is 0:
            cluster = cmds.cluster(cv, name='Cluster_Root')
        else:
            cluster = cmds.cluster(cv, name='Cluster_'+str(i))
        if i > 1:
            cmds.parent(cluster, 'Cluster_%sHandle' % str(i-1), relative=False)
        elif i is 1:
            cmds.parent(cluster, 'Cluster_RootHandle')

    cmds.ikHandle(startJoint='Rig_Root', endEffector='Rig_Spine_'+str(spineCount), name='Spine_IK', curve=spineCurve, createCurve=False, parentCurve=True, roc=True, solver='ikSplineSolver')

# Define Controller Shapes
def createController(spineValue, fingerValue):
    # Global Control Shape
    arrorPtList = [[2.0,0.0,2.0],[2.0,0.0,1.0],[3.0,0.0,1.0],[3.0,0.0,2.0],[5.0,0.0,0.0],[3.0,0.0,-2.0],[3.0,0.0,-1.0],[2.0,0.0,-1.0],
                 [2.0,0.0,-2.0],[1.0,0.0,-2.0],[1.0,0.0,-3.0],[2.0,0.0,-3.0],[0.0,0.0,-5.0],[-2.0,0.0,-3.0],[-1.0,0.0,-3.0],[-1.0,0.0,-2.0],
                 [-2.0,0.0,-2.0],[-2.0,0.0,-1.0],[-3.0,0.0,-1.0],[-3.0,0.0,-2.0],[-5.0,0.0,0.0],[-3.0,0.0,2.0],[-3.0,0.0,1.0],[-2.0,0.0,1.0],
                 [-2.0,0.0,2.0],[-1.0,0.0,2.0],[-1.0,0.0,3.0],[-2.0,0.0,3.0],[0.0,0.0,5.0],[2.0,0.0,3.0],[1.0,0.0,3.0],[1.0,0.0,2.0],[2.0,0.0,2.0]]
    globArror = cmds.curve(p=arrorPtList, degree=1, name='Global_Shape')
    cmds.scale(3,3,3, globArror)

    # Spine Control Shape
    spineShape = cmds.circle(nr=(0,1,0), c=(0,0,0), radius=1, s=8, name='Spine_Shape')
    selectionTip = cmds.select('Spine_Shape.cv[5]')
    cmds.move(0, 0, 1.5, selectionTip, relative=True)
    selectionEdge = cmds.select('Spine_Shape.cv[4]', 'Spine_Shape.cv[6]')
    cmds.scale(0.25, 0.25, 0.25, selectionEdge, relative=True)
    cmds.move(0, 0, 0.75, relative=True)
    cmds.rotate(0, 0, 90, spineShape)
    cmds.scale(0.5, 0.5, 0.5, spineShape)

    # Hand Control Shape
    handShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=10, name='Hand_Shape')[0]
    selection6 = cmds.select('Hand_Shape.cv[7:9]', 'Hand_Shape.cv[0]')
    cmds.scale(1.5, 1.5, 1.5, selection6, relative=True)
    cmds.scale(1.5, 1.5, 1, handShape)

    # Pole Vector Shape
    cmds.circle(nr=(0,1,0), c=(0,0,0), radius=1, s=8, name='PoleVector_Shape')
    selection1 = cmds.select('PoleVector_Shape.cv[6]', 'PoleVector_Shape.cv[0]')
    cmds.scale(0.5, 0.5, 0.5, selection1)
    cmds.move(-0.5, 0, 0, selection1)

    # Foot Control Shape
    footShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Foot_Shape')[0]
    selection2 = cmds.select('Foot_Shape.cv[0:2]')
    cmds.move(0, 0, -1.5, selection2, relative=True)
    cmds.scale(1.8, 1.8, 1.8, footShape)

    # Pelvis Control Shape
    cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=10, name='Pelvis_Shape')
    selection3 = cmds.select('Pelvis_Shape.cv[1]', 'Pelvis_Shape.cv[6]')
    cmds.scale(0.3, 0.3, 0.3, selection3)
    cmds.move(0, -0.8, 0, selection3, relative=True)
    selection4 = cmds.select('Pelvis_Shape.cv[3:4]', 'Pelvis_Shape.cv[8:9]')
    cmds.move(0, -0.2, 0, selection4, relative=True)
    cmds.xform('Pelvis_Shape', centerPivots=True)

    # Shoulder Control Shape
    shoulderShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=14, name='Shoulder_Shape')
    cmds.select('Shoulder_Shape.cv[3]', 'Shoulder_Shape.cv[13]')
    cmds.move(0, 0, 0.6, relative=True)
    cmds.select('Shoulder_Shape.cv[6]', 'Shoulder_Shape.cv[10]')
    cmds.move(0, 0, -0.6, relative=True)
    cmds.select('Shoulder_Shape.cv[4]', 'Shoulder_Shape.cv[12]')
    cmds.move(0, -1.5, -1.5, relative=True)
    cmds.select('Shoulder_Shape.cv[5]', 'Shoulder_Shape.cv[11]')
    cmds.move(0, -1.5, 1.5, relative=True)
    cmds.select('Shoulder_Shape.cv[0]', 'Shoulder_Shape.cv[9]')
    cmds.move(-0.2, 0.7, 0, relative=True)
    cmds.select('Shoulder_Shape.cv[1]', 'Shoulder_Shape.cv[8]')
    cmds.move(0, 0.7, 0, relative=True)
    cmds.select('Shoulder_Shape.cv[2]', 'Shoulder_Shape.cv[7]')
    cmds.move(0.2, 0.7, 0, relative=True)
    cmds.rotate(0, 90, 0, shoulderShape)
    cmds.scale(1.2, 1, 1, shoulderShape)

    # Finger Control Shape
    fingerShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=6, name='Finger_Shape')
    cmds.select('Finger_Shape.cv[3]', 'Finger_Shape.cv[5]')
    cmds.scale(0.2, 0.2, 0.2, relative=True)
    cmds.select('Finger_Shape.cv[1]', 'Finger_Shape.cv[4]')
    cmds.move(0, 0, 1, relative=True)
    cmds.scale(0.2, 0.2, 0.4, fingerShape)
    cmds.rotate(90, 0, 0, fingerShape)

    # Thumb Control Shape
    thumbShape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='Thumb_Shape')
    cmds.scale(0.2, 0.2, 0.2, thumbShape)

    placeController(spineValue, fingerValue)

# Place Controllers and freeze transform
def placeController(spineValue, fingerValue):
    globalCtrl = cmds.duplicate('Global_Shape', name='Global_Ctrl')
    #globalCtrlPos = cmds.xform('Loc_Master', query=True, t=True, ws=True)
    cmds.move(0, 0, 0, globalCtrl)
    cmds.makeIdentity(globalCtrl, apply=True, t=1, r=1, s=1)
    
    pelvisCtrl = cmds.duplicate('Pelvis_Shape', name='Pelvis_Ctrl')
    pelvisCtrlPos = cmds.xform('Rig_Base', q=True, t=True, ws=True)
    cmds.move(pelvisCtrlPos[0], pelvisCtrlPos[1], pelvisCtrlPos[2], pelvisCtrl)
    cmds.scale(5.5, 5, 5, pelvisCtrl)
    cmds.makeIdentity(pelvisCtrl, apply=True, t=1, r=1, s=1)

    for spine in range(0, spineValue+1):
        if spine is 0:
            spineCtrl = cmds.duplicate('Spine_Shape', name='Spine_Root_Ctrl')[0]
            spinePos = cmds.xform('Rig_Root', q=True, t=True, ws=True)
        else:
            spineCtrl = cmds.duplicate('Spine_Shape', name='Spine_%s_Ctrl' % str(spine))[0]
            spinePos = cmds.xform('Rig_Spine_%s' % str(spine), q=True, t=True, ws=True)
        cmds.move(spinePos[0], spinePos[1], spinePos[2] - 5, spineCtrl)
        cmds.move(spinePos[0], spinePos[1], spinePos[2], spineCtrl+'.scalePivot', spineCtrl+'.rotatePivot', absolute=True)
        cmds.makeIdentity(spineCtrl, apply=True, t=1, r=1, s=1)

    neck_Ctrl = cmds.duplicate('Thumb_Shape', name='Neck_Ctrl')
    neckPos = cmds.xform('Rig_Neck', q=True, t=True, ws=True)
    cmds.move(neckPos[0], neckPos[1], neckPos[2], neck_Ctrl)
    cmds.rotate(0, 0, 90, neck_Ctrl)
    cmds.scale(2.5, 2.5, 2.5, neck_Ctrl)
    cmds.makeIdentity(neck_Ctrl, apply=True, t=1, r=1, s=1)

    for side in 'LR':
        pvl_Ctrl = cmds.duplicate('PoleVector_Shape', name='%s_Leg_PoleVector_Ctrl' % side)
        pvl_Pos = cmds.xform('Rig_%s_Knee' % side, q=True, t=True, ws=True)
        cmds.move(pvl_Pos[0], pvl_Pos[1], pvl_Pos[2]+5, pvl_Ctrl)
        cmds.rotate(0, 90, 0, pvl_Ctrl)
        cmds.makeIdentity(pvl_Ctrl, apply=True, t=1, r=1, s=1)
 
        pva_Ctrl = cmds.duplicate('PoleVector_Shape', name='%s_Arm_PoleVector_Ctrl' % side)
        pva_Pos = cmds.xform('Rig_%s_Elbow' % side, q=True, t=True, ws=True)
        cmds.move(pva_Pos[0], pva_Pos[1], pva_Pos[2]-5, pva_Ctrl)
        cmds.rotate(0, -90, 0, pva_Ctrl)
        cmds.makeIdentity(pva_Ctrl, apply=True, t=1, r=1, s=1)

        foot_Ctrl = cmds.duplicate('Foot_Shape', name='%s_Foot_Ctrl' % side)
        cmds.addAttr(foot_Ctrl, longName='foot_Roll', attributeType='double', defaultValue=0, minValue=-10, maxValue=40, keyable=True)
        cmds.addAttr(foot_Ctrl, longName='foot_Bank', attributeType='double', defaultValue=0, minValue=-20, maxValue=20, keyable=True)
        foot_Pos = cmds.xform('Rig_%s_Ball' % side, q=True, t=True, ws=True)
        cmds.move(foot_Pos[0], foot_Pos[1], foot_Pos[2]+2, foot_Ctrl)
        cmds.makeIdentity(foot_Ctrl, apply=True, t=1, r=1, s=1)

        hand_Ctrl = cmds.duplicate('Hand_Shape', name='%s_Hand_Ctrl' % side)[0]
        cmds.addAttr(hand_Ctrl, longName='foreArm_Twist', attributeType='double', defaultValue=0, minValue=-90, maxValue=90, keyable=True)
        cmds.addAttr(hand_Ctrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=True)
        wrist_z_Rot = cmds.xform('Loc_%s_Shoulder' % side, q=True, ro=True, os=True)[2]
        wrist_x_Rot = cmds.xform('Loc_%s_Elbow' %side, q=True, ro=True, os=True)[0]
        hand_Pos = cmds.xform('Rig_%s_Wrist' % side, q=True, t=True, ws=True)
        if side is 'L':
            cmds.rotate(wrist_x_Rot, 0, wrist_z_Rot, hand_Ctrl, absolute=True)
            cmds.move(hand_Pos[0], hand_Pos[1], hand_Pos[2], hand_Ctrl, absolute=True)
        if side is 'R':
            cmds.rotate(-wrist_x_Rot, 0, -wrist_z_Rot, hand_Ctrl, absolute=True)
            cmds.move(hand_Pos[0], hand_Pos[1], hand_Pos[2], hand_Ctrl, absolute=True)
            cmds.rotate(0, 180, 0, hand_Ctrl, relative=True)
        cmds.move(hand_Pos[0], hand_Pos[1], hand_Pos[2], hand_Ctrl+'.scalePivot', hand_Ctrl+'.rotatePivot')
        cmds.makeIdentity(hand_Ctrl, apply=True, t=1, r=1, s=1)

        # Shoulder Control
        shoulder_Ctrl = cmds.duplicate('Shoulder_Shape', name='%s_Shoulder_Ctrl' % side)[0]
        shoulder_Pos = cmds.xform('Rig_%s_Shoulder' % side, q=True, t=True, ws=True)
        clavicle_Pos = cmds.xform('Rig_%s_Clavicle' % side, q=True, t=True, ws=True)
        elbow_Pos = cmds.xform('Rig_%s_Elbow' % side, q=True, t=True, ws=True)
        cmds.move(shoulder_Pos[0], shoulder_Pos[1] + 1, shoulder_Pos[2], shoulder_Ctrl, absolute=True)
        cmds.move(clavicle_Pos[0], clavicle_Pos[1], clavicle_Pos[2], shoulder_Ctrl + '.scalePivot', shoulder_Ctrl + '.rotatePivot', absolute=True)
        cmds.makeIdentity(shoulder_Ctrl, apply=True, t=1, r=1, s=1)

        # Hand IK
        IK_Ctrl = cmds.duplicate('Thumb_Shape', name='%s_IKHand_Ctrl' % side)[0]
        cmds.move(hand_Pos[0], hand_Pos[1], hand_Pos[2], IK_Ctrl, absolute=True)
        cmds.rotate(0, 0, wrist_z_Rot, IK_Ctrl)
        cmds.scale(1.5, 1.5, 1.5, IK_Ctrl)
        cmds.makeIdentity(IK_Ctrl, apply=True, t=1, r=1, s=1)

        # Hand FK
        FK_Shoulder_Ctrl = cmds.duplicate('Thumb_Shape', name='%s_FK_Shoulder_Ctrl' % side)[0]
        cmds.move(shoulder_Pos[0], shoulder_Pos[1], shoulder_Pos[2], FK_Shoulder_Ctrl, absolute=True)
        cmds.scale(1.5, 1.5, 1.5, FK_Shoulder_Ctrl)
        cmds.makeIdentity(FK_Shoulder_Ctrl, apply=True, t=1, r=1, s=1)

        FK_Arm_Offset = cmds.group(em=True, name='%s_FK_Arm_Offset_Grp' % side)
        cmds.move(shoulder_Pos[0], shoulder_Pos[1], shoulder_Pos[2], FK_Arm_Offset, absolute=True)
        cmds.parent(FK_Shoulder_Ctrl, FK_Arm_Offset, absolute=True)
        cmds.rotate(0, 0, wrist_z_Rot, FK_Arm_Offset)

        FK_Elbow_Ctrl = cmds.duplicate('Thumb_Shape', name='%s_FK_Elbow_Ctrl' % side)[0]
        cmds.move(elbow_Pos[0], elbow_Pos[1], elbow_Pos[2], FK_Elbow_Ctrl, absolute=True)
        cmds.scale(1.5, 1.5, 1.5, FK_Elbow_Ctrl)
        cmds.makeIdentity(FK_Elbow_Ctrl, apply=True, t=1, r=1, s=1)

        FK_Elbow_Offset = cmds.group(em=True, name='%s_FK_Elbow_Offset_Grp' % side)
        cmds.move(elbow_Pos[0], elbow_Pos[1], elbow_Pos[2], FK_Elbow_Offset, absolute=True)
        cmds.parent(FK_Elbow_Ctrl, FK_Elbow_Offset)
        cmds.rotate(0, 0, wrist_z_Rot, FK_Elbow_Offset)

        cmds.parent(FK_Elbow_Offset, FK_Shoulder_Ctrl)

        # Finger Control T-Pose

        for finger in range(1, fingerValue+1):
            if finger is 1:
                # Thumb
                for i in range(1, 4):
                    thumbCtrl = cmds.duplicate('Thumb_Shape', name='%s_Thumb_%s_Ctrl' % (side, i))[0]
                    thumbPos = cmds.xform('Rig_%s_Finger1_%s' % (side, i), q=True, t=True, ws=True)
                    cmds.move(thumbPos[0], thumbPos[1], thumbPos[2], thumbCtrl)
                    cmds.makeIdentity(thumbCtrl, apply=True, t=1, r=1, s=1)
                    if not i is 1:
                        cmds.parent(thumbCtrl, '%s_Thumb_%s_Ctrl' % (side, i-1))
                cmds.addAttr(hand_Ctrl, longName='Thumb_Curl', attributeType='double', defaultValue=0, minValue=-10, maxValue=40, keyable=True)
                cmds.parent('%s_Thumb_1_Ctrl' % side, hand_Ctrl, relative=True)
            else:
                # Other Finger
                for i in range(1, 4):
                    fingerCtrl = cmds.duplicate('Finger_Shape', name='%s_Finger%s_%s_Ctrl' % (side, finger, i))[0]
                    fingerPos = cmds.xform('Rig_%s_Finger%s_%s' % (side, finger, i), q=True, t=True, ws=True)
                    cmds.move(fingerPos[0], fingerPos[1]+1, fingerPos[2], fingerCtrl)
                    cmds.move(fingerPos[0], fingerPos[1], fingerPos[2], fingerCtrl+'.rotatePivot', fingerCtrl+'.scalePivot')
                    cmds.makeIdentity(fingerCtrl, apply=True, t=1, r=1, s=1)
                    if not i is 1:
                        cmds.parent(fingerCtrl, '%s_Finger%s_%s_Ctrl' % (side, finger, i-1))
                cmds.addAttr(hand_Ctrl, longName='finger%s_Curl' % finger, attributeType='double', defaultValue=0, minValue=-10, maxValue=40, keyable=True)
                cmds.rotate(wrist_x_Rot, 0, wrist_z_Rot, '%s_Finger%s_1_Ctrl' % (side, finger), absolute=True)
                cmds.parent('%s_Finger%s_1_Ctrl' % (side, finger), hand_Ctrl, relative=True)

        '''
        # Finger Control Not T-Pose
        for finger in range(1, fingerValue+1):
            if finger is 1:
                # Thumb
                for i in range(1, 4):
                    thumbCtrl = cmds.duplicate('Thumb_Shape', name='%s_Thumb_%s_Ctrl' % (side, i))[0]
                    thumbPos = cmds.xform('Rig_%s_Finger1_%s' % (side, i), q=True, t=True, ws=True)
                    cmds.rotate(wrist_x_Rot + 90, 0, wrist_z_Rot, thumbCtrl, absolute=True)
                    cmds.move(thumbPos[0], thumbPos[1], thumbPos[2], thumbCtrl)
                    cmds.makeIdentity(thumbCtrl, apply=True, t=1, r=1, s=1)
                    if not i is 1:
                        cmds.parent(thumbCtrl, '%s_Thumb_%s_Ctrl' % (side, i-1))
                cmds.addAttr(hand_Ctrl, longName='Thumb_Curl', attributeType='double', defaultValue=0, minValue=-10, maxValue=40, keyable=True)
                cmds.parent('%s_Thumb_1_Ctrl' % side, hand_Ctrl, relative=True)
            else:
                # Other Finger
                for i in range(1, 4):
                    fingerCtrl = cmds.duplicate('Finger_Shape', name='%s_Finger%s_%s_Ctrl' % (side, finger, i))[0]
                    fingerPos = cmds.xform('Rig_%s_Finger%s_%s' % (side, finger, i), q=True, t=True, ws=True)

                    cmds.move(fingerPos[0], fingerPos[1], fingerPos[2], fingerCtrl)
                    cmds.rotate(wrist_x_Rot + 90, 0, wrist_z_Rot, '%s_Finger%s_%s_Ctrl' % (side, finger, i), absolute=True)
                    cmds.move(fingerPos[0], fingerPos[1], fingerPos[2], fingerCtrl + '.rotatePivot', fingerCtrl + '.scalePivot')

                    if i is 1:
                        off_Grp = cmds.group(em=True, name='%s_Finger%s_Offset' % (side, finger))
                        cmds.move(fingerPos[0], fingerPos[1], fingerPos[2], off_Grp)
                        cmds.rotate(wrist_x_Rot + 90, 0, wrist_z_Rot, off_Grp, absolute=True)
                        cmds.move(fingerPos[0], fingerPos[1], fingerPos[2], off_Grp + '.rotatePivot', off_Grp + '.scalePivot')
                    if not i is 1:
                        cmds.parent(fingerCtrl, '%s_Finger%s_%s_Ctrl' % (side, finger, i-1))

                    cmds.move(0, 0, -1, '%s_Finger%s_%s_Ctrl' % (side, finger, i), relative=True)  # offset
                    cmds.move(0, 0, 1,  '%s_Finger%s_%s_Ctrl' % (side, finger, i) + '.rotatePivot',  '%s_Finger%s_%s_Ctrl' % (side, finger, i) + '.scalePivot', relative=True)
                    cmds.makeIdentity('%s_Finger%s_%s_Ctrl' % (side, finger, i), apply=True, t=1, r=1, s=1)

                cmds.addAttr(hand_Ctrl, longName='finger%s_Curl' % finger, attributeType='double', defaultValue=0, minValue=-10, maxValue=40, keyable=True)
                cmds.parent('%s_Finger%s_1_Ctrl' % (side, finger), off_Grp)
                cmds.makeIdentity('%s_Finger%s_1_Ctrl' % (side, finger), apply=True, t=1, r=1, s=1)
                cmds.parent(off_Grp, hand_Ctrl, relative=True)
    '''
    groupController(spineValue)
    deleteShape()

# Group Controllers
def groupController(spineValue):
    globalCtrl = cmds.ls('Global_Ctrl')
    ctrlGrp = cmds.group(em=True, n='Ctrl_Grp')
    pelvisCtrl = cmds.ls('Pelvis_Ctrl')
    rootCtrl = cmds.ls('Spine_Root_Ctrl')

    for spine in range(1, spineValue+1):
        spineCtrl = cmds.ls('Spine_%s_Ctrl' % str(spine))
        if spine is 1:
            cmds.parent(spineCtrl, rootCtrl)
        else:
            cmds.parent(spineCtrl, 'Spine_%s_Ctrl' % str(spine-1))

    topSpineCtrl = cmds.ls('Spine_%s_Ctrl' % str(spineValue))
    cmds.parent(cmds.ls('Neck_Ctrl'), topSpineCtrl)

    for side in 'LR':
        shoulderCtrl = cmds.ls('%s_Shoulder_Ctrl' % side)
        armPVCtrl = cmds.ls('%s_Arm_*_Ctrl' % side)
        handCtrl = cmds.ls('%s_Hand_Ctrl' % side)
        cmds.parent(armPVCtrl, shoulderCtrl)
        cmds.parent(handCtrl, shoulderCtrl)

        cmds.parent('%s_FK_Arm_Offset_Grp' % side, shoulderCtrl)
        cmds.parent('%s_IKHand_Ctrl' % side, shoulderCtrl)

        cmds.parent(shoulderCtrl, topSpineCtrl)

        legPVCtrl = cmds.ls('%s_Leg_*_Ctrl' % side)
        footCtrl = cmds.ls('%s_Foot_Ctrl' % side)
        cmds.parent(legPVCtrl, footCtrl)
        cmds.parent(footCtrl, ctrlGrp)

    cmds.parent(rootCtrl, pelvisCtrl)
    cmds.parent(pelvisCtrl, ctrlGrp)
    cmds.select(ctrlGrp)
    if not cmds.ls('Ctrl_Layer'):
        cmds.createDisplayLayer(nr=True, name='Ctrl_Layer')
    else:
        cmds.editDisplayLayerMembers('Ctrl_Layer', ctrlGrp)

    cmds.parent(ctrlGrp, globalCtrl)
    cmds.parent('Rig_Grp', globalCtrl)

    groupIK()
    colorController()
    lockAttr()

# Color-code Controllers
def colorController():
    allCtrls = cmds.ls('*_Ctrl')
    for ctrl in allCtrls:
        cmds.setAttr(ctrl+'.overrideEnabled', 1)
        cmds.setAttr(ctrl+'.overrideColor', 17)
    for side in 'LR':
        if side is 'L':
            controllers = cmds.ls('L_*_Ctrl')
            for ctrl in controllers:
                cmds.setAttr(ctrl+'.overrideColor', 6)
        elif side is 'R':
            controllers = cmds.ls('R_*_Ctrl')
            for ctrl in controllers:
                cmds.setAttr(ctrl+'.overrideColor', 13)
    cmds.setAttr('Global_Ctrl.overrideColor', 16)

# Lock Controllers
def lockAttr():
    pvs = cmds.ls('*_PoleVector_Ctrl')
    for pv in pvs:
        for transform in 'rs':
            for axis in 'xyz':
                cmds.setAttr(pv+'.'+transform+axis, l=1, k=0)

    footCtrls = cmds.ls('*_Foot_Ctrl')
    for ctrl in footCtrls:
        for axis in 'xyz':
            cmds.setAttr(ctrl+'.s'+axis, l=1, k=0)
        cmds.setAttr(ctrl+'.rz', l=1, k=0)

    shoulderCtrls = cmds.ls('*_Shoulder_Ctrl') # include shoulder control + shoulder fk control
    for ctrl in shoulderCtrls:
        for transform in 'ts':
            for axis in 'xyz':
                cmds.setAttr(ctrl+'.'+transform+axis, l=1, k=0)

    elbowCtrls = cmds.ls('*_Elbow_Ctrl')
    for ctrl in elbowCtrls:
        for transform in 'ts':
            for axis in 'xyz':
                cmds.setAttr(ctrl + '.' + transform + axis, l=1, k=0)

    handCtrls = cmds.ls('*_Hand_Ctrl')
    for ctrl in handCtrls:
        for axis in 'xyz':
            cmds.setAttr(ctrl+'.s'+axis, l=1, k=0)

    pelvisCtrl = cmds.ls('Pelvis_Ctrl')
    for ctrl in pelvisCtrl:
        for axis in 'xyz':
            cmds.setAttr(ctrl+'.s'+axis, l=1, k=0)

    fingerCtrls = cmds.ls('*_Finger*_Ctrl')
    for fingerCtrl in fingerCtrls:
        for transform in 's':
            for axis in 'xyz':
                cmds.setAttr(fingerCtrl+'.'+transform+axis, l=True,k=0)
        cmds.setAttr(fingerCtrl+'.rx', l=1, k=0)

    spineCtrls = cmds.ls('Spine_*_Ctrl')
    for ctrl in spineCtrls:
        for axis in 'xyz':
            cmds.setAttr(ctrl+'.s'+axis, l=1, k=0)

    '''allCtrls = cmds.ls('*_Ctrl')
    for ctrl in allCtrls:
        cmds.setAttr(ctrl+'.visibility', l=1, k=0)'''

# Group IK handles
def groupIK():
    IKs = cmds.ls('*_IK')
    IK_Grp = cmds.group(IKs, name='IK_Grp')
    cmds.parent(IK_Grp, 'Global_Ctrl')
    cluster = cmds.ls('Cluster_Root*', transforms=True)
    cmds.parent(cluster, IK_Grp)
    spineCurve = cmds.ls('spineCurve')
    cmds.parent(spineCurve, IK_Grp)

    cmds.select(IK_Grp)
    if not cmds.ls('IK_Layer'):
        cmds.createDisplayLayer(nr=True, name='IK_Layer')
    else:
        cmds.editDisplayLayerMembers('IK_Layer', IK_Grp)

    cmds.setAttr('IK_Layer.visibility', 0)

# Delete all controller shapes
def deleteShape():
    shapes = cmds.ls('*_Shape')
    cmds.delete(shapes)


