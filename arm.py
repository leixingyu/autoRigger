import maya.cmds as cmds
import base, hand, limb

class Arm(base.Base):
    def __init__(self, side, id):
        base.Base.__init__(self, side, id)
        self.metaType = 'Arm'
        self.createNaming()
        self.setLocAttr(startPos=[0, 10, 0])
        self.limb = limb.Limb(side=self.side, id=id, type='Arm')
        self.hand = hand.Hand(side=self.side, id=id)

    def setLocAttr(self, startPos=[0, 0, 0], distance=2, interval=0.5, gap=2, scale=0.2):
        self.startPos = startPos
        self.distance = distance
        self.interval = interval
        self.gap = gap
        self.scale = scale

    def buildGuide(self):
        #--- Limb ---#
        self.limb.setLocAttr(startPos=self.startPos, interval=self.distance)
        self.limb.buildGuide()

        #--- Hand ---#
        if self.side == 'L':
            self.hand.setLocAttr(startPos=[self.startPos[0] + 2 * self.distance + self.gap, self.startPos[1], self.startPos[2]],
                                 interval=self.interval, distance=self.gap)
        elif self.side == 'R':
            self.hand.setLocAttr(startPos=[self.startPos[0] - 2 * self.distance - self.gap, self.startPos[1], self.startPos[2]],
                                 interval=self.interval, distance=self.gap)
        wristLoc = self.hand.buildGuide()

        #--- Connect ---#
        cmds.parent(wristLoc, self.limb.locList[-1])  # parent wrist to the tip of limb

    def constructJnt(self):
        self.limb.constructJnt()
        self.hand.constructJnt()

    def placeCtrl(self):
        self.limb.placeCtrl()
        self.hand.placeCtrl()

    def addConstraint(self):
        self.limb.addConstraint()
        self.hand.addConstraint()
        #--- Connect ---#
        cmds.parentConstraint(self.limb.jntList[-1], self.hand.wrist.jntName, mo=True)

    def lockCtrl(self):
        self.limb.lockCtrl()

    def colorCtrl(self):
        self.limb.colorCtrl()
        self.hand.colorCtrl()

    def deleteGuide(self):
        limbGrp = cmds.ls(self.limb.locGrpName)
        cmds.delete(limbGrp)
        handGrp = cmds.ls(self.hand.locGrpName)
        cmds.delete(handGrp)
