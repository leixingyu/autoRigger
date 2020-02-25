import maya.cmds as cmds
import base
import quadSpine
import backLeg
import frontLeg
import tail
import misc

reload(base)
reload(quadSpine)
reload(backLeg)
reload(frontLeg)
reload(tail)

class Quadruped(base.Base):
    def __init__(self, prefix, side='NA', id='standard'):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Quadruped'
        self.constructNameSpace(self.metaType)

        self.setLocAttr()

    def setLocAttr(self):
        self.leftArm = frontLeg.FrontLeg(prefix=self.prefix, side='L', id='standard')
        self.rightArm = frontLeg.FrontLeg(prefix=self.prefix, side='R', id='standard')

        self.leftLeg = backLeg.BackLeg(prefix=self.prefix, side='L', id='standard')
        self.rightLeg = backLeg.BackLeg(prefix=self.prefix, side='R', id='standard')

        self.spine = quadSpine.QuadSpine(prefix=self.prefix, side='NA', id='spine')
        self.tail = tail.Tail(prefix=self.prefix, side='NA', id='tip')

        self.leftArm.setLocAttr(startPos=[2, 5, 3])

        self.rightArm.setLocAttr(startPos=[-2, 5, 3])

        self.leftLeg.setLocAttr(startPos=[2, 5, -3])

        self.rightLeg.setLocAttr(startPos=[-2, 5, -3])

        self.spine.setLocAttr(startPos=[0, 6, -3])

        self.tail.setLocAttr(startPos=[0, 6, -4])

    def buildGuide(self):
        self.leftArm.buildGuide()
        self.rightArm.buildGuide()
        self.leftLeg.buildGuide()
        self.rightLeg.buildGuide()
        self.spine.buildGuide()
        self.tail.buildGuide()

    def constructJnt(self):
        leftShoulder = self.leftArm.constructJnt()
        rightShoulder = self.rightArm.constructJnt()
        leftHip = self.leftLeg.constructJnt()
        rightHip = self.rightLeg.constructJnt()
        spineRoot = self.spine.constructJnt()
        tailRoot = self.tail.constructJnt()

        # parent leg root joints to root spline joint
        misc.batchParent([leftShoulder, rightShoulder], self.spine.topSpine)

        # parent arm root joints to top spline joint
        misc.batchParent([leftHip, rightHip], spineRoot)

        # parent tail to spine
        cmds.parent(tailRoot, spineRoot)

    def placeCtrl(self):
        self.leftArm.placeCtrl()
        self.rightArm.placeCtrl()
        self.leftLeg.placeCtrl()
        self.rightLeg.placeCtrl()
        self.spine.placeCtrl()
        self.tail.placeCtrl()

        cmds.addAttr(self.spine.masterCtrl, longName='FK_IK', attributeType='double', defaultValue=1, minValue=0, maxValue=1, keyable=True)

    def addConstraint(self):
        self.leftArm.addConstraint()
        self.rightArm.addConstraint()
        self.leftLeg.addConstraint()
        self.rightLeg.addConstraint()
        self.spine.addConstraint()
        self.tail.addConstraint()

        # parenting the front and back leg and tail under spine ctrl
        misc.batchParent([self.leftArm.shoulderCtrl, self.rightArm.shoulderCtrl], self.spine.topCtrl)
        misc.batchParent([self.leftLeg.hipCtrl, self.rightLeg.hipCtrl], self.spine.rootCtrl)
        cmds.parentConstraint(self.spine.rootCtrl, self.tail.masterCtrl, mo=True)

        # hide tail ctrl and connect ik/fk switch to spine master ctrl
        #cmds.setAttr(self.tail.masterCtrl+'.visibility', 0)
        cmds.connectAttr(self.spine.masterCtrl+'.FK_IK', self.tail.masterCtrl+'.FK_IK')

    def colorCtrl(self):
        self.leftArm.colorCtrl()
        self.rightArm.colorCtrl()
        self.leftLeg.colorCtrl()
        self.rightLeg.colorCtrl()
        self.spine.colorCtrl()

    def deleteGuide(self):
        loc = cmds.ls(self.locGrp)
        cmds.delete(loc)


