import maya.cmds as cmds
import base, foot, limb

class Leg(base.Base):
    def __init__(self, side, id):
        base.Base.__init__(self, side, id)
        self.metaType = 'Leg'

        self.createNaming()
        self.setLocAttr(startPos=[0, 8.4, 0])
        self.limb = limb.Limb(side=self.side, id=id, type='Leg')
        self.foot = foot.Foot(side=self.side, id=id)

    def setLocAttr(self, startPos=[0, 0, 0], distance=4, interval=0.5, height=0.4, scale=0.2):
        self.startPos = startPos
        self.distance = distance
        self.interval = interval
        self.height = height
        self.scale = scale

    def buildGuide(self):
        #--- Limb ---#
        self.limb.setLocAttr(startPos=self.startPos, interval=self.distance)
        self.limb.buildGuide()

        #--- Foot ---#
        self.foot.setLocAttr(startPos=[self.startPos[0], self.startPos[1]-2*self.distance, self.startPos[2]],
                             interval=self.interval, height=self.height)
        footGrp = self.foot.buildGuide()

        #--- Connect ---#
        cmds.parent(footGrp, self.limb.locList[-1])

    def constructJnt(self):
        self.limb.constructJnt()
        self.foot.constructJnt()

    def placeCtrl(self):
        self.limb.placeCtrl()
        self.foot.placeCtrl()

    def addConstraint(self):
        self.limb.addConstraint()
        self.foot.addConstraint()

        #--- Connect ---#
        # IK constraint #
        cmds.parentConstraint(self.foot.revAnkleJntName, self.limb.ikCtrlName, mo=True)
        cmds.setAttr(self.limb.ikCtrlName+'.visibility', 0)

        # FK constraint #
        cmds.parentConstraint(self.limb.jntList[-1], self.foot.fkAnkleJntName, mo=True)
        cmds.parent(self.foot.fkCtrlName, self.limb.fkCtrlList[-1])

        # IK/FK switch #
        cmds.setDrivenKeyframe(self.limb.switchCtrl+'.FK_IK', currentDriver=self.foot.switchCtrlName+'.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.limb.switchCtrl+'.FK_IK', currentDriver=self.foot.switchCtrlName+'.FK_IK', driverValue=0, value=0)

        # Sub controller visibility and channel hide #
        cmds.setDrivenKeyframe(self.limb.ikCtrlName+'.visibility', currentDriver=self.limb.switchCtrl+'.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.limb.ikCtrlName+'.visibility', currentDriver=self.limb.switchCtrl+'.FK_IK', driverValue=0, value=0)
        cmds.setAttr(self.limb.switchCtrl+'.FK_IK', l=1, k=0)

    def deleteGuide(self):
        self.foot.deleteGuide()
        self.limb.deleteGuide()

    def colorCtrl(self):
        self.limb.colorCtrl()
        self.foot.colorCtrl()