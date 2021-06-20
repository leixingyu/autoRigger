import maya.cmds as cmds
from . import base, finger
from utility import outliner


class Hand(base.Base):
    """ This module creates a Hand rig with multiple fingers and a wrist """

    def __init__(self, side, base_name, finger_count=5):
        """ Initialize Hand class

        :param side: str
        :param base_name: str
        :param finger_count: int, number of fingers
        """

        base.Base.__init__(self, side, base_name)
        self.meta_type = 'Hand'
        self.base_name = base_name
        self.assign_naming()
        self.finger_count = finger_count
        self.finger_list = []

    @staticmethod
    def set_controller_shape():
        hand_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=10, name='Hand_tempShape')[0]
        selection = cmds.select('Hand_tempShape.cv[7:9]', 'Hand_tempShape.cv[0]')
        cmds.scale(1.5, 1, 1.5, selection, relative=1)
        cmds.scale(1.8, 1, 1.3, hand_shape)

    def set_locator_attr(self, start_pos=[0, 0, 0], interval=0.5, distance=2, scale=0.2):
        self.start_pos = start_pos
        self.interval = interval
        self.distance = distance
        self.scale = scale

    def build_guide(self):
        grp = cmds.group(em=1, n=self.loc_grp_name)
        side_factor = 1
        if self.side == 'R': side_factor = -1

        # Finger Locators
        z_value = self.start_pos[2]
        offsets = [z_value+2*self.interval, z_value+self.interval, z_value, z_value-self.interval, z_value-2*self.interval]

        thumb = finger.Finger(side=self.side, base_name='thumb', finger_type='Thumb')
        thumb.set_locator_attr(start_pos=[self.start_pos[0]-side_factor*0.7, self.start_pos[1], offsets[0]], interval=0.3)  # x offset 0.7
        thumb_grp = thumb.build_guide()

        index = finger.Finger(side=self.side, base_name='index')
        index.set_locator_attr(start_pos=[self.start_pos[0], self.start_pos[1], offsets[1]], interval=0.5)
        index_grp = index.build_guide()

        middle = finger.Finger(side=self.side, base_name='middle')
        middle.set_locator_attr(start_pos=[self.start_pos[0], self.start_pos[1], offsets[2]], interval=0.55)
        middle_grp = middle.build_guide()

        ring = finger.Finger(side=self.side, base_name='ring')
        ring.set_locator_attr(start_pos=[self.start_pos[0], self.start_pos[1], offsets[3]], interval=0.5)
        ring_grp = ring.build_guide()

        pinky = finger.Finger(side=self.side, base_name='pinky')
        pinky.set_locator_attr(start_pos=[self.start_pos[0]-side_factor*0.3, self.start_pos[1], offsets[4]], interval=0.4)  # x offset 0.3
        pinky_grp = pinky.build_guide()

        self.finger_list = [thumb, index, middle, ring, pinky]

        # Single Wrist Locator
        self.wrist = base.Base(side=self.side, base_name='wrist')
        self.wrist.set_locator_attr(start_pos=[self.start_pos[0]-side_factor*self.distance, self.start_pos[1], self.start_pos[2]])
        wrist = self.wrist.build_guide()

        # Cleanup
        outliner.batch_parent([thumb_grp, index_grp, middle_grp, ring_grp, pinky_grp], wrist)
        cmds.parent(wrist, grp)
        cmds.parent(grp, self.loc_grp)

        return wrist

    def construct_joint(self):
        fingers = [finger.construct_joint() for finger in self.finger_list]
        wrist = self.wrist.construct_joint()
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
            cmds.parentConstraint(self.wrist.jnt_name, obj, mo=1)

    def color_controller(self):
        for obj in self.finger_list:
            obj.color_controller()




