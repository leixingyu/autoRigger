import maya.cmds as cmds

from autoRigger.chain import finger
from autoRigger.base import bone, base
from autoRigger import util

from utility.setup import outliner


# TODO: make so the finger count is not hard coded
# FIXME: lets get rid of the side factor and use direction instead


class Hand(bone.Bone):
    """ This module creates a Hand rig with multiple fingers and a wrist """

    def __init__(self, side, name, interval=0.5, distance=2):

        bone.Bone.__init__(self, side, name)

        self._rtype = 'hand'

        self.interval = interval
        self.distance = distance

        self.fingers = list()
        self.constraints = list()

        self.thumb = finger.Finger(side, name='thumb', length=1.2)
        self.index = finger.Finger(side, name='index', length=2.0)
        self.middle = finger.Finger(side, name='middle', length=2.2)
        self.ring = finger.Finger(side, name='ring', length=2.0)
        self.pinky = finger.Finger(side, name='pinky', length=1.6)

        # Single Wrist Locator
        self.wrist = base.Base(self._side, name='wrist')

        self.fingers = [self.thumb, self.index, self.middle, self.ring, self.pinky]

    def set_controller_shape(self):
        for obj in self.fingers:
            obj.set_controller_shape()

        self.wrist.set_controller_shape()

    def create_namespace(self):
        for finger in self.fingers:
            finger.create_namespace()

        self.wrist.create_namespace()

    def create_locator(self):
        for finger in self.fingers:
            finger.create_locator()

        self.wrist.create_locator()
        # move around the locators
        side_factor = 1
        if self._side == 'r':
            side_factor = -1

        util.move(self.thumb.locs[0], [0, 0, 2 * self.interval])
        util.move(self.index.locs[0], [0, 0, 1 * self.interval])
        util.move(self.ring.locs[0], [0, 0, -1 * self.interval])
        util.move(self.pinky.locs[0], [0, 0, -2 * self.interval])

        util.move(self.wrist.locs[0], [-side_factor * self.distance, 0, 0])

        outliner.batch_parent([finger.locs[0] for finger in self.fingers], self.wrist.locs[0])

        return self.wrist.locs[0]

    def create_joint(self):
        fingers = [finger.create_joint() for finger in self.fingers]
        wrist = self.wrist.create_joint()
        outliner.batch_parent(fingers, wrist)

    def place_controller(self):
        self.wrist.place_controller()

        # placing finger controller
        for obj in self.fingers:
            finger_grp = obj.place_controller()
            self.constraints.append(finger_grp)

    def add_constraint(self):
        self.wrist.add_constraint()

        # add individual finger constraint
        for obj in self.fingers:
            obj.add_constraint()

        for obj in self.constraints:
            cmds.parentConstraint(self.wrist.jnts[0], obj, mo=1)

    def color_controller(self):
        self.wrist.color_controller()
        
        for obj in self.fingers:
            obj.color_controller()
