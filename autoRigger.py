"""
AutoRigger provides procedural approach for maya rigging
"""

import logging
import os

import maya.cmds as cmds
from Qt import QtCore, QtGui, QtWidgets
from Qt import _loadUi

from . import util
from .base import base
from .chain import finger, tail, chainFK, chainIK, chainEP, chainFKIK
from .chain.limb import limbFKIK
from .chain.limb.arm import arm
from .chain.limb.leg import leg, legBack, legFront
from .chain.spine import spine, spineQuad
from .constant import RigComponents, RigType, Side
from .module import foot, hand
from .template import biped, quadruped
from .utility.common import setup


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
UI_PATH = os.path.join('ui', 'autoRigger.ui')


class AutoRiggerWindow(QtWidgets.QMainWindow):
    """
    Main dialog window class
    """

    def __init__(self, parent=setup.get_maya_main_window()):
        """
        Initialize AutoRigger class
        """
        super(AutoRiggerWindow, self).__init__(parent)
        _loadUi(os.path.join(CURRENT_PATH, UI_PATH), self)

        self.setWindowFlags(QtCore.Qt.Window)

        # Reset list icon and item
        self.items = list()
        self.to_build = list()

        # Reset tab position and populate list
        self.connect_signals()
        self.connect_items()
        self.ui_tabWidget.setCurrentIndex(0)
        self.refresh_items()

        # position could be numeric value
        int_only = QtGui.QIntValidator()
        self.ui_worldX.setValidator(int_only)
        self.ui_worldY.setValidator(int_only)
        self.ui_worldZ.setValidator(int_only)

    def connect_signals(self):
        """
        Connect signals and slots
        """
        self.ui_tabWidget.currentChanged.connect(lambda: self.refresh_items())
        self.ui_listWidget.itemClicked.connect(lambda: self.initialize_field())
        self.ui_guideBtn.clicked.connect(lambda: self.create_guide())
        self.ui_buildBtn.clicked.connect(lambda: self.create_rig())
        self.ui_clearBtn.clicked.connect(lambda: self.empty_scene())

    def connect_items(self):
        """
        Connect Rig comp items with icon and text
        """
        for comp in RigComponents:
            icon = QtGui.QIcon()
            icon.addFile(os.path.join(CURRENT_PATH, 'ui', 'icon', comp.value+'.png'))

            item = QtWidgets.QListWidgetItem()
            item.setText(comp.value)
            item.setIcon(icon)
            self.items.append(item)

    def refresh_items(self):
        """
        Clear and Re-generate Rig comp items in the list widget
        """
        self.clear_items(self.ui_listWidget)
        comps = list()
        tab_index = self.ui_tabWidget.currentIndex()

        # Biped
        if tab_index == RigType.BIPED:
            comps = [
                RigComponents.BIPED,
                RigComponents.HEAD,
                RigComponents.ARM,
                RigComponents.SPINE,
                RigComponents.LEG
            ]

        # Quadruped
        elif tab_index == RigType.QUADRUPED:
            comps = [
                RigComponents.QUAD,
                RigComponents.LEG_BACK,
                RigComponents.LEG_FRONT,
                RigComponents.SPINE_QUAD,
                RigComponents.TAIL
            ]

        # Chain
        elif tab_index == RigType.CHAIN:
            comps = [
                RigComponents.CHAIN_FK,
                RigComponents.CHAIN_IK,
                RigComponents.CHAIN_EP,
                RigComponents.CHAIN_FKIK
            ]

        # Custom
        elif tab_index == RigType.CUSTOM:
            comps = RigComponents

        tab_items = [tab_item.value for tab_item in comps]
        items = [item for item in self.items if item.text() in tab_items]
        for item in items:
            self.ui_listWidget.addItem(item)

    def initialize_field(self):
        """
        Change the field format after clicking item
        """
        self.reset_field()
        item_name = self.ui_listWidget.currentItem().text()
        print(item_name)

        # TODO: change field based on item clicked

    def create_guide(self):
        """
        Fetch all field info and build the rig guide
        """
        # Base name
        base_name = self.ui_nameEdit.text() if self.ui_nameEdit.text() else 'null'

        # Side
        side = [Side.LEFT, Side.RIGHT, Side.MIDDLE][self.ui_sideCBox.currentIndex()]

        # Identify the item type and build it
        item = self.ui_listWidget.currentItem().text()
        if item == RigComponents.FINGER.value:
            obj = finger.Finger(side, base_name)
        elif item == RigComponents.HAND.value:
            obj = hand.Hand(side, base_name)
        elif item == RigComponents.LIMB.value:
            obj = limbFKIK.LimbFKIK(side, base_name, length=6)
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
            obj = legFront.LegFront(side, base_name)
        elif item == RigComponents.LEG_BACK.value:
            obj = legBack.LegBack(side, base_name)
        elif item == RigComponents.TAIL.value:
            obj = tail.Tail(side, base_name)
        elif item == RigComponents.SPINE_QUAD.value:
            obj = spineQuad.SpineQuad(side, base_name)
        elif item == RigComponents.QUAD.value:
            obj = quadruped.Quadruped(side, base_name)
        elif item == RigComponents.BASE.value:
            obj = base.Base(side, base_name)

        elif item == RigComponents.CHAIN_FK.value:
            obj = chainFK.ChainFK(side, base_name,
                                  segment=5, length=10, direction=[1, 0, 0])
        elif item == RigComponents.CHAIN_IK.value:
            obj = chainIK.ChainIK(side, base_name,
                                  segment=5, length=10, direction=[1, 0, 0])
        elif item == RigComponents.CHAIN_EP.value:
            obj = chainEP.ChainEP(side, base_name, segment=20, curve='curve1')
        elif item == RigComponents.CHAIN_FKIK.value:
            obj = chainFKIK.ChainFKIK(side, base_name,
                                      segment=5, length=10, direction=[1, 0, 0])
        else:
            logging.error("object name not found, using base comp instead")
            return

        # obj.set_locator_attr([pos_x, pos_y, pos_z])
        obj.build_guide()

        self.to_build.append(obj)
        self.reset_field()

    def create_rig(self):
        """
        Build the Rig based on the to_build list and guide
        """
        for item in self.to_build:
            item.build_rig()
        self.to_build = list()

    def clear_items(self, widget):
        """
        This clears all items in the list widget without deleting them
        
        :param widget: QListWidget
        """
        while widget.takeItem(0):
            widget.takeItem(0)
        self.reset_field()

    def reset_field(self):
        """
        Reset all field to default value
        """
        self.ui_nameEdit.setText('')
        self.ui_sideCBox.setCurrentIndex(0)
        self.ui_worldX.setText('')
        self.ui_worldY.setText('')
        self.ui_worldZ.setText('')

    def empty_scene(self):
        """
        Delete all master groups
        """
        self.to_build = list()
        for grp in [
            util.G_LOC_GRP,
            util.G_JNT_GRP,
            util.G_CTRL_GRP,
            util.G_MESH_GRP
        ]:
            try:
                cmds.delete(grp)
            except:
                pass


def show():
    window = AutoRiggerWindow()
    try:
        window.close()
    except:
        pass
    window.setAttribute(QtCore.Qt.WA_DeleteOnClose)
    window.show()
    return window
