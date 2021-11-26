import maya.cmds as cmds

from . import chain
from .. import util, shape
from ..base import bone
from ..utility.rigging import transform
from ..utility.useful import algorithm


class ChainEP(chain.Chain):
    """
    Create an EP (Edit Point) control rig system for a chain-like joints

    The EP serves as controllers like in a EP-curve with fall-off influence
    """

    def __init__(self, side, name, segment, curve, cv=0):
        """
        Extend: specify the guide curve and the number of control vertices
        which affects the fall-off influences;
        the number of cv should be less than the segment

        :param curve: str. curve transform name used for guide
        :param cv: int. number of control vertices
        """
        chain.Chain.__init__(self, side, name, segment)

        if not cv:
            cv = self.segment
        if cv < 2:
            raise ValueError('in-sufficient control points')

        self.clusters = list()
        self.guide_curve = None
        self.curve = curve
        self.cvs = list()

        percents = algorithm.get_percentages(cv)
        for p in percents:
            integer = int(round(p*(self.segment-1)))
            self.cvs.append(integer)

    @bone.update_base_name
    def assign_secondary_naming(self):
        """
        Override: create segment based naming and guide curve name
        """
        for index in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base, index))
            self.jnts.append('{}{}_jnt'.format(self.base, index))
            self.ctrls.append('{}{}_ctrl'.format(self.base, index))
            self.offsets.append(
                '{}{}_offset'.format(self.base, index))
            self.clusters.append('{}{}_cluster'.format(self.base, index))

        self.guide_curve = '{}_curve'.format(self.base)

    def create_locator(self):
        """
        Override: create guide locators evenly distributed on guide curve
        """
        locs = util.create_locators_on_curve(self.curve, self.segment)
        for index, loc in enumerate(locs):
            cmds.rename(loc, self.locs[index])
            if index:
                cmds.parent(self.locs[index], self.locs[index-1])
        cmds.parent(self.locs[0], util.G_LOC_GRP)

    def set_shape(self):
        """
        Override: setup sphere as controller shape
        """
        self._shape = shape.make_sphere(self._scale)

    def place_controller(self):
        """
        Override: create and place controller based on control vertices
        """
        # TODO: use clear_xform
        for index in self.cvs:
            cmds.duplicate(self._shape, n=self.ctrls[index])
            cmds.group(em=1, n=self.offsets[index])

            transform.match_xform(self.offsets[index], self.jnts[index])

            cmds.parent(self.ctrls[index], self.offsets[index], r=1)
            cmds.parent(self.offsets[index], util.G_CTRL_GRP)

    def add_constraint(self):
        """
        Override: add smooth fall-off constraint between joints and controller
        """
        # smooth fall-off constraint along the chain
        for i in range(len(self.cvs)-1):
            head = self.cvs[i]
            tail = self.cvs[i+1]
            for j in range(head, tail+1):
                gap = 1.00/(tail - head)

                # parent constraint will break things
                cmds.pointConstraint(self.ctrls[head], self.jnts[j],
                                     w=1 - ((j-head) * gap), mo=1)
                cmds.pointConstraint(self.ctrls[tail], self.jnts[j],
                                     w=(j-head) * gap, mo=1)
                cmds.orientConstraint(self.ctrls[head], self.jnts[j],
                                      w=1 - ((j-head) * gap), mo=1)
                cmds.orientConstraint(self.ctrls[tail], self.jnts[j],
                                      w=(j-head) * gap, mo=1)
