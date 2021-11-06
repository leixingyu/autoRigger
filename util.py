import maya.cmds as cmds

from utility.rigging import nurbs


G_LOC_GRP = '_Locators'
G_CTRL_GRP = '_Controllers'
G_JNT_GRP = '_Joints'
G_MESH_GRP = '_Meshes'


def create_locators_on_curve(curve, sample):
    locs = list()

    points, tangents = nurbs.get_point_on_curve(curve, sample)

    for index in range(len(points)):
        point = points[index]
        tangent = tangents[index]

        loc = cmds.spaceLocator()
        locs.append(loc)
        temp_node = cmds.createNode('transform')

        cmds.xform(temp_node, t=[point.x+tangent.x, point.y+tangent.y, point.z+tangent.z])
        cmds.xform(loc, t=[point.x, point.y, point.z])

        constraint = cmds.aimConstraint(temp_node, loc)[0]

        cmds.delete([temp_node, constraint])

    return locs


def create_outliner_grp():
    """ Create different groups in the outliner """

    for grp in [G_LOC_GRP, G_JNT_GRP, G_CTRL_GRP, G_MESH_GRP]:
        if not cmds.ls(grp):
            cmds.group(em=1, name=grp)


def move(obj, pos):
    """

    :param obj: str. root
    :param pos: list. position x, y and z
    """

    return cmds.move(pos[0], pos[1], pos[2], obj, relative=1)


def move_to(obj, pos):
    """

    :param obj:
    :param pos:
    :return:
    """

    return cmds.move(pos[0], pos[1], pos[2], obj, absolute=1)


def matchXform(source, target):
    """
    Match source rotation and translation to the target

    :param source:
    :param target:
    :return:
    """

    pos = cmds.xform(target, q=1, t=1, ws=1)
    rot = cmds.xform(target, q=1, ro=1, ws=1)

    cmds.move(pos[0], pos[1], pos[2], source)
    cmds.rotate(rot[0], rot[1], rot[2], source)