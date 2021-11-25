import maya.cmds as cmds

from utility.nurbs import util


G_LOC_GRP = '_Locators'
G_CTRL_GRP = '_Controllers'
G_JNT_GRP = '_Joints'
G_MESH_GRP = '_Meshes'


def create_locators_on_curve(curve, sample):
    """
    Create locators uniformly spread on curve

    :param curve: str. single nurbsCurve node
    :param sample: int. number of sample points
    :return: list. list of locators created
    """
    locs = list()
    points, tangents = util.get_point_on_curve(curve, sample)
    for index in range(len(points)):
        point = points[index]
        tangent = tangents[index]

        loc = cmds.spaceLocator()
        locs.append(loc)
        temp_node = cmds.createNode('transform')

        cmds.xform(
            temp_node,
            t=[point.x+tangent.x, point.y+tangent.y, point.z+tangent.z]
        )
        cmds.xform(loc, t=[point.x, point.y, point.z])
        constraint = cmds.aimConstraint(temp_node, loc)[0]
        cmds.delete([temp_node, constraint])

    return locs


def create_outliner_grp():
    """
    Create different groups in the outliner
    """
    for grp in [G_LOC_GRP, G_JNT_GRP, G_CTRL_GRP, G_MESH_GRP]:
        if not cmds.ls(grp):
            cmds.group(em=1, name=grp)


def move(obj, pos):
    """
    Move object relative to its current position

    :param obj: str. maya object
    :param pos: list. position x, y and z
    """
    return cmds.move(pos[0], pos[1], pos[2], obj, r=1)


def move_to(obj, pos):
    """
    Move object to an absolute position (i.e. set transform to position)

    :param obj: str. maya object
    :param pos: list. position x, y and z
    """
    return cmds.move(pos[0], pos[1], pos[2], obj, absolute=1)


def uniform_scale(obj, scale):
    """
    Scale object relative to its current scale

    :param obj: str. maya object
    :param scale: int. uniform scale value
    """
    if cmds.nodeType(obj) == 'joint':
        default = cmds.getAttr('{}.radius'.format(obj))
        return cmds.setAttr('{}.radius'.format(obj), scale * default)

    return cmds.scale(scale, scale, scale, obj)
