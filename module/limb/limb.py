import maya.cmds as cmds

from autoRigger.module.base import bone
from autoRigger.module.chain import chain, chainIK, chainFK, chainFKIK
from autoRigger import util
from utility.setup import outliner
from utility.rigging import joint, nurbs
from utility.datatype import vector


class Limb_(chainFKIK.ChainFKIK):

    def __init__(self, side, name, segment=3, length=6, ltype='null'):
        chain.Chain.__init__(self, side, name, segment)

        self.master_ctrl = None

        self.ltype = ltype
        direction = [0, -1, 0]
        if ltype == 'arm' and side == 'l':
            direction = [1, 0, 0]
        elif ltype == 'arm' and side == 'r':
            direction = [-1, 0, 0]

        self.ik_chain = chainIK.ChainIK(side, name, segment, length, direction)
        self.fk_chain = chainFK.ChainFK(side, name, segment, length, direction)

        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(direction).normalize()


class Limb(bone.Bone):
    """ This module create a Limb rig which is used in arm or leg """

    def __init__(self, side, name, interval=2, ltype='null'):
        """ Initialize Limb class with side, name and type of the limb
        
        :param side: str
        :param name: str
        :param ltype: str, 'arm', 'leg' or 'null'
        """
        bone.Bone.__init__(self, side, name)

        self._rtype = 'limb'

        self.interval = interval
        self.scale = 0.4

        self.limb_components = ['root', 'middle', 'top']
        self.direction = 'vertical'
        if ltype == 'arm':
            self.limb_components = ['shoulder', 'elbow', 'wrist']
            self.direction = 'horizontal'
        elif ltype == 'leg':
            self.limb_components = ['clavicle', 'knee', 'ankle']

        self.ik_jnts = list()
        self.fk_jnts = list()
        self.fk_ctrls = list()
        self.fk_offsets = list()

    def create_namespace(self):
        self.base_name = '{}_{}_{}'.format(self._rtype, self._side, self._name)

        # initialize multiple names
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

    def set_controller_shape(self):
        self._shape = list(range(4))

        self._shape[0] = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name=self.namer.tmp)[0]
        self._shape[1] = cmds.circle(nr=(1, 0, 0), c=(0, 0, 0), radius=1, s=6, name=self.namer.tmp)[0]
        self._shape[2] = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name=self.namer.tmp)[0]
        cmds.rotate(0, 90, 0, self._shape[2])

        arrow_pts = [
            [2.0, 0.0, 2.0], [2.0, 0.0, 1.0], [3.0, 0.0, 1.0], [3.0, 0.0, 2.0], [5.0, 0.0, 0.0], [3.0, 0.0, -2.0], [3.0, 0.0, -1.0], [2.0, 0.0, -1.0],
            [2.0, 0.0, -2.0], [1.0, 0.0, -2.0], [1.0, 0.0, -3.0], [2.0, 0.0, -3.0], [0.0, 0.0, -5.0], [-2.0, 0.0, -3.0], [-1.0, 0.0, -3.0], [-1.0, 0.0, -2.0],
            [-2.0, 0.0, -2.0], [-2.0, 0.0, -1.0], [-3.0, 0.0, -1.0], [-3.0, 0.0, -2.0], [-5.0, 0.0, 0.0], [-3.0, 0.0, 2.0], [-3.0, 0.0, 1.0], [-2.0, 0.0, 1.0],
            [-2.0, 0.0, 2.0], [-1.0, 0.0, 2.0], [-1.0, 0.0, 3.0], [-2.0, 0.0, 3.0], [0.0, 0.0, 5.0], [2.0, 0.0, 3.0], [1.0, 0.0, 3.0], [1.0, 0.0, 2.0], [2.0, 0.0, 2.0]
        ]
        self._shape[3] = cmds.curve(p=arrow_pts, degree=1, name=self.namer.tmp)
        cmds.scale(0.3, 0.3, 0.3, self._shape[3])

    def create_locator(self):
        side_factor, horizontal_factor, vertical_factor = 1, 1, 0
        if self._side == 'r':
            side_factor = -1

        if self.direction == 'vertical':
            horizontal_factor, vertical_factor = 0, 1

        # Root
        cmds.spaceLocator(n=self.locs[0])
        cmds.scale(self.scale, self.scale, self.scale, self.locs[0])

        # Middle
        cmds.spaceLocator(n=self.locs[1])
        cmds.parent(self.locs[1], self.locs[0], relative=1)
        util.move(self.locs[1], [self.interval*side_factor*horizontal_factor, -self.interval*vertical_factor, 0])

        # Top
        cmds.spaceLocator(n=self.locs[2])
        cmds.parent(self.locs[2], self.locs[1], relative=1)
        util.move(self.locs[2], [self.interval*side_factor*horizontal_factor, -self.interval*vertical_factor, 0])

        cmds.parent(self.locs[0], util.G_LOC_GRP)
        return self.locs[0]

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
        outliner.batch_parent([self.jnts[0], self.ik_jnts[0], self.fk_jnts[0]], util.G_JNT_GRP)
        joint.orient_joint([self.jnts[0], self.ik_jnts[0], self.fk_jnts[0]])
        return cmds.ls(self.jnts[0])

    def place_controller(self):
        # FK Setup
        for i in range(len(self.fk_ctrls)):
            cmds.duplicate(self._shape[0], name=self.fk_ctrls[i])
            cmds.group(em=1, name=self.fk_offsets[i])
            nurbs.clear_nurbs_transform(self.fk_ctrls[i], self.fk_offsets[i], self.jnts[i])

        cmds.parent(self.fk_offsets[2], self.fk_ctrls[1])
        cmds.parent(self.fk_offsets[1], self.fk_ctrls[0])

        # IK Setup
        cmds.duplicate(self._shape[1], name=self.ik_ctrl)
        cmds.group(em=1, name=self.ik_offset)
        nurbs.clear_nurbs_transform(self.ik_ctrl, self.ik_offset, self.jnts[2])

        cmds.duplicate(self._shape[2], name=self.ik_pole)
        cmds.group(em=1, name=self.ik_pole_offset)
        if self.direction == 'vertical':
            util.move(self.ik_pole, [0, 3, 0])
        elif self.direction == 'horizontal':
            util.move(self.ik_pole, [0, -3, 0])
        nurbs.clear_nurbs_transform(self.ik_pole, self.ik_pole_offset, self.jnts[1])

        # IK/FK Switch Setup
        cmds.duplicate(self._shape[3], name=self.switch_ctrl)
        cmds.group(em=1, name=self.switch_offset)
        cmds.addAttr(
            self.switch_ctrl,
            longName='FK_IK',
            attributeType='double',
            defaultValue=1, minValue=0, maxValue=1, keyable=1
        )
        cmds.rotate(0, 0, 90, self.switch_ctrl, relative=1)
        nurbs.clear_nurbs_transform(self.switch_ctrl, self.switch_offset, self.jnts[0])

        # Cleanup
        cmds.parent(self.switch_offset, util.G_CTRL_GRP)

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
        if self.direction == 'vertical':
            joint.set_prefer_angle(self.ik_jnts[1], [0, 0, -1])
        else:
            joint.set_prefer_angle(self.ik_jnts[1], [0, 0, 1])

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
