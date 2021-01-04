import maya.cmds as cmds
import maya.OpenMaya as om
import base
from utility import joint, outliner


class Limb(base.Base):
    """ This module create a Limb rig which is used in arm or leg """
    
    def __init__(self, side, base_name, limb_type='Null'):
        """ Initialize Limb class with side, name and type of the limb
        
        :param side: str
        :param base_name: str
        :param limb_type: str, 'Arm', 'Leg' or 'Null'
        """
        
        base.Base.__init__(self, side, base_name)
        self.meta_type = 'Limb'
        self.set_limb_type(limb_type)
        self.assign_naming()
        self.assign_secondary_naming()
        self.set_locator_attr([0, 0, 0], 2)

    def set_limb_type(self, limb_type):
        self.limb_components = []
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
        self.loc_list, self.jnt_list, self.ik_jnt_list, self.fk_jnt_list,\
        self.ctrl_list, self.fk_ctrl_list, self.fk_offset_list\
            = ([] for i in range(7))  
        
        for component in self.limb_components:
            self.loc_list.append     ('{}{}_loc'.format(self.name, component))
            self.jnt_list.append     ('{}{}_jnt'.format(self.name, component))
            self.ik_jnt_list.append   ('{}{}_ik_jnt'.format(self.name, component))
            self.fk_jnt_list.append   ('{}{}_fk_jnt'.format(self.name, component))
            self.ctrl_list.append    ('{}{}_ctrl'.format(self.name, component))
            self.fk_ctrl_list.append  ('{}{}_fk_ctrl'.format(self.name, component))
            self.fk_offset_list.append('{}{}_fk_offset'.format(self.name, component))
            
        # ik has different ctrl name
        self.ik_ctrl_name =   '{}_ik_ctrl'.format(self.name)
        self.ik_pole_name =   '{}_ikpole_ctrl'.format(self.name)
        self.ik_offset_name = '{}_ik_offset'.format(self.name)

    def set_locator_attr(self, start_pos=[0, 0, 0], interval=2, scale=0.4):
        self.start_pos = start_pos
        self.interval = interval
        self.scale = scale

    @staticmethod
    def set_controller_shape():
        limb_fk_shape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='LimbFK_tempShape')
        #cmds.scale(0.2, 0.2, 0.2, limb_fk_shape)

        limb_ik_shape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name='LimbIK_tempShape')

        limb_ik_pole_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='LimbIKPole_tempShape')
        selection = cmds.select('LimbIKPole_tempShape.cv[6]', 'LimbIKPole_tempShape.cv[0]')
        cmds.scale(0.5, 0.5, 0.5, selection)
        cmds.move(-0.5, 0, 0, selection)
        cmds.rotate(0, 90, 0, limb_ik_pole_shape)

        arrow_pt_list = [[2.0, 0.0, 2.0], [2.0, 0.0, 1.0], [3.0, 0.0, 1.0], [3.0, 0.0, 2.0], [5.0, 0.0, 0.0], [3.0, 0.0, -2.0], [3.0, 0.0, -1.0], [2.0, 0.0, -1.0],
                       [2.0, 0.0, -2.0], [1.0, 0.0, -2.0], [1.0, 0.0, -3.0], [2.0, 0.0, -3.0], [0.0, 0.0, -5.0], [-2.0, 0.0, -3.0], [-1.0, 0.0, -3.0], [-1.0, 0.0, -2.0],
                       [-2.0, 0.0, -2.0], [-2.0, 0.0, -1.0], [-3.0, 0.0, -1.0], [-3.0, 0.0, -2.0], [-5.0, 0.0, 0.0], [-3.0, 0.0, 2.0], [-3.0, 0.0, 1.0], [-2.0, 0.0, 1.0],
                       [-2.0, 0.0, 2.0], [-1.0, 0.0, 2.0], [-1.0, 0.0, 3.0], [-2.0, 0.0, 3.0], [0.0, 0.0, 5.0], [2.0, 0.0, 3.0], [1.0, 0.0, 3.0], [1.0, 0.0, 2.0], [2.0, 0.0, 2.0]]
        switch_shape = cmds.curve(p=arrow_pt_list, degree=1, name='Switch_tempShape')
        cmds.scale(0.3, 0.3, 0.3, switch_shape)

    def build_guide(self):
        grp = cmds.group(em=True, n=self.loc_grp_name)

        side_factor, horizontal_factor, vertical_factor = 1, 1, 0
        if self.side == 'R':             side_factor = -1
        if self.direction == 'Vertical': horizontal_factor, vertical_factor = 0, 1

        # Root
        limb_root = cmds.spaceLocator(n=self.loc_list[0])
        cmds.parent(limb_root, grp, relative=True)
        cmds.move(self.start_pos[0], self.start_pos[1], self.start_pos[2], limb_root, relative=True)
        cmds.scale(self.scale, self.scale, self.scale, limb_root)

        # Middle
        limb_mid = cmds.spaceLocator(n=self.loc_list[1])
        cmds.parent(limb_mid, limb_root, relative=True)
        cmds.move(self.interval*side_factor*horizontal_factor, -self.interval*vertical_factor, 0, limb_mid, relative=True)  # move limb joint along +x axis

        # Top
        limb_top = cmds.spaceLocator(n=self.loc_list[2])
        cmds.parent(limb_top, limb_mid, relative=True)
        cmds.move(self.interval*side_factor*horizontal_factor, -self.interval*vertical_factor, 0, limb_top, relative=True)  # move limb joint along +x axis

        # Cleanup
        self.color_locator()
        cmds.parent(grp, self.loc_grp)
        return grp

    def construct_joint(self):
        # Result joint
        cmds.select(clear=True)
        for i, component in enumerate(self.limb_components):
            loc = cmds.ls(self.loc_list[i], transforms=True)
            loc_pos = cmds.xform(loc, q=True, t=True, ws=True)
            jnt = cmds.joint(p=loc_pos, name=self.jnt_list[i])
            cmds.setAttr(jnt+'.radius', 1)

        # FK Joint
        cmds.select(clear=True)
        for i, component in enumerate(self.limb_components):
            loc = cmds.ls(self.loc_list[i], transforms=True)
            loc_pos = cmds.xform(loc, q=True, t=True, ws=True)
            fk_jnt = cmds.joint(p=loc_pos, name=self.fk_jnt_list[i])
            cmds.setAttr(fk_jnt+'.radius', 1)

        # IK Joint
        cmds.select(clear=True)
        for i, component in enumerate(self.limb_components):
            loc = cmds.ls(self.loc_list[i], transforms=True)
            loc_pos = cmds.xform(loc, q=True, t=True, ws=True)
            ik_jnt = cmds.joint(p=loc_pos, name=self.ik_jnt_list[i])
            cmds.setAttr(ik_jnt+'.radius', 1)

        # Cleanup
        outliner.batch_parent([self.jnt_list[0], self.ik_jnt_list[0], self.fk_jnt_list[0]], self.jnt_grp)
        joint.orient_joint([self.jnt_list[0], self.ik_jnt_list[0], self.fk_jnt_list[0]])
        return cmds.ls(self.jnt_list[0])

    def place_controller(self):
        self.set_controller_shape()
        root_pos, mid_pos, top_pos = [cmds.xform(self.jnt_list[i], q=True, t=True, ws=True) for i in range(len(self.limb_components))]
        root_rot, mid_rot, top_rot = [cmds.xform(self.jnt_list[i], q=True, ro=True, ws=True) for i in range(len(self.limb_components))]

        # FK Setup
        root_fk_ctrl = cmds.duplicate('LimbFK_tempShape', name=self.fk_ctrl_list[0])[0]
        cmds.move(root_pos[0], root_pos[1], root_pos[2], root_fk_ctrl, absolute=True)
        # if self.direction == 'Vertical': cmds.rotate(0, 0, 90, root_fk_ctrl)
            
        root_offset = cmds.group(em=True, name=self.fk_offset_list[0])
        cmds.move(root_pos[0], root_pos[1], root_pos[2], root_offset)
        cmds.parent(root_fk_ctrl, root_offset)
        cmds.rotate(root_rot[0], root_rot[1], root_rot[2], root_offset)
        cmds.makeIdentity(root_fk_ctrl, apply=True, t=1, r=1, s=1)

        mid_fk_ctrl = cmds.duplicate('LimbFK_tempShape', name=self.fk_ctrl_list[1])[0]
        cmds.move(mid_pos[0], mid_pos[1], mid_pos[2], mid_fk_ctrl, absolute=True)
        # if self.direction == 'Vertical': cmds.rotate(0, 0, 90, mid_fk_ctrl)
            
        mid_offset = cmds.group(em=True, name=self.fk_offset_list[1])
        cmds.move(mid_pos[0], mid_pos[1], mid_pos[2], mid_offset)
        cmds.parent(mid_fk_ctrl, mid_offset)
        cmds.rotate(mid_rot[0], mid_rot[1], mid_rot[2], mid_offset)
        cmds.makeIdentity(mid_fk_ctrl, apply=True, t=1, r=1, s=1)

        top_fk_ctrl = cmds.duplicate('LimbFK_tempShape', name=self.fk_ctrl_list[2])[0]
        cmds.move(top_pos[0], top_pos[1], top_pos[2], top_fk_ctrl, absolute=True)
        # if self.direction == 'Vertical': cmds.rotate(0, 0, 90, top_fk_ctrl)

        top_offset = cmds.group(em=True, name=self.fk_offset_list[2])
        cmds.move(top_pos[0], top_pos[1], top_pos[2], top_offset)
        cmds.parent(top_fk_ctrl, top_offset)
        cmds.rotate(top_rot[0], top_rot[1], top_rot[2], top_offset)
        cmds.makeIdentity(top_fk_ctrl, apply=True, t=1, r=1, s=1)

        cmds.parent(top_offset, mid_fk_ctrl)
        cmds.parent(mid_offset, root_fk_ctrl)

        # IK Setup
        ik_ctrl = cmds.duplicate('LimbIK_tempShape', name=self.ik_ctrl_name)[0]
        cmds.move(top_pos[0], top_pos[1], top_pos[2], ik_ctrl, absolute=True)
        # if self.direction == 'Vertical': cmds.rotate(0, 0, 90, ik_ctrl)

        offset_grp = cmds.group(em=True, name=self.ik_offset_name)
        cmds.move(top_pos[0], top_pos[1], top_pos[2], offset_grp)
        cmds.parent(ik_ctrl, offset_grp)
        cmds.rotate(top_rot[0], top_rot[1], top_rot[2], offset_grp)
        cmds.makeIdentity(ik_ctrl, apply=True, t=1, r=1, s=1)

        pole_ctrl = cmds.duplicate('LimbIKPole_tempShape', name=self.ik_pole_name)
        if self.direction == 'Vertical':
            cmds.move(mid_pos[0], mid_pos[1], mid_pos[2]+3, pole_ctrl, absolute=True)
        elif self.direction == 'Horizontal':
            cmds.move(mid_pos[0], mid_pos[1], mid_pos[2]-3, pole_ctrl, absolute=True)
            cmds.rotate(0, 180, 0, pole_ctrl, relative=True)
        cmds.makeIdentity(pole_ctrl, apply=True, t=1, r=1, s=1)

        # IK/FK Switch Setup
        self.switch_ctrl = cmds.duplicate('Switch_tempShape', name='{}_switch_ctrl'.format(self.name))[0]
        # if self.direction == 'Vertical':
        #     cmds.move(root_pos[0], root_pos[1], root_pos[2], self.switch_ctrl, absolute=True)
        # elif self.direction == 'Horizontal':
        cmds.move(root_pos[0], root_pos[1], root_pos[2], self.switch_ctrl, absolute=True)
        cmds.rotate(0, 0, 90, self.switch_ctrl, relative=True)
        cmds.addAttr(self.switch_ctrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=True)

        offset_grp = cmds.group(em=True, name='{}_switch_offset'.format(self.name))
        cmds.move(root_pos[0], root_pos[1], root_pos[2], offset_grp)
        cmds.parent(self.switch_ctrl, offset_grp)
        cmds.rotate(root_rot[0], root_rot[1], root_rot[2], offset_grp)
        cmds.makeIdentity(self.switch_ctrl, apply=True, t=1, r=1, s=1)

        # Cleanup
        self.delete_shape()
        cmds.parent(offset_grp, self.ctrl_grp)

    def add_constraint(self):
        # Result Joint + IK/FK Switch
        for i, type in enumerate(self.limb_components):
            if i == 0:
                cmds.parentConstraint(self.ik_jnt_list[i], self.fk_jnt_list[i], self.jnt_list[i])
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jnt_list[i], self.ik_jnt_list[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=1, value=1)
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jnt_list[i], self.fk_jnt_list[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=1, value=0)
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jnt_list[i], self.ik_jnt_list[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=0, value=0)
                cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jnt_list[i], self.fk_jnt_list[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=0, value=1)
            else:
                cmds.orientConstraint(self.ik_jnt_list[i], self.fk_jnt_list[i], self.jnt_list[i])
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jnt_list[i], self.ik_jnt_list[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=1, value=1)
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.jnt_list[i], self.fk_jnt_list[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=1, value=0)
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W0'.format(self.jnt_list[i], self.ik_jnt_list[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=0, value=0)
                cmds.setDrivenKeyframe('{}_orientConstraint1.{}W1'.format(self.jnt_list[i], self.fk_jnt_list[i]), currentDriver='{}.FK_IK'.format(self.switch_ctrl), driverValue=0, value=1)

        for i, component in enumerate(self.limb_components):
            cmds.setDrivenKeyframe(self.fk_ctrl_list[i]+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=1)
            cmds.setDrivenKeyframe(self.fk_ctrl_list[i]+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=0)

        cmds.setDrivenKeyframe(self.ik_ctrl_name+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ik_ctrl_name+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=0)
        cmds.setDrivenKeyframe(self.ik_pole_name+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.ik_pole_name+'.visibility', currentDriver=self.switch_ctrl+'.FK_IK', driverValue=0, value=0)

        # FK Setup
        for i, component in enumerate(self.limb_components): cmds.orientConstraint(self.fk_ctrl_list[i], self.fk_jnt_list[i], mo=True)
        cmds.setAttr(self.fk_jnt_list[0]+'.visibility', 0)

        # IK Setup
        # Set Preferred Angles #
        middle_ik_jnt = self.ik_jnt_list[1]
        if self.direction == 'Vertical':
            cmds.rotate(0, 0, -20, middle_ik_jnt, relative=True)
            cmds.joint(middle_ik_jnt, edit=True, ch=True, setPreferredAngles=True)
            cmds.rotate(0, 0, 20, middle_ik_jnt, relative=True)
        else:
            if self.side == 'L':
                cmds.rotate(0, 0, 20, middle_ik_jnt, relative=True)
                cmds.joint(middle_ik_jnt, edit=True, ch=True, setPreferredAngles=True)
                cmds.rotate(0, 0, -20, middle_ik_jnt, relative=True)
            elif self.side == 'R':
                cmds.rotate(0, 0, 20, middle_ik_jnt, relative=True)
                cmds.joint(middle_ik_jnt, edit=True, ch=True, setPreferredAngles=True)
                cmds.rotate(0, 0, -20, middle_ik_jnt, relative=True)
        cmds.setAttr(self.ik_jnt_list[0]+'.visibility', 0)

        # IK Handle #
        ik_handle = cmds.ikHandle(startJoint=self.ik_jnt_list[0], endEffector=self.ik_jnt_list[-1], name='{}_ikhandle'.format(self.name), solver='ikRPsolver')[0]
        cmds.pointConstraint(self.ik_ctrl_name, ik_handle, mo=True)
        cmds.orientConstraint(self.ik_ctrl_name, self.ik_jnt_list[-1], mo=True)
        cmds.poleVectorConstraint(self.ik_pole_name, ik_handle)
        cmds.aimConstraint(middle_ik_jnt, self.ik_pole_name, mo=True)
        cmds.setAttr(ik_handle+'.visibility', 0)

        # Cleanup
        cmds.pointConstraint(self.switch_ctrl, self.ik_jnt_list[0], mo=True)
        cmds.pointConstraint(self.switch_ctrl, self.fk_jnt_list[0], mo=True)
        outliner.batch_parent([self.ik_offset_name, self.ik_pole_name, self.fk_offset_list[0], ik_handle], self.switch_ctrl)

    def lock_controller(self):
        fk_mid_ctrl = cmds.ls(self.fk_ctrl_list[1], transforms=True)[0]
        if self.direction == 'Horizontal':
            cmds.setAttr(fk_mid_ctrl+'.rz', l=True, k=0)
            cmds.setAttr(fk_mid_ctrl+'.rx', l=True, k=0)
        else:
            cmds.setAttr(fk_mid_ctrl+'.rz', l=True, k=0)
            cmds.setAttr(fk_mid_ctrl+'.ry', l=True, k=0)

    def ik_snap(self):
        """ Snap IK joint to FK joint"""
        fk_root_pos = cmds.xform(self.fk_jnt_list[0], ws=True, q=True, t=True)
        fk_mid_pos = cmds.xform(self.fk_jnt_list[1], ws=True, q=True, t=True)
        fk_top_pos = cmds.xform(self.fk_jnt_list[-1], ws=True, q=True, t=True)
        fk_top_rot = cmds.xform(self.fk_jnt_list[-1], ws=True, q=True, ro=True)

        fk_root_vec = om.MVector(fk_root_pos[0], fk_root_pos[1], fk_root_pos[2])
        fk_mid_vec = om.MVector(fk_mid_pos[0], fk_mid_pos[1], fk_mid_pos[2])
        fk_top_vec = om.MVector(fk_top_pos[0], fk_top_pos[1], fk_top_pos[2])

        mid_point_vec = (fk_root_vec + fk_top_vec) / 2
        pole_dir = fk_mid_vec - mid_point_vec
        pole_pos = fk_mid_vec + pole_dir

        ik_ctrl_pos = cmds.xform(self.ik_ctrl_name, ws=True, q=True, sp=True)
        pv_ctrl_pos = cmds.xform(self.ik_pole_name, ws=True, q=True, sp=True)

        cmds.rotate(fk_top_rot[0], fk_top_rot[1], fk_top_rot[2], self.ik_ctrl_name)
        cmds.move(fk_top_pos[0]-ik_ctrl_pos[0], fk_top_pos[1]-ik_ctrl_pos[1], fk_top_pos[2]-ik_ctrl_pos[2], self.ik_ctrl_name, relative=True)
        cmds.move(pole_pos[0]-pv_ctrl_pos[0], pole_pos[1]-pv_ctrl_pos[1], pole_pos[2]-pv_ctrl_pos[2], self.ik_pole_name, relative=True)

    def fk_snap(self):
        """ Snap FK joint to IK joint"""
        ik_root_rot = cmds.xform(self.ik_jnt_list[0], os=True, q=True, ro=True)
        ik_mid_rot = cmds.xform(self.ik_jnt_list[1], os=True, q=True, ro=True)
        ik_top_rot = cmds.xform(self.ik_jnt_list[-1], os=True, q=True, ro=True)

        cmds.rotate(ik_root_rot[0], ik_root_rot[1], ik_root_rot[2], self.fk_ctrl_list[0])
        cmds.rotate(ik_mid_rot[0], ik_mid_rot[1], ik_mid_rot[2], self.fk_ctrl_list[1])
        cmds.rotate(ik_top_rot[0], ik_top_rot[1], ik_top_rot[2], self.fk_ctrl_list[-1])
