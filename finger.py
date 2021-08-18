import logging

import maya.cmds as cmds
from . import rig


class Finger(rig.Bone):
    """ This module creates one finger rig """

    def __init__(
            self,
            side,
            name,
            rig_type='Finger',
            pos=[0, 0, 0],
            interval=0.5,
            segment=4,
            finger_type='Other'
    ):

        """ Initialize Finger class with side, name and type of finger

        :param side: str
        :param name: str
        :param finger_type: str, 'Thumb' or 'Other'
        """

        self.segment = segment
        self.finger_type = finger_type

        self.pos = pos
        self.interval = interval

        self.ctrl_spacer = 1
        self.ctrl_scale = 1
        self.scale = 0.3

        self.finger_shape = None

        self.locs, self.jnts, self.ctrls, self.ctrl_offsets = ([] for _ in range(4))  # ik has different ctrl name

        rig.Bone.__init__(self, side, name, rig_type)

    def assign_secondary_naming(self):
        for i in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base_name, i))
            self.jnts.append('{}{}_jnt'.format(self.base_name, i))
        for i in range(self.segment-1):
            self.ctrls.append('{}{}_ctrl'.format(self.base_name, i))
            self.ctrl_offsets.append('{}{}_offset'.format(self.base_name, i))

    def set_controller_shape(self):
        # Finger Shape
        if self.finger_type == 'Other':
            self.finger_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=6, name='Finger_tempShape')[0]
            cmds.select('{}.cv[3]'.format(self.finger_shape), '{}.cv[5]'.format(self.finger_shape))
            cmds.scale(0.2, 0.2, 0.2, relative=1)
            cmds.select('{}.cv[1]'.format(self.finger_shape), '{}.cv[4]'.format(self.finger_shape))
            cmds.move(0, 0, 1, relative=1)
            cmds.scale(0.2, 0.2, 0.4, self.finger_shape)
            cmds.rotate(90, 0, 0, self.finger_shape)

        # Thumb Shape
        elif self.finger_type == 'Thumb':
            self.finger_shape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='Finger_tempShape')[0]
            cmds.scale(0.2, 0.2, 0.2, self.finger_shape)

        # Global Scale
        cmds.scale(self.ctrl_scale, self.ctrl_scale, self.ctrl_scale, self.finger_shape, relative=1)

    def create_locator(self):
        grp = cmds.group(em=1, n=self.loc_grp)
        for i in range(self.segment):
            finger = cmds.spaceLocator(n=self.locs[i])
            # root locator of finger parent to the locator group
            if i is 0:
                cmds.parent(finger, grp, relative=1)
                cmds.move(self.pos[0], self.pos[1], self.pos[2], finger, absolute=1)
                cmds.scale(self.scale, self.scale, self.scale, finger)
            # non-root locator parent to the previous locator
            else:
                cmds.parent(finger, self.locs[i-1], relative=1)
                if self._side == 'L':  # move finger locator along +x axis
                    cmds.move(self.interval, 0, 0, finger, relative=1)
                elif self._side == 'R':  # move finger locator along -x axis
                    cmds.move(-self.interval, 0, 0, finger, relative=1)

        cmds.parent(grp, self.loc_global_grp)
        cmds.select(clear=1)
        return grp

    def create_joint(self):
        cmds.select(clear=1)

        for i, loc in enumerate(self.locs):
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnts[i])
            cmds.setAttr(jnt+'.radius', self.scale)
        cmds.parent(self.jnts[0], self.jnt_global_grp)
        return cmds.ls(self.jnts[0])

    def place_controller(self):
        for i in range(self.segment-1):
            jnt_pos = cmds.xform(self.jnts[i], q=1, t=1, ws=1)
            jnt_rot = cmds.xform(self.jnts[i], q=1, ro=1, ws=1)

            ctrl = None
            if self.finger_type == 'Other':
                ctrl = cmds.duplicate(self.finger_shape, name=self.ctrls[i])[0]
                cmds.move(
                    jnt_pos[0],
                    jnt_pos[1] + self.ctrl_spacer,
                    jnt_pos[2],
                    ctrl
                )

                cmds.move(
                    jnt_pos[0],
                    jnt_pos[1],
                    jnt_pos[2],
                    ctrl + '.rotatePivot',
                    ctrl + '.scalePivot'
                )

            elif self.finger_type == 'Thumb':
                ctrl = cmds.duplicate(self.finger_shape, name=self.ctrls[i])[0]
                cmds.move(jnt_pos[0], jnt_pos[1], jnt_pos[2], ctrl)

            else:
                logging.error('Unexpected finger type %s' % self.finger_type)

            offset_grp = cmds.group(em=1, name=self.ctrl_offsets[i])
            cmds.move(jnt_pos[0], jnt_pos[1], jnt_pos[2], offset_grp)
            cmds.parent(ctrl, offset_grp)
            cmds.rotate(jnt_rot[0], jnt_rot[1], jnt_rot[2], offset_grp)
            cmds.makeIdentity(ctrl, apply=1, t=1, r=1, s=1)

            if i == 0:
                cmds.parent(offset_grp, self.ctrl_global_grp)
            elif i != 0:
                cmds.parent(offset_grp, self.ctrls[i-1])

        return cmds.ls(self.ctrl_offsets[0])

    def add_constraint(self):
        for i in range(self.segment-1):
            ctrl = cmds.ls(self.ctrls[i])[0]
            jnt = cmds.ls(self.jnts[i])
            cmds.orientConstraint(ctrl, jnt, mo=1)

    def lock_controller(self):
        if self.finger_type != 'Thumb':
            for ctrl in self.ctrls:
                if ctrl not in self.ctrl_offsets:
                    for transform in 's':
                        for axis in 'xyz':
                            cmds.setAttr('{}.{}{}'.format(ctrl, transform, axis), l=1, k=0)
                    cmds.setAttr(ctrl+'.rx', l=1, k=0)
