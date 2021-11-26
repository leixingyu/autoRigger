import maya.cmds as cmds

import util
from utility import nurbs
from utility.useful import strGenerator


NAMER = strGenerator.StrGenerator(prefix='tmp_')


def make_circle(scale=1, name=None):
    """
    Make a circle nurbs curve
    """
    if not name:
        name = NAMER.tmp

    return cmds.circle(
        nr=(0, 1, 0),
        c=(0, 0, 0),
        s=8,
        radius=scale,
        name=name)[0]


def make_arrow(scale=1, name=None):
    """
    Make a four-directional arrow nurbs curve
    """
    if not name:
        name = NAMER.tmp

    arrow_pts = [
        [2.0, 0.0, 2.0], [2.0, 0.0, 1.0], [3.0, 0.0, 1.0], [3.0, 0.0, 2.0],
        [5.0, 0.0, 0.0], [3.0, 0.0, -2.0], [3.0, 0.0, -1.0],
        [2.0, 0.0, -1.0],
        [2.0, 0.0, -2.0], [1.0, 0.0, -2.0], [1.0, 0.0, -3.0],
        [2.0, 0.0, -3.0], [0.0, 0.0, -5.0], [-2.0, 0.0, -3.0],
        [-1.0, 0.0, -3.0], [-1.0, 0.0, -2.0],
        [-2.0, 0.0, -2.0], [-2.0, 0.0, -1.0], [-3.0, 0.0, -1.0],
        [-3.0, 0.0, -2.0], [-5.0, 0.0, 0.0], [-3.0, 0.0, 2.0],
        [-3.0, 0.0, 1.0], [-2.0, 0.0, 1.0],
        [-2.0, 0.0, 2.0], [-1.0, 0.0, 2.0], [-1.0, 0.0, 3.0],
        [-2.0, 0.0, 3.0], [0.0, 0.0, 5.0], [2.0, 0.0, 3.0],
        [1.0, 0.0, 3.0], [1.0, 0.0, 2.0], [2.0, 0.0, 2.0]
    ]

    arrow = cmds.curve(p=arrow_pts, degree=1, name=name)
    util.uniform_scale(arrow, scale * 0.5)
    cmds.makeIdentity(arrow, apply=1, s=1)
    return arrow


def make_sphere(scale=1, name=None):
    """
    Make a sphere nurbs curve
    """
    if not name:
        name = NAMER.tmp

    c1 = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), s=8, radius=scale)[0]
    c2 = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), s=8, radius=scale)[0]
    c3 = cmds.circle(nr=(0, 0, 1), c=(0, 0, 0), s=8, radius=scale)[0]

    sphere = nurbs.util.merge_curves(name=name, curves=[c1, c2, c3])
    return sphere


def make_text(text, scale=1, name=None):
    """
    Make a nurbs curve with text

    :param text: str. text for display
    :return: str. transform node of the shape curve
    """
    if not name:
        name = NAMER.tmp

    curve = nurbs.util.make_curve_by_text(text=text, name=name)
    util.uniform_scale(curve, scale)
    cmds.makeIdentity(curve, apply=1, r=1, t=1, s=1)
    # make it align on the ground plane
    cmds.rotate(-90, 0, 0, curve, r=1)
    return curve
