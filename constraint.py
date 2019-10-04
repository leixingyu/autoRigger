import maya.cmds as cmds

# Build Constraint on Controllers
def buildConstraint(spineValue, fingerValue):
    for side in 'LR':
        # Foot Constraint
        heelLoc = cmds.xform('Rig_%s_Heel' % side, q=True, t=True, ws=True)
        footCtrl = cmds.ls('%s_Foot_Ctrl' % side)[0]
        cmds.move(heelLoc[0], heelLoc[1], heelLoc[2], '%s.scalePivot' % footCtrl, '%s.rotatePivot' % footCtrl,
                  absolute=True)
        innerJnt = cmds.ls('Rig_%s_Reverse_Inner' % side)[0]
        cmds.parentConstraint(footCtrl, innerJnt, sr='z', mo=True)

        outerJnt = cmds.ls('Rig_%s_Reverse_Outer' % side)[0]

        reverseAnkle = cmds.ls('Rig_%s_Reverse_Ankle' % side)
        footIK = cmds.ls('%s_Leg_IK' % side)
        cmds.pointConstraint(reverseAnkle, footIK, mo=True)

        ankelJnt = cmds.ls('Rig_%s_Ankle' % side)
        #cmds.orientConstraint(reverseAnkle, ankelJnt, mo=True)
        
        ballJnt = cmds.ls('Rig_%s_Ball' % side)
        reverseBall = cmds.ls('Rig_%s_Reverse_Ball' % side)[0]
        #cmds.parentConstraint(reverseBall, ballJnt)

        toeJnt = cmds.ls('Rig_%s_Toe' % side)
        reverseToe = cmds.ls('Rig_%s_Reverse_Toe' % side)[0]
        #cmds.pointConstraint(reverseToe, toeJnt)

        cmds.orientConstraint(reverseBall, ankelJnt, mo=True)
        cmds.orientConstraint(reverseToe, ballJnt, mo=True)

        legPoleVec = cmds.ls('%s_Leg_PoleVector_Ctrl' % side)
        cmds.poleVectorConstraint(legPoleVec, footIK)

        # Set Foot Roll
        cmds.setDrivenKeyframe('Rig_%s_Heel.rotateX' % side, currentDriver='%s_Foot_Ctrl.foot_Roll' % side, driverValue=0, value=0)
        cmds.setDrivenKeyframe('Rig_%s_Heel.rotateX' % side, currentDriver='%s_Foot_Ctrl.foot_Roll' % side, driverValue=-10, value=-25)

        cmds.setDrivenKeyframe(reverseBall+'.rotateX', currentDriver='%s_Foot_Ctrl.foot_Roll' % side, driverValue=0, value=0)
        cmds.setDrivenKeyframe(reverseBall+'.rotateX', currentDriver='%s_Foot_Ctrl.foot_Roll' % side, driverValue=20, value=25)

        cmds.setDrivenKeyframe(reverseToe+'.rotateX', currentDriver='%s_Foot_Ctrl.foot_Roll' % side, driverValue=20, value=0)
        cmds.setDrivenKeyframe(reverseToe+'.rotateX', currentDriver='%s_Foot_Ctrl.foot_Roll' % side, driverValue=40, value=25)

        # Set Foot Bank
        cmds.setDrivenKeyframe(innerJnt + '.rotateZ', currentDriver='%s_Foot_Ctrl.foot_Bank' % side, driverValue=0, value=0)
        cmds.setDrivenKeyframe(outerJnt + '.rotateZ', currentDriver='%s_Foot_Ctrl.foot_Bank' % side, driverValue=0, value=0)
        if side is 'R':
            cmds.setDrivenKeyframe(innerJnt + '.rotateZ', currentDriver='%s_Foot_Ctrl.foot_Bank' % side, driverValue=-20, value=-30)
            cmds.setDrivenKeyframe(outerJnt + '.rotateZ', currentDriver='%s_Foot_Ctrl.foot_Bank' % side, driverValue=20, value=30)
        else:
            cmds.setDrivenKeyframe(innerJnt + '.rotateZ', currentDriver='%s_Foot_Ctrl.foot_Bank' % side, driverValue=-20, value=30)
            cmds.setDrivenKeyframe(outerJnt + '.rotateZ', currentDriver='%s_Foot_Ctrl.foot_Bank' % side, driverValue=20, value=-30)

        # Arm & Hand Constraint
        # Hand IK Constraint
        cmds.pointConstraint('Rig_%s_Shoulder' % side, 'RigIK_%s_Shoulder' % side)
        cmds.pointConstraint('Rig_%s_Shoulder' % side, 'RigFK_%s_Shoulder' % side)

        handCtrl = cmds.ls('%s_Hand_Ctrl' % side)
        wristJnt = cmds.ls('Rig_%s_Wrist' % side)
        armIK = cmds.ls('%s_Arm_IK' % side)
        handIK = cmds.ls('%s_IKHand_Ctrl' % side)

        cmds.pointConstraint(handIK, armIK, mo=True)
        cmds.pointConstraint(wristJnt, handCtrl, mo=True)
        cmds.orientConstraint(handCtrl, wristJnt, mo=True)

        cmds.pointConstraint('RigIK_%s_Wrist' % side, 'RigFK_%s_Wrist' % side, wristJnt)
        cmds.orientConstraint('RigIK_%s_Elbow' % side, 'RigFK_%s_Elbow' % side, 'Rig_%s_Elbow' % side)
        cmds.orientConstraint('RigIK_%s_Shoulder' % side, 'RigFK_%s_Shoulder' % side, 'Rig_%s_Shoulder' % side)
        cmds.orientConstraint('RigIK_%s_ForeArm' % side, 'RigFK_%s_ForeArm' % side, 'Rig_%s_ForeArm' % side, sk='x')

        # Hand FK Constraint
        if side is 'L':
            cmds.orientConstraint('%s_FK_Shoulder_Ctrl' % side, 'RigFK_%s_Shoulder' % side, mo=True)
        else:
            cmds.orientConstraint('%s_FK_Shoulder_Ctrl' % side, 'RigFK_%s_Shoulder' % side, mo=True)
        cmds.orientConstraint('%s_FK_Elbow_Ctrl' % side, 'RigFK_%s_Elbow' % side, mo=True)

        # FK/IK Switch
        # ForeArm
        cmds.setDrivenKeyframe('Rig_%s_ForeArm_orientConstraint1.RigIK_%s_ForeArmW0' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=1)
        cmds.setDrivenKeyframe('Rig_%s_ForeArm_orientConstraint1.RigFK_%s_ForeArmW1' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=0)
        cmds.setDrivenKeyframe('Rig_%s_ForeArm_orientConstraint1.RigIK_%s_ForeArmW0' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=0)
        cmds.setDrivenKeyframe('Rig_%s_ForeArm_orientConstraint1.RigFK_%s_ForeArmW1' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=1)

        cmds.setDrivenKeyframe('Rig_%s_Elbow_orientConstraint1.RigIK_%s_ElbowW0' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=1)
        cmds.setDrivenKeyframe('Rig_%s_Elbow_orientConstraint1.RigFK_%s_ElbowW1' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=0)
        cmds.setDrivenKeyframe('Rig_%s_Elbow_orientConstraint1.RigIK_%s_ElbowW0' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=0)
        cmds.setDrivenKeyframe('Rig_%s_Elbow_orientConstraint1.RigFK_%s_ElbowW1' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=1)

        cmds.setDrivenKeyframe('Rig_%s_Wrist_pointConstraint1.RigIK_%s_WristW0' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=1)
        cmds.setDrivenKeyframe('Rig_%s_Wrist_pointConstraint1.RigFK_%s_WristW1' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=0)
        cmds.setDrivenKeyframe('Rig_%s_Wrist_pointConstraint1.RigIK_%s_WristW0' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=0)
        cmds.setDrivenKeyframe('Rig_%s_Wrist_pointConstraint1.RigFK_%s_WristW1' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=1)

        cmds.setDrivenKeyframe('Rig_%s_Shoulder_orientConstraint1.RigIK_%s_ShoulderW0' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=1)
        cmds.setDrivenKeyframe('Rig_%s_Shoulder_orientConstraint1.RigFK_%s_ShoulderW1' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=0)
        cmds.setDrivenKeyframe('Rig_%s_Shoulder_orientConstraint1.RigIK_%s_ShoulderW0' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=0)
        cmds.setDrivenKeyframe('Rig_%s_Shoulder_orientConstraint1.RigFK_%s_ShoulderW1' % (side, side), currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=1)

        # visibilty of controller
        #IK visiblity
        cmds.setDrivenKeyframe('%s_Arm_PoleVector_Ctrl.visibility' % side, currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=1)
        cmds.setDrivenKeyframe('%s_IKHand_Ctrl.visibility' % side, currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=1)
        cmds.setDrivenKeyframe('%s_Arm_PoleVector_Ctrl.visibility' % side, currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=0)
        cmds.setDrivenKeyframe('%s_IKHand_Ctrl.visibility' % side, currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=0)
        #FK visiblity
        cmds.setDrivenKeyframe('%s_FK_Elbow_Ctrl.visibility' % side, currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=1)
        cmds.setDrivenKeyframe('%s_FK_Shoulder_Ctrl.visibility' % side, currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=0, value=1)
        cmds.setDrivenKeyframe('%s_FK_Elbow_Ctrl.visibility' % side, currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=0)
        cmds.setDrivenKeyframe('%s_FK_Shoulder_Ctrl.visibility' % side, currentDriver='%s_Hand_Ctrl.FK_IK' % side, driverValue=1, value=0)

        armPoleVec = cmds.ls('%s_Arm_PoleVector_Ctrl' % side)
        cmds.poleVectorConstraint(armPoleVec, armIK)

        cmds.connectAttr('%s_Hand_Ctrl.foreArm_Twist' % side, 'Rig_%s_ForeArm.rotateX' % side)

        # Shoulder Constraint
        shoulderCtrl = cmds.ls('%s_Shoulder_Ctrl' % side)
        clavicleJnt = cmds.ls('Rig_%s_Clavicle' % side)
        cmds.parentConstraint(shoulderCtrl, clavicleJnt, mo=True)

        # Finger Constraint
        for finger in range(1, fingerValue+1):
            # Thumb Curl
            # non T-pose, T-pose is rotateY
            if finger is 1:
                for i in range(1, 4):
                    thumbCtrl = cmds.ls('%s_Thumb_%s_Ctrl' % (side, i))[0]
                    thumbJnt = cmds.ls('Rig_%s_Finger1_%s' % (side, i))
                    cmds.orientConstraint(thumbCtrl, thumbJnt, mo=True)
                    cmds.setDrivenKeyframe(thumbCtrl + '.rotateZ', currentDriver='%s_Hand_Ctrl.Thumb_Curl' % side, driverValue=0, value=0)
                    if side is 'L':
                        cmds.setDrivenKeyframe(thumbCtrl + '.rotateZ', currentDriver='%s_Hand_Ctrl.Thumb_Curl' % side, driverValue=-10, value=15)
                        cmds.setDrivenKeyframe(thumbCtrl + '.rotateZ', currentDriver='%s_Hand_Ctrl.Thumb_Curl' % side, driverValue=40, value=-60)
                    elif side is 'R':
                        cmds.setDrivenKeyframe(thumbCtrl + '.rotateZ', currentDriver='%s_Hand_Ctrl.Thumb_Curl' % side, driverValue=-10, value=-15)
                        cmds.setDrivenKeyframe(thumbCtrl + '.rotateZ', currentDriver='%s_Hand_Ctrl.Thumb_Curl' % side, driverValue=40, value=60)
            # Other Finger Curl
            # non T-pose, T-pose is rotateZ
            else:
                for i in range(1, 4):
                    fingerCtrl = cmds.ls('%s_Finger%s_%s_Ctrl' % (side, finger, i))[0]
                    fingerJnt = cmds.ls('Rig_%s_Finger%s_%s' % (side, finger, i))
                    cmds.orientConstraint(fingerCtrl, fingerJnt, mo=True)
                    cmds.setDrivenKeyframe(fingerCtrl+'.rotateY', currentDriver='%s_Hand_Ctrl.finger%s_Curl' % (side, finger), driverValue=0, value=0)
                    if side is 'R':
                        cmds.setDrivenKeyframe(fingerCtrl + '.rotateY', currentDriver='%s_Hand_Ctrl.finger%s_Curl' % (side, finger), driverValue=-10, value=-15)
                        cmds.setDrivenKeyframe(fingerCtrl + '.rotateY', currentDriver='%s_Hand_Ctrl.finger%s_Curl' % (side, finger), driverValue=40, value=60)
                    elif side is 'L':
                        cmds.setDrivenKeyframe(fingerCtrl + '.rotateY', currentDriver='%s_Hand_Ctrl.finger%s_Curl' % (side, finger), driverValue=-10, value=15)
                        cmds.setDrivenKeyframe(fingerCtrl + '.rotateY', currentDriver='%s_Hand_Ctrl.finger%s_Curl' % (side, finger), driverValue=40, value=-60)

    # Neck Constraint
    NeckJnt = cmds.ls('Rig_Neck')
    NeckCtrl = cmds.ls('Neck_Ctrl')
    cmds.parentConstraint(NeckCtrl, NeckJnt, mo=True)

    # Spine Constraint
    for spine in range(0, spineValue+1):
        if spine is 0:
            spineCluster = cmds.ls('Cluster_RootHandle')
            spineCtrl = cmds.ls('Spine_Root_Ctrl')
        else:
            spineCluster = cmds.ls('Cluster_%sHandle' % str(spine))
            spineCtrl = cmds.ls('Spine_%s_Ctrl' % str(spine))
        cmds.pointConstraint(spineCtrl, spineCluster)

        if spine is spineValue:
            cmds.connectAttr('Spine_%s_Ctrl.rotateY' % str(spine), 'Spine_IK.twist')

    # Pelvis Constraint
    baseJnt = cmds.ls('Rig_Base')
    pelvisCtrl = cmds.ls('Pelvis_Ctrl')
    cmds.parentConstraint(pelvisCtrl, baseJnt, mo=True)

# Bind Skin Geo
def bindSkin():
    mesh = cmds.ls(selection=True)[0]
    cmds.createDisplayLayer(nr=True, name='Geo_Layer')
    cmds.skinCluster(mesh, 'Rig_Root', bm=3, sm=1, dr=0.1)
    cmds.geomBind('skinCluster1', bm=3, gvp=[256, 1])

def deleteLayer():
    layers = cmds.ls('*_Layer')
    cmds.delete(layers)


