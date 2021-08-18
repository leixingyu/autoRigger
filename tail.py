import maya.cmds as cmds
from . import rig
from utility import joint, outliner


class Tail(rig.Bone):
    """ This module creates a quadruped tail rig"""

    def __init__(self, side, name, rig_type='Tail', pos=[0, 6, -4], length=4.0, segment=6):
        """ Initialize Tail class with side and name

        :param side: str
        :param name: str
        """

        self.segment = segment
        self.pos = pos
        self.interval = length / (self.segment-1)
        self.scale = 0.4

        self.locs, self.jnts, self.ik_jnts, self.fk_jnts, self.fk_ctrls, self.ik_ctrls, self.fk_offsets,  self.clusters, self.ik_offsets = ([] for _ in range(9))

        rig.Bone.__init__(self, side, name, rig_type)

    def assign_secondary_naming(self):
        for i in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base_name, i))
            self.jnts.append('{}{}_jnt'.format(self.base_name, i))
            self.fk_jnts.append('{}{}fk_jnt'.format(self.base_name, i))
            self.ik_jnts.append('{}{}ik_jnt'.format(self.base_name, i))
            self.fk_ctrls.append('{}{}fk_ctrl'.format(self.base_name, i))
            self.ik_ctrls.append('{}{}ik_ctrl'.format(self.base_name, i))
            self.fk_offsets.append('{}{}fk_offset'.format(self.base_name, i))
            self.ik_offsets.append('{}{}ik_offset'.format(self.base_name, i))
            self.clusters.append('{}{}_cluster'.format(self.base_name, i))

        # ik has different ctrl name
        self.master_ctrl = '{}master_ctrl'.format(self.base_name)
        self.ik_curve = '{}ik_curve'.format(self.base_name)
        self.tail_ik = '{}_ik'.format(self.base_name)

    @staticmethod
    def set_controller_shape():
        sphere = cmds.createNode('implicitSphere')
        sphere_ctrl = cmds.rename(cmds.listRelatives(sphere, p=1), 'TailIK_tempShape')
        cmds.scale(0.2, 0.2, 0.2, sphere_ctrl)

        ctrl_shape = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=8, name='TailFK_tempShape')
        cmds.scale(0.3, 0.3, 0.3, ctrl_shape)

    def create_locator(self):
        grp = cmds.group(em=1, n=self.loc_grp)

        for i in range(self.segment):
            tail = cmds.spaceLocator(n=self.locs[i])
            # root locator of tail parent to the tail group
            if i is 0:
                cmds.parent(tail, grp, relative=1)
                cmds.move(self.pos[0], self.pos[1], self.pos[2], tail, absolute=1)
                cmds.scale(self.scale, self.scale, self.scale, tail)
            # tail locator parent to the previous locator
            else:
                cmds.parent(tail, self.locs[i-1], relative=1)
                # move tail locator along -y axis
                cmds.move(0, -self.interval, 0, tail, relative=1)

        cmds.parent(grp, self.loc_global_grp)
        return grp

    def create_joint(self):
        # Result jnt
        cmds.select(clear=1)
        for i, loc in enumerate(self.locs):
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnts[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        # IK jnt
        cmds.select(clear=1)
        for i, loc in enumerate(self.locs):
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.ik_jnts[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        # FK jnt
        cmds.select(clear=1)
        for i, loc in enumerate(self.locs):
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.fk_jnts[i])
            cmds.setAttr(jnt+'.radius', self.scale)

        # Cleanup
        cmds.setAttr(self.fk_jnts[0]+'.visibility', 0)
        cmds.setAttr(self.ik_jnts[0]+'.visibility', 0)
        outliner.batch_parent([self.jnts[0], self.fk_jnts[0], self.ik_jnts[0]], self.jnt_global_grp)
        joint.orient_joint([self.jnts[0], self.fk_jnts[0], self.ik_jnts[0]])
        return self.jnts[0]

    def place_controller(self):

        # Master control
        cmds.duplicate('TailIK_tempShape', name=self.master_ctrl)
        tail_pos = cmds.xform(self.jnts[0], q=1, t=1, ws=1)
        cmds.move(tail_pos[0], tail_pos[1], tail_pos[2]-1, self.master_ctrl)
        cmds.addAttr(self.master_ctrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=1)

        # IK and FK control has the same setup
        for i in range(self.segment):
            cmds.duplicate('TailIK_tempShape', name=self.ik_ctrls[i])
            cmds.group(em=1, name=self.ik_offsets[i])
            cmds.duplicate('TailFK_tempShape', name=self.fk_ctrls[i])
            cmds.group(em=1, name=self.fk_offsets[i])

        for i, tail in enumerate(self.jnts):
            tail_pos = cmds.xform(tail, q=1, t=1, ws=1)
            tail_rot = cmds.xform(tail, q=1, ro=1, ws=1)
            cmds.move(tail_pos[0], tail_pos[1], tail_pos[2], self.ik_offsets[i])
            cmds.rotate(tail_rot[0], tail_rot[1], tail_rot[2], self.ik_offsets[i])
            cmds.move(tail_pos[0], tail_pos[1], tail_pos[2], self.fk_offsets[i])
            cmds.rotate(tail_rot[0], tail_rot[1], tail_rot[2], self.fk_offsets[i])
        for i in range(self.segment):
            cmds.parent(self.ik_ctrls[i], self.ik_offsets[i], relative=1)
            cmds.parent(self.fk_ctrls[i], self.fk_offsets[i], relative=1)
            if i != 0:
                cmds.parent(self.ik_offsets[i], self.ik_ctrls[i-1])
                cmds.parent(self.fk_offsets[i], self.fk_ctrls[i-1])
            else:
                outliner.batch_parent([self.ik_offsets[i], self.fk_offsets[i]], self.master_ctrl)

        # Cleanup
        cmds.parent(self.master_ctrl, self.ctrl_global_grp)
        return self.master_ctrl

    def build_ik(self):
        curve_points = []
        for i, tail in enumerate(self.ik_jnts):
            tail_pos = cmds.xform(tail, q=1, t=1, ws=1)
            curve_points.append(tail_pos)

        tail_curve = cmds.curve(p=curve_points, name=self.ik_curve)
        cmds.setAttr(tail_curve+'.visibility', 0)
        # turning off inherit transform avoid curve move/scale twice as much
        cmds.inheritTransform(tail_curve, off=1)

        cvs = cmds.ls(self.ik_curve+'.cv[0:]', fl=1)
        for i, cv in enumerate(cvs):
            cluster = cmds.cluster(cv, name=self.clusters[i])[-1]
            cmds.setAttr(cluster+'.visibility', 0)

        cmds.ikHandle(startJoint=self.ik_jnts[0], endEffector=self.ik_jnts[self.segment-1], name=self.tail_ik, curve=tail_curve, createCurve=False,
                      parentCurve=1, roc=1, solver='ikSplineSolver')
        cmds.setAttr(self.tail_ik+'.visibility', 0)
        cmds.parent(self.tail_ik, self.ctrl_global_grp)

    def build_fk(self):
        pass

    def add_constraint(self):
        self.build_ik()
        for i in range(self.segment):
            tail_cluster = cmds.ls('{}Handle'.format(self.clusters[i]))
            tail_ctrl = cmds.ls(self.ik_ctrls[i])
            cmds.parent(tail_cluster, tail_ctrl)

        self.build_fk()
        for i, tail_jnt in enumerate(self.fk_jnts):
            tail_ctrl = cmds.ls(self.fk_ctrls[i])
            cmds.parentConstraint(tail_ctrl, tail_jnt)

        # IK, FK to result jnt
        for i in range(self.segment):
            ik_tail = cmds.ls(self.ik_jnts[i])
            fk_tail = cmds.ls(self.fk_jnts[i])
            final_tail = cmds.ls(self.jnts[i])
            cmds.parentConstraint(ik_tail, fk_tail, final_tail)

        # IK FK switch
        for i in range(self.segment):
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jnts[i], self.ik_jnts[i]), currentDriver=self.master_ctrl+'.FK_IK', driverValue=1, value=1)
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jnts[i], self.fk_jnts[i]), currentDriver=self.master_ctrl+'.FK_IK', driverValue=1, value=0)
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W0'.format(self.jnts[i], self.ik_jnts[i]), currentDriver=self.master_ctrl+'.FK_IK', driverValue=0, value=0)
            cmds.setDrivenKeyframe('{}_parentConstraint1.{}W1'.format(self.jnts[i], self.fk_jnts[i]), currentDriver=self.master_ctrl+'.FK_IK', driverValue=0, value=1)
    
            cmds.setDrivenKeyframe(self.ik_ctrls[i]+'.visibility', currentDriver=self.master_ctrl+'.FK_IK', driverValue=1, value=1)
            cmds.setDrivenKeyframe(self.ik_ctrls[i]+'.visibility', currentDriver=self.master_ctrl+'.FK_IK', driverValue=0, value=0)
            cmds.setDrivenKeyframe(self.fk_ctrls[i]+'.visibility', currentDriver=self.master_ctrl+'.FK_IK', driverValue=0, value=1)
            cmds.setDrivenKeyframe(self.fk_ctrls[i]+'.visibility', currentDriver=self.master_ctrl+'.FK_IK', driverValue=1, value=0)

    def lock_controller(self):
        for ctrl in self.fk_ctrls+self.ik_ctrls+[self.master_ctrl]:
            for transform in 's':
                for axis in 'xyz':
                    cmds.setAttr('{}.{}{}'.format(ctrl, transform, axis), l=1, k=0)
