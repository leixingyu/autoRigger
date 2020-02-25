from Qt import QtCore, QtGui, QtWidgets
from Qt import _loadUi
import os
from autoRiggerPlus import misc, base, finger, foot, spline, limb, hand, arm, leg, biped, backLeg, frontLeg, tail, quadSpine, quadruped

class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MyWindow, self).__init__()
        _loadUi('autoRigger.ui', self)

        '''init ui variables'''
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.prefix = 'NoName'
        self.toBuildList = []
        self.current = None

        self.connectFunc()

    def connectFunc(self):
        self.setPrefixBtn.clicked.connect(self.setPrefix)

        # biped
        self.baseThumb.clicked.connect(self.baseClick)
        self.fingerThumb.clicked.connect(self.fingerClick)
        self.footThumb.clicked.connect(self.footClick)
        self.spineThumb.clicked.connect(self.spineClick)
        self.limbThumb.clicked.connect(self.limbClick)
        #self.headThumb.clicked.connect(self.headClick)

        self.bipedThumb.clicked.connect(self.bipedClick)
        self.handThumb.clicked.connect(self.handClick)
        self.armThumb.clicked.connect(self.armClick)
        self.legThumb.clicked.connect(self.legClick)

        # quadruped
        self.qspineThumb.clicked.connect(self.qspineClick)
        self.tailThumb.clicked.connect(self.tailClick)

        # utility
        self.buildCurrentBtn.clicked.connect(self.buildCurrent)
        self.buildAllBtn.clicked.connect(self.buildAll)
        self.mirrorBtn.clicked.connect(self.mirrorLoc)

    def setPrefix(self):
        if self.prefixEdit.text():
            self.prefix = str(self.prefixEdit.text())

    def buildCurrent(self):
        self.current.buildRig()
        self.toBuildList.remove(self.current)

    def buildAll(self):
        for obj in self.toBuildList:
            try: obj.buildRig()
            except:
                print(str(obj) + 'buildRig Fail')
                pass
        self.toBuildList = []

    def mirrorLoc(self):
        misc.mirrorLoc()

    '''Module'''

    def baseClick(self):
        id, side, startPos, = self.setBaseAttr()
        b = base.Base(prefix=self.prefix, side=side, id=id)
        self.baseIDEdit.setText('')
        self.current = b
        self.toBuildList.append(b)
        b.setLocAttr(startPos=startPos)
        b.buildGuide()

    def setBaseAttr(self):
        id = 'base_id'
        if self.baseIDEdit.text(): id = self.baseIDEdit.text()

        side = 'L'
        if self.baseRBtn.isChecked(): side = 'R'
        elif self.baseNABtn.isChecked(): side = 'NA'

        startPos = [0, 0, 0]
        if self.basePosXEdit.text() and self.basePosYEdit.text() and self.basePosZEdit.text():
            try: startPos = [float(self.basePosXEdit.text()), float(self.basePosYEdit.text()), float(self.basePosZEdit.text())]
            except: print('start position type error, using default base start position [0, 0, 0]')
        
        return id, side, startPos

    def fingerClick(self):
        id, side, type, startPos, interval, segment = self.setFingerAttr()
        f = finger.Finger(prefix=self.prefix, side=side, id=id, type=type)
        self.fingerIDEdit.setText('')
        self.current = f
        self.toBuildList.append(f)
        f.setLocAttr(startPos=startPos, interval=interval, segment=segment)
        f.buildGuide()

    def setFingerAttr(self):
        id = 'finger_id'
        if self.fingerIDEdit.text(): id = self.fingerIDEdit.text()

        side = 'L'
        if self.fingerRBtn.isChecked(): side = 'R'
        elif self.fingerNABtn.isChecked(): side = 'NA'

        type = 'Other'
        if self.fingerThumbBtn.isChecked(): type = 'Thumb'

        startPos = [0, 0, 0]
        if self.fingerPosXEdit.text() and self.fingerPosYEdit.text() and self.fingerPosZEdit.text():
            try: startPos = [float(self.fingerPosXEdit.text()), float(self.fingerPosYEdit.text()), float(self.fingerPosZEdit.text())]
            except: print('start position type error, using default finger start position [0, 0, 0]')

        interval = 0.5
        if self.fingerIntvEdit.text():
            try: interval = float(self.fingerIntvEdit.text())
            except: print('interval type error, using default finger interval value 0.5')

        segment = 4
        if self.fingerSgmtEdit.text():
            try: segment = int(self.fingerSgmtEdit.text())
            except: print('segment type error, using default finger segment value 4')

        return id, side, type, startPos, interval, segment

    def footClick(self):
        id, side, startPos, interval, height = self.setFootAttr()
        f = foot.Foot(prefix=self.prefix, side=side, id=id)
        self.footIDEdit.setText('')
        self.current = f
        self.toBuildList.append(f)
        f.setLocAttr(startPos=startPos, interval=interval, height=height)
        f.buildGuide()

    def setFootAttr(self):
        id = 'foot_id'
        if self.footIDEdit.text(): id = self.footIDEdit.text()

        side = 'L'
        if self.footRBtn.isChecked(): side = 'R'
        elif self.footNABtn.isChecked(): side = 'NA'

        startPos = [0, 0, 0]
        if self.footPosXEdit.text() and self.footPosYEdit.text() and self.footPosZEdit.text():
            try: startPos = [float(self.footPosXEdit.text()), float(self.footPosYEdit.text()), float(self.footPosZEdit.text())]
            except: print('start position type error, using default foot start position [0, 0, 0]')

        interval = 0.5
        if self.footIntvEdit.text():
            try: interval = float(self.footIntvEdit.text())
            except: print('interval type error, using default foot interval value 0.5')

        height = 0.4
        if self.footHghtEdit.text():
            try: height = float(self.footHghtEdit.text())
            except: print('segment type error, using default foot segment value 0.4')

        return id, side, startPos, interval, height

    def spineClick(self):
        id, side, startPos, length, segment = self.setSpineAttr()
        s = spline.Spline(prefix=self.prefix, side=side, id=id)
        self.spineIDEdit.setText('')
        self.current = s
        self.toBuildList.append(s)
        s.setLocAttr(startPos=startPos, length=length, segment=segment)
        s.buildGuide()

    def setSpineAttr(self):
        id = 'spine_id'
        if self.spineIDEdit.text(): id = self.spineIDEdit.text()

        side = 'NA'

        startPos = [0, 0, 0]
        if self.spinePosXEdit.text() and self.spinePosYEdit.text() and self.spinePosZEdit.text():
            try: startPos = [float(self.spinePosXEdit.text()), float(self.spinePosYEdit.text()), float(self.spinePosZEdit.text())]
            except: print('start position type error, using default spine start position [0, 0, 0]')

        length = 6.0
        if self.spineLgthEdit.text():
            try: length = float(self.spineLgthEdit.text())
            except: print('interval type error, using default spine interval value 6.0')

        segment = 6
        if self.spineSgmtEdit.text():
            try: segment = int(self.spineSgmtEdit.text())
            except: print('segment type error, using default spine segment value 6')

        return id, side, startPos, length, segment
    
    def limbClick(self):
        id, side, type, startPos, interval = self.setLimbAttr()
        l = limb.Limb(prefix=self.prefix, side=side, id=id, type=type)
        self.limbIDEdit.setText('')
        self.current = l
        self.toBuildList.append(l)
        l.setLocAttr(startPos=startPos, interval=interval)
        l.buildGuide()

    def setLimbAttr(self):
        id = 'limb_id'
        if self.limbIDEdit.text(): id = self.limbIDEdit.text()

        side = 'L'
        if self.limbRBtn.isChecked(): side = 'R'
        elif self.limbNABtn.isChecked(): side = 'NA'

        type = 'NA'
        if self.limbArmBtn.isChecked(): type = 'Arm'
        elif self.limbLegBtn.isChecked(): type = 'Leg'

        startPos = [0, 0, 0]
        if self.limbPosXEdit.text() and self.limbPosYEdit.text() and self.limbPosZEdit.text():
            try: startPos = [float(self.limbPosXEdit.text()), float(self.limbPosYEdit.text()), float(self.limbPosZEdit.text())]
            except: print('start position type error, using default limb start position [0, 0, 0]')

        interval = 2.0
        if self.limbIntvEdit.text():
            try: interval = float(self.limbIntvEdit.text())
            except: print('interval type error, using default limb interval value 2.0')

        return id, side, type, startPos, interval

    '''Template'''

    def bipedClick(self):
        id, side, startPos = self.setBipedAttr()
        b = biped.Biped(prefix=self.prefix, side=side, id=id)
        self.bipedIDEdit.setText('')
        self.current = b
        self.toBuildList.append(b)
        b.setLocAttr(startPos=startPos)
        b.buildGuide()

    def setBipedAttr(self):
        id = 'biped_id'
        if self.bipedIDEdit.text(): id = self.bipedIDEdit.text()

        side = 'NA'

        startPos = [0, 8.4, 0]
        if self.bipedPosXEdit.text() and self.bipedPosYEdit.text() and self.bipedPosZEdit.text():
            try: startPos = [float(self.bipedPosXEdit.text()), float(self.bipedPosYEdit.text()), float(self.bipedPosZEdit.text())]
            except: print('start position type error, using default biped start position [0, 0, 0]')

        return id, side, startPos

    def handClick(self):
        id, side, startPos, interval, distance = self.setHandAttr()
        h = hand.Hand(prefix=self.prefix, side=side, id=id)
        self.handIDEdit.setText('')
        self.current = h
        self.toBuildList.append(h)
        h.setLocAttr(startPos=startPos, interval=interval, distance=distance)
        h.buildGuide()

    def setHandAttr(self):
        id = 'hand_id'
        if self.handIDEdit.text(): id = self.handIDEdit.text()

        side = 'L'
        if self.handRBtn.isChecked(): side = 'R'
        elif self.handNABtn.isChecked(): side = 'NA'

        startPos = [0, 0, 0]
        if self.handPosXEdit.text() and self.handPosYEdit.text() and self.handPosZEdit.text():
            try: startPos = [float(self.handPosXEdit.text()), float(self.handPosYEdit.text()), float(self.handPosZEdit.text())]
            except: print('start position type error, using default hand start position [0, 0, 0]')

        interval = 0.5
        if self.handIntvEdit.text():
            try: interval = float(self.handIntvEdit.text())
            except: print('interval type error, using default hand interval value 0.5')

        distance = 2.0
        if self.handDistEdit.text():
            try: distance = float(self.handDistEdit.text())
            except: print('interval type error, using default hand interval value 2.0')

        return id, side, startPos, interval, distance

    def armClick(self):
        id, side, startPos, interval, distance, gap = self.setArmAttr()
        a = arm.Arm(prefix=self.prefix, side=side, id=id)
        self.armIDEdit.setText('')
        self.current = a
        self.toBuildList.append(a)
        a.setLocAttr(startPos=startPos, interval=interval, distance=distance, gap=gap)
        a.buildGuide()

    def setArmAttr(self):
        id = 'arm_id'
        if self.armIDEdit.text(): id = self.armIDEdit.text()

        side = 'L'
        if self.armRBtn.isChecked(): side = 'R'
        elif self.armNABtn.isChecked(): side = 'NA'

        startPos = [0, 0, 0]
        if self.armPosXEdit.text() and self.armPosYEdit.text() and self.armPosZEdit.text():
            try: startPos = [float(self.armPosXEdit.text()), float(self.armPosYEdit.text()), float(self.armPosZEdit.text())]
            except: print('start position type error, using default arm start position [0, 0, 0]')

        interval = 0.5
        if self.armIntvEdit.text():
            try: interval = float(self.armIntvEdit.text())
            except: print('interval type error, using default arm interval value 0.5')

        distance = 2.0
        if self.armDistEdit.text():
            try: distance = float(self.armDistEdit.text())
            except: print('interval type error, using default arm interval value 2.0')

        gap = 2.0
        if self.armGapEdit.text():
            try: gap = float(self.armGapEdit.text())
            except: print('interval type error, using default arm interval value 2.0')

        return id, side, startPos, interval, distance, gap
    
    def legClick(self):
        id, side, startPos, interval, distance, height = self.setLegAttr()
        l = leg.Leg(prefix=self.prefix, side=side, id=id)
        self.legIDEdit.setText('')
        self.current = l
        self.toBuildList.append(l)
        l.setLocAttr(startPos=startPos, interval=interval, distance=distance, height=height)
        l.buildGuide()

    def setLegAttr(self):
        id = 'leg_id'
        if self.legIDEdit.text(): id = self.legIDEdit.text()

        side = 'L'
        if self.legRBtn.isChecked(): side = 'R'
        elif self.legNABtn.isChecked(): side = 'NA'

        startPos = [0, 0, 0]
        if self.legPosXEdit.text() and self.legPosYEdit.text() and self.legPosZEdit.text():
            try: startPos = [float(self.legPosXEdit.text()), float(self.legPosYEdit.text()), float(self.legPosZEdit.text())]
            except: print('start position type error, using default leg start position [0, 0, 0]')

        interval = 0.5
        if self.legIntvEdit.text():
            try: interval = float(self.legIntvEdit.text())
            except: print('interval type error, using default leg interval value 0.5')

        distance = 2.0
        if self.legDistEdit.text():
            try: distance = float(self.legDistEdit.text())
            except: print('interval type error, using default leg interval value 2.0')

        height = 2.0
        if self.legHghtEdit.text():
            try: height = float(self.legHghtEdit.text())
            except: print('interval type error, using default leg interval value 2.0')

        return id, side, startPos, interval, distance, height

    def qspineClick(self):
        id, side, startPos, length, segment = self.setQSpineAttr()
        s = quadSpine.QuadSpine(prefix=self.prefix, side=side, id=id)
        self.qspineIDEdit.setText('')
        self.current = s
        self.toBuildList.append(s)
        s.setLocAttr(startPos=startPos, length=length, segment=segment)
        s.buildGuide()

    def setQSpineAttr(self):
        id = 'quadSpine_id'
        if self.qspineIDEdit.text(): id = self.qspineIDEdit.text()

        side = 'NA'

        startPos = [0, 0, 0]
        if self.qspinePosXEdit.text() and self.qspinePosYEdit.text() and self.qspinePosZEdit.text():
            try:
                startPos = [float(self.qspinePosXEdit.text()), float(self.qspinePosYEdit.text()), float(self.qspinePosZEdit.text())]
            except:
                print('start position type error, using default spine start position [0, 0, 0]')

        length = 6.0
        if self.qspineLgthEdit.text():
            try:
                length = float(self.qspineLgthEdit.text())
            except:
                print('interval type error, using default spine interval value 6.0')

        segment = 7
        if self.qspineSgmtEdit.text():
            try:
                segment = int(self.qspineSgmtEdit.text())
            except:
                print('segment type error, using default spine segment value 7')

        return id, side, startPos, length, segment

    def tailClick(self):
        id, side, startPos, length, segment = self.setTailAttr()
        t = tail.Tail(prefix=self.prefix, side=side, id=id)
        self.qspineIDEdit.setText('')
        self.current = t
        self.toBuildList.append(t)
        t.setLocAttr(startPos=startPos, length=length, segment=segment)
        t.buildGuide()

    def setTailAttr(self):
        id = 'tail_id'
        if self.tailIDEdit.text(): id = self.tailIDEdit.text()

        side = 'NA'

        startPos = [0, 0, 0]
        if self.tailPosXEdit.text() and self.tailPosYEdit.text() and self.tailPosZEdit.text():
            try:
                startPos = [float(self.tailPosXEdit.text()), float(self.tailPosYEdit.text()), float(self.tailPosZEdit.text())]
            except:
                print('start position type error, using default tail start position [0, 0, 0]')

        length = 4.0
        if self.tailLgthEdit.text():
            try:
                length = float(self.tailLgthEdit.text())
            except:
                print('interval type error, using default tail interval value 6.0')

        segment = 6
        if self.tailSgmtEdit.text():
            try:
                segment = int(self.tailSgmtEdit.text())
            except:
                print('segment type error, using default tail segment value 7')

        return id, side, startPos, length, segment

path = os.path.dirname(os.path.abspath(__file__)) + r'\ui'
os.chdir(path)
#currentDir = os.getcwd()
window = MyWindow()
window.show()