import maya.cmds as cmds

def batchParent(list, parent):
    """
    Grouping multiple objects to the same parent
    Args:
        list(list): list of objects to group
        parent(string): the parent
    """
    for item in list:
        cmds.parent(item, parent, relative=False)

def makeTextCurve(string, name):
    """
    Make a controller out of text
    Args:
        string(string): input text for the controller shape
        name(string): name of the controller

    Returns:
        transform group of the controller
    """
    temp = cmds.group(em=True)
    ctrl = cmds.group(em=True, name=name)

    text = cmds.textCurves(text=string)
    textShape = cmds.listRelatives(text, ad=True)
    for shape in textShape:
        if cmds.nodeType(shape) == 'nurbsCurve':
            cmds.parent(shape, temp, absolute=True, shape=True)
    cmds.delete(text)

    textShape = cmds.listRelatives(temp, children=True)
    for transform in textShape:
        cmds.makeIdentity(transform, apply=True, t=1, r=1, s=1)

    textShape = cmds.listRelatives(temp, ad=True)
    for shape in textShape:
        if cmds.nodeType(shape) == 'nurbsCurve':
            cmds.parent(shape, ctrl, relative=True, shape=True)
    cmds.delete(temp)
    cmds.select(clear=True)
    return ctrl

def orientJnt(jnt):
    if type(jnt) == 'list':
        for j in jnt:
            cmds.select(j, add=True)
    else:
        cmds.select(jnt)
    cmds.joint(e=True, ch=True, oj='xyz', zso=True)

def mirrorLoc():
    sl = cmds.ls(selection=True)
    if not sl:
        print('no locator selected')
    else:
        cmds.select(sl, hi=True)  # expand selection to the entire hierarchy
        left = cmds.ls(selection=True, transforms=True)
        right = []
        for loc in left:
            temp = loc.replace('left', 'right')
            right.append(temp.replace('_L_', '_R_'))

        if len(left) == len(right):
            for i in range(len(left)):
                transform = cmds.getAttr(left[i]+'.t')
                cmds.setAttr(right[i]+'.tx', -transform[0][0])
                cmds.setAttr(right[i]+'.ty', transform[0][1])
                cmds.setAttr(right[i]+'.tz', transform[0][2])
                rotation = cmds.getAttr(left[i]+'.r')
                cmds.setAttr(right[i]+'.rx', rotation[0][0])
                cmds.setAttr(right[i]+'.ry', -rotation[0][1])
                cmds.setAttr(right[i]+'.rz', -rotation[0][2])
        else: print('left and right locator not match')

