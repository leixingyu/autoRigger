import maya.cmds as cmds

from autoRigger.base import bone
from autoRigger import util
from ..chain import chainIK


class SpineIK(chainIK.ChainIK):
    """ This module creates a biped spine rig"""

    def __init__(self, side, name, length=6.0, segment=6):
        """ Initialize Spine class with side and name

        :param side: str
        :param name: str
        """
        chainIK.ChainIK.__init__(self, side, name, segment, length, direction=[0, 1, 0])

        self._rtype = 'spine'


class Spine(bone.Bone):
    """ This module creates a biped spine rig"""

    def __init__(self, side, name, length=6.0, segment=6):
        """ Initialize Spine class with side and name

        :param side: str
        :param name: str
        """
        bone.Bone.__init__(self, side, name)
        self._rtype = 'spine'

        self.interval = length/(segment-1)
        self.segment = segment
        self.scale = 0.5

        self.locs, self.jnts, self.ctrls, self.clusters = ([] for i in range(4))

    def create_namespace(self):
        self.base_name = '{}_{}_{}'.format(self._rtype, self._side, self._name)

        for i in range(self.segment):
            self.locs.append('{}{}_loc'.format(self.base_name, i))
            self.jnts.append('{}{}_jnt'.format(self.base_name, i))
            self.ctrls.append('{}{}_ctrl'.format(self.base_name, i))
            self.offsets.append('{}{}_offset'.format(self.base_name, i))
            self.clusters.append('{}{}_cluster'.format(self.base_name, i))

        # ik has different ctrl name
        self.ik_curve = '{}ik_curve'.format(self.base_name)
        self.ik = '{}_ik'.format(self.base_name)

    def set_controller_shape(self):
        self._shape = list(range(2))

        self._shape[0] = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name=self.namer.tmp)[0]
        cmds.scale(2, 2, 2, self._shape[0])

        self._shape[1] = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name=self.namer.tmp)[0]
        cmds.move(0, 0, 0.75, relative=1)
        cmds.rotate(0, 0, 90, self._shape[1])
        cmds.scale(0.5, 0.5, 0.5, self._shape[1])

    def create_locator(self):
        for i in range(self.segment):
            spine = cmds.spaceLocator(n=self.locs[i])
            # root locator of spine parent to the spine group
            if i == 0:
                cmds.scale(self.scale, self.scale, self.scale, spine)
            # spine locator parent to the previous locator
            else:
                cmds.parent(spine, self.locs[i-1], relative=1)
                # move spine locator along +y axis
                cmds.move(0, self.interval, 0, spine, relative=1)

        cmds.parent(self.locs[0], util.G_LOC_GRP)
        return self.locs[0]

    def create_joint(self):
        cmds.select(clear=1)

        for i, loc in enumerate(self.locs):
            loc_pos = cmds.xform(loc, q=1, t=1, ws=1)
            jnt = cmds.joint(p=loc_pos, name=self.jnts[i])
            cmds.setAttr(jnt + '.radius', self.scale)

        cmds.parent(self.jnts[0], util.G_JNT_GRP)
        return self.jnts[0]
    
    def place_controller(self):
        grp = cmds.group(em=1, name=self.offsets[0])
        
        for i, spine in enumerate(self.jnts):
            spine_pos = cmds.xform(spine, q=1, t=1, ws=1)
            cmds.duplicate(self._shape[0], name=self.ctrls[i])
            if i == 0:
                cmds.move(spine_pos[0], spine_pos[1], spine_pos[2], self.ctrls[i])
                cmds.makeIdentity(self.ctrls[i], apply=1, t=1, r=1, s=1)
            elif i != 0:
                cmds.parent(self.ctrls[i], self.ctrls[i-1])

                cmds.move(spine_pos[0], spine_pos[1], spine_pos[2]-5, self.ctrls[i])
                cmds.move(spine_pos[0], spine_pos[1], spine_pos[2], self.ctrls[i]+'.scalePivot',
                          self.ctrls[i]+'.rotatePivot', absolute=1)
            cmds.makeIdentity(self.ctrls[i], apply=1, t=1, r=1, s=1)

        cmds.parent(self.ctrls[0], grp)
        cmds.parent(grp, util.G_CTRL_GRP)
        return grp

    def build_ik(self):
        # Create Spine Curve
        curve_points = []
        for i, spine in enumerate(self.jnts):
            spine_pos = cmds.xform(spine, q=1, t=1, ws=1)
            curve_points.append(spine_pos)

        cmds.curve(p=curve_points, name=self.ik_curve)
        cmds.setAttr(self.ik_curve+'.visibility', 0)
        # turning off inherit transform avoid curve move/scale twice as much
        cmds.inheritTransform(self.ik_curve, off=1)

        # Create Spline IK
        cmds.ikHandle(startJoint=self.jnts[0], endEffector=self.jnts[-1], name=self.ik, curve=self.ik_curve, createCurve=False, parentCurve=1, roc=1, solver='ikSplineSolver')
        cmds.setAttr(self.ik+'.visibility', 0)
        cmds.parent(self.ik, util.G_CTRL_GRP)

        # Create Cluster
        cvs = cmds.ls('{}.cv[0:]'.format(self.ik_curve), fl=1)
        for i, cv in enumerate(cvs):
            cluster = cmds.cluster(cv, name=self.clusters[i])[-1]
            if i != 0:
                cmds.parent(cluster, '{}Handle'.format(self.clusters[i-1]), relative=False)
            else:
                cmds.parent(cluster, util.G_CTRL_GRP)
            cmds.setAttr(cluster+'.visibility', 0)

    def add_constraint(self):
        self.build_ik()
        for i in range(0, self.segment):
            spine_cluster = cmds.ls('{}Handle'.format(self.clusters[i]))
            spine_ctrl = cmds.ls(self.ctrls[i])
            cmds.pointConstraint(spine_ctrl, spine_cluster)
        cmds.connectAttr(self.ctrls[-1]+'.rotateY', '{}.twist'.format(self.ik))
