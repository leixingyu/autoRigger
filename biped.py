import maya.cmds as cmds
import util, base, arm, leg, spine

class Biped(base.Base):
    def __init__(self, side, id):
        base.Base.__init__(self, side, id)
        self.metaType = 'Biped'
        self.createNaming()
        self.setLocAttr(startPos=[0, 8.4, 0], spineL=5.0)

        self.leftArm = arm.Arm(side='L', id='arm')
        self.rightArm = arm.Arm(side='R', id='arm')
        self.leftLeg = leg.Leg(side='L', id='leg')
        self.rightLeg = leg.Leg(side='R', id='leg')
        self.spine = spine.Spine(side='M', id='spine')
        self.neck = base.Base(side='M', id='neck')
        self.head = base.Base(side='M', id='head')
        self.tip = base.Base(side='M', id='tip')

    def setLocAttr(self, startPos=[0, 0, 0], spineL=6.0, scale=0.2):
        self.startPos = startPos
        self.spineL = spineL
        self.scale = scale

    def buildGuide(self):
        self.leftArm.setLocAttr(startPos=[self.startPos[0]+2, self.startPos[1]+self.spineL, self.startPos[2]])
        self.rightArm.setLocAttr(startPos=[self.startPos[0]-2, self.startPos[1]+self.spineL, self.startPos[2]])
        self.leftLeg.setLocAttr(startPos=[self.startPos[0]+1, self.startPos[1], self.startPos[2]])
        self.rightLeg.setLocAttr(startPos=[self.startPos[0]-1, self.startPos[1], self.startPos[2]])
        self.spine.setLocAttr(startPos=self.startPos, length=self.spineL)
        self.neck.setLocAttr(startPos=[self.startPos[0], self.startPos[1]+self.spineL+1, self.startPos[2]])
        self.head.setLocAttr(startPos=[self.startPos[0], self.startPos[1]+self.spineL+1.5, self.startPos[2]])
        self.tip.setLocAttr(startPos=[self.startPos[0], self.startPos[1]+self.spineL+2, self.startPos[2]])

        self.leftArm.buildGuide()
        self.rightArm.buildGuide()
        self.leftLeg.buildGuide()
        self.rightLeg.buildGuide()
        self.spine.buildGuide()
        self.neck.buildGuide()
        self.head.buildGuide()
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

        #--- Connect ---#
        # Leg root to spine root #
        leftLegJnt = cmds.ls(self.leftLeg.limb.jntList[0])
        rightLegJnt = cmds.ls(self.rightLeg.limb.jntList[0])
        rootSpineJnt = cmds.ls(self.spine.rootSpine)
        util.batchParent([leftLegJnt, rightLegJnt], rootSpineJnt)

        # Arm root spine root #
        leftArmJnt = cmds.ls(self.leftArm.limb.jntList[0])
        rightArmJnt = cmds.ls(self.rightArm.limb.jntList[0])
        topSpineJnt = cmds.ls(self.spine.topSpine)
        util.batchParent([leftArmJnt, rightArmJnt], topSpineJnt)

        # Neck to spine tip, head to neck #
        cmds.parent(self.neck.jnt, topSpineJnt)
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

        #--- Connect ---#
        # Leg driven by root spine control #
        cmds.parentConstraint(self.spine.globalCtrl, self.leftLeg.limb.switchCtrl, mo=True)
        cmds.parentConstraint(self.spine.globalCtrl, self.rightLeg.limb.switchCtrl, mo=True)

        # Arm driven by top spine control #
        cmds.parentConstraint(self.spine.topCtrl, self.leftArm.limb.switchCtrl, mo=True)
        cmds.parentConstraint(self.spine.topCtrl, self.rightArm.limb.switchCtrl, mo=True)

        # Neck to Head chain #
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


