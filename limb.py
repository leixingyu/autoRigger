import maya.cmds as cmds
from . import rig
from utility import joint, outliner


class Limb(rig.Bone):
    """ This module create a Limb rig which is used in arm or leg """

    def __init__(self, side, name, rig_type='Limb', pos=[0, 0, 0], interval=2, limb_type='Null'):
        """ Initialize Limb class with side, name and type of the limb
        
        :param side: str
        :param name: str
        :param limb_type: str, 'Arm', 'Leg' or 'Null'
        """

        self.pos = pos
        self.interval = interval
        self.scale = 0.4

        self.limb_components = []
        self.direction = None

        # unique to limb
        self.set_limb_type(limb_type)

        self.locs, self.jnts, self.ik_jnts, self.fk_jnts, self.ctrls, self.fk_ctrls, self.fk_offsets = ([] for _ in range(7))

        rig.Bone.__init__(self, side, name, rig_type)

    def set_limb_type(self, limb_type):
        if limb_type == 'Arm':
            self.limb_components = ['shoulder', 'elbow', 'wrist']
            self.direction = 'Horizontal'
        elif limb_type == 'Leg':
            self.limb_components = ['clavicle', 'knee', 'ankle']
            self.direction = 'Vertical'
        else:
            self.limb_components = ['root', 'middle', 'top']
            self.direction = 'Vertical'

    def assign_secondary_naming(self):
        # initialize mulitple names
        for component in self.limb_components:
            self.locs.append('{}{}_loc'.format(self.base_name, component))
            self.jnts.append('{}{}_jnt'.format(self.base_name, component))
            self.ik_jnts.append('{}{}_ik_jnt'.format(self.base_name, component))
            self.fk_jnts.append('{}{}_fk_jnt'.format(self.base_name, component))
            self.ctrls.append('{}{}_ctrl'.format(self.base_name, component))
            self.fk_ctrls.append('{}{}_fk_ctrl'.format(self.base_name, component))
            self.fk_offsets.append('{}{}_fk_offset'.format(self.base_name, component))

        # ik has different ctrl name
        self.ik_ctrl = '{}_ik_ctrl'.format(self.base_name)
        self.ik_pole = '{}_ikpole_ctrl'.format(self.base_name)
        self.ik_offset = '{}_ik_offset'.format(self.base_name)
        self.ik_pole_offset = '{}_ikpole_offset'.format(self.base_name)

        self.switch_ctrl = '{}_switch_ctrl'.format(self.base_name)
        self.switch_offset = '{}_switch_offset'.format(self.base_name)

    @staticmethod
    def set_controller_shape():
        cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='LimbFK_tempShape')
        # cmds.scale(0.2, 0.2, 0.2, limb_fk_shape)

        cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='LimbIK_tempShape')

        limb_ik_pole_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='LimbIKPole_tempShape')
        selection = cmds.select('LimbIKPole_tempShape.cv[6]', 'LimbIKPole_tempShape.cv[0]')
        cmds.scale(0.5, 0.5, 0.5, selection)
        cmds.move(-0.5, 0, 0, selection)
        cmds.rotate(0, 90, 0, limb_ik_pole_shape)

        arrow_pts = [
            [2.0, 0.0, 2.0], [2.0, 0.0, 1.0], [3.0, 0.0, 1.0], [3.0, 0.0, 2.0], [5.0, 0.0, 0.0], [3.0, 0.0, -2.0], [3.0, 0.0, -1.0], [2.0, 0.0, -1.0],
            [2.0, 0.0, -2.0], [1.0, 0.0, -2.0], [1.0, 0.0, -3.0], [2.0, 0.0, -3.0], [0.0, 0.0, -5.0], [-2.0, 0.0, -3.0], [-1.0, 0.0, -3.0], [-1.0, 0.0, -2.0],
            [-2.0, 0.0, -2.0], [-2.0, 0.0, -1.0], [-3.0, 0.0, -1.0], [-3.0, 0.0, -2.0], [-5.0, 0.0, 0.0], [-3.0, 0.0, 2.0], [-3.0, 0.0, 1.0], [-2.0, 0.0, 1.0],
            [-2.0, 0.0, 2.0], [-1.0, 0.0, 2.0], [-1.0, 0.0, 3.0], [-2.0, 0.0, 3.0], [0.0, 0.0, 5.0], [2.0, 0.0, 3.0], [1.0, 0.0, 3.0], [1.0, 0.0, 2.0], [2.0, 0.0, 2.0]
        ]
        switch_shape = cmds.curve(p=arrow_pts, degree=1, name='Switch_tempShape')
        cmds.scale(0.3, 0.3, 0.3, switch_shape)

    def create_locator(self):
        grp = cmds.group(em=1, n=self.loc_grp)

        side_factor, horizontal_factor, vertical_factor = 1, 1, 0
        if self._side == 'R':
            side_factor = -1

        if self.direction == 'Vertical':
            horizontal_factor, vertical_factor = 0, 1

        # Root
        limb_root = cmds.spaceLocator(n=self.locs[0])
        cmds.parent(limb_root, grp, relative=1)
        cmds.move(self.pos[0], self.pos[1], self.pos[2], limb_root, relative=1)
        cmds.scale(self.scale, self.scale, self.scale, limb_root)

        # Middle
        limb_mid = cmds.spaceLocator(n=self.locs[1])
        cmds.parent(limb_mid, limb_root, relative=1)
        cmds.move(self.interval*side_factor*horizontal_factor, -self.interval*vertical_factor, 0, limb_mid, relative=1)  # move limb joint along +x axis

        # Top
        limb_top = cmds.spaceLocator(n=self.locs[2])
        cmds.parent(limb_top, limb_mid, relative=1)
        cmds.move(self.interval*side_factor*horizontal_factor, -self.interval*vertical_factor, 0, limb_top, relative=1)  # move limb joint along +x axis

        # Cleanup
        cmds.parent(grp, self.loc_global_grp)
        return grp

    def create_joint(self):
        # Result joint
        cmds.select(clear=1)
        for i, component in enumerate(self.limb_components):
            loc = cmds.ls(self.locs[i], transforms=1)
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnts[i])
            cmds.setAttr(jnt+'.radius', 1)

        # FK Joint
        cmds.select(clear=1)
        for i, component in enumerate(self.limb_components):
            loc = cmds.ls(self.locs[i], transforms=1)
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            fk_jnt = cmds.joint(p=loc_pos, name=self.fk_jnts[i])
            cmds.setAttr(fk_jnt+'.radius', 1)

        # IK Joint
        cmds.select(clear=1)
        for i, component in enumerate(self.limb_components):
            loc = cmds.ls(self.locs[i], transforms=1)
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            ik_jnt = cmds.joint(p=loc_pos, name=self.ik_jnts[i])
            cmds.setAttr(ik_jnt+'.radius', 1)

        # Cleanup
        outliner.batch_parent([self.jnts[0], self.ik_jnts[0], self.fk_jnts[0]], self.jnt_global_grp)
        joint.orient_joint([self.jnts[0], self.ik_jnts[0], self.fk_jnts[0]])
        return cmds.ls(self.jnts[0])

    def place_controller(self):
        root_pos, mid_pos, top_pos = [cmds.xform(self.jnts[i], q=1, t=1, ws=1) for i in range(len(self.limb_components))]
        root_rot, mid_rot, top_rot = [cmds.xform(self.jnts[i], q=1, ro=1, ws=1) for i in range(len(self.limb_components))]

        # FK Setup

        # Root
        root_fk_ctrl = cmds.duplicate('LimbFK_tempShape', name=self.fk_ctrls[0])[0]
        cmds.move(root_pos[0], root_pos[1], root_pos[2], root_fk_ctrl, absolute=1)

        root_offset = cmds.group(em=1, name=self.fk_offsets[0])
        cmds.move(root_pos[0], root_pos[1], root_pos[2], root_offset)
        cmds.parent(root_fk_ctrl, root_offset)
        cmds.rotate(root_rot[0], root_rot[1], root_rot[2], root_offset)
        cmds.makeIdentity(root_fk_ctrl, apply=1, t=1, r=1, s=1)

        # Mid
        mid_fk_ctrl = cmds.duplicate('LimbFK_tempShape', name=self.fk_ctrls[1])[0]
        cmds.move(mid_pos[0], mid_pos[1], mid_pos[2], mid_fk_ctrl, absolute=1)

        mid_offset = cmds.group(em=1, name=self.fk_offsets[1])
        cmds.move(mid_pos[0], mid_pos[1], mid_pos[2], mid_offset)
        cmds.parent(mid_fk_ctrl, mid_offset)
        cmds.rotate(mid_rot[0], mid_rot[1], mid_rot[2], mid_offset)
        cmds.makeIdentity(mid_fk_ctrl, apply=1, t=1, r=1, s=1)

        # Top
        top_fk_ctrl = cmds.duplicate('LimbFK_tempShape', name=self.fk_ctrls[2])[0]
        cmds.move(top_pos[0], top_pos[1], top_pos[2], top_fk_ctrl, absolute=1)

        top_offset = cmds.group(em=1, name=self.fk_offsets[2])
        cmds.move(top_pos[0], top_pos[1], top_pos[2], top_offset)
        cmds.parent(top_fk_ctrl, top_offset)
        cmds.rotate(top_rot[0], top_rot[1], top_rot[2], top_offset)
        cmds.makeIdentity(top_fk_ctrl, apply=1, t=1, r=1, s=1)

        cmds.parent(top_offset, mid_fk_ctrl)
        cmds.parent(mid_offset, root_fk_ctrl)

        # IK Setup

        # Root
        ik_ctrl = cmds.duplicate('LimbIK_tempShape', name=self.ik_ctrl)[0]
        cmds.move(top_pos[0], top_pos[1], top_pos[2], ik_ctrl, absolute=1)

        offset_grp = cmds.group(em=1, name=self.ik_offset)
        cmds.move(top_pos[0], top_pos[1], top_pos[2], offset_grp)
        cmds.parent(ik_ctrl, offset_grp)
        cmds.rotate(top_rot[0], top_rot[1], top_rot[2], offset_grp)
        cmds.makeIdentity(ik_ctrl, apply=1, t=1, r=1, s=1)

        # Pole
        pole_ctrl = cmds.duplicate('LimbIKPole_tempShape', name=self.ik_pole)
        if self.direction == 'Vertical':
            cmds.move(mid_pos[0], mid_pos[1], mid_pos[2]+3, pole_ctrl, absolute=1)
        elif self.direction == 'Horizontal':
            cmds.move(mid_pos[0], mid_pos[1], mid_pos[2]-3, pole_ctrl, absolute=1)
            cmds.rotate(0, 180, 0, pole_ctrl, relative=1)

        offset_grp = cmds.group(em=1, name=self.ik_pole_offset)
        cmds.move(mid_pos[0], mid_pos[1], mid_pos[2], offset_grp)
        cmds.parent(pole_ctrl, offset_grp)
        cmds.makeIdentity(pole_ctrl, apply=1, t=1, r=1, s=1)

        # IK/FK Switch Setup
        cmds.duplicate('Switch_tempShape', name=self.switch_ctrl)
        cmds.move(root_pos[0], root_pos[1], root_pos[2], self.switch_ctrl, absolute=1)
        cmds.rotate(0, 0, 90, self.switch_ctrl, relative=1)
        cmds.addAttr(self.switch_ctrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=1)

        cmds.group(em=1, name=self.switch_offset)
        cmds.move(root_pos[0], root_pos[1], root_pos[2], self.switch_offset)
        cmds.parent(self.switch_ctrl, self.switch_offset)
        cmds.rotate(root_rot[0], root_rot[1], root_rot[2], self.switch_offset)
        cmds.makeIdentity(self.switch_ctrl, apply=1, t=1, r=1, s=1)

        # Cleanup
        cmds.parent(self.switch_offset, self.ctrl_global_grp)

    def add_constraint(self):
        # Result Joint + IK/FK Switch
        for i, _ in enumerate(self.limb_components):
            if i == 0:
                cmds.parentConstraint(self.ik_jnts[i], self.fk_jnts[i], self.jnts[i])
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jnts[i], self.ik_jnts[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=1, value=1)
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jnts[i], self.fk_jnts[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=1, value=0)
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jnts[i], self.ik_jnts[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=0, value=0)
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jnts[i], self.fk_jnts[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=0, value=1)
            else:
                cmds.orientConstraint(self.ik_jnts[i], self.fk_jnts[i], self.jnts[i])
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jnts[i], self.ik_jnts[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=1, value=1)
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.jnts[i], self.fk_jnts[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=1, value=0)
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jnts[i], self.ik_jnts[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=0, value=0)
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.jnts[i], self.fk_jnts[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=0, value=1)

        for i, component in enumerate(self.limb_components):
            cmds.setDrivenKeyframe(self.fk_ctrls[i]+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=1)
            cmds.setDrivenKeyframe(self.fk_ctrls[i]+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=0)

        cmds.setDrivenKeyframe(self.ik_ctrl+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ik_ctrl+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.ik_pole+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ik_pole+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=0)

        # FK Setup
        for i, component in enumerate(self.limb_components):
            cmds.orientConstraint(self.fk_ctrls[i], self.fk_jnts[i], mo=1)
        cmds.setAttr(self.fk_jnts[0]+'.visibility', 0)

        # IK Setup
        # Set Preferred Angles #
        middle_ik_jnt = self.ik_jnts[1]
        if self.direction == 'Vertical':
            cmds.rotate(0, 0, -20, middle_ik_jnt, relative=1)
            cmds.joint(middle_ik_jnt, edit=1, ch=1, setPreferredAngles=1)
            cmds.rotate(0, 0, 20, middle_ik_jnt, relative=1)
        else:
            if self._side == 'L':
                cmds.rotate(0, 0, 20, middle_ik_jnt, relative=1)
                cmds.joint(middle_ik_jnt, edit=1, ch=1, setPreferredAngles=1)
                cmds.rotate(0, 0, -20, middle_ik_jnt, relative=1)
            elif self._side == 'R':
                cmds.rotate(0, 0, 20, middle_ik_jnt, relative=1)
                cmds.joint(middle_ik_jnt, edit=1, ch=1, setPreferredAngles=1)
                cmds.rotate(0, 0, -20, middle_ik_jnt, relative=1)
        cmds.setAttr(self.ik_jnts[0]+'.visibility', 0)

        # IK Handle #
        ik_handle = cmds.ikHandle(startJoint=self.ik_jnts[0], endEffector=self.ik_jnts[-1], name='{}_ikhandle'.format(self.base_name), solver='ikRPsolver')[0]
        cmds.pointConstraint(self.ik_ctrl, ik_handle, mo=1)
        cmds.orientConstraint(self.ik_ctrl, self.ik_jnts[-1], mo=1)
        cmds.poleVectorConstraint(self.ik_pole, ik_handle)
        cmds.setAttr(ik_handle+'.visibility', 0)

        # Cleanup
        cmds.pointConstraint(self.switch_ctrl, self.ik_jnts[0], mo=1)
        cmds.pointConstraint(self.switch_ctrl, self.fk_jnts[0], mo=1)
        outliner.batch_parent([self.ik_offset, self.ik_pole_offset, self.fk_offsets[0], ik_handle], self.switch_ctrl)

    def lock_controller(self):
        # FIXME: locking seems to be wrong

        fk_mid_ctrl = cmds.ls(self.fk_ctrls[1], transforms=1)[0]
        if self.direction == 'Horizontal':
            cmds.setAttr(fk_mid_ctrl+'.rz', l=1, k=0)
            cmds.setAttr(fk_mid_ctrl+'.rx', l=1, k=0)
        else:
            cmds.setAttr(fk_mid_ctrl+'.rz', l=1, k=0)
            cmds.setAttr(fk_mid_ctrl+'.ry', l=1, k=0)
