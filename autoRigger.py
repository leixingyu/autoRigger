#!/usr/bin/env python
""" AutoRigger provides procedural approach for maya rigging """

from enum import Enum, IntEnum, unique
import os
import warnings
from utility.Qt import QtCore, QtGui, QtWidgets
from utility.Qt import _loadUi
from utility import setup
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


@unique
class RigComponents(Enum):
    BASE = 'base'
    FINGER = 'finger'
    HAND = 'hand'
    LIMB = 'limb'
    ARM = 'arm'
    FOOT = 'foot'
    LEG = 'leg'
    HEAD = 'head'
    SPINE = 'spine'
    BIPED = 'biped'
    LEG_FRONT = 'legfront'
    LEG_BACK = 'legback'
    SPINE_QUAD = 'spinequad'
    TAIL = 'tail'
    QUAD = 'quad'


@unique
class RigType(IntEnum):
    BIPED = 0
    QUADRUPED = 1
    BIRD = 2
    CUSTOM = 3


class AutoRigger(QtWidgets.QDialog):
    """ This module is the class for the main dialog """

    def __init__(self, parent=setup.get_maya_main_window()):
        """ Initialize AutoRigger class with parent window

        :param parent: window instance
        """

        super(AutoRigger, self).__init__(parent)
        _loadUi(CURRENT_PATH + r'\ui\autoRigger.ui', self)

        self.setWindowFlags(QtCore.Qt.Window)

        # Reset list icon and item
        self.items = []
        self.to_build = []

        # Connect signals and slots
        self.ui_tabWidget.currentChanged.connect(lambda: self.refresh_items())
        self.ui_listWidget.itemClicked.connect(lambda: self.initialize_field())
        self.ui_guideBtn.clicked.connect(lambda: self.create_guide())
        self.ui_buildBtn.clicked.connect(lambda: self.create_rig())

        # Reset tab position and populate list
        self.connect_items()
        self.ui_tabWidget.setCurrentIndex(0)
        self.refresh_items()

        # position could be numeric value
        int_only = QtGui.QIntValidator()
        self.ui_worldX.setValidator(int_only)
        self.ui_worldY.setValidator(int_only)
        self.ui_worldZ.setValidator(int_only)

    def connect_items(self):
        """ Connect Rig component items with icon and text """
        
        for component in RigComponents:
            icon = QtGui.QIcon()
            icon.addFile(os.path.join(CURRENT_PATH + r'\ui', component.value + '.png'))

            item = QtWidgets.QListWidgetItem()
            item.setText(component.value)
            item.setIcon(icon)
            self.items.append(item)

    def refresh_items(self):
        """ Clear and Re-generate Rig component items in the list widget """
        
        self.clear_items(self.ui_listWidget)
        components = []
        tab_index = self.ui_tabWidget.currentIndex()

        # Biped
        if tab_index == RigType.BIPED:
            components = [RigComponents.BIPED, RigComponents.HEAD,
                          RigComponents.ARM, RigComponents.SPINE,
                          RigComponents.LEG]

        # Quadruped
        elif tab_index == RigType.QUADRUPED:
            components = [RigComponents.QUAD, RigComponents.LEG_BACK,
                          RigComponents.LEG_FRONT, RigComponents.SPINE_QUAD,
                          RigComponents.TAIL]

        # Bird
        elif tab_index == RigType.BIRD:
            pass

        # Custom
        elif tab_index == RigType.CUSTOM:
            components = RigComponents

        tab_items = [tab_item.value for tab_item in components]
        items = [item for item in self.items if item.text() in tab_items]
        for item in items:
            self.ui_listWidget.addItem(item)

    def initialize_field(self):
        """ Change the field format after clicking item """
        
        self.reset_field()
        item_name = self.ui_listWidget.currentItem().text()
        print item_name

        # TODO: change field based on item clicked

    def create_guide(self):
        """ Fetch all field info and build the rig guide """
        
        # Base name
        base_name = self.ui_nameEdit.text() if self.ui_nameEdit.text() else 'null'

        # Side
        side = ['L', 'R', 'M'][self.ui_sideCBox.currentIndex()]

        # Start Position
        pos_x = int(self.ui_worldX.text()) if self.ui_worldX.text() else 0
        pos_y = int(self.ui_worldY.text()) if self.ui_worldZ.text() else 0
        pos_z = int(self.ui_worldY.text()) if self.ui_worldZ.text() else 0

        # Identify the item type and build it
        item = self.ui_listWidget.currentItem().text()
        if item == RigComponents.FINGER.value:
            obj = finger.Finger(side, base_name)
        elif item == RigComponents.HAND.value:
            obj = hand.Hand(side, base_name, 5)
        elif item == RigComponents.LIMB.value:
            obj = limb.Limb(side, base_name)
        elif item == RigComponents.ARM.value:
            obj = arm.Arm(side, base_name)
        elif item == RigComponents.FOOT.value:
            obj = foot.Foot(side, base_name)
        elif item == RigComponents.LEG.value:
            obj = leg.Leg(side, base_name)
        elif item == RigComponents.SPINE.value:
            obj = spine.Spine(side, base_name)
        elif item == RigComponents.BIPED.value:
            obj = biped.Biped(side, base_name)
        elif item == RigComponents.LEG_FRONT.value:
            obj = leg.LegFront(side, base_name)
        elif item == RigComponents.LEG_BACK.value:
            obj = leg.LegBack(side, base_name)
        elif item == RigComponents.TAIL.value:
            obj = tail.Tail(side, base_name)
        elif item == RigComponents.SPINE_QUAD.value:
            obj = spine.SpineQuad(side, base_name)
        elif item == RigComponents.QUAD.value:
            obj = quadruped.Quadruped(side, base_name)
        else:
            warnings.warn("object name not found, using base component instead")
            obj = base.Base(side, base_name)
        obj.set_locator_attr([pos_x, pos_y, pos_z])
        obj.build_guide()
        self.to_build.append(obj)
        self.reset_field()

    def create_rig(self):
        """ Build the Rig based on the to_build list and guide """
        
        for item in self.to_build:
            item.build_rig()
        self.to_build = []

    def clear_items(self, widget):
        """ This clears all items in the list widget without deleting them 
        
        :param widget: QListWidget
        """

        while widget.takeItem(0):
            widget.takeItem(0)
        self.reset_field()

    def reset_field(self):
        """ Reset all field to default value """
        
        self.ui_nameEdit.setText('')
        self.ui_sideCBox.setCurrentIndex(0)
        self.ui_worldX.setText('')
        self.ui_worldY.setText('')
        self.ui_worldZ.setText('')


def show():
    window = AutoRigger()
    window.show()
    return window
