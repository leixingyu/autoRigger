import maya.cmds as cmds
from . import base, foot, limb
from utility import joint, outliner


class Leg(base.Base):
    """ This module create a biped leg rig"""

    def __init__(self, side, base_name):
        """ Initialize Leg class with side and name

        :param side: str
        :param base_name: str
        """

        base.Base.__init__(self, side, base_name)
        self.meta_type = 'Leg'
        self.assign_naming()
        self.set_locator_attr(start_pos=[0, 8.4, 0])
        self.limb = limb.Limb(side=self.side, base_name=base_name, limb_type='Leg')
        self.foot = foot.Foot(side=self.side, base_name=base_name)

    def set_locator_attr(self, start_pos=[0, 0, 0], distance=4, interval=0.5, height=0.4, scale=0.2):
        self.start_pos = start_pos
        self.distance = distance
        self.interval = interval
        self.height = height
        self.scale = scale

    def build_guide(self):
        # Limb
        self.limb.set_locator_attr(start_pos=self.start_pos, interval=self.distance)
        self.limb.build_guide()

        # Foot
        self.foot.set_locator_attr(start_pos=[self.start_pos[0], self.start_pos[1]-2*self.distance, self.start_pos[2]], interval=self.interval, height=self.height)
        foot_grp = self.foot.build_guide()

        # Connect
        cmds.parent(foot_grp, self.limb.loc_list[-1])

    def construct_joint(self):
        self.limb.construct_joint()
        self.foot.construct_joint()

    def place_controller(self):
        self.limb.place_controller()
        self.foot.place_controller()

    def add_constraint(self):
        self.limb.add_constraint()
        self.foot.add_constraint()

        # Connect
        # IK constraint #
        cmds.parentConstraint(self.foot.rev_ankle_jnt_name, self.limb.ik_ctrl_name, mo=1)
        cmds.setAttr(self.limb.ik_ctrl_name+'.visibility', 0)

        # FK constraint #
        cmds.parentConstraint(self.limb.jnt_list[-1], self.foot.fk_ankle_jnt_name, mo=1)
        cmds.parent(self.foot.fk_ctrl_name, self.limb.fk_ctrl_list[-1])

        # IK/FK switch #
        cmds.setDrivenKeyframe(self.limb.switch_ctrl+'.FK_IK', currentDriver=self.foot.switch_ctrl_name+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.limb.switch_ctrl+'.FK_IK', currentDriver=self.foot.switch_ctrl_name+'.FK_IK', driverValue=0, value=0)

        # Sub controller visibility and channel hide #
        cmds.setDrivenKeyframe(self.limb.ik_ctrl_name+'.visibility', currentDriver=self.limb.switch_ctrl+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.limb.ik_ctrl_name+'.visibility', currentDriver=self.limb.switch_ctrl+'.FK_IK', driverValue=0, value=0)
        cmds.setAttr(self.limb.switch_ctrl+'.FK_IK', l=1, k=0)

    def delete_guide(self):
        self.foot.delete_guide()
        self.limb.delete_guide()

    def color_controller(self):
        self.limb.color_controller()
        self.foot.color_controller()


class LegFront(base.Base):
    """ This module creates a quadruped front leg rig"""

    def __init__(self, side, base_name):
        """ Initialize LegFront with side and name

        :param side: str
        :param base_name: str
        """

        base.Base.__init__(self, side, base_name)
        self.meta_type = 'FrontLeg'
        self.assign_naming()
        self.assign_secondary_naming()

    def assign_secondary_naming(self):
        self.loc_list, self.jnt_list, self.ctrl_list, self.ctrl_offset_list = ([] for i in range(4))
        self.limb_components = ['shoulder', 'elbow', 'wrist', 'paw', 'toe']
        for component in self.limb_components:
            self.loc_list.append('{}{}_loc'.format(self.name, component))
            self.jnt_list.append('{}{}_jnt'.format(self.name, component))
            self.ctrl_list.append('{}{}_ctrl'.format(self.name, component))
            self.ctrl_offset_list.append('{}{}_offset'.format(self.name, component))

        # ik has different ctrl name
        self.leg_ik_name = '{}leg_ik'.format(self.name)
        self.foot_ik_name = '{}foot_ik'.format(self.name)
        self.toe_ik_name = '{}toe_ik'.format(self.name)

    def set_locator_attr(self, start_pos=[0, 5, 3], distance=1.5, height=0.2, scale=0.4):
        self.start_pos = start_pos
        self.distance = distance
        self.height = height
        self.scale = scale

    @staticmethod
    def set_controller_shape():
        sphere = cmds.createNode('implicitSphere')
        sphere_ctrl = cmds.rename(cmds.listRelatives(sphere, p=1), 'Shoulder_tempShape')
        cmds.scale(0.5, 0.5, 0.5, sphere_ctrl)

        pole = cmds.createNode('implicitSphere')
        pole_ctrl = cmds.rename(cmds.listRelatives(pole, p=1), 'Pole_tempShape')
        cmds.scale(0.2, 0.2, 0.2, pole_ctrl)

        ctrl_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Paw_tempShape')
        cmds.scale(0.5, 0.5, 0.5, ctrl_shape)

    def build_guide(self):
        grp = cmds.group(em=1, n=self.loc_grp_name)

        # Shoulder
        shoulder = cmds.spaceLocator(n=self.loc_list[0])
        cmds.parent(shoulder, grp, relative=1)
        cmds.move(self.start_pos[0], self.start_pos[1], self.start_pos[2], shoulder, relative=1)
        cmds.scale(self.scale, self.scale, self.scale, shoulder)

        # Elbow
        elbow = cmds.spaceLocator(n=self.loc_list[1])
        cmds.parent(elbow, shoulder, relative=1)
        cmds.move(0, -self.distance, -0.5 * self.distance, elbow, relative=1)

        # Wrist
        wrist = cmds.spaceLocator(n=self.loc_list[2])
        cmds.parent(wrist, elbow, relative=1)
        cmds.move(0, -self.distance, 0, wrist, relative=1)

        # Paw
        paw = cmds.spaceLocator(n=self.loc_list[3])
        cmds.parent(paw, wrist, relative=1)
        cmds.move(0, -self.distance+self.height, 0.5 * self.distance, paw, relative=1)

        # Toe
        toe = cmds.spaceLocator(n=self.loc_list[4])
        cmds.parent(toe, paw, relative=1)
        cmds.move(0, 0, 0.5 * self.distance, toe, relative=1)

        self.color_locator()
        cmds.parent(grp, self.loc_grp)
        return grp

    def construct_joint(self):
        cmds.select(clear=1)
        for index in range(len(self.loc_list)):
            loc = cmds.ls(self.loc_list[index], transforms=1)
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnt_list[index])
            cmds.setAttr(jnt+'.radius', self.scale)

        cmds.parent(self.jnt_list[0], self.jnt_grp)
        joint.orient_joint(self.jnt_list[0])
        return self.jnt_list[0]

    def place_controller(self):
        self.set_controller_shape()

        # Shoulder
        shoulder = cmds.ls(self.jnt_list[0])
        shoulder_ctrl = cmds.duplicate('Shoulder_tempShape', name=self.ctrl_list[0])[0]
        shoulder_pos = cmds.xform(shoulder, q=1, ws=1, t=1)
        shoulder_rot = cmds.xform(shoulder, q=1, ws=1, ro=1)

        shoulder_ctrl_offset = cmds.group(em=1, name=self.ctrl_offset_list[0])
        cmds.move(shoulder_pos[0], shoulder_pos[1], shoulder_pos[2], shoulder_ctrl_offset)
        cmds.rotate(shoulder_rot[0], shoulder_rot[1], shoulder_rot[2], shoulder_ctrl_offset)
        cmds.parent(shoulder_ctrl, shoulder_ctrl_offset, relative=1)

        # Front foot
        paw = cmds.ls(self.jnt_list[3])
        paw_ctrl = cmds.duplicate('Paw_tempShape', name=self.ctrl_list[3])[0]
        paw_pos = cmds.xform(paw, q=1, ws=1, t=1)
        cmds.move(paw_pos[0], 0, paw_pos[2], paw_ctrl)

        # custom attribute for later pivot group access
        cmds.addAttr(paw_ctrl, longName='Flex', attributeType='double', keyable=1)
        cmds.addAttr(paw_ctrl, longName='Swivel', attributeType='double', keyable=1)
        cmds.addAttr(paw_ctrl, longName='Toe_Tap', attributeType='double', keyable=1)
        cmds.addAttr(paw_ctrl, longName='Toe_Tip', attributeType='double', keyable=1)
        cmds.addAttr(paw_ctrl, longName='Wrist', attributeType='double', keyable=1)
        cmds.makeIdentity(paw_ctrl, apply=1, t=1, r=1, s=1)

        # Elbow control - aka. pole vector
        elbow = cmds.ls(self.jnt_list[1])
        pole_ctrl = cmds.duplicate('Pole_tempShape', name=self.ctrl_list[1])[0]
        pole_ctrl_offset = cmds.group(em=1, name=self.ctrl_offset_list[1])
        elbow_pos = cmds.xform(elbow, q=1, ws=1, t=1)
        cmds.move(elbow_pos[0], elbow_pos[1], elbow_pos[2]-self.distance, pole_ctrl_offset)
        cmds.parent(pole_ctrl, pole_ctrl_offset, relative=1)
        cmds.parent(pole_ctrl_offset, paw_ctrl)

        outliner.batch_parent([shoulder_ctrl_offset, paw_ctrl], self.ctrl_grp)
        self.delete_shape()

    def build_ik(self):
        cmds.ikHandle(startJoint=self.jnt_list[0], endEffector=self.jnt_list[2], name=self.leg_ik_name, solver='ikRPsolver')
        cmds.ikHandle(startJoint=self.jnt_list[2], endEffector=self.jnt_list[3], name=self.foot_ik_name, solver='ikSCsolver')
        cmds.ikHandle(startJoint=self.jnt_list[3], endEffector=self.jnt_list[4], name=self.toe_ik_name, solver='ikSCsolver')
        cmds.setAttr(self.leg_ik_name+'.visibility', 0)
        cmds.setAttr(self.foot_ik_name+'.visibility', 0)
        cmds.setAttr(self.toe_ik_name+'.visibility', 0)

    def add_measurement(self):
        # add length segment
        shoulder_pos = cmds.xform(self.jnt_list[0], q=1, ws=1, t=1)
        elbow_pos = cmds.xform(self.jnt_list[1], q=1, ws=1, t=1)
        wrist_pos = cmds.xform(self.jnt_list[2], q=1, ws=1, t=1)
        straighten_len = ((shoulder_pos[0]-elbow_pos[0]) ** 2+(shoulder_pos[1]-elbow_pos[1]) ** 2+(shoulder_pos[2]-elbow_pos[2]) ** 2) ** 0.5+ \
                        ((wrist_pos[0]-elbow_pos[0]) ** 2+(wrist_pos[1]-elbow_pos[1]) ** 2+(wrist_pos[2]-elbow_pos[2]) ** 2) ** 0.5

        # create measurement
        measure_shape = cmds.distanceDimension(sp=shoulder_pos, ep=wrist_pos)
        locs = cmds.listConnections(measure_shape)
        measure_node = cmds.listRelatives(measure_shape, parent=1, type='transform')
        length_node = '{}length_node'.format(self.name)
        shoulder_loc = '{}shoulder_node'.format(self.name)
        elbow_loc = '{}elbow_node'.format(self.name)
        cmds.rename(measure_node, length_node)
        cmds.rename(locs[0], shoulder_loc)
        cmds.rename(locs[1], elbow_loc)

        stretch_node = cmds.shadingNode('multiplyDivide', asUtility=1, name='{}stretch_node'.format(self.name))
        cmds.setAttr(stretch_node+'.operation', 2)
        cmds.setAttr(stretch_node+'.input2X', straighten_len)
        cmds.connectAttr(length_node+'.distance', stretch_node+'.input1X')

        condition_node = cmds.shadingNode('condition', asUtility=1, name='{}condition_node'.format(self.name))
        cmds.connectAttr(stretch_node+'.outputX', condition_node+'.firstTerm')
        cmds.setAttr(condition_node+'.secondTerm', 1)
        cmds.setAttr(condition_node+'.operation', 2)  # Greater than
        cmds.connectAttr(stretch_node+'.outputX', condition_node+'.colorIf1R')
        cmds.setAttr(condition_node+'.colorIfFalseR', 1)

        cmds.connectAttr(condition_node+'.outColorR', self.jnt_list[0]+'.scaleX')
        cmds.connectAttr(condition_node+'.outColorR', self.jnt_list[1]+'.scaleX')

        cmds.setAttr(length_node+'.visibility', 0)
        cmds.setAttr(shoulder_loc+'.visibility', 0)
        cmds.setAttr(elbow_loc+'.visibility', 0)
        outliner.batch_parent([length_node, shoulder_loc, elbow_loc], self.ctrl_grp)

        cmds.parentConstraint(self.ctrl_list[0], shoulder_loc)
        cmds.parentConstraint(self.ctrl_list[3], elbow_loc, mo=1)

    def add_constraint(self):
        self.build_ik()

        # Shoulder pivot
        cmds.parentConstraint(self.ctrl_list[0], self.jnt_list[0])

        # Front foot pivot group
        toe_tap_pivot_grp = cmds.group(em=1, name='{}toetap_pivot_grp'.format(self.name))
        flex_pivot_grp = cmds.group(em=1, name='{}flex_pivot_grp'.format(self.name))
        swivel_pivot_grp = cmds.group(em=1, name='{}swivel_pivot_grp'.format(self.name))
        toe_tip_pivot_grp = cmds.group(em=1, name='{}toetip_pivot_grp'.format(self.name))
        wrist_pivot_grp = cmds.group(em=1, name='{}wrist_pivot_grp'.format(self.name))

        paw_pos = cmds.xform(self.jnt_list[3], q=1, ws=1, t=1)
        toe_pos = cmds.xform(self.jnt_list[4], q=1, ws=1, t=1)
        wrist_pos = cmds.xform(self.jnt_list[2], q=1, ws=1, t=1)
        cmds.move(paw_pos[0], paw_pos[1], paw_pos[2], toe_tap_pivot_grp)
        cmds.move(paw_pos[0], paw_pos[1], paw_pos[2], flex_pivot_grp)
        cmds.move(paw_pos[0], paw_pos[1], paw_pos[2], swivel_pivot_grp)
        cmds.move(toe_pos[0], toe_pos[1], toe_pos[2], toe_tip_pivot_grp)
        cmds.move(wrist_pos[0], wrist_pos[1], wrist_pos[2], wrist_pivot_grp)

        cmds.parent(self.toe_ik_name, toe_tap_pivot_grp)
        outliner.batch_parent([self.leg_ik_name, self.foot_ik_name], flex_pivot_grp)
        outliner.batch_parent([toe_tap_pivot_grp, flex_pivot_grp], swivel_pivot_grp)
        cmds.parent(swivel_pivot_grp, toe_tip_pivot_grp)
        cmds.parent(toe_tip_pivot_grp, wrist_pivot_grp)
        cmds.parent(wrist_pivot_grp, self.ctrl_list[3])

        cmds.connectAttr(self.ctrl_list[3]+'.Flex', flex_pivot_grp+'.rotateX')
        cmds.connectAttr(self.ctrl_list[3]+'.Swivel', swivel_pivot_grp+'.rotateY')
        cmds.connectAttr(self.ctrl_list[3]+'.Toe_Tap', toe_tap_pivot_grp+'.rotateX')
        cmds.connectAttr(self.ctrl_list[3]+'.Toe_Tip', toe_tip_pivot_grp+'.rotateX')
        cmds.connectAttr(self.ctrl_list[3]+'.Wrist', wrist_pivot_grp+'.rotateX')

        # Pole vector constraint
        cmds.poleVectorConstraint(self.ctrl_list[1], self.leg_ik_name)

        # Scalable rig setup
        self.add_measurement()


class LegBack(base.Base):
    """ This module creates a quadruped back leg rig"""

    def __init__(self, side, base_name):
        """ Initialize LegFront with side and name

        :param side: str
        :param base_name: str
        """

        base.Base.__init__(self, side, base_name)
        self.meta_type = 'BackLeg'
        self.assign_naming()
        self.assign_secondary_naming()

    def assign_secondary_naming(self):
        self.loc_list, self.jnt_list, self.ctrl_list, self.ctrl_offset_list, self.jnt_helper_list = ([] for i in range(5))
        self.limb_components = ['hip', 'knee', 'ankle', 'paw', 'toe']
        for component in self.limb_components:
            self.loc_list.append('{}{}_loc'.format(self.name, component))
            self.jnt_list.append('{}{}_jnt'.format(self.name, component))
            self.jnt_helper_list.append('{}{}helper_jnt'.format(self.name, component))
            self.ctrl_list.append('{}{}_ctrl'.format(self.name, component))
            self.ctrl_offset_list.append('{}{}_offset'.format(self.name, component))

        # ik has different ctrl name
        self.leg_ik_name = '{}leg_ik'.format(self.name)
        self.foot_ik_name = '{}foot_ik'.format(self.name)
        self.toe_ik_name = '{}toe_ik'.format(self.name)
        self.helper_ik_name = '{}helper_ik'.format(self.name)

    def set_locator_attr(self, start_pos=[0, 5, -3], distance=1.5, height=0.2, scale=0.4):
        self.start_pos = start_pos
        self.distance = distance
        self.height = height
        self.scale = scale

    @staticmethod
    def set_controller_shape():
        sphere = cmds.createNode('implicitSphere')
        sphere_ctrl = cmds.rename(cmds.listRelatives(sphere, p=1), 'Hip_tempShape')
        cmds.scale(0.5, 0.5, 0.5, sphere_ctrl)

        pole = cmds.createNode('implicitSphere')
        pole_ctrl = cmds.rename(cmds.listRelatives(pole, p=1), 'Pole_tempShape')
        cmds.scale(0.2, 0.2, 0.2, pole_ctrl)

        ctrl_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Foot_tempShape')
        cmds.scale(0.5, 0.5, 0.5, ctrl_shape)

    def build_guide(self):
        grp = cmds.group(em=1, n=self.loc_grp_name)

        # Hip
        hip = cmds.spaceLocator(n=self.loc_list[0])
        cmds.parent(hip, grp, relative=1)
        cmds.move(self.start_pos[0], self.start_pos[1], self.start_pos[2], hip, relative=1)
        cmds.scale(self.scale, self.scale, self.scale, hip)

        # Knee
        knee = cmds.spaceLocator(n=self.loc_list[1])
        cmds.parent(knee, hip, relative=1)
        cmds.move(0, -self.distance, 0, knee, relative=1)

        # Ankle
        ankle = cmds.spaceLocator(n=self.loc_list[2])
        cmds.parent(ankle, knee, relative=1)
        cmds.move(0, -self.distance, -0.5 * self.distance, ankle, relative=1)

        # Foot
        foot = cmds.spaceLocator(n=self.loc_list[3])
        cmds.parent(foot, ankle, relative=1)
        cmds.move(0, -self.distance+self.height, 0, foot, relative=1)

        # Toe
        toe = cmds.spaceLocator(n=self.loc_list[4])
        cmds.parent(toe, foot, relative=1)
        cmds.move(0, 0, 0.5 * self.distance, toe, relative=1)

        self.color_locator()
        cmds.parent(grp, self.loc_grp)
        return grp

    def construct_joint(self):
        # Result joint chain
        cmds.select(clear=1)
        for index in range(len(self.loc_list)):
            loc = cmds.ls(self.loc_list[index], transforms=1)
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnt_list[index])
            cmds.setAttr(jnt+'.radius', self.scale)
        joint.orient_joint(self.jnt_list[0])
        cmds.parent(self.jnt_list[0], self.jnt_grp)

        # Helper joint chain
        cmds.select(clear=1)
        for index in range(len(self.loc_list[:-1])):
            loc = cmds.ls(self.loc_list[index], transforms=1)
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnt_helper_list[index])
            cmds.setAttr(jnt+'.radius', 1)
        joint.orient_joint(self.jnt_helper_list[0])
        cmds.parent(self.jnt_helper_list[0], self.jnt_grp)
        cmds.setAttr(self.jnt_helper_list[0]+'.visibility', 0)

        return self.jnt_list[0]

    def place_controller(self):
        self.set_controller_shape()

        # Hip
        hip = cmds.ls(self.jnt_list[0])
        hip_ctrl = cmds.duplicate('Hip_tempShape', name=self.ctrl_list[0])[0]
        hip_pos = cmds.xform(hip, q=1, ws=1, t=1)
        hip_rot = cmds.xform(hip, q=1, ws=1, ro=1)

        hip_ctrl_offset = cmds.group(em=1, name=self.ctrl_offset_list[0])
        cmds.move(hip_pos[0], hip_pos[1], hip_pos[2], hip_ctrl_offset)
        cmds.rotate(hip_rot[0], hip_rot[1], hip_rot[2], hip_ctrl_offset)
        cmds.parent(hip_ctrl, hip_ctrl_offset, relative=1)

        # Back foot
        foot = cmds.ls(self.jnt_list[3])
        foot_ctrl = cmds.duplicate('Foot_tempShape', name=self.ctrl_list[3])[0]
        foot_pos = cmds.xform(foot, q=1, ws=1, t=1)
        cmds.move(foot_pos[0], 0, foot_pos[2], foot_ctrl)
        cmds.makeIdentity(foot_ctrl, apply=1, t=1, r=1, s=1)

        # custom attribute for later pivot group access
        cmds.addAttr(foot_ctrl, longName='Flex', attributeType='double', keyable=1)
        cmds.addAttr(foot_ctrl, longName='Swivel', attributeType='double', keyable=1)
        cmds.addAttr(foot_ctrl, longName='Toe_Tap', attributeType='double', keyable=1)
        cmds.addAttr(foot_ctrl, longName='Toe_Tip', attributeType='double', keyable=1)

        # Ankle control - poleVector
        ankle = cmds.ls(self.jnt_list[2])
        pole_ctrl = cmds.duplicate('Pole_tempShape', name=self.ctrl_list[2])[0]
        pole_ctrl_offset = cmds.group(em=1, name=self.ctrl_offset_list[2])
        ankle_pos = cmds.xform(ankle, q=1, ws=1, t=1)
        cmds.move(ankle_pos[0], ankle_pos[1], ankle_pos[2]+self.distance, pole_ctrl_offset)
        cmds.parent(pole_ctrl, pole_ctrl_offset, relative=1)
        cmds.parent(pole_ctrl_offset, foot_ctrl)

        outliner.batch_parent([hip_ctrl_offset, foot_ctrl], self.ctrl_grp)
        self.delete_shape()

    def build_ik(self):
        cmds.ikHandle(startJoint=self.jnt_list[0], endEffector=self.jnt_list[2], name=self.leg_ik_name, solver='ikRPsolver')
        cmds.ikHandle(startJoint=self.jnt_list[2], endEffector=self.jnt_list[3], name=self.foot_ik_name, solver='ikSCsolver')
        cmds.ikHandle(startJoint=self.jnt_list[3], endEffector=self.jnt_list[4], name=self.toe_ik_name, solver='ikSCsolver')
        cmds.ikHandle(startJoint=self.jnt_helper_list[0], endEffector=self.jnt_helper_list[3], name=self.helper_ik_name, solver='ikRPsolver')
        cmds.setAttr(self.leg_ik_name+'.visibility', 0)
        cmds.setAttr(self.foot_ik_name+'.visibility', 0)
        cmds.setAttr(self.toe_ik_name+'.visibility', 0)
        cmds.setAttr(self.helper_ik_name+'.visibility', 0)

    def add_measurement(self):
        # add length segment
        hip_pos = cmds.xform(self.jnt_list[0], q=1, ws=1, t=1)
        knee_pos = cmds.xform(self.jnt_list[1], q=1, ws=1, t=1)
        ankle_pos = cmds.xform(self.jnt_list[2], q=1, ws=1, t=1)
        foot_pos = cmds.xform(self.jnt_list[3], q=1, ws=1, t=1)
        straighten_len = ((knee_pos[0]-ankle_pos[0]) ** 2+(knee_pos[1]-ankle_pos[1]) ** 2+(knee_pos[2]-ankle_pos[2]) ** 2) ** 0.5+ \
                        ((foot_pos[0]-ankle_pos[0]) ** 2+(foot_pos[1]-ankle_pos[1]) ** 2+(foot_pos[2]-ankle_pos[2]) ** 2) ** 0.5+ \
                        ((hip_pos[0]-knee_pos[0]) ** 2+(hip_pos[1]-knee_pos[1]) ** 2+(hip_pos[2]-knee_pos[2]) ** 2) ** 0.5

        # create measurement
        measure_shape = cmds.distanceDimension(sp=hip_pos, ep=foot_pos)
        locs = cmds.listConnections(measure_shape)
        measure_node = cmds.listRelatives(measure_shape, parent=1, type='transform')
        length_node = '{}length_node'.format(self.name)
        hip_loc = '{}hip_node'.format(self.name)
        ankle_loc = '{}ankle_node'.format(self.name)
        cmds.rename(measure_node, length_node)
        cmds.rename(locs[0], hip_loc)
        cmds.rename(locs[1], ankle_loc)

        stretch_node = cmds.shadingNode('multiplyDivide', asUtility=1, name='{}stretch_node'.format(self.name))
        cmds.setAttr(stretch_node+'.operation', 2)
        cmds.setAttr(stretch_node+'.input2X', straighten_len)
        cmds.connectAttr(length_node+'.distance', stretch_node+'.input1X')

        condition_node = cmds.shadingNode('condition', asUtility=1, name='{}condition_node'.format(self.name))
        cmds.connectAttr(stretch_node+'.outputX', condition_node+'.firstTerm')
        cmds.setAttr(condition_node+'.secondTerm', 1)
        cmds.setAttr(condition_node+'.operation', 2)  # greater than
        cmds.connectAttr(stretch_node+'.outputX', condition_node+'.colorIf1R')
        cmds.setAttr(condition_node+'.colorIfFalseR', 1)

        for joint in [self.jnt_list[0], self.jnt_list[1], self.jnt_list[2],
                      self.jnt_helper_list[0], self.jnt_helper_list[1], self.jnt_helper_list[2]]:
            cmds.connectAttr(condition_node+'.outColorR', joint+'.scaleX')

        cmds.setAttr(length_node+'.visibility', 0)
        cmds.setAttr(hip_loc+'.visibility', 0)
        cmds.setAttr(ankle_loc+'.visibility', 0)
        outliner.batch_parent([length_node, hip_loc, ankle_loc], self.ctrl_grp)

        cmds.parentConstraint(self.ctrl_list[0], hip_loc)
        cmds.parentConstraint(self.ctrl_list[3], ankle_loc, mo=1)

    def add_constraint(self):
        self.build_ik()

        # Shoulder pivot
        cmds.parentConstraint(self.ctrl_list[0], self.jnt_list[0])
        cmds.parentConstraint(self.ctrl_list[0], self.jnt_helper_list[0])

        # Front foot pivot group
        toe_tap_pivot_grp = cmds.group(em=1, name='{}toetap_pivot_grp'.format(self.name))
        flex_pivot_grp = cmds.group(em=1, name='{}flex_pivot_grp'.format(self.name))
        flex_offset_grp = cmds.group(em=1, name='{}flex_offset_grp'.format(self.name))
        swivel_pivot_grp = cmds.group(em=1, name='{}swivel_pivot_grp'.format(self.name))
        toe_tip_pivot_grp = cmds.group(em=1, name='{}toetip_pivot_grp'.format(self.name))

        foot_pos = cmds.xform(self.jnt_list[3], q=1, ws=1, t=1)
        toe_pos = cmds.xform(self.jnt_list[4], q=1, ws=1, t=1)

        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2], flex_offset_grp)
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2], flex_pivot_grp)
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2], toe_tap_pivot_grp)
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2], swivel_pivot_grp)
        cmds.move(toe_pos[0], toe_pos[1], toe_pos[2], toe_tip_pivot_grp)

        outliner.batch_parent([self.leg_ik_name, self.foot_ik_name], flex_pivot_grp)
        cmds.parent(flex_pivot_grp, flex_offset_grp)
        cmds.parentConstraint(self.jnt_helper_list[3], flex_offset_grp, mo=1)
        outliner.batch_parent([self.toe_ik_name, self.helper_ik_name], toe_tap_pivot_grp)
        outliner.batch_parent([toe_tap_pivot_grp, flex_offset_grp], toe_tip_pivot_grp)
        cmds.parent(toe_tip_pivot_grp, swivel_pivot_grp)
        cmds.parent(swivel_pivot_grp, self.ctrl_list[3])

        cmds.connectAttr(self.ctrl_list[3]+'.Flex', flex_pivot_grp+'.rotateX')
        cmds.connectAttr(self.ctrl_list[3]+'.Swivel', swivel_pivot_grp+'.rotateY')
        cmds.connectAttr(self.ctrl_list[3]+'.Toe_Tap', toe_tap_pivot_grp+'.rotateX')
        cmds.connectAttr(self.ctrl_list[3]+'.Toe_Tip', toe_tip_pivot_grp+'.rotateX')

        # Pole vector constraint
        cmds.poleVectorConstraint(self.ctrl_list[2], self.leg_ik_name)
        cmds.poleVectorConstraint(self.ctrl_list[2], self.helper_ik_name)
        cmds.parent(self.ctrl_offset_list[2], swivel_pivot_grp)

        # Scalable rig setup
        self.add_measurement()
