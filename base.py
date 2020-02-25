import maya.cmds as cmds
import misc

class Base(object):
    def __init__(self, prefix, side='NA', id='idPlaceHolder'):
        self.prefix = prefix
        self.side = side
        self.id = id
        metaType = 'Base'
        self.constructNameSpace(metaType)
        self.createOutlierGrp()
        self.setLocAttr()

    '''
    Create the name space formatting for current module
    '''
    def constructNameSpace(self, metaType):
        self.locGrp = '_Locators'
        self.ctrlGrp = '_Controllers'
        self.jntGrp = '_Joints'
        self.meshGrp = '_Meshes'

        self.name = '_' + self.side + '_' + metaType + '_' + self.id

        self.locName = self.prefix + '_Loc' + self.name
        self.locGrpName = self.prefix + '_LocGrp' + self.name
        self.jntName = self.prefix + '_Jnt' + self.name
        self.jntGrpName = self.prefix + '_JntGrp' + self.name
        self.ctrlName = self.prefix + '_Ctrl' + self.name
        self.ctrlGrpName = self.prefix + '_CtrlGrp' + self.name
        self.ctrlOffsetGrpName = self.prefix + '_CtrlOffsetGrp' + self.name

    '''
    Create the different parent groups in outlier
    '''
    def createOutlierGrp(self):
        for grp in [self.locGrp, self.ctrlGrp, self.jntGrp, self.meshGrp]:
            if not cmds.ls(grp):
                cmds.group(em=True, name=grp)

    '''
    Set locator attribute
    '''
    def setLocAttr(self, startPos=[0, 0, 0], scale=0.2):
        self.startPos = startPos
        self.scale = scale

    '''
    Create a single locator
    '''
    def buildGuide(self):
        self.loc = cmds.spaceLocator(n=self.locName)
        grp = cmds.group(em=True, name=self.locGrpName)

        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], self.loc, relative=True)
        cmds.scale(self.scale, self.scale, self.scale, self.loc)

        cmds.parent(self.loc, grp)
        cmds.parent(grp, self.locGrp)

        self.colorLoc()
        return grp

    '''
    default functions
    '''
    def constructJnt(self):
        cmds.select(clear=True)
        locPos = cmds.xform(self.locName, q=True, t=True, ws=True)

        self.jnt = cmds.joint(p=locPos, name=self.jntName)
        cmds.setAttr(self.jnt + '.radius', 1)

        cmds.parent(self.jnt, self.jntGrp)
        misc.orientJnt(self.jnt)
        return self.jnt

    def placeCtrl(self):
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
        cmds.parentConstraint(self.ctrl, self.jnt)

    '''
    Delete the locator group from the scene
    '''
    def deleteGuide(self):
        grp = cmds.ls(self.locGrpName)
        cmds.delete(grp)

    '''
    Delete temporary controller shape in the scene
    '''
    def deleteShape(self):
        shapes = cmds.ls('*_tempShape*')
        cmds.delete(shapes)

    '''
    Color-code the controller based on the side
    '''
    def colorCtrl(self):
        ctrls = cmds.ls(self.ctrlName+'*')
        for ctrl in ctrls:
            if cmds.nodeType(ctrl) in ['nurbsCurve', 'transform']:
            #print cmds.nodeType(ctrl)
                cmds.setAttr(ctrl + '.overrideEnabled', 1)
                if self.side == 'L':
                    cmds.setAttr(ctrl + '.overrideColor', 6)
                elif self.side == 'R':
                    cmds.setAttr(ctrl + '.overrideColor', 13)
                else:
                    cmds.setAttr(ctrl + '.overrideColor', 17)

    '''
    Color-code the controller based on the side
    '''
    def colorLoc(self):
        locs = cmds.ls(self.locName+'*')
        for loc in locs:
            if cmds.nodeType(loc) in ['transform']:
            #print cmds.nodeType(ctrl)
                cmds.setAttr(loc + '.overrideEnabled', 1)
                if self.side == 'L':
                    cmds.setAttr(loc + '.overrideColor', 6)
                elif self.side == 'R':
                    cmds.setAttr(loc + '.overrideColor', 13)
                else:
                    cmds.setAttr(loc + '.overrideColor', 17)

    '''
    lock specific attribute(s) in a controller
    '''
    def lockCtrl(self):
        pass

    '''
    Build the skeleton, add controller and constraints
    '''
    def buildRig(self):
        self.constructJnt()
        self.placeCtrl()
        self.deleteGuide()
        self.colorCtrl()
        self.addConstraint()
        self.lockCtrl()




