import maya.cmds as cmds

from autoRigger.module.base import bone
from autoRigger import util
from . import chain, chainFK, chainIK

from utility.algorithm import vector
reload(vector)
from utility.setup import outliner
from utility.rigging import joint


class ChainFKIK(chain.Chain):
    """ This module creates a quadruped tail rig"""

    def __init__(self, side, name, length=4.0, segment=6, direction=[0, 1, 0]):
        """ Initialize Tail class with side and name

        :param side: str
        :param name: str
        """

        self.master_ctrl = None

        chain.Chain.__init__(self, side, name, length, segment, direction)

        self.ik_chain = chainIK.ChainIK(side, name, length, segment, direction)
        self.fk_chain = chainFK.ChainFK(side, name, length, segment, direction)

    def assign_secondary_naming(self):
        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base_name, index))
            self.jnts.append('{}{}_jnt'.format(self.base_name, index))

        self.master_ctrl = '{}master_ctrl'.format(self.base_name)

    def set_controller_shape(self):
        self.ik_chain.set_controller_shape()
        self.fk_chain.set_controller_shape()

        # master control
        sphere = cmds.createNode('implicitSphere')
        self._shape = cmds.rename(cmds.listRelatives(sphere, p=1), self.namer.tmp)

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

        pos = cmds.xform(self.jnts[0], q=1, t=1, ws=1)

        distance = (vector.Vector(pos)-self.interval * self.dir).as_list
        util.move(self.master_ctrl, distance)

        cmds.addAttr(self.master_ctrl, longName='FK_IK',
                     attributeType='double', defaultValue=1, minValue=0,
                     maxValue=1, keyable=1)

        cmds.parent(self.ik_chain.offsets[0], self.master_ctrl)
        cmds.parent(self.fk_chain.offsets[0], self.master_ctrl)

        # Cleanup
        cmds.parent(self.master_ctrl, util.G_CTRL_GRP)
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
