import maya.cmds as cmds
from . import base
from utility import joint, outliner


class Tail(base.Base):
    """ This module creates a quadruped tail rig"""

    def __init__(self, side, base_name):
        """ Initialize Tail class with side and name

        :param side: str
        :param base_name: str
        """

        self.segment = 6
        base.Base.__init__(self, side, base_name)
        self.metaType = 'Tail'
        self.assign_naming()
        self.assign_secondary_naming()

    def assign_secondary_naming(self):
        self.loc_list, self.jnt_list, self.ik_jnt_list, self.fk_jnt_list,\
        self.fk_ctrl_list, self.ik_ctrl_list, self.fk_offset_list,\
        self.cluster_list, self.ik_offset_list = ([] for i in range(9))

        for i in range(self.segment):
            self.loc_list.append('{}{}_loc'.format(self.name, i))
            self.jnt_list.append('{}{}_jnt'.format(self.name, i))
            self.fk_jnt_list.append('{}{}fk_jnt'.format(self.name, i))
            self.ik_jnt_list.append('{}{}ik_jnt'.format(self.name, i))
            self.fk_ctrl_list.append('{}{}fk_ctrl'.format(self.name, i))
            self.ik_ctrl_list.append('{}{}ik_ctrl'.format(self.name, i))
            self.fk_offset_list.append('{}{}fk_offset'.format(self.name, i))
            self.ik_offset_list.append('{}{}ik_offset'.format(self.name, i))
            self.cluster_list.append('{}{}_cluster'.format(self.name, i))
        # ik has different ctrl name
        self.master_ctrl = '{}master_ctrl'.format(self.name)
        self.ik_curve = '{}ik_curve'.format(self.name)
        self.tail_ik = '{}_ik'.format(self.name)

    @staticmethod
    def set_controller_shape():
        sphere = cmds.createNode('implicitSphere')
        sphere_ctrl = cmds.rename(cmds.listRelatives(sphere, p=1), 'TailIK_tempShape')
        cmds.scale(0.2, 0.2, 0.2, sphere_ctrl)

        ctrl_shape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=8, name='TailFK_tempShape')
        cmds.scale(0.3, 0.3, 0.3, ctrl_shape)

    def set_locator_attr(self, start_pos=[0, 6, -4], length=4.0, scale=0.4):
        self.start_pos = start_pos
        self.interval = length / (self.segment-1)
        self.scale = scale

    def build_guide(self):
        grp = cmds.group(em=1, n=self.loc_grp_name)

        for i in range(self.segment):
            tail = cmds.spaceLocator(n=self.loc_list[i])
            # root locator of tail parent to the tail group
            if i is 0:
                cmds.parent(tail, grp, relative=1)
                cmds.move(self.start_pos[0], self.start_pos[1], self.start_pos[2], tail, absolute=1)
                cmds.scale(self.scale, self.scale, self.scale, tail)
            # tail locator parent to the previous locator
            else:
                cmds.parent(tail, self.loc_list[i-1], relative=1)
                # move tail locator along -y axis
                cmds.move(0, -self.interval, 0, tail, relative=1)

        self.color_locator()
        cmds.parent(grp, self.loc_grp)
        return grp

    def construct_joint(self):
        # Result jnt
        cmds.select(clear=1)
        for i, loc in enumerate(self.loc_list):
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnt_list[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        # IK jnt
        cmds.select(clear=1)
        for i, loc in enumerate(self.loc_list):
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.ik_jnt_list[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        # FK jnt
        cmds.select(clear=1)
        for i, loc in enumerate(self.loc_list):
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.fk_jnt_list[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        # Cleanup
        cmds.setAttr(self.fk_jnt_list[0]+'.visibility', 0)
        cmds.setAttr(self.ik_jnt_list[0]+'.visibility', 0)
        outliner.batch_parent([self.jnt_list[0], self.fk_jnt_list[0], self.ik_jnt_list[0]], self.jnt_grp)
        joint.orient_joint([self.jnt_list[0], self.fk_jnt_list[0], self.ik_jnt_list[0]])
        return self.jnt_list[0]

    def place_controller(self):
        self.set_controller_shape()

        # Master control
        cmds.duplicate('TailIK_tempShape', name=self.master_ctrl)
        tail_pos = cmds.xform(self.jnt_list[0], q=1, t=1, ws=1)
        cmds.move(tail_pos[0], tail_pos[1], tail_pos[2]-1, self.master_ctrl)
        cmds.addAttr(self.master_ctrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=1)

        # IK and FK control has the same setup
        for i in range(self.segment):
            cmds.duplicate('TailIK_tempShape', name=self.ik_ctrl_list[i])
            cmds.group(em=1, name=self.ik_offset_list[i])
            cmds.duplicate('TailFK_tempShape', name=self.fk_ctrl_list[i])
            cmds.group(em=1, name=self.fk_offset_list[i])

        for i, tail in enumerate(self.jnt_list):
            tail_pos = cmds.xform(tail, q=1, t=1, ws=1)
            tail_rot = cmds.xform(tail, q=1, ro=1, ws=1)
            cmds.move(tail_pos[0], tail_pos[1], tail_pos[2], self.ik_offset_list[i])
            cmds.rotate(tail_rot[0], tail_rot[1], tail_rot[2], self.ik_offset_list[i])
            cmds.move(tail_pos[0], tail_pos[1], tail_pos[2], self.fk_offset_list[i])
            cmds.rotate(tail_rot[0], tail_rot[1], tail_rot[2], self.fk_offset_list[i])
        for i in range(self.segment):
            cmds.parent(self.ik_ctrl_list[i], self.ik_offset_list[i], relative=1)
            cmds.parent(self.fk_ctrl_list[i], self.fk_offset_list[i], relative=1)
            if i != 0:
                cmds.parent(self.ik_offset_list[i], self.ik_ctrl_list[i-1])
                cmds.parent(self.fk_offset_list[i], self.fk_ctrl_list[i-1])
            else:
                outliner.batch_parent([self.ik_offset_list[i], self.fk_offset_list[i]], self.master_ctrl)

        # Cleanup
        cmds.parent(self.master_ctrl, self.ctrl_grp)
        self.delete_shape()
        return self.master_ctrl

    def build_ik(self):
        curve_points = []
        for i, tail in enumerate(self.ik_jnt_list):
            tail_pos = cmds.xform(tail, q=1, t=1, ws=1)
            curve_points.append(tail_pos)

        tail_curve = cmds.curve(p=curve_points, name=self.ik_curve)
        cmds.setAttr(tail_curve+'.visibility', 0)
        # turning off inherit transform avoid curve move/scale twice as much
        cmds.inheritTransform(tail_curve, off=1)

        cvs = cmds.ls(self.ik_curve+'.cv[0:]', fl=1)
        for i, cv in enumerate(cvs):
            cluster = cmds.cluster(cv, name=self.cluster_list[i])[-1]
            cmds.setAttr(cluster+'.visibility', 0)

        cmds.ikHandle(startJoint=self.ik_jnt_list[0], endEffector=self.ik_jnt_list[self.segment-1], name=self.tail_ik, curve=tail_curve, createCurve=False,
                      parentCurve=1, roc=1, solver='ikSplineSolver')
        cmds.setAttr(self.tail_ik+'.visibility', 0)
        cmds.parent(self.tail_ik, self.ctrl_grp)

    def build_fk(self):
        pass

    def add_constraint(self):
        self.build_ik()
        for i in range(self.segment):
            tail_cluster = cmds.ls('{}Handle'.format(self.cluster_list[i]))
            tail_ctrl = cmds.ls(self.ik_ctrl_list[i])
            cmds.parent(tail_cluster, tail_ctrl)

        self.build_fk()
        for i, tail_jnt in enumerate(self.fk_jnt_list):
            tail_ctrl = cmds.ls(self.fk_ctrl_list[i])
            cmds.parentConstraint(tail_ctrl, tail_jnt)

        # IK, FK to result jnt
        for i in range(self.segment):
            ik_tail = cmds.ls(self.ik_jnt_list[i])
            fk_tail = cmds.ls(self.fk_jnt_list[i])
            final_tail = cmds.ls(self.jnt_list[i])
            cmds.parentConstraint(ik_tail, fk_tail, final_tail)

        # IK FK switch
        for i in range(self.segment):
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jnt_list[i], self.ik_jnt_list[i]), currentDriver=self.master_ctrl+'.FK_IK', driverValue=1, value=1)
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jnt_list[i], self.fk_jnt_list[i]), currentDriver=self.master_ctrl+'.FK_IK', driverValue=1, value=0)
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jnt_list[i], self.ik_jnt_list[i]), currentDriver=self.master_ctrl+'.FK_IK', driverValue=0, value=0)
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jnt_list[i], self.fk_jnt_list[i]), currentDriver=self.master_ctrl+'.FK_IK', driverValue=0, value=1)
    
            cmds.setDrivenKeyframe(self.ik_ctrl_list[i]+'.visibility', currentDriver=self.master_ctrl+'.FK_IK', driverValue=1, value=1)
            cmds.setDrivenKeyframe(self.ik_ctrl_list[i]+'.visibility', currentDriver=self.master_ctrl+'.FK_IK', driverValue=0, value=0)
            cmds.setDrivenKeyframe(self.fk_ctrl_list[i]+'.visibility', currentDriver=self.master_ctrl+'.FK_IK', driverValue=0, value=1)
            cmds.setDrivenKeyframe(self.fk_ctrl_list[i]+'.visibility', currentDriver=self.master_ctrl+'.FK_IK', driverValue=1, value=0)

    def lock_controller(self):
        for ctrl in self.fk_ctrl_list+self.ik_ctrl_list+[self.master_ctrl]:
            for transform in 's':
                for axis in 'xyz':
                    cmds.setAttr('{}.{}{}'.format(ctrl, transform, axis), l=1, k=0)


