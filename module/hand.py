import maya.cmds as cmds

from .. import util
from ..base import bone, base
from ..chain import finger
from ..constant import Side
from ..utility.common import hierarchy


# TODO: make so the finger count is not hard coded
# FIXME: lets get rid of the side factor and use direction instead


class Hand(bone.Bone):
    """
    Hand rig module with multiple fingers and a wrist
    """

    def __init__(self, side, name, interval=0.5, distance=2):
        bone.Bone.__init__(self, side, name)
        self._rtype = 'hand'

        self.interval = interval
        self.distance = distance

        self.wrist = base.Base(side, 'wrist')
        self.thumb = finger.Finger(side, 'thumb', length=1.2)
        self.index = finger.Finger(side, 'index', length=2.0)
        self.middle = finger.Finger(side, 'middle', length=2.2)
        self.ring = finger.Finger(side, 'ring', length=2.0)
        self.pinky = finger.Finger(side, 'pinky', length=1.6)

        self.fingers = [
            self.thumb,
            self.index,
            self.middle,
            self.ring,
            self.pinky
        ]

        self._comps.append(self.wrist)
        self._comps.extend(self.fingers)

    def create_locator(self):
        super(Hand, self).create_locator()

        # move around the locators
        side_factor = 1
        if self._side == Side.RIGHT:
            side_factor = -1

        util.move(self.thumb.locs[0], [0, 0, 2 * self.interval])
        util.move(self.index.locs[0], [0, 0, 1 * self.interval])
        util.move(self.ring.locs[0], [0, 0, -1 * self.interval])
        util.move(self.pinky.locs[0], [0, 0, -2 * self.interval])

        util.move(self.wrist.locs[0], [-side_factor * self.distance, 0, 0])
        cmds.rotate(0, 0, 90, self.wrist.locs[0])

        hierarchy.batch_parent(
            [f.locs[0] for f in self.fingers], self.wrist.locs[0])

    def create_joint(self):
        super(Hand, self).create_joint()

        fingers = [obj.jnts[0] for obj in self.fingers]
        wrist = self.wrist.jnts[0]
        hierarchy.batch_parent(fingers, wrist)

    def add_constraint(self):
        super(Hand, self).add_constraint()

        for obj in self.fingers:
            # add individual finger constraint
            cmds.parentConstraint(self.wrist.jnts[0], obj.offsets[0], mo=1)
