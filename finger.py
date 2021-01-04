import maya.cmds as cmds
import base


class Finger(base.Base):
    """ This module creates one finger rig """

    def __init__(self, side, base_name, finger_type='Other'):
        """ Initialize Finger class with side, name and type of finger

        :param side: str
        :param base_name: str
        :param finger_type: str, 'Thumb' or 'Other'
        """

        base.Base.__init__(self, side, base_name)
        self.meta_type = 'Finger'
        self.segment = 4
        self.finger_type = finger_type
        self.assign_naming()
        self.assign_secondary_naming()

    def assign_secondary_naming(self):
        self.loc_list, self.jnt_list, self.ctrl_list, self.ctrl_offset_list = ([] for i in range(4))  # ik has different ctrl name
        for i in range(self.segment):
            self.loc_list.append('{}{}_loc'.format(self.name, i))
            self.jnt_list.append('{}{}_jnt'.format(self.name, i))
            self.ctrl_list.append('{}{}_ctrl'.format(self.name, i))
            self.ctrl_offset_list.append('{}{}_offset'.format(self.name, i))

    @staticmethod
    def set_controller_shape():
        # Finger Shape
        finger_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=6, name='Finger_tempShape')
        cmds.select('Finger_tempShape.cv[3]', 'Finger_tempShape.cv[5]')
        cmds.scale(0.2, 0.2, 0.2, relative=True)
        cmds.select('Finger_tempShape.cv[1]', 'Finger_tempShape.cv[4]')
        cmds.move(0, 0, 1, relative=True)
        cmds.scale(0.2, 0.2, 0.4, finger_shape)
        cmds.rotate(90, 0, 0, finger_shape)

        # Thumb Shape
        thumb_shape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='Thumb_tempShape')
        cmds.scale(0.2, 0.2, 0.2, thumb_shape)

    def set_locator_attr(self, start_pos=[0, 0, 0], interval=0.5, scale=0.2):
        self.start_pos = start_pos
        self.interval = interval
        self.scale = scale

    def build_guide(self):
        grp = cmds.group(em=True, n=self.loc_grp_name)
        for i in range(self.segment):
            finger = cmds.spaceLocator(n=self.loc_list[i])
            # root locator of finger parent to the locator group
            if i is 0:
                cmds.parent(finger, grp, relative=True)
                cmds.move(self.start_pos[0], self.start_pos[1], self.start_pos[2], finger, absolute=True)
                cmds.scale(self.scale, self.scale, self.scale, finger)
            # non-root locator parent to the previous locator
            else:
                cmds.parent(finger, self.loc_list[i-1], relative=True)
                if self.side == 'L':  # move finger locator along +x axis
                    cmds.move(self.interval, 0, 0, finger, relative=True)
                elif self.side == 'R':  # move finger locator along -x axis
                    cmds.move(-self.interval, 0, 0, finger, relative=True)

        cmds.parent(grp, self.loc_grp)
        self.color_locator()
        cmds.select(clear=True)
        return grp

    def construct_joint(self):
        cmds.select(clear=True)

        for i, loc in enumerate(self.loc_list):
            loc_pos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=loc_pos, name=self.jnt_list[i])
            cmds.setAttr(jnt+'.radius', self.scale)
        cmds.parent(self.jnt_list[0], self.jnt_grp)
        return cmds.ls(self.jnt_list[0])

    def place_controller(self):
        self.set_controller_shape()

        for i in range(self.segment-1):
            jnt_pos = cmds.xform(self.jnt_list[i], q=True, t=True, ws=True)
            jnt_rot = cmds.xform(self.jnt_list[i], q=True, ro=True, ws=True)

            if self.finger_type != 'Thumb':
                ctrl = cmds.duplicate('Finger_tempShape', name=self.ctrl_list[i])[0]
                cmds.move(jnt_pos[0], jnt_pos[1]+1, jnt_pos[2], ctrl)
                cmds.move(jnt_pos[0], jnt_pos[1], jnt_pos[2], ctrl+'.rotatePivot', ctrl+'.scalePivot')
            else:
                ctrl = cmds.duplicate('Thumb_tempShape', name=self.ctrl_list[i])[0]
                cmds.move(jnt_pos[0], jnt_pos[1], jnt_pos[2], ctrl)

            offset_grp = cmds.group(em=True, name=self.ctrl_offset_list[i])
            cmds.move(jnt_pos[0], jnt_pos[1], jnt_pos[2], offset_grp)
            cmds.parent(ctrl, offset_grp)
            cmds.rotate(jnt_rot[0], jnt_rot[1], jnt_rot[2], offset_grp)
            cmds.makeIdentity(ctrl, apply=True, t=1, r=1, s=1)

            if i == 0:
                cmds.parent(offset_grp, self.ctrl_grp)
            elif i != 0:
                cmds.parent(offset_grp, self.ctrl_list[i-1])

        self.delete_shape()
        return cmds.ls(self.ctrl_offset_list[0])

    def add_constraint(self):
        for i in range(self.segment-1):
            ctrl = cmds.ls(self.ctrl_list[i])[0]
            jnt = cmds.ls(self.jnt_list[i])
            cmds.orientConstraint(ctrl, jnt, mo=True)

    def lock_controller(self):
        if self.finger_type != 'Thumb':
            for ctrl in self.ctrl_list:
                if ctrl not in self.ctrl_offset_list:
                    for transform in 's':
                        for axis in 'xyz':
                            cmds.setAttr('{}.{}{}'.format(ctrl, transform, axis), l=True, k=0)
                    cmds.setAttr(ctrl+'.rx', l=1, k=0)