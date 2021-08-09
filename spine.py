import maya.cmds as cmds
from . import rig
from utility import joint, outliner


class Spine(rig.Bone):
    """ This module creates a biped spine rig"""

    def __init__(self, side, base_name, start_pos=[0, 0, 0], length=6.0, segment=6):
        """ Initialize Spine class with side and name

        :param side: str
        :param base_name: str
        """

        rig.Bone.__init__(self, side, base_name)
        self.metaType = 'Spine'

        self.start_pos = start_pos
        self.interval = length/(segment-1)
        self.segment = segment
        self.scale = 0.5

        self.initial_setup()

    def assign_secondary_naming(self):
        self.loc_list, self.jnt_list, self.ctrl_list, self.cluster_list = ([] for i in range(4))
        for i in range(self.segment):
            self.loc_list.append('{}{}_loc'.format(self.name, i))
            self.jnt_list.append('{}{}_jnt'.format(self.name, i))
            self.ctrl_list.append('{}{}_ctrl'.format(self.name, i))
            self.cluster_list.append('{}{}_cluster'.format(self.name, i))
        # ik has different ctrl name
        self.ik_curve = '{}ik_curve'.format(self.name)
        self.ik_name = '{}_ik'.format(self.name)

    @staticmethod
    def set_controller_shape():
        global_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='SpineGlobal_tempShape')
        cmds.scale(2, 2, 2, global_shape)

        spine_shape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name='Spine_tempShape')
        selection_tip = cmds.select('Spine_tempShape.cv[5]')
        cmds.move(0, 0, 1.5, selection_tip, relative=1)
        selection_edge = cmds.select('Spine_tempShape.cv[4]', 'Spine_tempShape.cv[6]')
        cmds.scale(0.25, 0.25, 0.25, selection_edge, relative=1)
        cmds.move(0, 0, 0.75, relative=1)
        cmds.rotate(0, 0, 90, spine_shape)
        cmds.scale(0.5, 0.5, 0.5, spine_shape)

    def create_locator(self):
        grp = cmds.group(em=1, n=self.loc_grp_name)

        for i in range(self.segment):
            spine = cmds.spaceLocator(n=self.loc_list[i])
            # root locator of spine parent to the spine group
            if i is 0:
                cmds.parent(spine, grp, relative=1)
                cmds.move(self.start_pos[0], self.start_pos[1], self.start_pos[2], spine, absolute=1)
                cmds.scale(self.scale, self.scale, self.scale, spine)
            # spine locator parent to the previous locator
            else:
                cmds.parent(spine, self.loc_list[i-1], relative=1)
                # move spine locator along +y axis
                cmds.move(0, self.interval, 0, spine, relative=1)

        cmds.parent(grp, self.loc_global_grp)
        return grp

    def create_joint(self):
        cmds.select(clear=1)

        for i, loc in enumerate(self.loc_list):
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnt_list[i])
            cmds.setAttr(jnt + '.radius', self.scale)

        cmds.parent(self.jnt_list[0], self.jnt_global_grp)
        return self.jnt_list[0]
    
    def place_controller(self):
        grp = cmds.group(em=1, name=self.ctrl_grp_name)
        
        for i, spine in enumerate(self.jnt_list):
            spine_pos = cmds.xform(spine, q=1, t=1, ws=1)
            spine_ctrl = cmds.duplicate('Spine_tempShape', name=self.ctrl_list[i])[0]
            if i == 0:
                self.global_ctrl = cmds.duplicate('SpineGlobal_tempShape', name=self.ctrl_name)[0]
                cmds.move(spine_pos[0], spine_pos[1], spine_pos[2], self.global_ctrl)
                cmds.makeIdentity(self.global_ctrl, apply=1, t=1, r=1, s=1)
                cmds.parent(spine_ctrl, self.global_ctrl, relative=1)
            elif i != 0:
                cmds.parent(spine_ctrl, self.ctrl_list[i-1])
            cmds.move(spine_pos[0], spine_pos[1], spine_pos[2]-5, spine_ctrl)
            cmds.move(spine_pos[0], spine_pos[1], spine_pos[2], spine_ctrl+'.scalePivot', spine_ctrl+'.rotatePivot', absolute=1)
            cmds.makeIdentity(spine_ctrl, apply=1, t=1, r=1, s=1)

            # parent line shape under curve transform (combine curve shape)
            line = cmds.curve(degree=1, point=[(spine_pos[0], spine_pos[1], spine_pos[2]), (spine_pos[0], spine_pos[1], spine_pos[2]-5)], name='{}line{}_ctrl'.format(self.name, i))
            line_shape = cmds.listRelatives(line, shapes=1)
            cmds.parent(line_shape, spine_ctrl, relative=1, shape=1)
            cmds.delete(line)

        cmds.parent(self.ctrl_name, grp)
        cmds.parent(grp, self.ctrl_global_grp)
        return grp

    def build_ik(self):
        # Create Spine Curve
        curve_points = []
        for i, spine in enumerate(self.jnt_list):
            spine_pos = cmds.xform(spine, q=1, t=1, ws=1)
            curve_points.append(spine_pos)
        cmds.curve(p=curve_points, name=self.ik_curve)
        cmds.setAttr(self.ik_curve+'.visibility', 0)
        # turning off inherit transform avoid curve move/scale twice as much
        cmds.inheritTransform(self.ik_curve, off=1)

        # Create Spline IK
        cmds.ikHandle(startJoint=self.jnt_list[0], endEffector=self.jnt_list[-1], name=self.ik_name, curve=self.ik_curve, createCurve=False, parentCurve=1, roc=1, solver='ikSplineSolver')
        cmds.setAttr(self.ik_name+'.visibility', 0)
        cmds.parent(self.ik_name, self.ctrl_global_grp)

        # Create Cluster
        cvs = cmds.ls('{}.cv[0:]'.format(self.ik_curve), fl=1)
        for i, cv in enumerate(cvs):
            cluster = cmds.cluster(cv, name=self.cluster_list[i])[-1]
            if i != 0: cmds.parent(cluster, '{}Handle'.format(self.cluster_list[i-1]), relative=False)
            else: cmds.parent(cluster, self.ctrl_global_grp)
            cmds.setAttr(cluster+'.visibility', 0)

    def add_constraint(self):
        self.build_ik()
        for i in range(0, self.segment):
            spine_cluster = cmds.ls('{}Handle'.format(self.cluster_list[i]))
            spine_ctrl = cmds.ls(self.ctrl_list[i])
            cmds.pointConstraint(spine_ctrl, spine_cluster)
        cmds.connectAttr(self.ctrl_list[-1]+'.rotateY', '{}.twist'.format(self.ik_name))

    def lock_controller(self):
        for ctrl in self.ctrl_list:
            for transform in 'ts':
                for axis in 'xyz':
                    cmds.setAttr(ctrl+'.'+transform+axis, l=1, k=0)


class SpineQuad(rig.Bone):
    """ This module creates a quadruped spine rig """

    def __init__(self, side, base_name, start_pos=[0, 6, -3], length=6.0, segment=7):
        """ Initialize SpineQuad class with side and name

        :param side: str
        :param base_name: str
        """

        rig.Bone.__init__(self, side, base_name)
        self.meta_type = 'Spine'

        self.start_pos = start_pos
        self.interval = length / (segment-1)
        self.segment = segment
        self.scale = 0.4

        self.initial_setup()

    def assign_secondary_naming(self):
        self.loc_list, self.jnt_list, self.cluster_list, self.ctrl_list, self.ctrlOffset_list = ([] for i in range(5))
        for i in range(self.segment):
            self.loc_list.append('{}{}_loc'.format(self.name, i))
            self.jnt_list.append('{}{}_jnt'.format(self.name, i))

        for name in ['root', 'mid', 'top']:
            self.ctrl_list.append('{}{}_ctrl'.format(self.name, name))
            self.ctrlOffset_list.append('{}{}_offset'.format(self.name, name))
            self.cluster_list.append('{}{}_cluster'.format(self.name, name))

        # ik has different ctrl name
        self.master_ctrl = '{}master_ctrl'.format(self.name, name)
        self.master_offset = '{}master_offset'.format(self.name, name)
        self.ik_curve = '{}ik_curve'.format(self.name)
        self.ik_name = '{}_ik'.format(self.name)

    @staticmethod
    def set_controller_shape():
        sphere = cmds.createNode('implicitSphere')
        sphere_ctrl = cmds.rename(cmds.listRelatives(sphere, p=1), 'Master_tempShape')
        cmds.scale(0.3, 0.3, 0.3, sphere_ctrl)

        ctrl_shape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=8, name='Spine_tempShape')
        cmds.scale(1, 1, 1, ctrl_shape)

    def create_locator(self):
        grp = cmds.group(em=1, n=self.loc_grp_name)

        for i in range(self.segment):
            spine = cmds.spaceLocator(n=self.loc_list[i])
            if i is 0:
                cmds.parent(spine, grp, relative=1)
                cmds.move(self.start_pos[0], self.start_pos[1], self.start_pos[2], spine, absolute=1)
                cmds.scale(self.scale, self.scale, self.scale, spine)
            else:
                cmds.parent(spine, self.loc_list[i-1], relative=1)
                # move spine locator along +z axis
                cmds.move(0, 0, self.interval, spine, relative=1)

        cmds.parent(grp, self.loc_global_grp)
        return grp

    def create_joint(self):
        cmds.select(clear=1)

        for i, loc in enumerate(self.loc_list):
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnt_list[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        cmds.parent(self.jnt_list[0], self.jnt_global_grp)
        joint.orient_joint(self.jnt_list[0])
        return self.jnt_list[0]

    def place_controller(self):
        root_pos = cmds.xform(self.jnt_list[0], q=1, t=1, ws=1)
        root_rot = cmds.xform(self.jnt_list[0], q=1, ro=1, ws=1)
        top_pos = cmds.xform(self.jnt_list[-1], q=1, t=1, ws=1)
        top_rot = cmds.xform(self.jnt_list[-1], q=1, ro=1, ws=1)

        # master ctrl is positioned on top of root ctrl
        cmds.duplicate('Master_tempShape', name=self.master_ctrl)
        cmds.group(em=1, name=self.master_offset)
        cmds.move(root_pos[0], root_pos[1]+2, root_pos[2], self.master_offset)
        cmds.parent(self.master_ctrl, self.master_offset, relative=1)

        # root ctrl is positioned at the root joint
        # root ctrl needs to be accessed outside for parenting
        cmds.duplicate('Spine_tempShape', name=self.ctrl_list[0])
        cmds.group(em=1, name=self.ctrlOffset_list[0])
        cmds.move(root_pos[0], root_pos[1], root_pos[2], self.ctrlOffset_list[0])
        cmds.rotate(root_rot[0], root_rot[1], root_rot[2], self.ctrlOffset_list[0])
        cmds.parent(self.ctrl_list[0], self.ctrlOffset_list[0], relative=1)

        # top ctrl is positioned at the top joint
        # top ctrl needs to be accessed outside for parenting
        cmds.duplicate('Spine_tempShape', name=self.ctrl_list[-1])
        cmds.group(em=1, name=self.ctrlOffset_list[-1])
        cmds.move(top_pos[0], top_pos[1], top_pos[2], self.ctrlOffset_list[-1])
        cmds.rotate(top_rot[0], top_rot[1], top_rot[2], self.ctrlOffset_list[-1])
        cmds.parent(self.ctrl_list[-1], self.ctrlOffset_list[-1], relative=1)

        # mid ctrl is positioned at the middle joint / or middle two joint
        if self.segment % 2 != 0:
            index = int((self.segment-1)/2)
            mid_pos = cmds.xform(self.jnt_list[index], q=1, t=1, ws=1)
            mid_rot = cmds.xform(self.jnt_list[index], q=1, ro=1, ws=1)
        else:
            mid_upper_pos = cmds.xform(self.jnt_list[(self.segment+1) / 2], q=1, t=1, ws=1)
            mid_upper_rot = cmds.xform(self.jnt_list[(self.segment+1) / 2], q=1, ro=1, ws=1)
            mid_lower_pos = cmds.xform(self.jnt_list[(self.segment-1) / 2], q=1, t=1, ws=1)
            mid_lower_rot = cmds.xform(self.jnt_list[(self.segment-1) / 2], q=1, ro=1, ws=1)
            mid_pos = [(mid_upper_pos[0]+mid_lower_pos[0]) / 2, (mid_upper_pos[1]+mid_lower_pos[1]) / 2, (mid_upper_pos[2]+mid_lower_pos[2]) / 2]
            mid_rot = [(mid_upper_rot[0]+mid_lower_rot[0]) / 2, (mid_upper_rot[1]+mid_lower_rot[1]) / 2, (mid_upper_rot[2]+mid_lower_rot[2]) / 2]

        cmds.duplicate('Spine_tempShape', name=self.ctrl_list[1])
        cmds.group(em=1, name=self.ctrlOffset_list[1])
        cmds.move(mid_pos[0], mid_pos[1], mid_pos[2], self.ctrlOffset_list[1])
        cmds.rotate(mid_rot[0], mid_rot[1], mid_rot[2], self.ctrlOffset_list[1])
        cmds.parent(self.ctrl_list[1], self.ctrlOffset_list[1], relative=1)

        # Cleanup
        outliner.batch_parent([self.ctrlOffset_list[0], self.ctrlOffset_list[1], self.ctrlOffset_list[-1]], self.master_ctrl)
        cmds.parent(self.master_offset, self.ctrl_global_grp)
        return self.master_ctrl

    def build_ik(self):
        # use ik auto create curve with 2 span (5 cvs), exclude the root joint
        cmds.ikHandle(startJoint=self.jnt_list[1], endEffector=self.jnt_list[-1], name=self.ik_name, createCurve=1,
                      parentCurve=False, roc=1, solver='ikSplineSolver', simplifyCurve=1, numSpans=2)
        cmds.rename('curve1', self.ik_curve)

        cmds.cluster(self.ik_curve+'.cv[0:1]', name=self.cluster_list[0])
        cmds.cluster(self.ik_curve+'.cv[2]', name=self.cluster_list[1])
        cmds.cluster(self.ik_curve+'.cv[3:4]', name=self.cluster_list[-1])

        cmds.setAttr(self.ik_name+'.visibility', 0)  # hide ik
        cmds.parent(self.ik_name, self.ctrl_global_grp)

    def add_constraint(self):
        # each ik control is the parent of spine clusters
        self.build_ik()
        for i, cluster in enumerate(self.cluster_list):
            spine_cluster = cmds.ls('{}Handle'.format(cluster))
            spine_ctrl = cmds.ls(self.ctrl_list[i])
            cmds.parent(spine_cluster, spine_ctrl)

        # middle control is driven by the top and root control
        cmds.pointConstraint(self.ctrl_list[-1], self.ctrl_list[0], self.ctrl_list[1])
        cmds.parentConstraint(self.ctrl_list[0], self.jnt_list[0])

        # scaling of the spine
        arc_len = cmds.arclen(self.ik_curve, constructionHistory=1)
        cmds.rename(arc_len, self.ik_curve+'Info')
        cmds.parent(self.ik_curve, self.ctrl_global_grp)
        cmds.setAttr(self.ik_curve+'.visibility', 0)

        # create curve length node and multiply node
        init_len = cmds.getAttr(self.ik_curve+'Info.arcLength')
        stretch_node = cmds.shadingNode('multiplyDivide', asUtility=1, name=self.ctrl_name+'Stretch')
        cmds.setAttr(stretch_node+'.operation', 2)
        cmds.setAttr(stretch_node+'.input2X', init_len)
        cmds.connectAttr(self.ik_curve+'Info.arcLength', stretch_node+'.input1X')
        for i in range(self.segment):
            cmds.connectAttr(stretch_node+'.outputX', self.jnt_list[i]+'.scaleX')

        # enable advance twist control
        cmds.setAttr(self.ik_name+'.dTwistControlEnable', 1)
        cmds.setAttr(self.ik_name+'.dWorldUpType', 4)
        cmds.connectAttr(self.ctrl_list[0]+'.worldMatrix[0]', self.ik_name+'.dWorldUpMatrix', f=1)
        cmds.connectAttr(self.ctrl_list[-1]+'.worldMatrix[0]', self.ik_name+'.dWorldUpMatrixEnd', f=1)

    def lock_controller(self):
        for ctrl in self.ctrl_list+[self.master_ctrl]:
            for transform in 's':
                for axis in 'xyz':
                    cmds.setAttr(ctrl+'.'+transform+axis, l=1, k=0)
