import maya.cmds as cmds

from . import chain
from ..base import bone
from ..utility.datatype import vector


class ChainFK(chain.Chain):
    """
    Create a FK control rig system for a chain-like joints
    """

    def __init__(self, side, name, segment, length, direction):
        """
        Extend: specify length and direction of the chain

        :param length: float. total length of rig chain
        :param direction: vector.Vector. world direction from root to top node
        """
        chain.Chain.__init__(self, side, name, segment)

        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(direction).normalize()

    @bone.update_base_name
    def create_namespace(self):
        """
        Override: create segment based naming
        """
        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base, index))
            self.jnts.append('{}{}fk_jnt'.format(self.base, index))
            self.ctrls.append('{}{}fk_ctrl'.format(self.base, index))
            self.offsets.append(
                '{}{}fk_offset'.format(self.base, index))

    def add_constraint(self):
        """
        Override: constraint joints with corresponding controllers
        """
        for index, jnt in enumerate(self.jnts):
            cmds.parentConstraint(self.ctrls[index], jnt)
