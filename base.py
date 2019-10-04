import maya.cmds as cmds

class Base(object):
    def __init__(self, prefix, side, id='idPlaceHolder'):
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
    Create a single locator locator
    '''
    def buildGuide(self):
        locator = cmds.spaceLocator(n=self.locName)
        cmds.move(self.startPos[0], self.startPos[1], self.startPos[2], locator, relative=True)
        cmds.scale(self.scale, self.scale, self.scale, locator)

        cmds.parent(locator, self.locGrp)
        return locator

    '''
    default functions
    '''
    def constructJnt(self):
        cmds.select(clear=True)
        locPos = cmds.xform(self.locName, q=True, t=True, ws=True)
        jnt = cmds.joint(p=locPos, name=self.jntName)
        cmds.setAttr(jnt + '.radius', 1)
        return jnt

    def placeCtrl(self):
        print('default placing controller, needs override')

    def addConstraint(self):
        print('default adding constraint, needs override')

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
            cmds.setAttr(ctrl + '.overrideEnabled', 1)
            if self.side == 'L':
                cmds.setAttr(ctrl + '.overrideColor', 6)
            elif self.side == 'R':
                cmds.setAttr(ctrl + '.overrideColor', 13)
            else:
                cmds.setAttr(ctrl + '.overrideColor', 17)

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
        self.deleteGuide()
        self.placeCtrl()
        self.colorCtrl()
        self.lockCtrl()
        self.addConstraint()




