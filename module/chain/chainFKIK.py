import maya.cmds as cmds

from autoRigger import util
from . import chain, chainFK, chainIK

from utility.datatype import vector
from utility.rigging import joint


class ChainFKIK(chain.Chain):

    def __init__(self, side, name, segment, length, direction):

        chain.Chain.__init__(self, side, name, segment)
        self.master_ctrl = None
        self.master_offset = None

        self.ik_chain = chainIK.ChainIK(side, name, segment, length, direction)
        self.fk_chain = chainFK.ChainFK(side, name, segment, length, direction)

        # master controller location
        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(direction).normalize()

    def create_namespace(self):
        self.ik_chain.create_namespace()
        self.fk_chain.create_namespace()

        self.base_name = '{}_{}_{}'.format(self._rtype, self._side, self._name)
        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base_name, index))
            self.jnts.append('{}{}_jnt'.format(self.base_name, index))

        self.master_offset = '{}master_offset'.format(self.base_name)
        self.master_ctrl = '{}master_ctrl'.format(self.base_name)

    def set_controller_shape(self):
        self.ik_chain.set_controller_shape()
        self.fk_chain.set_controller_shape()

        # master control
        arrow_pts = [
            [2.0, 0.0, 2.0], [2.0, 0.0, 1.0], [3.0, 0.0, 1.0], [3.0, 0.0, 2.0],
            [5.0, 0.0, 0.0], [3.0, 0.0, -2.0], [3.0, 0.0, -1.0],
            [2.0, 0.0, -1.0],
            [2.0, 0.0, -2.0], [1.0, 0.0, -2.0], [1.0, 0.0, -3.0],
            [2.0, 0.0, -3.0], [0.0, 0.0, -5.0], [-2.0, 0.0, -3.0],
            [-1.0, 0.0, -3.0], [-1.0, 0.0, -2.0],
            [-2.0, 0.0, -2.0], [-2.0, 0.0, -1.0], [-3.0, 0.0, -1.0],
            [-3.0, 0.0, -2.0], [-5.0, 0.0, 0.0], [-3.0, 0.0, 2.0],
            [-3.0, 0.0, 1.0], [-2.0, 0.0, 1.0],
            [-2.0, 0.0, 2.0], [-1.0, 0.0, 2.0], [-1.0, 0.0, 3.0],
            [-2.0, 0.0, 3.0], [0.0, 0.0, 5.0], [2.0, 0.0, 3.0],
            [1.0, 0.0, 3.0], [1.0, 0.0, 2.0], [2.0, 0.0, 2.0]
        ]
        self._shape = cmds.curve(p=arrow_pts, degree=1, name=self.namer.tmp)

    def create_joint(self):
        self.ik_chain.create_joint()
        self.fk_chain.create_joint()

        # Result jnt
        cmds.select(clear=1)
        for index, loc in enumerate(self.locs):
            pos = cmds.xform(loc, q=1, t=1, ws=1)
            cmds.joint(p=pos, name=self.jnts[index])

        # Cleanup
        cmds.setAttr(self.ik_chain.jnts[0]+'.visibility', 0)
        cmds.setAttr(self.fk_chain.jnts[0]+'.visibility', 0)

        cmds.parent(self.jnts[0], util.G_JNT_GRP)
        joint.orient_joint(self.jnts[0])

        return self.jnts[0]

    def place_controller(self):
        self.ik_chain.place_controller()
        self.fk_chain.place_controller()

        # Master control
        cmds.duplicate(self._shape, name=self.master_ctrl)
        cmds.group(name=self.master_offset, em=1)

        pos = cmds.xform(self.jnts[0], q=1, t=1, ws=1)
        distance = (vector.Vector(pos)-self.interval * self.dir).as_list
        util.move(self.master_offset, distance)
        cmds.parent(self.master_ctrl, self.master_offset, relative=1)
        cmds.makeIdentity(self.master_ctrl, apply=1, t=1, r=1, s=1)

        cmds.addAttr(self.master_ctrl, longName='FK_IK',
                     attributeType='double', defaultValue=1, minValue=0,
                     maxValue=1, keyable=1)

        cmds.parent(self.ik_chain.offsets[0], self.master_ctrl)
        cmds.parent(self.ik_chain.offsets[-1], self.master_ctrl)
        cmds.parent(self.fk_chain.offsets[0], self.master_ctrl)

        # Cleanup
        cmds.parent(self.master_offset, util.G_CTRL_GRP)
        return self.master_ctrl

    def add_constraint(self):
        self.ik_chain.add_constraint()
        self.fk_chain.add_constraint()

        # IK, FK to result jnt
        for index in range(self.segment):
            cmds.parentConstraint(
                self.ik_chain.jnts[index],
                self.fk_chain.jnts[index],
                self.jnts[index]
            )

        # IK FK switch
        for index in range(self.segment):
            cmds.setDrivenKeyframe(
                '{}_parentConstraint1.{}W0'.format(self.jnts[index],self.ik_chain.jnts[index]),
                cd=self.master_ctrl+'.FK_IK', dv=1, v=1)
            cmds.setDrivenKeyframe(
                '{}_parentConstraint1.{}W1'.format(self.jnts[index], self.fk_chain.jnts[index]),
                cd=self.master_ctrl+'.FK_IK', dv=1, v=0)
            cmds.setDrivenKeyframe(
                '{}_parentConstraint1.{}W0'.format(self.jnts[index], self.ik_chain.jnts[index]),
                cd=self.master_ctrl+'.FK_IK', dv=0, v=0)
            cmds.setDrivenKeyframe(
                '{}_parentConstraint1.{}W1'.format(self.jnts[index], self.fk_chain.jnts[index]),
                cd=self.master_ctrl+'.FK_IK', dv=0, v=1)

            cmds.setDrivenKeyframe(self.ik_chain.ctrls[index]+'.visibility', cd=self.master_ctrl+'.FK_IK', dv=1, v=1)
            cmds.setDrivenKeyframe(self.ik_chain.ctrls[index]+'.visibility', cd=self.master_ctrl+'.FK_IK', dv=0, v=0)
            cmds.setDrivenKeyframe(self.fk_chain.ctrls[index]+'.visibility', cd=self.master_ctrl+'.FK_IK', dv=0, v=1)
            cmds.setDrivenKeyframe(self.fk_chain.ctrls[index]+'.visibility', cd=self.master_ctrl+'.FK_IK', dv=1, v=0)
