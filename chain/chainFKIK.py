import maya.cmds as cmds

from . import chain, chainFK, chainIK
from .. import util, shape
from ..base import bone
from ..utility.datatype import vector
from ..utility.rigging import joint, transform


ATTRS = {
    'sw': 'FK_IK'
}


class ChainFKIK(chain.Chain):
    """
    Abstract FK/IK type Chain module
    """

    def __init__(self, side, name, segment, length, direction, is_stretch=0):
        chain.Chain.__init__(self, side, name, segment)

        self.ik_chain = chainIK.ChainIK(side, name, segment, length, direction, is_stretch)
        self.fk_chain = chainFK.ChainFK(side, name, segment, length, direction)

        # master controller location
        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(direction).normalize()

    @bone.update_base_name
    def create_namespace(self):
        self.ik_chain.create_namespace()
        self.fk_chain.create_namespace()

        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base_name, index))
            self.jnts.append('{}{}_jnt'.format(self.base_name, index))

        self.offsets.append('{}master_offset'.format(self.base_name))
        self.ctrls.append('{}master_ctrl'.format(self.base_name))

    def set_shape(self):
        self.ik_chain.set_shape()
        self.fk_chain.set_shape()
        self._shape = shape.make_arrow(self._scale)

    def create_joint(self):
        self.ik_chain.create_joint()
        self.fk_chain.create_joint()

        # Result jnt
        cmds.select(clear=1)
        for index, loc in enumerate(self.locs):
            pos = cmds.xform(loc, q=1, t=1, ws=1)
            cmds.joint(p=pos, n=self.jnts[index])
            util.uniform_scale(self.jnts[index], self._scale)

        # Cleanup
        cmds.setAttr(self.ik_chain.jnts[0]+'.v', 0)
        cmds.setAttr(self.fk_chain.jnts[0]+'.v', 0)

        cmds.parent(self.jnts[0], util.G_JNT_GRP)
        joint.orient_joint(self.jnts[0])

    def place_controller(self):
        self.ik_chain.place_controller()
        self.fk_chain.place_controller()

        # Master control
        cmds.duplicate(self._shape, n=self.ctrls[0])
        cmds.rotate(0, 0, 90, self.ctrls[0])
        cmds.group(n=self.offsets[0], em=1)
        transform.clear_xform(self.ctrls[0], self.offsets[0], self.jnts[0])
        cmds.addAttr(
            self.ctrls[0],
            sn='sw', ln=ATTRS['sw'], at='double',
            dv=1, min=0, max=1,
            k=1)

        cmds.parent(self.ik_chain.offsets[0], self.ctrls[0])
        cmds.parent(self.ik_chain.offsets[-1], self.ctrls[0])
        cmds.parent(self.fk_chain.offsets[0], self.ctrls[0])
        cmds.parent(self.offsets[0], util.G_CTRL_GRP)

    def add_constraint(self):
        self.ik_chain.add_constraint()
        self.fk_chain.add_constraint()

        # IK, FK to result jnt
        for index in range(self.segment):
            cons = cmds.parentConstraint(
                self.ik_chain.jnts[index],
                self.fk_chain.jnts[index],
                self.jnts[index])[0]

            cmds.setDrivenKeyframe(
                '{}.w0'.format(cons), cd=self.ctrls[0]+'.sw', dv=1, v=1)
            cmds.setDrivenKeyframe(
                '{}.w1'.format(cons), cd=self.ctrls[0]+'.sw', dv=1, v=0)
            cmds.setDrivenKeyframe(
                '{}.w0'.format(cons), cd=self.ctrls[0]+'.sw', dv=0, v=0)
            cmds.setDrivenKeyframe(
                '{}.w1'.format(cons), cd=self.ctrls[0]+'.sw', dv=0, v=1)

            cmds.setDrivenKeyframe(self.ik_chain.ctrls[index]+'.v',
                                   cd=self.ctrls[0]+'.sw', dv=1, v=1)
            cmds.setDrivenKeyframe(self.ik_chain.ctrls[index]+'.v',
                                   cd=self.ctrls[0]+'.sw', dv=0, v=0)
            cmds.setDrivenKeyframe(self.fk_chain.ctrls[index]+'.v',
                                   cd=self.ctrls[0]+'.sw', dv=0, v=1)
            cmds.setDrivenKeyframe(self.fk_chain.ctrls[index]+'.v',
                                   cd=self.ctrls[0]+'.sw', dv=1, v=0)
