import maya.cmds as cmds

# Create Center Joints
def createJoints(value):
    cmds.group(em=True, n='Rig_Grp')

    root = cmds.ls('Loc_Root')
    rootPos = cmds.xform(root, q=True, t=True, ws=True)
    rootJnt = cmds.joint(p=rootPos, name='Rig_Root')

    spines = []
    allSpines = cmds.ls('Loc_Spine_*')
    for spine in allSpines:
        if not cmds.ls(spine, type = 'shape'):
            spines.append(spine)
    numSpine = len(spines)

    for i, spine in enumerate(spines, start=1):
        spinePos = cmds.xform(spine, q=True, t=True, ws=True)
        cmds.joint(p=spinePos, name='Rig_Spine_'+str(i))
    
    neck = cmds.ls('Loc_Neck')
    neckPos = cmds.xform(neck, q=True, t=True, ws=True)
    cmds.joint(p=neckPos, name='Rig_Neck')

    head = cmds.ls('Loc_Head')
    headPos = cmds.xform(head, q=True, t=True, ws=True)
    cmds.joint(p=headPos, name='Rig_Head')

    cmds.select(clear=True)
    base = cmds.ls('Loc_Base')
    basePos = cmds.xform(base, q=True, t=True, ws=True)
    baseJnt = cmds.joint(p=basePos, name='Rig_Base')
    cmds.parent(baseJnt, rootJnt)

    createLimbsJoints(numSpine)
    createHandsJoints(value)

# Create Symmetric Limbs Joints
def createLimbsJoints(value):
    for side in 'LR':
        # ARM Part
        cmds.select(clear=True)

        clavicle = cmds.ls('Loc_%s_Clavicle' % side)
        claviclePos = cmds.xform(clavicle, q=True, t=True, ws=True)
        clavicleJoint = cmds.joint(p=claviclePos, name='Rig_%s_Clavicle' % side)
        
        shoulder = cmds.ls('Loc_%s_Shoulder' % side)
        shoulderPos = cmds.xform(shoulder, q=True, t=True, ws=True)
        shoulderJoint = cmds.joint(p=shoulderPos, name='Rig_%s_Shoulder' % side)

        elbow = cmds.ls('Loc_%s_Elbow' % side)
        elbowPos = cmds.xform(elbow, q=True, t=True, ws=True)
        elbowJoint = cmds.joint(p=elbowPos, name='Rig_%s_Elbow' % side)

        # Secondary ForeArm Joint
        if cmds.objExists('Loc_%s_ForeArm' % side):
            foreArm = cmds.ls('Loc_%s_ForeArm' % side)
            foreArmPos = cmds.xform(foreArm, q=True, t=True, ws=True)
            cmds.joint(p=foreArmPos, name='Rig_%s_ForeArm' % side)

        wrist = cmds.ls('Loc_%s_Wrist' % side)
        wristPos = cmds.xform(wrist, q=True, t=True, ws=True)
        wristJoint = cmds.joint(p=wristPos, name='Rig_%s_Wrist' % side)

        cmds.select(clear=True)
        shoulderIKJoint = cmds.joint(p=shoulderPos, name='RigIK_%s_Shoulder' % side)
        elbowIKJoint = cmds.joint(p=elbowPos, name='RigIK_%s_Elbow' % side)
        cmds.joint(p=foreArmPos, name='RigIK_%s_ForeArm' % side)
        wristIKJoint = cmds.joint(p=wristPos, name='RigIK_%s_Wrist' % side)

        cmds.select(clear=True)
        shoulderFKJoint = cmds.joint(p=shoulderPos, name='RigFK_%s_Shoulder' % side)
        elbowFKJoint = cmds.joint(p=elbowPos, name='RigFK_%s_Elbow' % side)
        cmds.joint(p=foreArmPos, name='RigFK_%s_ForeArm' % side)
        wristFKJoint = cmds.joint(p=wristPos, name='RigFK_%s_Wrist' % side)

        cmds.parent(shoulderFKJoint, 'Rig_Grp')
        cmds.parent(shoulderIKJoint, 'Rig_Grp')

        cmds.parent(clavicleJoint, 'Rig_Spine_'+str(value))
        
        # LEG Part
        cmds.select(clear=True)
        pelvis = cmds.ls('Loc_%s_Pelvis' % side)
        pelvisPos = cmds.xform(pelvis, q=True, t=True, ws=True)
        pelvisJoint = cmds.joint(p=pelvisPos, name='Rig_%s_Pelvis' % side)

        knee = cmds.ls('Loc_%s_Knee' % side)
        kneePos = cmds.xform(knee, q=True, t=True, ws=True)
        kneeJoint = cmds.joint(p=kneePos, name='Rig_%s_Knee' % side)

        ankle = cmds.ls('Loc_%s_Ankle' % side)
        anklePos = cmds.xform(ankle, q=True, t=True, ws=True)
        ankleJoint = cmds.joint(p=anklePos, name='Rig_%s_Ankle' % side)

        ball = cmds.ls('Loc_%s_Ball' % side)
        ballPos = cmds.xform(ball, q=True, t=True, ws=True)
        ballJoint = cmds.joint(p=ballPos, name='Rig_%s_Ball' % side)

        toe = cmds.ls('Loc_%s_Toe' % side)
        toePos = cmds.xform(toe, q=True, t=True, ws=True)
        toeJoint = cmds.joint(p=toePos, name='Rig_%s_Toe' % side)
        
        # Secondary Reverse Foot Joint
        if cmds.objExists('Loc_%s_ReverseFoot' % side):
            cmds.select(clear=True)
            innerLoc = cmds.ls('Loc_%s_Foot_Inner' % side)
            innerPos = cmds.xform(innerLoc, q=True, t=True, ws=True)
            innerJoint = cmds.joint(p=innerPos, radius=0.8, name='Rig_%s_Reverse_Inner' % side)

            outerLoc = cmds.ls('Loc_%s_Foot_Outer' % side)
            outerPos = cmds.xform(outerLoc, q=True, t=True, ws=True)
            outerJoint = cmds.joint(p=outerPos, radius=0.8, name='Rig_%s_Reverse_Outer' % side)

            heelLoc = cmds.ls('Loc_%s_Heel' % side)
            heelPos = cmds.xform(heelLoc, q=True, t=True, ws=True)
            heelJoint = cmds.joint(p=heelPos, radius=0.8, name='Rig_%s_Heel' % side)

            reverseToeJoint = cmds.joint(p=toePos, radius=0.8, name='Rig_%s_Reverse_Toe' % side)
            reverseBallJoint = cmds.joint(p=ballPos, radius=0.8, name='Rig_%s_Reverse_Ball' % side)
            reverseAnkleJoint = cmds.joint(p=anklePos, radius=0.8, name='Rig_%s_Reverse_Ankle' % side)

            cmds.parent(innerJoint, 'Rig_Grp')

        cmds.parent(pelvisJoint, 'Rig_Base')

# Create Hand Joints
def createHandsJoints(value):
    for side in 'LR':
        for i in range(1, value+1):
            cmds.select(clear=True)
            for j in range(1, 5):
                finger = cmds.ls('Loc_%s_Finger%s_%s' % (side, i, j))
                fingerPos = cmds.xform(finger, q=True, t=True, ws=True)
                fingerJnt = cmds.joint(p=fingerPos, name='Rig_%s_Finger%s_%s' % (side, i, j))
                cmds.setAttr(fingerJnt+'.radius', 0.5)
                if j is 1:
                    cmds.parent(fingerJnt, 'Rig_%s_Wrist' % side)

# Orient Joints
def orientJoints():
    rig = cmds.select('Rig_Root', 'RigFK_L_Shoulder', 'RigIK_L_Shoulder', 'RigFK_R_Shoulder', 'RigIK_R_Shoulder')
    cmds.joint(e=True, ch=True, oj='xyz', sao='zup', zso=True)
    if not cmds.ls('Rig_Layer'):
        cmds.createDisplayLayer(nr=True, name='Rig_Layer')
    else:
        cmds.editDisplayLayerMembers('Rig_Layer', rig)

# Delete Joints
def deleteJoints():
    group = cmds.ls('Rig_Grp')
    cmds.delete(group)

def IKFKLayer():
    IKJoint = cmds.ls('RigIK_*')
    FKJoint = cmds.ls('RigFK_*')
    innerJoint = cmds.ls('Rig_*_Reverse_Inner')
    cmds.select(cmds.ls(FKJoint, IKJoint, innerJoint))

    if not cmds.ls('Secondary_Jnt_Layer'):
        cmds.createDisplayLayer(nr=True, name='Secondary_Jnt_Layer')
    else:
        cmds.editDisplayLayerMembers('Secondary_Jnt_Layer', innerJoint)
        cmds.editDisplayLayerMembers('Secondary_Jnt_Layer', IKJoint)
        cmds.editDisplayLayerMembers('Secondary_Jnt_Layer', FKJoint)

    cmds.setAttr('Secondary_Jnt_Layer.visibility', 0)