"""
AutoRigger provides procedural approach for maya rigging
"""

import logging
import os

import maya.cmds as cmds
from Qt import QtCore, QtGui, QtWidgets
from Qt import _loadUi

from . import util, constant
from . import rigItem
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

TAB_RIG_MAPPING = {
    RigType.BIPED: [
        rigItem.BaseItem,
        rigItem.ChainFKItem
    ],

    RigType.CHAIN: [
        rigItem.ChainFKItem
    ]

}


class AutoRiggerWindow(QtWidgets.QMainWindow):
    """
    Main dialog window class
    """

    def __init__(self, parent=setup.get_maya_main_window()):
        """
        Initialization
        """
        super(AutoRiggerWindow, self).__init__(parent)
        _loadUi(os.path.join(constant.UI_DIR, 'autoRigger.ui'), self)

        self.setWindowFlags(QtCore.Qt.Window)

        self.to_build = list()

        self.item = None

        # reset tab position and populate list
        self.connect_signals()
        # self.refresh_items()

    def connect_signals(self):
        """
        Connect signals and slots
        """
        self.ui_tab_widget.currentChanged.connect(self.refresh_tab)
        self.ui_list_widget.currentItemChanged.connect(self.update_current)
        self.ui_guide_btn.clicked.connect(self.create_guide)
        self.ui_build_btn.clicked.connect(self.create_rig)
        self.ui_clear_btn.clicked.connect(self.empty_scene)

    def update_current(self, item):
        """

        :param item: QListWidgetItem. current selected item
        :return:
        """
        self.item = item
        self.initialize_field()

    def refresh_tab(self, index):
        """
        Clear and Re-generate Rig comp items in the list widget
        """

        while self.ui_list_widget.item(0):
            item = self.ui_list_widget.takeItem(0)
            del item

        comps = TAB_RIG_MAPPING[index]
        for func in comps:
            item = func()
            self.ui_list_widget.addItem(item)

    def initialize_field(self):
        """
        Change the field format after clicking item
        """
        for i in reversed(range(self.ui_custom_layout.count())):
            self.ui_custom_layout.itemAt(i).widget().setParent(None)

        self.ui_custom_layout.addWidget(self.item.base_widget)
        if self.item.extra_widget:
            self.ui_custom_layout.addWidget(self.item.extra_widget)

    def create_guide(self):
        """
        Fetch all field info and build the rig guide
        """
        args = self.item.parse_base()

        if self.item.extra_widget:
            ex_args = self.item.parse_extra()
            args = args.extend(ex_args)

        self.item.build_guide(*args)

        # self.to_build.append(obj)
        # self.reset_field()

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
