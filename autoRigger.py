from Qt import QtCore, QtGui, QtWidgets
from Qt import _loadUi
import maya.OpenMayaUI
import os
import warnings
from shiboken2 import wrapInstance
import base, finger, foot, spine, limb, hand, arm, leg, biped, tail, quadSpine, quadruped

PATH = os.path.dirname(os.path.abspath(__file__))+r'\ui'
COMPONENTS = [
    'base',     #  0
    'finger',   #  1
    'hand',     #  2
    'limb',     #  3
    'arm',      #  4
    'foot',     #  5
    'leg',      #  6
    'head',     #  7
    'spine',    #  8
    'biped',    #  9
    'legfront', #  10
    'legback',  #  11
    'spinequad',#  12
    'tail',     #  13
    'quad',     #  14
]

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
        self.ui_iconList = []
        for component in COMPONENTS:
            self.ui_iconList.append(QtGui.QIcon())

        for index, icon in enumerate(self.ui_iconList):
            icon.addFile(os.path.join(PATH, COMPONENTS[index]+'.png'))

    def generateItem(self):
        self.ui_itemList = []
        for component in COMPONENTS:
            self.ui_itemList.append(QtWidgets.QListWidgetItem())

        for index, item in enumerate(self.ui_itemList):
            item.setText(COMPONENTS[index])
            item.setIcon(self.ui_iconList[index])

    def refreshList(self):
        self.clearList(self.ui_listWidget)
        index = self.ui_tabWidget.currentIndex()
        ### Biped ###
        if index == 0:   list = map(self.ui_itemList.__getitem__, [9, 4, 6, 7, 8])
        ### Quadruped ###
        elif index == 1: list = map(self.ui_itemList.__getitem__, [14, 10, 11, 12, 13])
        ### Bird ###
        elif index == 2: list = []
        ### Custom ###
        elif index == 3: list = map(self.ui_itemList.__getitem__, [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13])
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
        ### Biped ###
        if itemName == 'finger':        obj = finger.Finger(side, id)
        elif itemName == 'hand':        obj = hand.Hand(side, id, 5)
        elif itemName == 'limb':        obj = limb.Limb(side, id)
        elif itemName == 'arm':         obj = arm.Arm(side, id)
        elif itemName == 'foot':        obj = foot.Foot(side, id)
        elif itemName == 'leg':         obj = leg.Leg(side, id)
        elif itemName == 'spine':       obj = spine.Spine(side, id)
        elif itemName == 'biped':       obj = biped.Biped(side, id)

        ### Quadruped ###
        elif itemName == 'legfront':   obj = leg.LegFront(side, id)
        elif itemName == 'legback':    obj = leg.LegBack(side, id)
        elif itemName == 'tail':       obj = tail.Tail(side, id)
        elif itemName == 'spinequad':  obj = spine.SpineQuad(side, id)
        elif itemName == 'quad' :      obj = quadruped.Quadruped(side, id)

        else:
            warnings.warn("object name not found, use base component instead")
            obj = base.Base(side, id)

        obj.setLocAttr(pos)
        obj.buildGuide()
        self.toBuild.append(obj)
        self.clearField()
        #print id, side, pos

    def createModule(self):
        for item in self.toBuild:
            item.buildRig()
        self.toBuild = []

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

def show():
    os.chdir(PATH)
    #currentDir = os.getcwd()
    window = AutoRigger()
    window.show()
    return window
