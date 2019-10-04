import maya.cmds as cmds
import base
import foot
import limb
import misc

reload(base)
reload(limb)
reload(foot)

class Leg(base.Base):
    def __init__(self, prefix, side, id):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Leg'

        self.constructNameSpace(self.metaType)
        self.setLocAttr(startPos=[1, 4.4, 0])
        self.limb = limb.Limb(prefix=self.prefix, side=self.side, id='a', type='Leg')
        self.foot = foot.Foot(prefix=self.prefix, side=self.side, id='a')

    def setLocAttr(self, startPos=[0, 0, 0], distance=2, interval=0.5, height=0.4, scale=0.2):
        self.startPos = startPos
        self.distance = distance
        self.interval = interval
        self.height = height
        self.scale = scale

    def buildGuide(self):
        self.limb.setLocAttr(startPos=self.startPos, interval=self.distance)
        self.limb.buildGuide()

        self.foot.setLocAttr(startPos=[self.startPos[0], self.startPos[1]-2*self.distance, self.startPos[2]], interval=self.interval, height=self.height)
        self.foot.buildGuide()

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
        orgIK = cmds.ls(self.limb.ctrlName+'IK')
        ikHandle = cmds.ls(self.limb.prefix+'_IK'+self.limb.name)
        ankle = cmds.ls(self.foot.jntName+'ankle')

        cmds.delete(orgIK)
        cmds.parentConstraint(ankle, ikHandle)

        cmds.setDrivenKeyframe(self.foot.ctrlName+'.visibility', currentDriver=self.limb.ctrlName+'IKFK_Switch.FK_IK', driverValue=1, value=1)
        cmds.setDrivenKeyframe(self.foot.ctrlName+'.visibility', currentDriver=self.limb.ctrlName+'IKFK_Switch.FK_IK', driverValue=0, value=0)

        '''TODO: FK mode'''

    def deleteGuide(self):
        limbGrp = cmds.ls(self.limb.locGrpName)
        cmds.delete(limbGrp)
        footGrp = cmds.ls(self.foot.locGrpName)
        cmds.delete(footGrp)
