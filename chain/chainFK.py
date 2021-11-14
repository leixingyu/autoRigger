import maya.cmds as cmds

from . import chain
from ..base import bone
from ..utility.datatype import vector


class ChainFK(chain.Chain):
    """
    Abstract FK type Chain module
    """

    def __init__(self, side, name, segment, length, direction):
        chain.Chain.__init__(self, side, name, segment)

        self.interval = length / (self.segment-1)
        self.dir = vector.Vector(direction).normalize()

    @bone.update_base_name
    def create_namespace(self):
        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base_name, index))
            self.jnts.append('{}{}fk_jnt'.format(self.base_name, index))
            self.ctrls.append('{}{}fk_ctrl'.format(self.base_name, index))
            self.offsets.append(
                '{}{}fk_offset'.format(self.base_name, index))

    def add_constraint(self):
        for index, jnt in enumerate(self.jnts):
            cmds.parentConstraint(self.ctrls[index], jnt)
