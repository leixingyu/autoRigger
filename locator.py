import maya.cmds as cmds

step = 3
lockMode = False

def createLocators(spineValue, fingerValue):
    # Create Fundamental Locators
    if not cmds.objExists('Loc_Master'):
        cmds.group(em=True, name='Loc_Master')

    root = cmds.spaceLocator(n='Loc_Root')
    cmds.move(0, 6.5*step, 0, root, absolute=True)
    cmds.parent(root, 'Loc_Master', relative=True)

    # Create Separate Locators
    createSpine(spineValue)
    createArms('left', spineValue)
    createArms('right', spineValue)
    createHand('left', fingerValue)
    createHand('right', fingerValue)
    createLegs('left')
    createLegs('right')
    createHead(spineValue)

    # Create Display Layer and add items
    locs = cmds.ls('Loc_*')
    cmds.select(locs)
    cmds.createDisplayLayer(nr=True, name='Loc_Layer')

# Spine Locators
'''
def createSpine(value):
    for i in range(1, value+1):
        spine = cmds.spaceLocator(n='Loc_Spine_%s' % str(i))
        if i is 1:
            cmds.parent(spine, 'Loc_Root', relative=True)
        else:
            cmds.parent(spine, 'Loc_Spine_%s' % str(i-1), relative=True)
        cmds.move(0, step, 0, spine, relative=True)'''

def createSpine(value):
    endSpine = cmds.spaceLocator(n='Loc_Spine_%s' % str(value))
    cmds.move(0, 30, -1, endSpine, relative=True)

    cmds.parent(endSpine, 'Loc_Master', relative=True)

# Arm Locators
def createArms(side, value):
    if side is 'left':
        armGrp = cmds.group(em=True, n='Loc_L_Arm_Grp')
        cmds.parent(armGrp, 'Loc_Spine_%s' % value)

        clavicle = cmds.spaceLocator(n='Loc_L_Clavicle')
        cmds.parent(clavicle, armGrp, relative=True)

        shoulder = cmds.spaceLocator(n='Loc_L_Shoulder')
        cmds.parent(shoulder, clavicle, relative=True)
        cmds.move(0.5*step, 1, 0, shoulder, relative=True)

        elbow = cmds.spaceLocator(n='Loc_L_Elbow')  # value on z-axis fixes ik flip issue
        cmds.parent(elbow, shoulder, relative=True)
        cmds.move(step*2, -0.5, 0, elbow, relative=True)

        wrist = cmds.spaceLocator(n='Loc_L_Wrist')
        cmds.parent(wrist, elbow, relative=True)
        cmds.move(step*2, 0, 0, wrist, relative=True)

        cmds.move(0.5*step, 28, -1, armGrp, absolute=True) # set base position for clavicle

    elif side is 'right':
        armGrp = cmds.group(em=True, n='Loc_R_Arm_Grp')
        cmds.parent(armGrp, 'Loc_Spine_%s' % value)

        clavicle = cmds.spaceLocator(n='Loc_R_Clavicle')
        cmds.parent(clavicle, armGrp, relative=True)

        shoulder = cmds.spaceLocator(n='Loc_R_Shoulder')
        cmds.parent(shoulder, clavicle, relative=True)
        cmds.move(-0.5 * step, 1, 0, shoulder, relative=True)

        elbow = cmds.spaceLocator(n='Loc_R_Elbow')
        cmds.parent(elbow, shoulder, relative=True)
        cmds.move(-step*2, -0.5, 0, elbow, relative=True)

        wrist = cmds.spaceLocator(n='Loc_R_Wrist')
        cmds.parent(wrist, elbow, relative=True)
        cmds.move(-step*2, 0, 0, wrist, relative=True)

        cmds.move(-0.5*step, 28, -1, armGrp, absolute=True)

# Hand Locators
def createHand(side, value):
    fingerWidth = 0.5
    if side is 'left':
        handGrp = cmds.group(em=True, n='Loc_L_Hand_Grp')
        cmds.parent(handGrp, 'Loc_L_Wrist', relative=True)
    elif side is 'right':
        handGrp = cmds.group(em=True, n='Loc_R_Hand_Grp')
        cmds.parent(handGrp, 'Loc_R_Wrist', relative=True)
    for i in range(1, value+1):
        pos = ((0.5*fingerWidth - (fingerWidth/(value-1))*(i-1))*step) # set the hand width according to width value
        createFingers(side, i, pos)

# Finger Locators
def createFingers(side, value, pos):
    fingScale = 0.2
    fingInitPos = 0.2 * step
    fingStep = 0.1 * step

    if side is 'left':
        for i in range(1, 5):
            finger = cmds.spaceLocator(n='Loc_L_Finger'+str(value)+'_'+str(i))
            if i is 1:
                cmds.parent(finger, 'Loc_L_Hand_Grp', relative=True)
                cmds.move(fingInitPos, 0, 0, finger, relative=True)
                cmds.scale(fingScale, fingScale, fingScale, finger)
            else:
                cmds.parent(finger, 'Loc_L_Finger'+str(value)+'_'+str(i-1), relative=True)
                cmds.move(fingStep, 0, 0, finger, relative=True)
        cmds.move(0, 0, pos, 'Loc_L_Finger'+str(value)+'_1', relative=True)
    elif side is 'right':
        for i in range(1, 5):
            finger = cmds.spaceLocator(n='Loc_R_Finger'+str(value)+'_'+str(i))
            if i is 1:
                cmds.parent(finger, 'Loc_R_Hand_Grp', relative=True)
                cmds.move(-fingInitPos, 0, 0, finger, relative=True)
                cmds.scale(fingScale, fingScale, fingScale, finger)
            else:
                cmds.parent(finger, 'Loc_R_Finger'+str(value)+'_'+str(i-1), relative=True)
                cmds.move(-fingStep, 0, 0, finger, relative=True)
        cmds.move(0, 0, pos, 'Loc_R_Finger'+str(value)+'_1', relative=True)

# Leg Locators
def createLegs(side):
    if not cmds.objExists('Loc_Base'):
        base = cmds.spaceLocator(n='Loc_Base')
        cmds.parent(base, 'Loc_Root', relative=True)
        cmds.move(0, -0.3*step, 0, base, relative=True)

    if side is 'left':
        legGrp = cmds.group(em=True, n='Loc_L_Leg_Grp')
        cmds.parent(legGrp, 'Loc_Base', relative=True)
        cmds.move(0.75*step, 0, 0, legGrp, relative=True)

        pelvis = cmds.spaceLocator(n='Loc_L_Pelvis')
        cmds.parent(pelvis, legGrp, relative=True)

        knee = cmds.spaceLocator(n='Loc_L_Knee')
        cmds.parent(knee, pelvis, relative=True)
        cmds.move(0, -3*step, 0.5, knee, relative=True) # value on z-axis fixes ik flip

        ankle = cmds.spaceLocator(n='Loc_L_Ankle')
        cmds.parent(ankle, knee, relative=True)
        cmds.move(0, -2.25*step, -1, ankle, relative=True)
        createFeet(side)

    elif side is 'right':
        legGrp = cmds.group(em=True, n='Loc_R_Leg_Grp')
        cmds.parent(legGrp, 'Loc_Base', relative=True)
        cmds.move(-0.75*step, 0, 0, legGrp, relative=True)

        pelvis = cmds.spaceLocator(n='Loc_R_Pelvis')
        cmds.parent(pelvis, legGrp, relative=True)

        knee = cmds.spaceLocator(n='Loc_R_Knee')
        cmds.parent(knee, pelvis, relative=True)
        cmds.move(0, -3*step, 0.5, knee, relative=True)

        ankle = cmds.spaceLocator(n='Loc_R_Ankle')
        cmds.parent(ankle, knee, relative=True)
        cmds.move(0, -2.25*step, -1, ankle, relative=True)
        createFeet(side)

# Feet Locators
def createFeet(side):
    if side is 'left':
        ball = cmds.spaceLocator(n='Loc_L_Ball')
        cmds.parent(ball, 'Loc_L_Ankle')
        cmds.move(2, 0, 0.8, ball, absolute=True)

        toe = cmds.spaceLocator(n='Loc_L_Toe')
        cmds.parent(toe, ball)
        cmds.move(2, 0, 3.2, toe, absolute=True)
    elif side is 'right':
        ball = cmds.spaceLocator(n='Loc_R_Ball')
        cmds.parent(ball, 'Loc_R_Ankle')
        cmds.move(-2, 0, 0.8, ball, absolute=True)

        toe = cmds.spaceLocator(n='Loc_R_Toe')
        cmds.parent(toe, ball)
        cmds.move(-2, 0, 3.2, toe, absolute=True)

# Head Locators
def createHead(value):
    neck = cmds.spaceLocator(n='Loc_Neck')
    cmds.parent(neck, 'Loc_Spine_'+str(value), relative=True)
    cmds.move(0, 2, 1, neck, relative=True)

    head = cmds.spaceLocator(n='Loc_Head')
    cmds.parent(head, neck, relative=True)
    cmds.move(0, step, (1/2.0)*step, head, relative=True)

# Create Secondary Locators: ForeArm & Reverse Foot
def secondaryLocators(value):

    # Additional Spine
    rootPos = cmds.xform('Loc_Root', q=True, t=True, ws=True)
    endPos = cmds.xform('Loc_Spine_%s' % str(value), q=True, t=True, ws=True)
    seg = []
    for i in range(3):
        seg.append((endPos[i]-rootPos[i])/value)
    currentPos = rootPos
    for i in range(1, value):
        currentSpine = cmds.spaceLocator(n='Loc_Spine_%s' % str(i))
        currentPos = [x + y for x, y in zip(seg, currentPos)]
        cmds.move(currentPos[0], currentPos[1], currentPos[2], currentSpine, absolute=True)
        cmds.parent(currentSpine, 'Loc_Master', relative=True)

    # ForeArm Twist
    for side in 'LR':
        elbowPos = cmds.xform('Loc_%s_Elbow' % side, q=True, t=True, ws=True)
        wristPos = cmds.xform('Loc_%s_Wrist' % side, q=True, t=True, ws=True)

        foreArmPos = [(elbowPos[0]+wristPos[0])/2, (elbowPos[1]+wristPos[1])/2, (elbowPos[2]+wristPos[2])/2]
        foreArm = cmds.spaceLocator(n='Loc_%s_ForeArm' % side)

        cmds.parent(foreArm, 'Loc_%s_Elbow' % side)
        cmds.move(foreArmPos[0], foreArmPos[1], foreArmPos[2], foreArm, absolute=True)
        cmds.parent('Loc_%s_Wrist' % side, foreArm, relative=False)

    # Reverse Foot
    for side in 'LR':
        reverseGrp = cmds.group(em=True, n='Loc_%s_ReverseFoot' % side)
        ballPos = cmds.xform('Loc_%s_Ball' % side, q=True, t=True, ws=True)

        innerLoc = cmds.spaceLocator(n='Loc_%s_Foot_Inner' % side)
        if side is 'L':
            cmds.move(ballPos[0]-0.3*step, ballPos[1], ballPos[2], innerLoc, absolute=True)
        else:
            cmds.move(ballPos[0]+0.3 * step, ballPos[1], ballPos[2], innerLoc, absolute=True)

        outerLoc = cmds.spaceLocator(n='Loc_%s_Foot_Outer' % side)
        if side is 'L':
            cmds.move(ballPos[0]+0.3*step, ballPos[1], ballPos[2],outerLoc, absolute=True)
        else:
            cmds.move(ballPos[0]-0.3 * step, ballPos[1], ballPos[2], outerLoc, absolute=True)
        heelLoc = cmds.spaceLocator(n='Loc_%s_Heel' % side)
        cmds.move(ballPos[0], ballPos[1], ballPos[2]-0.6*step, heelLoc, absolute=True)

        cmds.parent(heelLoc, outerLoc)
        cmds.parent(outerLoc, innerLoc)
        cmds.parent(innerLoc, reverseGrp)
        cmds.parent(reverseGrp, 'Loc_%s_Leg_Grp' % side)

# Mirror Locators
def mirror(side):
    leftList = [] # extracted list of all the left locators' transform node
    leftLocs = cmds.ls('Loc_L_*')
    for leftLoc in leftLocs:
        if not cmds.ls(leftLoc, shapes=True):
            leftList.append(leftLoc)

    rightList = [] # extracted list of all the right locators' transform node
    rightLocs = cmds.ls('Loc_R_*')
    for rightLoc in rightLocs:
        if not cmds.ls(rightLoc, shapes=True):
            rightList.append(rightLoc)
    rightList = sorted(rightList)

    if not len(leftList) == len(rightList):
        print('not symmetrical')
    else:
        if side is 'left':
            for i in range(0, len(leftList)):
                transform = cmds.getAttr(leftList[i]+'.t')
                cmds.setAttr(rightList[i]+'.tx', -transform[0][0])
                cmds.setAttr(rightList[i] + '.ty', transform[0][1])
                cmds.setAttr(rightList[i] + '.tz', transform[0][2])
                rotation = cmds.getAttr(leftList[i]+'.r')
                cmds.setAttr(rightList[i] + '.rx', rotation[0][0])
                cmds.setAttr(rightList[i] + '.ry', -rotation[0][1])
                cmds.setAttr(rightList[i] + '.rz', -rotation[0][2])
        elif side is 'right':
            for i in range(0, len(rightList)):
                transform = cmds.getAttr(rightList[i] + '.t')
                cmds.setAttr(leftList[i] + '.tx', -transform[0][0])
                cmds.setAttr(leftList[i] + '.ty', transform[0][1])
                cmds.setAttr(leftList[i] + '.tz', transform[0][2])
                rotation = cmds.getAttr(rightList[i] + '.r')
                cmds.setAttr(leftList[i] + '.rx', rotation[0][0])
                cmds.setAttr(leftList[i] + '.ry', -rotation[0][1])
                cmds.setAttr(leftList[i] + '.rz', -rotation[0][2])

# Delete Locators
def deleteLocators():
    group = cmds.ls('Loc_*')
    cmds.delete(group)

# Lock attribute function (Not in use)
'''def lockAll(mode=lockMode):
    global lockMode
    axis = 'xyz'
    attrs = 'trs'
    nodes = cmds.listRelatives('Loc_*', allParents=True)
    for node in nodes:
        for axe in axis:
            for attr in attrs:
                cmds.setAttr(node+'.'+attr+axe, lock=mode)
    if lockMode:
        lockMode = False
    else:
        lockMode = True'''
