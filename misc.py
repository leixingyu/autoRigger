import maya.cmds as cmds

def batchParent(list, parent):
    for item in list:
        cmds.parent(item, parent, relative=False)
