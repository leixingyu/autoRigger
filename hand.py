import maya.cmds as cmds
import util, base, finger

class Hand(base.Base):
    def __init__(self, side, id, fingerCount=5):
        base.Base.__init__(self, side, id)
        self.metaType = 'Hand'
        self.id = id
        self.createNaming()
        self.fingerCount = fingerCount
        self.fingerList = []

    def setCtrlShape(self):
        handShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=10, name='Hand_tempShape')[0]
        selection = cmds.select('Hand_tempShape.cv[7:9]', 'Hand_tempShape.cv[0]')
        cmds.scale(1.5, 1, 1.5, selection, relative=True)
        cmds.scale(1.8, 1, 1.3, handShape)

    def setLocAttr(self, startPos=[0, 0, 0], interval=0.5, distance=2, scale=0.2):
        self.startPos = startPos
        self.interval = interval
        self.distance = distance
        self.scale = scale

    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)
        sideFactor = 1
        if self.side == 'R': sideFactor = -1

        #--- Finger Locator ---#
        zValue = self.startPos[2]
        offsets = [zValue+2*self.interval, zValue+self.interval, zValue, zValue-self.interval, zValue-2*self.interval]

        thumb = finger.Finger(side=self.side, id='thumb', type='Thumb')
        thumb.setLocAttr(startPos=[self.startPos[0]-sideFactor*0.7, self.startPos[1], offsets[0]], interval=0.3)  # x offset 0.7
        thumbGrp = thumb.buildGuide()

        index = finger.Finger(side=self.side, id='index')
        index.setLocAttr(startPos=[self.startPos[0], self.startPos[1], offsets[1]], interval=0.5)
        indexGrp = index.buildGuide()

        middle = finger.Finger(side=self.side, id='middle')
        middle.setLocAttr(startPos=[self.startPos[0], self.startPos[1], offsets[2]], interval=0.55)
        middleGrp = middle.buildGuide()

        ring = finger.Finger(side=self.side, id='ring')
        ring.setLocAttr(startPos=[self.startPos[0], self.startPos[1], offsets[3]], interval=0.5)
        ringGrp = ring.buildGuide()

        pinky = finger.Finger(side=self.side, id='pinky')
        pinky.setLocAttr(startPos=[self.startPos[0]-sideFactor*0.3, self.startPos[1], offsets[4]], interval=0.4)  # x offset 0.3
        pinkyGrp = pinky.buildGuide()

        self.fingerList = [thumb, index, middle, ring, pinky]

        #--- Single Wrist Locator ---#
        self.wrist = base.Base(side=self.side, id='wrist')
        self.wrist.setLocAttr(startPos=[self.startPos[0]-sideFactor*self.distance, self.startPos[1], self.startPos[2]])
        wrist = self.wrist.buildGuide()

        #--- Cleanup ---#
        util.batchParent([thumbGrp, indexGrp, middleGrp, ringGrp, pinkyGrp], wrist)
        cmds.parent(wrist, grp)
        cmds.parent(grp, self.locGrp)
        return wrist

    def constructJnt(self):
        tempList = [] # list for parenting
        for obj in self.fingerList: tempList.append(obj.constructJnt())
        wrist = self.wrist.constructJnt()
        util.batchParent(tempList, wrist)

    def placeCtrl(self):
        self.constraintList = []
        for obj in self.fingerList:  # placing finger controller
            fingerGrp = obj.placeCtrl()
            self.constraintList.append(fingerGrp)

    def addConstraint(self):
        for obj in self.fingerList:
            obj.addConstraint()      # add individual finger constraint

        for obj in self.constraintList:
            cmds.parentConstraint(self.wrist.jntName, obj, mo=True)

    def colorCtrl(self):
        for obj in self.fingerList:
            obj.colorCtrl()




