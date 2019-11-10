import maya.cmds as cmds
import base
import foot
import limb
import misc

class Leg(base.Base):
    def __init__(self, prefix, side, id):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Leg'

        self.constructNameSpace(self.metaType)
        self.setLocAttr(startPos=[0, 8.4, 0])
        self.limb = limb.Limb(prefix=self.prefix, side=self.side, id=id, type='Leg')
        self.foot = foot.Foot(prefix=self.prefix, side=self.side, id=id)

    def setLocAttr(self, startPos=[0, 0, 0], distance=4, interval=0.5, height=0.4, scale=0.2):
        self.startPos = startPos
        self.distance = distance
        self.interval = interval
        self.height = height
        self.scale = scale

    def buildGuide(self):
        self.limb.setLocAttr(startPos=self.startPos, interval=self.distance)
        self.limb.buildGuide()

        self.foot.setLocAttr(startPos=[self.startPos[0],
                                       self.startPos[1]-2*self.distance,
                                       self.startPos[2]],
                             interval=self.interval, height=self.height)
        footGrp = self.foot.buildGuide()
        cmds.parent(footGrp, self.limb.topLocName)

    def constructJnt(self):
        self.limb.constructJnt()
        self.foot.constructJnt()

    def placeCtrl(self):
        self.limb.placeCtrl()
        self.foot.placeCtrl()

    def addConstraint(self):
        self.limb.addConstraint()
        self.foot.addConstraint()

        '''IK mode'''
        cmds.parentConstraint(self.foot.jntName+'reverseAnkle', self.limb.ctrlName+'IK', mo=True)
        cmds.setAttr(self.limb.ctrlName+'IK.visibility', 0)

        '''FK mode'''
        cmds.parentConstraint(self.limb.topJntName, self.foot.jntName+'ankleFK', mo=True)
        cmds.parent(self.foot.ctrlName+'FK', self.limb.topCtrlName+'FK')

        '''IK/FK Switch'''
        cmds.setDrivenKeyframe(self.limb.ctrlName+'IKFK_Switch.FK_IK', currentDriver=self.foot.ctrlName+'Switch.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.limb.ctrlName+'IKFK_Switch.FK_IK', currentDriver=self.foot.ctrlName+'Switch.FK_IK', driverValue=0, value=0)
        # hide limb ik top controller because its being controlled by foot controller
        cmds.setDrivenKeyframe(self.limb.ctrlName+'IK.visibility', currentDriver=self.limb.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=0)
        cmds.setDrivenKeyframe(self.limb.ctrlName+'IK.visibility', currentDriver=self.limb.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=0)

    def deleteGuide(self):
        limbGrp = cmds.ls(self.limb.locGrpName)
        cmds.delete(limbGrp)
        footGrp = cmds.ls(self.foot.locGrpName)
        cmds.delete(footGrp)

    def colorCtrl(self):
        self.limb.colorCtrl()
        self.foot.colorCtrl()
    