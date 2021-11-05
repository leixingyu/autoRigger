import maya.cmds as cmds

from . import foot
from .base import bone
from .limb import limb
from autoRigger import util
from utility.setup import outliner
from utility.rigging import joint


class Leg(bone.Bone):
    """ This module create a biped leg rig"""

    def __init__(self, side, name, rig_type='Leg', distance=4, interval=0.5, height=0.4):
        """ Initialize Leg class with side and name

        :param side: str
        :param name: str
        """

        self.distance = distance
        self.interval = interval
        self.height = height
        self.scale = 0.2

        bone.Bone.__init__(self, side, name, rig_type)

        self.limb = limb.Limb(
            side=self._side,
            name=name,
            interval=self.distance,
            limb_type='Leg'
        )

        self.foot = foot.Foot(
            side=self._side,
            name=name,
            interval=self.interval,
            height=self.height
        )

    def create_locator(self):
        self.limb.create_locator()
        self.foot.create_locator()

        util.move(self.foot.ankle_loc, [0, -2*self.distance, 0])

        cmds.parent(self.foot.ankle_loc, self.limb.locs[-1])

    def set_controller_shape(self):
        self.limb.set_controller_shape()
        self.foot.set_controller_shape()

    def create_joint(self):
        self.limb.create_joint()
        self.foot.create_joint()

    def place_controller(self):
        self.limb.place_controller()
        self.foot.place_controller()

    def add_constraint(self):
        self.limb.add_constraint()
        self.foot.add_constraint()

        # Connect
        # IK constraint #
        cmds.parentConstraint(self.foot.rev_ankle_jnt, self.limb.ik_ctrl, mo=1)
        cmds.setAttr(self.limb.ik_ctrl+'.visibility', 0)

        # FK constraint #
        cmds.parentConstraint(self.limb.jnts[-1], self.foot.fk_ankle_jnt, mo=1)
        cmds.parent(self.foot.fk_ctrl, self.limb.fk_ctrls[-1])

        # IK/FK switch #
        cmds.setDrivenKeyframe(self.limb.switch_ctrl+'.FK_IK', currentDriver=self.foot.switch_ctrl+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.limb.switch_ctrl+'.FK_IK', currentDriver=self.foot.switch_ctrl+'.FK_IK', driverValue=0, value=0)

        # Sub controller visibility and channel hide #
        cmds.setDrivenKeyframe(self.limb.ik_ctrl+'.visibility', currentDriver=self.limb.switch_ctrl+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.limb.ik_ctrl+'.visibility', currentDriver=self.limb.switch_ctrl+'.FK_IK', driverValue=0, value=0)
        cmds.setAttr(self.limb.switch_ctrl+'.FK_IK', l=1, k=0)

    def delete_guide(self):
        self.foot.delete_guide()
        self.limb.delete_guide()

    def color_controller(self):
        self.limb.color_controller()
        self.foot.color_controller()


class LegFront(bone.Bone):
    """ This module creates a quadruped front leg rig"""

    def __init__(self, side, name, rig_type='FrontLeg', distance=1.5, height=0.2):
        """ Initialize LegFront with side and name

        :param side: str
        :param name: str
        """
        self.distance = distance
        self.height = height
        self.scale = 0.4

        # names
        self.locs, self.jnts, self.ctrls, self.ctrl_offsets = ([] for _ in range(4))
        self.limb_components = ['shoulder', 'elbow', 'wrist', 'paw', 'toe']
        self.leg_ik = None
        self.foot_ik = None
        self.toe_ik = None

        bone.Bone.__init__(self, side, name, rig_type)

    def assign_secondary_naming(self):
        for component in self.limb_components:
            self.locs.append('{}{}_loc'.format(self.base_name, component))
            self.jnts.append('{}{}_jnt'.format(self.base_name, component))
            self.ctrls.append('{}{}_ctrl'.format(self.base_name, component))
            self.ctrl_offsets.append('{}{}_offset'.format(self.base_name, component))

        # ik has different ctrl name
        self.leg_ik = '{}leg_ik'.format(self.base_name)
        self.foot_ik = '{}foot_ik'.format(self.base_name)
        self.toe_ik = '{}toe_ik'.format(self.base_name)

    def set_controller_shape(self):
        self._shape = list(range(3))

        sphere = cmds.createNode('implicitSphere')
        self._shape[0] = cmds.rename(cmds.listRelatives(sphere, p=1), self.namer.tmp)
        cmds.scale(0.5, 0.5, 0.5, self._shape[0])

        pole = cmds.createNode('implicitSphere')
        self._shape[1] = cmds.rename(cmds.listRelatives(pole, p=1), self.namer.tmp)
        cmds.scale(0.2, 0.2, 0.2, self._shape[1])

        self._shape[2] = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name=self.namer.tmp)[0]
        cmds.scale(0.5, 0.5, 0.5, self._shape[2])

    def create_locator(self):

        # Shoulder
        shoulder = cmds.spaceLocator(n=self.locs[0])
        cmds.scale(self.scale, self.scale, self.scale, shoulder)

        # Elbow
        elbow = cmds.spaceLocator(n=self.locs[1])
        cmds.parent(elbow, shoulder, relative=1)
        cmds.move(0, -self.distance, -0.5 * self.distance, elbow, relative=1)

        # Wrist
        wrist = cmds.spaceLocator(n=self.locs[2])
        cmds.parent(wrist, elbow, relative=1)
        cmds.move(0, -self.distance, 0, wrist, relative=1)

        # Paw
        paw = cmds.spaceLocator(n=self.locs[3])
        cmds.parent(paw, wrist, relative=1)
        cmds.move(0, -self.distance+self.height, 0.5 * self.distance, paw, relative=1)

        # Toe
        toe = cmds.spaceLocator(n=self.locs[4])
        cmds.parent(toe, paw, relative=1)
        cmds.move(0, 0, 0.5 * self.distance, toe, relative=1)

        cmds.parent(self.locs[0], util.G_LOC_GRP)

    def create_joint(self):
        cmds.select(clear=1)
        for index in range(len(self.locs)):
            loc = cmds.ls(self.locs[index], transforms=1)
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnts[index])
            cmds.setAttr(jnt+'.radius', self.scale)

        cmds.parent(self.jnts[0], util.G_JNT_GRP)
        joint.orient_joint(self.jnts[0])
        return self.jnts[0]

    def place_controller(self):
        # Shoulder
        shoulder = cmds.ls(self.jnts[0])
        shoulder_ctrl = cmds.duplicate(self._shape[0], name=self.ctrls[0])[0]
        shoulder_pos = cmds.xform(shoulder, q=1, ws=1, t=1)
        shoulder_rot = cmds.xform(shoulder, q=1, ws=1, ro=1)

        shoulder_ctrl_offset = cmds.group(em=1, name=self.ctrl_offsets[0])
        cmds.move(shoulder_pos[0], shoulder_pos[1], shoulder_pos[2], shoulder_ctrl_offset)
        cmds.rotate(shoulder_rot[0], shoulder_rot[1], shoulder_rot[2], shoulder_ctrl_offset)
        cmds.parent(shoulder_ctrl, shoulder_ctrl_offset, relative=1)

        # Front foot
        paw = cmds.ls(self.jnts[3])
        paw_ctrl = cmds.duplicate(self._shape[2], name=self.ctrls[3])[0]
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
        elbow = cmds.ls(self.jnts[1])
        pole_ctrl = cmds.duplicate(self._shape[1], name=self.ctrls[1])[0]
        pole_ctrl_offset = cmds.group(em=1, name=self.ctrl_offsets[1])
        elbow_pos = cmds.xform(elbow, q=1, ws=1, t=1)
        cmds.move(elbow_pos[0], elbow_pos[1], elbow_pos[2]-self.distance, pole_ctrl_offset)
        cmds.parent(pole_ctrl, pole_ctrl_offset, relative=1)
        cmds.parent(pole_ctrl_offset, paw_ctrl)

        outliner.batch_parent([shoulder_ctrl_offset, paw_ctrl], util.G_CTRL_GRP)

    def build_ik(self):
        cmds.ikHandle(startJoint=self.jnts[0], endEffector=self.jnts[2], name=self.leg_ik, solver='ikRPsolver')
        cmds.ikHandle(startJoint=self.jnts[2], endEffector=self.jnts[3], name=self.foot_ik, solver='ikSCsolver')
        cmds.ikHandle(startJoint=self.jnts[3], endEffector=self.jnts[4], name=self.toe_ik, solver='ikSCsolver')
        cmds.setAttr(self.leg_ik+'.visibility', 0)
        cmds.setAttr(self.foot_ik+'.visibility', 0)
        cmds.setAttr(self.toe_ik+'.visibility', 0)

    def add_measurement(self):
        # add length segment
        shoulder_pos = cmds.xform(self.jnts[0], q=1, ws=1, t=1)
        elbow_pos = cmds.xform(self.jnts[1], q=1, ws=1, t=1)
        wrist_pos = cmds.xform(self.jnts[2], q=1, ws=1, t=1)
        straighten_len = ((shoulder_pos[0]-elbow_pos[0])**2+(shoulder_pos[1]-elbow_pos[1])**2+(shoulder_pos[2]-elbow_pos[2])**2)**0.5 + \
                        ((wrist_pos[0]-elbow_pos[0]) ** 2+(wrist_pos[1]-elbow_pos[1]) ** 2+(wrist_pos[2]-elbow_pos[2]) ** 2) ** 0.5

        # create measurement
        measure_shape = cmds.distanceDimension(sp=shoulder_pos, ep=wrist_pos)
        locs = cmds.listConnections(measure_shape)
        measure_node = cmds.listRelatives(measure_shape, parent=1, type='transform')
        length_node = '{}length_node'.format(self.base_name)
        shoulder_loc = '{}shoulder_node'.format(self.base_name)
        elbow_loc = '{}elbow_node'.format(self.base_name)
        cmds.rename(measure_node, length_node)
        cmds.rename(locs[0], shoulder_loc)
        cmds.rename(locs[1], elbow_loc)

        stretch_node = cmds.shadingNode('multiplyDivide', asUtility=1, name='{}stretch_node'.format(self.base_name))
        cmds.setAttr(stretch_node+'.operation', 2)
        cmds.setAttr(stretch_node+'.input2X', straighten_len)
        cmds.connectAttr(length_node+'.distance', stretch_node+'.input1X')

        condition_node = cmds.shadingNode('condition', asUtility=1, name='{}condition_node'.format(self.base_name))
        cmds.connectAttr(stretch_node+'.outputX', condition_node+'.firstTerm')
        cmds.setAttr(condition_node+'.secondTerm', 1)
        cmds.setAttr(condition_node+'.operation', 2)  # Greater than
        cmds.connectAttr(stretch_node+'.outputX', condition_node+'.colorIfTrueR')
        cmds.setAttr(condition_node+'.colorIfFalseR', 1)

        cmds.connectAttr(condition_node+'.outColorR', self.jnts[0]+'.scaleX')
        cmds.connectAttr(condition_node+'.outColorR', self.jnts[1]+'.scaleX')

        cmds.setAttr(length_node+'.visibility', 0)
        cmds.setAttr(shoulder_loc+'.visibility', 0)
        cmds.setAttr(elbow_loc+'.visibility', 0)
        outliner.batch_parent([length_node, shoulder_loc, elbow_loc], util.G_CTRL_GRP)

        cmds.parentConstraint(self.ctrls[0], shoulder_loc)
        cmds.parentConstraint(self.ctrls[3], elbow_loc, mo=1)

    def add_constraint(self):
        self.build_ik()

        # Shoulder pivot
        cmds.parentConstraint(self.ctrls[0], self.jnts[0])

        # Front foot pivot group
        toe_tap_pivot_grp = cmds.group(em=1, name='{}toetap_pivot_grp'.format(self.base_name))
        flex_pivot_grp = cmds.group(em=1, name='{}flex_pivot_grp'.format(self.base_name))
        swivel_pivot_grp = cmds.group(em=1, name='{}swivel_pivot_grp'.format(self.base_name))
        toe_tip_pivot_grp = cmds.group(em=1, name='{}toetip_pivot_grp'.format(self.base_name))
        wrist_pivot_grp = cmds.group(em=1, name='{}wrist_pivot_grp'.format(self.base_name))

        paw_pos = cmds.xform(self.jnts[3], q=1, ws=1, t=1)
        toe_pos = cmds.xform(self.jnts[4], q=1, ws=1, t=1)
        wrist_pos = cmds.xform(self.jnts[2], q=1, ws=1, t=1)
        cmds.move(paw_pos[0], paw_pos[1], paw_pos[2], toe_tap_pivot_grp)
        cmds.move(paw_pos[0], paw_pos[1], paw_pos[2], flex_pivot_grp)
        cmds.move(paw_pos[0], paw_pos[1], paw_pos[2], swivel_pivot_grp)
        cmds.move(toe_pos[0], toe_pos[1], toe_pos[2], toe_tip_pivot_grp)
        cmds.move(wrist_pos[0], wrist_pos[1], wrist_pos[2], wrist_pivot_grp)

        cmds.parent(self.toe_ik, toe_tap_pivot_grp)
        outliner.batch_parent([self.leg_ik, self.foot_ik], flex_pivot_grp)
        outliner.batch_parent([toe_tap_pivot_grp, flex_pivot_grp], swivel_pivot_grp)
        cmds.parent(swivel_pivot_grp, toe_tip_pivot_grp)
        cmds.parent(toe_tip_pivot_grp, wrist_pivot_grp)
        cmds.parent(wrist_pivot_grp, self.ctrls[3])

        cmds.connectAttr(self.ctrls[3]+'.Flex', flex_pivot_grp+'.rotateX')
        cmds.connectAttr(self.ctrls[3]+'.Swivel', swivel_pivot_grp+'.rotateY')
        cmds.connectAttr(self.ctrls[3]+'.Toe_Tap', toe_tap_pivot_grp+'.rotateX')
        cmds.connectAttr(self.ctrls[3]+'.Toe_Tip', toe_tip_pivot_grp+'.rotateX')
        cmds.connectAttr(self.ctrls[3]+'.Wrist', wrist_pivot_grp+'.rotateX')

        # Pole vector constraint
        cmds.poleVectorConstraint(self.ctrls[1], self.leg_ik)

        # Scalable rig setup
        self.add_measurement()


class LegBack(bone.Bone):
    """ This module creates a quadruped back leg rig"""

    def __init__(self, side, name, rig_type='BackLeg', distance=1.5, height=0.2):
        """ Initialize LegFront with side and name

        :param side: str
        :param name: str
        """

        self.distance = distance
        self.height = height
        self.scale = 0.4

        # names
        self.locs, self.jnts, self.ctrls, self.ctrl_offsets, self.jnt_helpers = ([] for i in range(5))
        self.limb_components = ['hip', 'knee', 'ankle', 'paw', 'toe']
        self.leg_ik = None
        self.foot_ik = None
        self.toe_ik = None
        self.helper_ik = None

        bone.Bone.__init__(self, side, name, rig_type)

    def assign_secondary_naming(self):
        for component in self.limb_components:
            self.locs.append('{}{}_loc'.format(self.base_name, component))
            self.jnts.append('{}{}_jnt'.format(self.base_name, component))
            self.jnt_helpers.append('{}{}helper_jnt'.format(self.base_name, component))
            self.ctrls.append('{}{}_ctrl'.format(self.base_name, component))
            self.ctrl_offsets.append('{}{}_offset'.format(self.base_name, component))

        # ik has different ctrl name
        self.leg_ik = '{}leg_ik'.format(self.base_name)
        self.foot_ik = '{}foot_ik'.format(self.base_name)
        self.toe_ik = '{}toe_ik'.format(self.base_name)
        self.helper_ik = '{}helper_ik'.format(self.base_name)

    def set_controller_shape(self):
        self._shape = list(range(3))

        sphere = cmds.createNode('implicitSphere')
        self._shape[0] = cmds.rename(cmds.listRelatives(sphere, p=1), self.namer.tmp)
        cmds.scale(0.5, 0.5, 0.5, self._shape[0])

        pole = cmds.createNode('implicitSphere')
        self._shape[1] = cmds.rename(cmds.listRelatives(pole, p=1), self.namer.tmp)
        cmds.scale(0.2, 0.2, 0.2, self._shape[1])

        self._shape[2] = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name=self.namer.tmp)[0]
        cmds.scale(0.5, 0.5, 0.5, self._shape[2])

    def create_locator(self):
        # Hip
        hip = cmds.spaceLocator(n=self.locs[0])
        cmds.scale(self.scale, self.scale, self.scale, hip)

        # Knee
        knee = cmds.spaceLocator(n=self.locs[1])
        cmds.parent(knee, hip, relative=1)
        cmds.move(0, -self.distance, 0, knee, relative=1)

        # Ankle
        ankle = cmds.spaceLocator(n=self.locs[2])
        cmds.parent(ankle, knee, relative=1)
        cmds.move(0, -self.distance, -0.5 * self.distance, ankle, relative=1)

        # Foot
        foot = cmds.spaceLocator(n=self.locs[3])
        cmds.parent(foot, ankle, relative=1)
        cmds.move(0, -self.distance+self.height, 0, foot, relative=1)

        # Toe
        toe = cmds.spaceLocator(n=self.locs[4])
        cmds.parent(toe, foot, relative=1)
        cmds.move(0, 0, 0.5 * self.distance, toe, relative=1)

        cmds.parent(self.locs[0], util.G_LOC_GRP)
        return self.locs[0]

    def create_joint(self):
        # Result joint chain
        cmds.select(clear=1)
        for index in range(len(self.locs)):
            loc = cmds.ls(self.locs[index], transforms=1)
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnts[index])
            cmds.setAttr(jnt+'.radius', self.scale)
        joint.orient_joint(self.jnts[0])
        cmds.parent(self.jnts[0], util.G_JNT_GRP)

        # Helper joint chain
        cmds.select(clear=1)
        for index in range(len(self.locs[:-1])):
            loc = cmds.ls(self.locs[index], transforms=1)
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnt_helpers[index])
            cmds.setAttr(jnt+'.radius', 1)
        joint.orient_joint(self.jnt_helpers[0])
        cmds.parent(self.jnt_helpers[0], util.G_JNT_GRP)
        cmds.setAttr(self.jnt_helpers[0]+'.visibility', 0)

        return self.jnts[0]

    def place_controller(self):
        # Hip
        hip = cmds.ls(self.jnts[0])
        hip_ctrl = cmds.duplicate(self._shape[0], name=self.ctrls[0])[0]
        hip_pos = cmds.xform(hip, q=1, ws=1, t=1)
        hip_rot = cmds.xform(hip, q=1, ws=1, ro=1)

        hip_ctrl_offset = cmds.group(em=1, name=self.ctrl_offsets[0])
        cmds.move(hip_pos[0], hip_pos[1], hip_pos[2], hip_ctrl_offset)
        cmds.rotate(hip_rot[0], hip_rot[1], hip_rot[2], hip_ctrl_offset)
        cmds.parent(hip_ctrl, hip_ctrl_offset, relative=1)

        # Back foot
        foot = cmds.ls(self.jnts[3])
        foot_ctrl = cmds.duplicate(self._shape[2], name=self.ctrls[3])[0]
        foot_pos = cmds.xform(foot, q=1, ws=1, t=1)
        cmds.move(foot_pos[0], 0, foot_pos[2], foot_ctrl)
        cmds.makeIdentity(foot_ctrl, apply=1, t=1, r=1, s=1)

        # custom attribute for later pivot group access
        cmds.addAttr(foot_ctrl, longName='Flex', attributeType='double', keyable=1)
        cmds.addAttr(foot_ctrl, longName='Swivel', attributeType='double', keyable=1)
        cmds.addAttr(foot_ctrl, longName='Toe_Tap', attributeType='double', keyable=1)
        cmds.addAttr(foot_ctrl, longName='Toe_Tip', attributeType='double', keyable=1)

        # Ankle control - poleVector
        ankle = cmds.ls(self.jnts[2])
        pole_ctrl = cmds.duplicate(self._shape[1], name=self.ctrls[2])[0]
        pole_ctrl_offset = cmds.group(em=1, name=self.ctrl_offsets[2])
        ankle_pos = cmds.xform(ankle, q=1, ws=1, t=1)
        cmds.move(ankle_pos[0], ankle_pos[1], ankle_pos[2]+self.distance, pole_ctrl_offset)
        cmds.parent(pole_ctrl, pole_ctrl_offset, relative=1)
        cmds.parent(pole_ctrl_offset, foot_ctrl)

        outliner.batch_parent([hip_ctrl_offset, foot_ctrl], util.G_CTRL_GRP)

    def build_ik(self):
        cmds.ikHandle(startJoint=self.jnts[0], endEffector=self.jnts[2], name=self.leg_ik, solver='ikRPsolver')
        cmds.ikHandle(startJoint=self.jnts[2], endEffector=self.jnts[3], name=self.foot_ik, solver='ikSCsolver')
        cmds.ikHandle(startJoint=self.jnts[3], endEffector=self.jnts[4], name=self.toe_ik, solver='ikSCsolver')
        cmds.ikHandle(startJoint=self.jnt_helpers[0], endEffector=self.jnt_helpers[3], name=self.helper_ik, solver='ikRPsolver')
        cmds.setAttr(self.leg_ik+'.visibility', 0)
        cmds.setAttr(self.foot_ik+'.visibility', 0)
        cmds.setAttr(self.toe_ik+'.visibility', 0)
        cmds.setAttr(self.helper_ik+'.visibility', 0)

    def add_measurement(self):
        # add length segment
        hip_pos = cmds.xform(self.jnts[0], q=1, ws=1, t=1)
        knee_pos = cmds.xform(self.jnts[1], q=1, ws=1, t=1)
        ankle_pos = cmds.xform(self.jnts[2], q=1, ws=1, t=1)
        foot_pos = cmds.xform(self.jnts[3], q=1, ws=1, t=1)
        straighten_len = ((knee_pos[0]-ankle_pos[0]) ** 2+(knee_pos[1]-ankle_pos[1]) ** 2+(knee_pos[2]-ankle_pos[2]) ** 2) ** 0.5+ \
                        ((foot_pos[0]-ankle_pos[0]) ** 2+(foot_pos[1]-ankle_pos[1]) ** 2+(foot_pos[2]-ankle_pos[2]) ** 2) ** 0.5+ \
                        ((hip_pos[0]-knee_pos[0]) ** 2+(hip_pos[1]-knee_pos[1]) ** 2+(hip_pos[2]-knee_pos[2]) ** 2) ** 0.5

        # create measurement
        measure_shape = cmds.distanceDimension(sp=hip_pos, ep=foot_pos)
        locs = cmds.listConnections(measure_shape)
        measure_node = cmds.listRelatives(measure_shape, parent=1, type='transform')
        length_node = '{}length_node'.format(self.base_name)
        hip_loc = '{}hip_node'.format(self.base_name)
        ankle_loc = '{}ankle_node'.format(self.base_name)
        cmds.rename(measure_node, length_node)
        cmds.rename(locs[0], hip_loc)
        cmds.rename(locs[1], ankle_loc)

        stretch_node = cmds.shadingNode('multiplyDivide', asUtility=1, name='{}stretch_node'.format(self.base_name))
        cmds.setAttr(stretch_node+'.operation', 2)
        cmds.setAttr(stretch_node+'.input2X', straighten_len)
        cmds.connectAttr(length_node+'.distance', stretch_node+'.input1X')

        condition_node = cmds.shadingNode('condition', asUtility=1, name='{}condition_node'.format(self.base_name))
        cmds.connectAttr(stretch_node+'.outputX', condition_node+'.firstTerm')
        cmds.setAttr(condition_node+'.secondTerm', 1)
        cmds.setAttr(condition_node+'.operation', 2)  # greater than
        cmds.connectAttr(stretch_node+'.outputX', condition_node+'.colorIfTrueR')
        cmds.setAttr(condition_node+'.colorIfFalseR', 1)

        for joint in [self.jnts[0], self.jnts[1], self.jnts[2],
                      self.jnt_helpers[0], self.jnt_helpers[1], self.jnt_helpers[2]]:
            cmds.connectAttr(condition_node+'.outColorR', joint+'.scaleX')

        cmds.setAttr(length_node+'.visibility', 0)
        cmds.setAttr(hip_loc+'.visibility', 0)
        cmds.setAttr(ankle_loc+'.visibility', 0)
        outliner.batch_parent([length_node, hip_loc, ankle_loc], util.G_CTRL_GRP)

        cmds.parentConstraint(self.ctrls[0], hip_loc)
        cmds.parentConstraint(self.ctrls[3], ankle_loc, mo=1)

    def add_constraint(self):
        self.build_ik()

        # Shoulder pivot
        cmds.parentConstraint(self.ctrls[0], self.jnts[0])
        cmds.parentConstraint(self.ctrls[0], self.jnt_helpers[0])

        # Front foot pivot group
        toe_tap_pivot_grp = cmds.group(em=1, name='{}toetap_pivot_grp'.format(self.base_name))
        flex_pivot_grp = cmds.group(em=1, name='{}flex_pivot_grp'.format(self.base_name))
        flex_offset_grp = cmds.group(em=1, name='{}flex_offset_grp'.format(self.base_name))
        swivel_pivot_grp = cmds.group(em=1, name='{}swivel_pivot_grp'.format(self.base_name))
        toe_tip_pivot_grp = cmds.group(em=1, name='{}toetip_pivot_grp'.format(self.base_name))

        foot_pos = cmds.xform(self.jnts[3], q=1, ws=1, t=1)
        toe_pos = cmds.xform(self.jnts[4], q=1, ws=1, t=1)

        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2], flex_offset_grp)
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2], flex_pivot_grp)
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2], toe_tap_pivot_grp)
        cmds.move(foot_pos[0], foot_pos[1], foot_pos[2], swivel_pivot_grp)
        cmds.move(toe_pos[0], toe_pos[1], toe_pos[2], toe_tip_pivot_grp)

        outliner.batch_parent([self.leg_ik, self.foot_ik], flex_pivot_grp)
        cmds.parent(flex_pivot_grp, flex_offset_grp)
        cmds.parentConstraint(self.jnt_helpers[3], flex_offset_grp, mo=1)
        outliner.batch_parent([self.toe_ik, self.helper_ik], toe_tap_pivot_grp)
        outliner.batch_parent([toe_tap_pivot_grp, flex_offset_grp], toe_tip_pivot_grp)
        cmds.parent(toe_tip_pivot_grp, swivel_pivot_grp)
        cmds.parent(swivel_pivot_grp, self.ctrls[3])

        cmds.connectAttr(self.ctrls[3]+'.Flex', flex_pivot_grp+'.rotateX')
        cmds.connectAttr(self.ctrls[3]+'.Swivel', swivel_pivot_grp+'.rotateY')
        cmds.connectAttr(self.ctrls[3]+'.Toe_Tap', toe_tap_pivot_grp+'.rotateX')
        cmds.connectAttr(self.ctrls[3]+'.Toe_Tip', toe_tip_pivot_grp+'.rotateX')

        # Pole vector constraint
        cmds.poleVectorConstraint(self.ctrls[2], self.leg_ik)
        cmds.poleVectorConstraint(self.ctrls[2], self.helper_ik)
        cmds.parent(self.ctrl_offsets[2], swivel_pivot_grp)

        # Scalable rig setup
        self.add_measurement()
