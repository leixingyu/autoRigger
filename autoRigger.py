#!/usr/bin/env python
""" AutoRigger provides procedural approach for maya rigging """

from utility.Qt import QtCore, QtGui, QtWidgets
from utility.Qt import _loadUi
from utility import other
import os
import warnings
import base
import finger
import foot
import spine
import limb
import hand
import arm
import leg
import biped
import tail
import quadruped

__author__ = "Xingyu Lei"
__maintainer__ = "Xingyu Lei"
__email__ = "wzaxzt@gmail.com"
__status__ = "development"

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
RIG_COMPONENTS = [
    'base',       # 0
    'finger',     # 1
    'hand',       # 2
    'limb',       # 3
    'arm',        # 4
    'foot',       # 5
    'leg',        # 6
    'head',       # 7
    'spine',      # 8
    'biped',      # 9
    'legfront',   # 10
    'legback',    # 11
    'spinequad',  # 12
    'tail',       # 13
    'quad',       # 14
]


class AutoRigger(QtWidgets.QDialog):
    """ This module is the class for the main dialog window """

    def __init__(self, parent=other.get_maya_main_window()):
        """ Initialize AutoRigger class with parent window

        :param parent: window instance
        """

        super(AutoRigger, self).__init__(parent)
        _loadUi(CURRENT_PATH + r'\ui\autoRigger.ui', self)

        self.setWindowFlags(QtCore.Qt.Window)

        # Reset list icon and item
        self.ui_icon_list = []
        self.ui_item_list = []

        # Connect signals and slots
        self.ui_tabWidget.currentChanged.connect(lambda: self.refresh_list())
        self.ui_listWidget.itemClicked.connect(lambda: self.element_clicked())
        self.ui_guideBtn.clicked.connect(lambda: self.create_guide())
        self.ui_buildBtn.clicked.connect(lambda: self.create_module())

        self.generate_icon()
        self.generate_item()

        self.toBuild = []

        # position could be numeric value
        int_only = QtGui.QIntValidator()
        self.ui_worldX.setValidator(int_only)
        self.ui_worldY.setValidator(int_only)
        self.ui_worldZ.setValidator(int_only)

        # Reset tab position and populate list
        self.ui_tabWidget.setCurrentIndex(0)
        self.refresh_list()

    def generate_icon(self):
        for _ in RIG_COMPONENTS:
            self.ui_icon_list.append(QtGui.QIcon())

        for index, icon in enumerate(self.ui_icon_list):
            icon.addFile(os.path.join(CURRENT_PATH + r'\ui', RIG_COMPONENTS[index] + '.png'))

    def generate_item(self):
        for _ in RIG_COMPONENTS:
            self.ui_item_list.append(QtWidgets.QListWidgetItem())

        for index, item in enumerate(self.ui_item_list):
            item.setText(RIG_COMPONENTS[index])
            item.setIcon(self.ui_icon_list[index])

    def refresh_list(self):
        self.clear_list(self.ui_listWidget)
        index = self.ui_tabWidget.currentIndex()

        # Biped
        if index == 0:
            items = map(self.ui_item_list.__getitem__, [9, 4, 6, 7, 8])

        # Quadruped
        elif index == 1:
            items = map(self.ui_item_list.__getitem__, [14, 10, 11, 12, 13])

        # Bird
        elif index == 2:
            items = []

        # Custom
        elif index == 3:
            items = map(self.ui_item_list.__getitem__,
                        [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13])

        else:
            print "list not created"
            return

        for item in items:
            self.ui_listWidget.addItem(item)

    def element_clicked(self):
        self.clear_field()
        item_name = self.ui_listWidget.currentItem().text()
        print item_name

        # TODO: change field based on item clicked

    def create_guide(self):
        # Fetch all field info

        # Base name
        if not self.ui_nameEdit.text(): 
            base_name = 'null'
        else: 
            base_name = self.ui_nameEdit.text()

        # Side
        side = ['L', 'R', 'M'][self.ui_sideCBox.currentIndex()]

        # Start Position
        pos = [0, 0, 0]
        if self.ui_worldX.text():
            pos[0] = int(self.ui_worldX.text())
        if self.ui_worldY.text():
            pos[1] = int(self.ui_worldY.text())
        if self.ui_worldZ.text():
            pos[2] = int(self.ui_worldZ.text())

        # Identify the item type and build it
        item_name = self.ui_listWidget.currentItem().text()

        # Biped
        if item_name == 'finger':
            obj = finger.Finger(side, base_name)
        elif item_name == 'hand':
            obj = hand.Hand(side, base_name, 5)
        elif item_name == 'limb':
            obj = limb.Limb(side, base_name)
        elif item_name == 'arm':
            obj = arm.Arm(side, base_name)
        elif item_name == 'foot':
            obj = foot.Foot(side, base_name)
        elif item_name == 'leg':
            obj = leg.Leg(side, base_name)
        elif item_name == 'spine':
            obj = spine.Spine(side, base_name)
        elif item_name == 'biped':
            obj = biped.Biped(side, base_name)

        # Quadruped
        elif item_name == 'legfront':
            obj = leg.LegFront(side, base_name)
        elif item_name == 'legback':
            obj = leg.LegBack(side, base_name)
        elif item_name == 'tail':
            obj = tail.Tail(side, base_name)
        elif item_name == 'spinequad':
            obj = spine.SpineQuad(side, base_name)
        elif item_name == 'quad':
            obj = quadruped.Quadruped(side, base_name)
        else:
            warnings.warn("object name not found, use base component instead")
            obj = base.Base(side, base_name)

        obj.set_locator_attr(pos)
        obj.build_guide()
        self.toBuild.append(obj)
        self.clear_field()

    def create_module(self):
        for item in self.toBuild:
            item.build_rig()
        self.toBuild = []

    def clear_list(self, widget):
        """ This clears all items in the list but not deleting them """

        while widget.takeItem(0):
            widget.takeItem(0)
        self.clear_field()

    def clear_field(self):
        self.ui_nameEdit.setText('')
        self.ui_sideCBox.setCurrentIndex(0)
        self.ui_worldX.setText('')
        self.ui_worldY.setText('')
        self.ui_worldZ.setText('')


def show():
    window = AutoRigger()
    window.show()
    return window
