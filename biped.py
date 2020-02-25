import maya.cmds as cmds
import base
import arm
import leg
import spline
import misc

class Biped(base.Base):
    def __init__(self, prefix, side, id):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Biped'

        self.constructNameSpace(self.metaType)
        self.setLocAttr(startPos=[0, 8.4, 0], spineL=5.0)

        self.leftArm = arm.Arm(prefix=self.prefix, side='L', id='leftArm')
        self.rightArm = arm.Arm(prefix=self.prefix, side='R', id='rightArm')

        self.leftLeg = leg.Leg(prefix=self.prefix, side='L', id='leftLeg')
        self.rightLeg = leg.Leg(prefix=self.prefix, side='R', id='rightLeg')

        self.spine = spline.Spline(prefix=self.prefix, side='NA', id='spine')
        self.neck = base.Base(prefix=self.prefix, side='NA', id='neck')
        self.head = base.Base(prefix=self.prefix, side='NA', id='head')
        self.tip = base.Base(prefix=self.prefix, side='NA', id='tip')

    def setLocAttr(self, startPos=[0, 0, 0], spineL=6.0, scale=0.2):
        self.startPos = startPos
        self.spineL = spineL
        self.scale = scale

    def buildGuide(self):
        self.leftArm.setLocAttr(startPos=[self.startPos[0]+2,
                                          self.startPos[1]+self.spineL,
                                          self.startPos[2]])
        self.leftArm.buildGuide()

        self.rightArm.setLocAttr(startPos=[self.startPos[0]-2,
                                          self.startPos[1]+self.spineL,
                                          self.startPos[2]])
        self.rightArm.buildGuide()

        self.leftLeg.setLocAttr(startPos=[self.startPos[0]+1,
                                          self.startPos[1],
                                          self.startPos[2]])
        self.leftLeg.buildGuide()

        self.rightLeg.setLocAttr(startPos=[self.startPos[0]-1,
                                          self.startPos[1],
                                          self.startPos[2]])
        self.rightLeg.buildGuide()

        self.spine.setLocAttr(startPos=self.startPos, length=self.spineL)
        self.spine.buildGuide()

        self.neck.setLocAttr(startPos=[self.startPos[0],
                                       self.startPos[1]+self.spineL+1,
                                       self.startPos[2]])
        self.neck.buildGuide()

        self.head.setLocAttr(startPos=[self.startPos[0],
                                       self.startPos[1]+self.spineL+1.5,
                                       self.startPos[2]])
        self.head.buildGuide()

        self.tip.setLocAttr(startPos=[self.startPos[0],
                                      self.startPos[1]+self.spineL+2,
                                      self.startPos[2]])
        self.tip.buildGuide()

    def constructJnt(self):
        self.leftArm.constructJnt()
        self.rightArm.constructJnt()
        self.leftLeg.constructJnt()
        self.rightLeg.constructJnt()
        self.spine.constructJnt()
        self.neck.constructJnt()
        self.head.constructJnt()
        self.tip.constructJnt()

        # parent leg root joints to root spline joint
        leftLegJnt = cmds.ls(self.leftLeg.limb.rootJntName)
        rightLegJnt = cmds.ls(self.rightLeg.limb.rootJntName)
        rootSplineJnt = cmds.ls(self.spine.rootSpine)
        misc.batchParent([leftLegJnt, rightLegJnt], rootSplineJnt)

        # parent arm root joints to top spline joint
        leftArmJnt = cmds.ls(self.leftArm.limb.rootJntName)
        rightArmJnt = cmds.ls(self.rightArm.limb.rootJntName)
        topSplineJnt = cmds.ls(self.spine.topSpine)
        misc.batchParent([leftArmJnt, rightArmJnt], topSplineJnt)

        # parent neck to top spline, head to neck
        cmds.parent(self.neck.jnt, topSplineJnt)
        cmds.parent(self.head.jnt, self.neck.jnt)
        cmds.parent(self.tip.jnt, self.head.jnt)

    def placeCtrl(self):
        self.leftArm.placeCtrl()
        self.rightArm.placeCtrl()
        self.leftLeg.placeCtrl()
        self.rightLeg.placeCtrl()
        self.spine.placeCtrl()
        self.neck.placeCtrl()
        self.head.placeCtrl()
        self.tip.placeCtrl()

    def addConstraint(self):
        self.leftArm.addConstraint()
        self.rightArm.addConstraint()
        self.leftLeg.addConstraint()
        self.rightLeg.addConstraint()
        self.spine.addConstraint()
        self.neck.addConstraint()
        self.head.addConstraint()
        self.tip.addConstraint()

        # constraint both leg top controller to the global spine controller
        cmds.parentConstraint(self.spine.globalCtrl, self.leftLeg.limb.switchCtrl, mo=True)
        cmds.parentConstraint(self.spine.globalCtrl, self.rightLeg.limb.switchCtrl, mo=True)

        # constraint both arm top controller to the top spine controller
        cmds.parentConstraint(self.spine.topCtrl, self.leftArm.limb.switchCtrl, mo=True)
        cmds.parentConstraint(self.spine.topCtrl, self.rightArm.limb.switchCtrl, mo=True)

        # use the ctrl offset group as parent for the ctrl
        cmds.parent(self.tip.ctrlOffsetGrp, self.head.ctrlOffsetGrp)
        cmds.parent(self.head.ctrlOffsetGrp, self.neck.ctrlOffsetGrp)
        cmds.parent(self.neck.ctrlOffsetGrp, self.spine.topCtrl)

    def colorCtrl(self):
        self.leftArm.colorCtrl()
        self.rightArm.colorCtrl()
        self.leftLeg.colorCtrl()
        self.rightLeg.colorCtrl()
        self.spine.colorCtrl()
        self.neck.colorCtrl()
        self.head.colorCtrl()
        self.tip.colorCtrl()

    def deleteGuide(self):
        loc = cmds.ls(self.locGrp)
        cmds.delete(loc)


