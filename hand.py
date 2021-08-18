import maya.cmds as cmds
from . import rig, base, finger
from utility import outliner

# TODO: make so the finger count is not hard coded
# FIXME: lets get rid of the side factor and use direction instead


class Hand(rig.Bone):
    """ This module creates a Hand rig with multiple fingers and a wrist """

    def __init__(self, side, name, rig_type='Hand', finger_count=5, pos=[0, 0, 0], interval=0.5, distance=2):
        """ Initialize Hand class

        :param side: str
        :param name: str
        :param finger_count: int, number of fingers
        :param interval: interval between each fingers
        :param distance: distance between finger root and wrist
        """

        rig.Bone.__init__(self, side, name, rig_type)

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

        hand_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=10, name='Hand_tempShape')[0]
        selection = cmds.select('Hand_tempShape.cv[7:9]', 'Hand_tempShape.cv[0]')
        cmds.scale(1.5, 1, 1.5, selection, relative=1)
        cmds.scale(1.8, 1, 1.3, hand_shape)

        cmds.scale(self.ctrl_scale, self.ctrl_scale, self.ctrl_scale, hand_shape, relative=1)

    def create_locator(self):
        grp = cmds.group(em=1, n=self.loc_grp)

        finger_grp = [finger.create_locator() for finger in self.finger_list]
        wrist_grp = self.wrist.create_locator()

        # Cleanup
        outliner.batch_parent(finger_grp, wrist_grp)
        cmds.parent(wrist_grp, grp)
        cmds.parent(grp, self.loc_global_grp)

        return wrist_grp

    def create_joint(self):
        fingers = [finger.create_joint() for finger in self.finger_list]
        wrist = self.wrist.create_joint()
        outliner.batch_parent(fingers, wrist)

    def place_controller(self):
        self.constraint_list = []

        # placing finger controller
        for obj in self.finger_list:
            finger_grp = obj.place_controller()
            self.constraint_list.append(finger_grp)

    def add_constraint(self):
        # add individual finger constraint
        for obj in self.finger_list:
            obj.add_constraint()

        for obj in self.constraint_list:
            cmds.parentConstraint(self.wrist.jnt, obj, mo=1)

    def color_controller(self):
        for obj in self.finger_list:
            obj.color_controller()
