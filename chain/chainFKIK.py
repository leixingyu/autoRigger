import maya.cmds as cmds

from . import chain, chainFK, chainIK
from .. import util, shape
from ..base import bone
from ..constant import ATTRS
from ..utility.datatype import vector
from ..utility.rigging import joint, transform


class ChainFKIKItem(chain.ChainItem):
    def __init__(self, name='chain-fkik'):
        super(ChainFKIKItem, self).__init__(name)

    def build_guide(self, *args, **kwargs):
        """Override"""
        self._obj = ChainFKIK(*args, **kwargs)
        self._obj.build_guide()


class ChainFKIK(chain.Chain):
    """
    Create a FK/IK control rig system for a chain-like joints

    This control rig consist of three overlapping joint chains:
    FK chain, IK chain and result joint chain
    in which, the result joint chain is driven by both FK and IK chain
    """

    def __init__(self, side, name, segment, length, direction, is_stretch=0):
        """
        Extend: create FK/IK and result three-chain system
        specify length and direction of the chain
        and whether it allows for stretching

        :param length: float. total length of rig chain
        :param direction: vector.Vector. world direction from root to top node
        :param is_stretch: bool. allow stretching for the rig
        """
        super(ChainFKIK, self).__init__(side, name, segment)

        self.ik_chain = chainIK.ChainIK(side, name, segment, length, direction, is_stretch)
        self.fk_chain = chainFK.ChainFK(side, name, segment, length, direction)

        # master controller location
        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(direction).normalize()

    @bone.update_base_name
    def create_namespace(self):
        """
        Override: create naming for all three chains
        """
        self.ik_chain.create_namespace()
        self.fk_chain.create_namespace()

        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base, index))
            self.jnts.append('{}{}_jnt'.format(self.base, index))

        self.offsets.append('{}master_offset'.format(self.base))
        self.ctrls.append('{}master_ctrl'.format(self.base))

    def set_shape(self):
        """
        Override: setup controller shapes for all three chains
        """
        self.ik_chain.set_shape()
        self.fk_chain.set_shape()
        self._shape = shape.make_arrow(self._scale)

    def create_joint(self):
        """
        Override: create FK, IK and result joint chain
        """
        self.ik_chain.create_joint()
        self.fk_chain.create_joint()

        # result jnt
        cmds.select(clear=1)
        for index, loc in enumerate(self.locs):
            pos = cmds.xform(loc, q=1, t=1, ws=1)
            cmds.joint(p=pos, n=self.jnts[index])
            util.uniform_scale(self.jnts[index], self._scale)

        # clean up
        cmds.setAttr(self.ik_chain.jnts[0]+'.v', 0)
        cmds.setAttr(self.fk_chain.jnts[0]+'.v', 0)

        cmds.parent(self.jnts[0], util.G_JNT_GRP)
        joint.orient_joint(self.jnts[0])

    def place_controller(self):
        """
        Override: create and place FK, IK and result chain controller
        """
        self.ik_chain.place_controller()
        self.fk_chain.place_controller()

        # result joint master control
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
        """
        Override: add constraint relationship between the result joint
        and the other two (FK/IK) chain
        """
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
