import maya.cmds as cmds
import base
import finger
import misc

class Hand(base.Base):
    def __init__(self, prefix, side, id, fingerCount=5):
        base.Base.__init__(self, prefix, side, id)
        self.metaType = 'Hand'

        self.constructNameSpace(self.metaType)
        self.setLocAttr()

        '''Additional attr'''
        self.fingerCount = fingerCount

        '''Init finger list'''
        self.fingerList = []

    '''
    Create controller shape for hand control
    '''
    def setCtrlShape(self):
        # hand shape
        handShape = cmds.circle(nr=(0, 1, 0), c=(0, 0, 0), radius=1, s=10, name='Hand_tempShape')[0]
        selection = cmds.select('Hand_tempShape.cv[7:9]', 'Hand_tempShape.cv[0]')
        cmds.scale(1.5, 1, 1.5, selection, relative=True)
        cmds.scale(1.8, 1, 1.3, handShape)

    '''
    Set locator attribute
    startPos: middle finger root pos
    interval: distance between each finger
    distance: distance between root point and wrist
    '''
    def setLocAttr(self, startPos=[0, 0, 0], interval=0.5, distance=2, scale=0.2):
        self.startPos = startPos
        self.interval = interval
        self.distance = distance
        self.scale = scale

    '''
    Create hand locator:
    (typically consist of 5 fingers and a single bone)
    
                     /-------(+)---(+)---(+)---(+)  <--id:Pinky
                   / -----------(+)----(+)----(+)----(+)  <--id:Ring
    id:wrist--> (+)----------(startPos)----(+)----(+)-----(+)  <--id:Middle
                   \ ------------(+)----(+)----(+)----(+)  <--id:Index
                     \-------(+)--(+)--(+)--(+)  <--id:Thumb
                     
    (example for left hand)
    
    '''
    def buildGuide(self):
        grp = cmds.group(em=True, n=self.locGrpName)
        sideFactor = 1
        if self.side == 'R': sideFactor = -1

        # finger locator
        zValue = self.startPos[2]
        offsets = [zValue+2*self.interval, zValue+self.interval, zValue, zValue-self.interval, zValue-2*self.interval]

        thumb = finger.Finger(prefix=self.prefix, side=self.side, id='thumb')
        thumb.setLocAttr(startPos=[self.startPos[0]-sideFactor*0.7, self.startPos[1], offsets[0]], interval=0.3)  # x offset 0.7
        thumbGrp = thumb.buildGuide()

        index = finger.Finger(prefix=self.prefix, side=self.side, id='index')
        index.setLocAttr(startPos=[self.startPos[0], self.startPos[1], offsets[1]], interval=0.5)
        indexGrp = index.buildGuide()

        middle = finger.Finger(prefix=self.prefix, side=self.side, id='middle')
        middle.setLocAttr(startPos=[self.startPos[0], self.startPos[1], offsets[2]], interval=0.55)
        middleGrp = middle.buildGuide()

        ring = finger.Finger(prefix=self.prefix, side=self.side, id='ring')
        ring.setLocAttr(startPos=[self.startPos[0], self.startPos[1], offsets[3]], interval=0.5)
        ringGrp = ring.buildGuide()

        pinky = finger.Finger(prefix=self.prefix, side=self.side, id='pinky')
        pinky.setLocAttr(startPos=[self.startPos[0]-sideFactor*0.3, self.startPos[1], offsets[4]], interval=0.4)  # x offset 0.3
        pinkyGrp = pinky.buildGuide()

        self.fingerList = [thumb, index, middle, ring, pinky]

        # single joint locator
        self.wrist = base.Base(prefix=self.prefix, side=self.side, id='wrist')
        self.wrist.setLocAttr(startPos=[self.startPos[0]-sideFactor*self.distance, self.startPos[1], self.startPos[2]])
        wrist = self.wrist.buildGuide()

        # parenting
        misc.batchParent([thumbGrp, indexGrp, middleGrp, ringGrp, pinkyGrp], wrist)
        cmds.parent(wrist, grp)
        cmds.parent(grp, self.locGrp)
        return wrist

    '''
    Create Hand Joint (Finger Joint + Single Bone Joint) 
    '''
    def constructJnt(self):
        tempList = [] # list for parenting

        for obj in self.fingerList:
            tempList.append(obj.constructJnt())
        wrist = self.wrist.constructJnt()

        misc.batchParent(tempList, wrist)
        cmds.parent(wrist, self.jntGrp)

    '''
    Place Hand Controller (Finger Controllers + Whole Hand Controller)
    '''
    def placeCtrl(self):
        '''
        # placing hand controller
        self.setCtrlShape()
        handCtrl = cmds.duplicate('Hand_tempShape', name=self.ctrlName)[0]
        handPos = cmds.xform(self.wrist.jntName, q=True, t=True, ws=True)
        cmds.rotate(0, 0, 0, handCtrl, absolute=True)
        if self.side == 'L':
            cmds.move(handPos[0]+1.4, handPos[1], handPos[2], handCtrl, absolute=True)
        elif self.side == 'R':
            cmds.move(handPos[0]-1.4, handPos[1], handPos[2], handCtrl, absolute=True)
            cmds.rotate(0, 180, 0, handCtrl, relative=True)
        cmds.move(handPos[0], handPos[1], handPos[2], handCtrl + '.scalePivot', handCtrl + '.rotatePivot')
        cmds.makeIdentity(handCtrl, apply=True, t=1, r=1, s=1)

        self.deleteShape()
        '''
        self.constraintList = []
        # placing finger controller
        for obj in self.fingerList:
            fingerGrp = obj.placeCtrl()
            self.constraintList.append(fingerGrp)

    '''
    Add constraint to finger controllers + hand controller
    '''
    def addConstraint(self):
        # add individual finger constraint
        for obj in self.fingerList:
            obj.addConstraint()

        # add finger controllers constraint
        wristJnt = cmds.ls(self.wrist.jntName)
        for obj in self.constraintList:
            cmds.parentConstraint(wristJnt, obj, mo=True)




