from Qt import QtCore, QtGui, QtWidgets
from Qt import _loadUi
import maya.OpenMayaUI
import os
import math
from shiboken2 import wrapInstance
import util, base, finger, foot, spine, limb, hand, arm, leg, biped, backLeg, frontLeg, tail, quadSpine, quadruped

PATH = os.path.dirname(os.path.abspath(__file__))+r'\ui'

def getMayaMainWindow():
    main_window_ptr = maya.OpenMayaUI.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QMainWindow)

class AutoRigger(QtWidgets.QDialog):
    def __init__(self, parent=getMayaMainWindow()):
        super(AutoRigger, self).__init__(parent)
        _loadUi('new.ui', self)

        self.setWindowFlags(QtCore.Qt.Window)

        #--- Connect signals and slots ---#
        self.ui_tabWidget.currentChanged.connect(lambda:self.refreshList())
        self.ui_listWidget.itemClicked.connect(self.itemClicked)
        self.ui_guideBtn.clicked.connect(self.createGuide)
        self.ui_buildBtn.clicked.connect(self.createModule)

        self.generateIcon()
        self.generateItem()

        self.toBuild = []

        # position could be numeric value
        intOnly = QtGui.QIntValidator()
        self.ui_worldX.setValidator(intOnly)
        self.ui_worldY.setValidator(intOnly)
        self.ui_worldZ.setValidator(intOnly)

        #--- Reset tab position and populate list ---#
        self.ui_tabWidget.setCurrentIndex(0)
        self.refreshList()

    def generateIcon(self):
        self.ui_baseIcon = QtGui.QIcon()
        self.ui_baseIcon.addFile(os.path.join(PATH, 'base.png'))

        self.ui_fingerIcon = QtGui.QIcon()
        self.ui_fingerIcon.addFile(os.path.join(PATH, 'finger.png'))

        self.ui_handIcon = QtGui.QIcon()
        self.ui_handIcon.addFile(os.path.join(PATH, 'hand.png'))

        self.ui_limbIcon = QtGui.QIcon()
        self.ui_limbIcon.addFile(os.path.join(PATH, 'limb.png'))

        self.ui_armIcon = QtGui.QIcon()
        self.ui_armIcon.addFile(os.path.join(PATH, 'arm.png'))

        self.ui_footIcon = QtGui.QIcon()
        self.ui_footIcon.addFile(os.path.join(PATH, 'foot.png'))

        self.ui_legIcon = QtGui.QIcon()
        self.ui_legIcon.addFile(os.path.join(PATH, 'leg.png'))

        self.ui_headIcon = QtGui.QIcon()
        self.ui_headIcon.addFile(os.path.join(PATH, 'head.png'))

        self.ui_bipedIcon = QtGui.QIcon()
        self.ui_bipedIcon.addFile(os.path.join(PATH, 'body.png'))

        self.ui_spineIcon = QtGui.QIcon()
        self.ui_spineIcon.addFile(os.path.join(PATH, 'spine.png'))

    def generateItem(self):
        self.ui_base = QtWidgets.QListWidgetItem('base')
        self.ui_base.setIcon(self.ui_baseIcon)

        self.ui_finger = QtWidgets.QListWidgetItem('finger')
        self.ui_finger.setIcon(self.ui_fingerIcon)

        self.ui_hand = QtWidgets.QListWidgetItem('hand')
        self.ui_hand.setIcon(self.ui_handIcon)

        self.ui_limb = QtWidgets.QListWidgetItem('limb')
        self.ui_limb.setIcon(self.ui_limbIcon)

        self.ui_arm = QtWidgets.QListWidgetItem('arm')
        self.ui_arm.setIcon(self.ui_armIcon)

        self.ui_foot = QtWidgets.QListWidgetItem('foot')
        self.ui_foot.setIcon(self.ui_footIcon)

        self.ui_leg = QtWidgets.QListWidgetItem('leg')
        self.ui_leg.setIcon(self.ui_legIcon)

        self.ui_head = QtWidgets.QListWidgetItem('head')
        self.ui_head.setIcon(self.ui_headIcon)

        self.ui_biped = QtWidgets.QListWidgetItem('full-biped')
        self.ui_biped.setIcon(self.ui_bipedIcon)

        self.ui_spine = QtWidgets.QListWidgetItem('spine')
        self.ui_spine.setIcon(self.ui_spineIcon)

    def refreshList(self):
        self.clearList(self.ui_listWidget)
        index = self.ui_tabWidget.currentIndex()
        if index == 0: list = [self.ui_biped, self.ui_spine, self.ui_arm, self.ui_leg, self.ui_head]
        elif index == 1: list = []
        elif index == 2: list = []
        elif index == 3: list = [self.ui_base, self.ui_finger, self.ui_hand, self.ui_limb, self.ui_foot, self.ui_spine, self.ui_arm, self.ui_leg, self.ui_head]
        else:
            print "list not created"
            return

        for item in list: self.ui_listWidget.addItem(item)

    def itemClicked(self):
        self.clearField()
        itemName = self.ui_listWidget.currentItem().text()
        #--- Also set field lock ---#

        print itemName

    def createGuide(self):
        #--- Fetch all field info ---#
        if not self.ui_nameEdit.text(): id = 'null'
        else: id = self.ui_nameEdit.text()

        side = ['L', 'R', 'M'][self.ui_sideCBox.currentIndex()]

        pos = [0, 0, 0]
        if self.ui_worldX.text(): pos[0] = int(self.ui_worldX.text())
        if self.ui_worldY.text(): pos[1] = int(self.ui_worldY.text())
        if self.ui_worldZ.text(): pos[2] = int(self.ui_worldZ.text())

        #--- Identify the item type and build it ---#
        itemName = self.ui_listWidget.currentItem().text()
        if itemName == 'finger':        obj = finger.Finger(side, id)
        elif itemName == 'hand':        obj = hand.Hand(side, id, 5)
        elif itemName == 'limb':        obj = limb.Limb(side, id)
        elif itemName == 'arm':         obj = arm.Arm(side, id)
        elif itemName == 'foot':        obj = foot.Foot(side, id)
        elif itemName == 'leg':         obj = leg.Leg(side, id)
        elif itemName == 'spine':       obj = spine.Spine(side, id)
        elif itemName == 'full-biped':  obj = biped.Biped(side, id)
        else: obj = base.Base(side, id)

        obj.setLocAttr(pos)
        obj.buildGuide()
        self.toBuild.append(obj)
        self.clearField()
        #print id, side, pos

    def createModule(self):
        for item in self.toBuild:
            item.buildRig()

    def clearList(self, widget):
        """ This clears all items in the list but not deleting them """
        while widget.takeItem(0):
            widget.takeItem(0)
        self.clearField()

    def clearField(self):
        self.ui_nameEdit.setText('')
        self.ui_sideCBox.setCurrentIndex(0)
        self.ui_worldX.setText('')
        self.ui_worldY.setText('')
        self.ui_worldZ.setText('')

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
        self.quadrupedThumb.clicked.connect(self.quadrupedClick)
        self.frontLegThumb.clicked.connect(self.frontLegClick)
        self.backLegThumb.clicked.connect(self.backLegClick)
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
        util.mirrorLoc()

    '''Module'''

    def baseClick(self):
        id, side, startPos, = self.setBaseAttr()
        b = base.Base(side=side, id=id)
        self.baseIDEdit.setText('')
        self.current = b
        self.toBuildList.append(b)
        b.setLocAttr(startPos=startPos)
        b.buildGuide()

    def setBaseAttr(self):
        id = 'null'
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
        f = finger.Finger(side=side, id=id, type=type)
        self.fingerIDEdit.setText('')
        self.current = f
        self.toBuildList.append(f)
        f.setLocAttr(startPos=startPos, interval=interval, segment=segment)
        f.buildGuide()

    def setFingerAttr(self):
        id = 'null'
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
        f = foot.Foot(side=side, id=id)
        self.footIDEdit.setText('')
        self.current = f
        self.toBuildList.append(f)
        f.setLocAttr(startPos=startPos, interval=interval, height=height)
        f.buildGuide()

    def setFootAttr(self):
        id = 'null'
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
        s = spine.Spine(side=side, id=id)
        self.spineIDEdit.setText('')
        self.current = s
        self.toBuildList.append(s)
        s.setLocAttr(startPos=startPos, length=length, segment=segment)
        s.buildGuide()

    def setSpineAttr(self):
        id = 'null'
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
        l = limb.Limb(side=side, id=id, type=type)
        self.limbIDEdit.setText('')
        self.current = l
        self.toBuildList.append(l)
        l.setLocAttr(startPos=startPos, interval=interval)
        l.buildGuide()

    def setLimbAttr(self):
        id = 'null'
        if self.limbIDEdit.text(): id = self.limbIDEdit.text()

        side = 'L'
        if self.limbRBtn.isChecked(): side = 'R'
        elif self.limbNABtn.isChecked(): side = 'M'

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
        b = biped.Biped(side=side, id=id)
        self.bipedIDEdit.setText('')
        self.current = b
        self.toBuildList.append(b)
        b.setLocAttr(startPos=startPos)
        b.buildGuide()

    def setBipedAttr(self):
        id = 'null'
        if self.bipedIDEdit.text(): id = self.bipedIDEdit.text()

        side = 'NA'

        startPos = [0, 8.4, 0]
        if self.bipedPosXEdit.text() and self.bipedPosYEdit.text() and self.bipedPosZEdit.text():
            try: startPos = [float(self.bipedPosXEdit.text()), float(self.bipedPosYEdit.text()), float(self.bipedPosZEdit.text())]
            except: print('start position type error, using default biped start position [0, 0, 0]')

        return id, side, startPos

    def handClick(self):
        id, side, startPos, interval, distance = self.setHandAttr()
        h = hand.Hand(side=side, id=id)
        self.handIDEdit.setText('')
        self.current = h
        self.toBuildList.append(h)
        h.setLocAttr(startPos=startPos, interval=interval, distance=distance)
        h.buildGuide()

    def setHandAttr(self):
        id = 'null'
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
        a = arm.Arm(side=side, id=id)
        self.armIDEdit.setText('')
        self.current = a
        self.toBuildList.append(a)
        a.setLocAttr(startPos=startPos, interval=interval, distance=distance, gap=gap)
        a.buildGuide()

    def setArmAttr(self):
        id = 'null'
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
        l = leg.Leg(side=side, id=id)
        self.legIDEdit.setText('')
        self.current = l
        self.toBuildList.append(l)
        l.setLocAttr(startPos=startPos, interval=interval, distance=distance, height=height)
        l.buildGuide()

    def setLegAttr(self):
        id = 'null'
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

    '''Quadruped Module'''

    def quadrupedClick(self):
        id, side, startPos = self.setQuadrupedAttr()
        q = quadruped.Quadruped(side=side, id=id)
        self.quadrupedIDEdit.setText('')
        self.current = q
        self.toBuildList.append(q)
        q.setLocAttr(startPos=startPos)
        q.buildGuide()

    def setQuadrupedAttr(self):
        id = 'null'
        if self.quadrupedIDEdit.text(): id = self.quadrupedIDEdit.text()

        side = 'NA'

        startPos = [0, 0, 0]
        if self.quadrupedPosXEdit.text() and self.quadrupedPosYEdit.text() and self.quadrupedPosZEdit.text():
            try: startPos = [float(self.quadrupedPosXEdit.text()), float(self.quadrupedPosYEdit.text()), float(self.quadrupedPosZEdit.text())]
            except: print('start position type error, using default quadruped start position [0, 0, 0]')

        return id, side, startPos

    def frontLegClick(self):
        id, side, startPos, distance, height = self.setFrontLegAttr()
        l = frontLeg.FrontLeg(side=side, id=id)
        self.frontLegIDEdit.setText('')
        self.current = l
        self.toBuildList.append(l)
        l.setLocAttr(startPos=startPos, distance=distance, height=height)
        l.buildGuide()

    def setFrontLegAttr(self):
        id = 'null'
        if self.frontLegIDEdit.text(): id = self.frontLegIDEdit.text()

        side = 'L'
        if self.frontLegRBtn.isChecked(): side = 'R'
        elif self.frontLegNABtn.isChecked(): side = 'NA'
            
        distance = 1.5
        if self.frontLegDistEdit.text():
            try: distance = float(self.frontLegDistEdit.text())
            except: print('interval type error, using default frontLeg interval value 1.5')

        height = 0.2
        if self.frontLegHghtEdit.text():
            try: height = float(self.frontLegHghtEdit.text())
            except: print('interval type error, using default frontLeg interval value 0.2')

        startPos = [0, math.ceil(3*distance+height), 0]
        if self.frontLegPosXEdit.text() and self.frontLegPosYEdit.text() and self.frontLegPosZEdit.text():
            try: startPos = [float(self.frontLegPosXEdit.text()), float(self.frontLegPosYEdit.text()), float(self.frontLegPosZEdit.text())]
            except: print('start position type error, using default frontLeg start position [0, 0, 0]')


        return id, side, startPos, distance, height

    def backLegClick(self):
        id, side, startPos, distance, height = self.setBackLegAttr()
        l = backLeg.BackLeg(side=side, id=id)
        self.backLegIDEdit.setText('')
        self.current = l
        self.toBuildList.append(l)
        l.setLocAttr(startPos=startPos, distance=distance, height=height)
        l.buildGuide()

    def setBackLegAttr(self):
        id = 'null'
        if self.backLegIDEdit.text(): id = self.backLegIDEdit.text()

        side = 'L'
        if self.backLegRBtn.isChecked():
            side = 'R'
        elif self.backLegNABtn.isChecked():
            side = 'NA'

        startPos = [0, 0, 0]
        if self.backLegPosXEdit.text() and self.backLegPosYEdit.text() and self.backLegPosZEdit.text():
            try:
                startPos = [float(self.backLegPosXEdit.text()), float(self.backLegPosYEdit.text()), float(self.backLegPosZEdit.text())]
            except:
                print('start position type error, using default backLeg start position [0, 0, 0]')

        distance = 1.5
        if self.backLegDistEdit.text():
            try:
                distance = float(self.backLegDistEdit.text())
            except:
                print('interval type error, using default backLeg interval value 1.5')

        height = 0.2
        if self.backLegHghtEdit.text():
            try:
                height = float(self.backLegHghtEdit.text())
            except:
                print('interval type error, using default backLeg interval value 0.2')

        return id, side, startPos, distance, height

    def qspineClick(self):
        id, side, startPos, length, segment = self.setQSpineAttr()
        s = quadSpine.QuadSpine(side=side, id=id)
        self.qspineIDEdit.setText('')
        self.current = s
        self.toBuildList.append(s)
        s.setLocAttr(startPos=startPos, length=length, segment=segment)
        s.buildGuide()

    def setQSpineAttr(self):
        id = 'null'
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
        t = tail.Tail(side=side, id=id)
        self.qspineIDEdit.setText('')
        self.current = t
        self.toBuildList.append(t)
        t.setLocAttr(startPos=startPos, length=length, segment=segment)
        t.buildGuide()

    def setTailAttr(self):
        id = 'null'
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

def show():
    path = os.path.dirname(os.path.abspath(__file__)) + r'\ui'
    os.chdir(path)
    #currentDir = os.getcwd()
    window = MyWindow()
    window.show()
    return window

def showNew():
    os.chdir(PATH)
    #currentDir = os.getcwd()
    window = AutoRigger()
    window.show()
    return window
