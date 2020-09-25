import maya.cmds as cmds
import util

class Base(object):
    def __init__(self, side='M', id='idPlaceHolder'):
        self.side = side
        self.id = id
        self.metaType = 'Base'
        self.createNaming()
        self.createOutlinerGrp()
        self.setLocAttr()

    def createNaming(self):
        """ Create primary naming convention """
        self.locGrp = '_Locators'
        self.ctrlGrp = '_Controllers'
        self.jntGrp = '_Joints'
        self.meshGrp = '_Meshes'

        self.name = '{}_{}_{}'.format(self.metaType, self.side, self.id)

        self.locName = '{}_loc'.format(self.name)
        self.locGrpName = '{}_locGrp'.format(self.name)
        self.jntName = '{}_jnt'.format(self.name)
        self.jntGrpName = '{}_jntGrp'.format(self.name)
        self.ctrlName = '{}_ctrl'.format(self.name)
        self.ctrlGrpName = '{}_ctrlGrp'.format(self.name)
        self.ctrlOffsetGrpName = '{}_offset'.format(self.name)

    def createSecondaryNaming(self):
        """ Create secondary naming convention for complex module """
        pass

    def createOutlinerGrp(self):
        """ Create different groups in the outliner """
        for grp in [self.locGrp, self.ctrlGrp, self.jntGrp, self.meshGrp]:
            if not cmds.ls(grp):
                cmds.group(em=True, name=grp)

    def setCtrlShape(self):
        """ Setting up controller curve shapes as templates """
        pass

    def setLocAttr(self, startPos=[0, 0, 0], scale=0.2):
        """ Setup Locator initial position and size as guide """
        self.startPos = startPos
        self.scale = scale

    def buildGuide(self):
        """ Create the rig guides for placement purpose """
        self.loc = cmds.spaceLocator(n=self.locName)
        grp = cmds.group(em=True, name=self.locGrpName)

        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], self.loc, relative=True)
        cmds.scale(self.scale, self.scale, self.scale, self.loc)

        cmds.parent(self.loc, grp)
        cmds.parent(grp, self.locGrp)

        self.colorLoc()
        return grp

    def colorLoc(self):
        """ Color-code the guide locators based on left, right, middle side """
        locs = cmds.ls('{}*_loc'.format(self.name))
        for loc in locs:
            if cmds.nodeType(loc) in ['transform']:
                cmds.setAttr(loc + '.overrideEnabled', 1)
                if self.side == 'L':
                    cmds.setAttr(loc + '.overrideColor', 6)
                elif self.side == 'R':
                    cmds.setAttr(loc + '.overrideColor', 13)
                else:
                    cmds.setAttr(loc + '.overrideColor', 17)

    def constructJnt(self):
        """ Create the rig joints based on the guide's transform """
        cmds.select(clear=True)
        locPos = cmds.xform(self.locName, q=True, t=True, ws=True)

        self.jnt = cmds.joint(p=locPos, name=self.jntName)
        cmds.setAttr(self.jnt + '.radius', 1)

        cmds.parent(self.jnt, self.jntGrp)
        util.orientJnt(self.jnt)
        return self.jnt

    def placeCtrl(self):
        """ Duplicate control shapes and place them based on guide's and joint's transform """
        self.ctrl = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=8, name=self.ctrlName)[0]

        jntPos = cmds.xform(self.jnt, q=True, t=True, ws=True)
        locRot = cmds.xform(self.loc, q=True, ro=True, ws=True)

        # use offset group to clear out rotation on ctrl
        self.ctrlOffsetGrp = cmds.group(em=True, name=self.ctrlOffsetGrpName)
        cmds.move(jntPos[0], jntPos[1], jntPos[2], self.ctrlOffsetGrp)
        cmds.rotate(locRot[0], locRot[1], locRot[2], self.ctrlOffsetGrp)

        cmds.parent(self.ctrl, self.ctrlOffsetGrp, relative=True)  # ctrl has transform relative to offset group, which is 0
        cmds.parent(self.ctrlOffsetGrp, self.ctrlGrp)

    def addConstraint(self):
        """ Add all necessary constraints for the controller to control the rig """
        cmds.parentConstraint(self.ctrl, self.jnt)

    def deleteGuide(self):
        """ Clear out locator guides to de-clutter the scene """
        grp = cmds.ls(self.locGrpName)
        cmds.delete(grp)

    def deleteShape(self):
        """ Delete control template shape to de-clutter the scene"""
        shapes = cmds.ls('*_tempShape*')
        cmds.delete(shapes)

    def colorCtrl(self):
        """ Color-code the controller based on left, right, middle side """
        ctrls = cmds.ls('{}*_ctrl'.format(self.name))
        for ctrl in ctrls:
            if cmds.nodeType(ctrl) in ['nurbsCurve', 'transform']:
                cmds.setAttr(ctrl + '.overrideEnabled', 1)
                if self.side == 'L':
                    cmds.setAttr(ctrl + '.overrideColor', 6)
                elif self.side == 'R':
                    cmds.setAttr(ctrl + '.overrideColor', 13)
                else:
                    cmds.setAttr(ctrl + '.overrideColor', 17)

    def lockCtrl(self):
        """ Lock or hide specific channels of a controller from the animator """
        pass

    def buildRig(self):
        """ Build the full rig based on the guide, mesh not skinned """
        self.constructJnt()
        self.placeCtrl()
        self.deleteGuide()
        self.colorCtrl()
        self.addConstraint()
        self.lockCtrl()




