import maya.cmds as cmds

from autoRigger.chain import finger
from autoRigger.base import bone, base
from autoRigger import util

from utility.setup import outliner


# TODO: make so the finger count is not hard coded
# FIXME: lets get rid of the side factor and use direction instead


class Hand(bone.Bone):
    """
    Hand rig mdule with multiple fingers and a wrist
    """

    def __init__(self, side, name, interval=0.5, distance=2):
        bone.Bone.__init__(self, side, name)
        self._rtype = 'hand'

        self.interval = interval
        self.distance = distance

        self.wrist = base.Base(self._side, name='wrist')
        self.thumb = finger.Finger(side, name='thumb', length=1.2)
        self.index = finger.Finger(side, name='index', length=2.0)
        self.middle = finger.Finger(side, name='middle', length=2.2)
        self.ring = finger.Finger(side, name='ring', length=2.0)
        self.pinky = finger.Finger(side, name='pinky', length=1.6)
        self.fingers = [self.thumb, self.index, self.middle, self.ring, self.pinky]

    def set_controller_shape(self):
        for obj in self.fingers:
            obj.set_controller_shape()

        self.wrist.set_controller_shape()

    def create_namespace(self):
        for obj in self.fingers:
            obj.create_namespace()

        self.wrist.create_namespace()

    def create_locator(self):
        for obj in self.fingers:
            obj.create_locator()

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

    def color_locator(self):
        for obj in self.fingers:
            obj.color_locator()

        self.wrist.color_locator()

    def create_joint(self):
        for obj in self.fingers:
            obj.create_joint()

        self.wrist.create_joint()

        fingers = [obj.jnts[0] for obj in self.fingers]
        wrist = self.wrist.jnts[0]
        outliner.batch_parent(fingers, wrist)

    def place_controller(self):
        self.wrist.place_controller()
        for obj in self.fingers:
            obj.place_controller()

    def add_constraint(self):
        self.wrist.add_constraint()

        for obj in self.fingers:
            obj.add_constraint()
            # add individual finger constraint
            cmds.parentConstraint(self.wrist.jnts[0], obj.offsets[0], mo=1)

    def delete_guide(self):
        self.wrist.delete_guide()

        for obj in self.fingers:
            obj.delete_guide()

    def color_controller(self):
        self.wrist.color_controller()
        
        for obj in self.fingers:
            obj.color_controller()
