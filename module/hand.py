import maya.cmds as cmds

from . import finger
from .base import bone, base
from autoRigger import util

from utility.setup import outliner


# TODO: make so the finger count is not hard coded
# FIXME: lets get rid of the side factor and use direction instead


class Hand(bone.Bone):
    """ This module creates a Hand rig with multiple fingers and a wrist """

    def __init__(self, side, name, interval=0.5, distance=2):

        bone.Bone.__init__(self, side, name, rig_type='hand')

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
        
        # self._shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=10, name=self.namer.tmp)[0]
        # #selection = cmds.select('{}Shape.cv[7:9]'.format(self._shape), '{}Shape.cv[0]'.format(self._shape))
        # #cmds.scale(1.5, 1, 1.5, selection, relative=1)
        # cmds.scale(1.8, 1, 1.3, self._shape)

    def create_locator(self):
        for finger in self.fingers:
            finger.create_locator()

        self.wrist.create_locator()

        self.move_locator()

        return self.wrist.loc

    def move_locator(self, pos=[0, 0, 0]):
        side_factor = 1
        if self._side == 'R':
            side_factor = -1

        # Finger Locators
        z_value = pos[2]
        offsets = [
            z_value+2 * self.interval,
            z_value+self.interval,
            z_value,
            z_value-self.interval,
            z_value-2 * self.interval
        ]

        util.move(self.thumb.locs[0], [pos[0], pos[1], offsets[0]])
        util.move(self.index.locs[0], [pos[0], pos[1], offsets[1]])
        util.move(self.middle.locs[0], [pos[0], pos[1], offsets[2]])
        util.move(self.ring.locs[0], [pos[0], pos[1], offsets[3]])
        util.move(self.pinky.locs[0], [pos[0], pos[1], offsets[4]])

        util.move(self.wrist.loc,
                  [pos[0]-side_factor * self.distance,
                   pos[1],
                   pos[2]]
                  )

        outliner.batch_parent([finger.locs[0] for finger in self.fingers], self.wrist.loc)

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
            cmds.parentConstraint(self.wrist.jnt, obj, mo=1)

    def color_controller(self):
        self.wrist.color_controller()
        
        for obj in self.fingers:
            obj.color_controller()


class Hand1(bone.Bone):
    """ This module creates a Hand rig with multiple fingers and a wrist """

    def __init__(self, side, name, rig_type='Hand', finger_count=5, pos=[0, 0, 0], interval=0.5, distance=2):
        """ Initialize Hand class

        :param side: str
        :param name: str
        :param finger_count: int, number of fingers
        :param interval: interval between each fingers
        :param distance: distance between finger root and wrist
        """

        bone.Bone.__init__(self, side, name, rig_type)

        self.finger_count = finger_count
        self.pos = pos
        self.interval = interval
        self.distance = distance

        self.finger_list = []
        self.ctrl_scale = 1

        side_factor = 1
        if self._side == 'R':
            side_factor = -1

        # Finger Locators
        z_value = self.pos[2]
        offsets = [
            z_value + 2 * self.interval,
            z_value + self.interval,
            z_value,
            z_value - self.interval,
            z_value - 2 * self.interval
        ]

        thumb = finger.Finger(
            side=self._side,
            name='thumb',
            pos=[
                self.pos[0],
                self.pos[1],
                offsets[0]
            ],
            interval=0.3,
            finger_type='Thumb'
        )

        index = finger.Finger(
            side=self._side,
            name='index',
            pos=[
                self.pos[0],
                self.pos[1],
                offsets[1]
            ],
            interval=0.5
        )

        middle = finger.Finger(
            side=self._side,
            name='middle',
            pos=[
                self.pos[0],
                self.pos[1],
                offsets[2]
            ],
            interval=0.55
        )

        ring = finger.Finger(
            side=self._side,
            name='ring',
            pos=[
                self.pos[0],
                self.pos[1],
                offsets[3]
            ],
            interval=0.5
        )

        pinky = finger.Finger(
            side=self._side,
            name='pinky',
            pos=[
                self.pos[0],
                self.pos[1],
                offsets[4]
            ],
            interval=0.4
        )

        # Single Wrist Locator
        self.wrist = base.Base(
            side=self._side,
            name='wrist',
            pos=[
                self.pos[0] - side_factor * self.distance,
                self.pos[1],
                self.pos[2]
            ]
        )

        self.finger_list = [thumb, index, middle, ring, pinky]

    def set_controller_shape(self):
        for obj in self.finger_list:
            obj.set_controller_shape()

        self._shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=10, name='Hand_tempShape')[0]
        selection = cmds.select('Hand_tempShape.cv[7:9]', 'Hand_tempShape.cv[0]')
        cmds.scale(1.5, 1, 1.5, selection, relative=1)
        cmds.scale(1.8, 1, 1.3, self._shape)

        cmds.scale(self.ctrl_scale, self.ctrl_scale, self.ctrl_scale, self._shape, relative=1)

    def create_locator(self):
        grp = cmds.group(em=1, n=self.loc_grp)

        finger_grp = [finger.create_locator() for finger in self.finger_list]
        wrist_grp = self.wrist.create_locator()

        # Cleanup
        outliner.batch_parent(finger_grp, wrist_grp)
        cmds.parent(wrist_grp, grp)
        cmds.parent(grp, util.G_LOC_GRP)

        return wrist_grp

    def create_joint(self):
        fingers = [finger.create_joint() for finger in self.finger_list]
        wrist = self.wrist.create_joint()
        outliner.batch_parent(fingers, wrist)

    def place_controller(self):
        self.constraints = []

        # placing finger controller
        for obj in self.finger_list:
            finger_grp = obj.place_controller()
            self.constraints.append(finger_grp)

    def add_constraint(self):
        # add individual finger constraint
        for obj in self.finger_list:
            obj.add_constraint()

        for obj in self.constraints:
            cmds.parentConstraint(self.wrist.jnt, obj, mo=1)

    def color_controller(self):
        for obj in self.finger_list:
            obj.color_controller()
