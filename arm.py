import maya.cmds as cmds
import base
import hand
import limb
import misc


class Arm(base.Base):
    def __init__(self, prefix, side, id):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Leg'

        self.constructNameSpace(self.metaType)
        self.setLocAttr(startPos=[1, 10, 0])
        self.limb = limb.Limb(prefix=self.prefix, side=self.side, id='a', type='Arm')
        self.hand = hand.Hand(prefix=self.prefix, side=self.side, id='a')

    def setLocAttr(self, startPos=[0, 0, 0], distance=2, interval=0.5, gap=2, scale=0.2):
        self.startPos = startPos
        self.distance = distance
        self.interval = interval
        self.gap = gap
        self.scale = scale

    def buildGuide(self):
        self.limb.setLocAttr(startPos=self.startPos, interval=self.distance)
        self.limb.buildGuide()

        self.hand.setLocAttr(startPos=[self.startPos[0]+2*self.distance+self.gap, self.startPos[1], self.startPos[2]], interval=self.interval, distance=self.gap)
        self.hand.buildGuide()

    def constructJnt(self):
        self.limb.constructJnt()
        self.hand.constructJnt()

    def placeCtrl(self):
        self.limb.placeCtrl()
        self.hand.placeCtrl()

    def addConstraint(self):
        self.limb.addConstraint()
        self.hand.addConstraint()

        cmds.parentConstraint(self.limb.topJntName, self.hand.wrist.jntName, mo=True)

    def deleteGuide(self):
        limbGrp = cmds.ls(self.limb.locGrpName)
        cmds.delete(limbGrp)
        handGrp = cmds.ls(self.hand.locGrpName)
        cmds.delete(handGrp)
