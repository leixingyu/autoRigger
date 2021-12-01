import os

from Qt import QtWidgets, QtGui, _loadUi

from . import constant
from .base import base
from .chain import chainFK
from .constant import RigComponents, RigType, Side


class RigItem(QtWidgets.QListWidgetItem):
    """
    A subclass of QListWidgetItem that contains the widgets correlates with
    the rig item and widget property
    """

    def __init__(self, name):
        super(RigItem, self).__init__()

        self.icon = '{}.png'.format(name)
        self.base_ui = None
        self.extra_ui = None

        self.setText(name)
        icon = QtGui.QIcon()
        path = os.path.join(constant.ICON_DIR, self.icon)
        icon.addFile(path)
        self.setIcon(icon)

        # property widget
        self.base_widget = None
        self.extra_widget = None

        # rig component object
        self._obj = None

    def init_base(self):
        pass

    def init_extra(self):
        pass

    def parse_extra(self):
        pass

    def parse_base(self):
        pass

    def build_guide(self, *args, **kwargs):
        pass

    def build_rig(self):
        pass


class BaseItem(RigItem):
    def __init__(self, name='base'):
        super(BaseItem, self).__init__(name)
        self.base_ui = 'base.ui'
        self.init_base()

    def build_guide(self, side, base_name):
        self._obj = base.Base(side, base_name)
        self._obj.build_guide()

    def init_base(self):
        """Override
        """
        self.base_widget = QtWidgets.QWidget()
        _loadUi(os.path.join(constant.UI_DIR, self.base_ui), self.base_widget)

        for side in Side:
            self.base_widget.ui_side_cbox.addItem(side.value)

    def parse_base(self):
        """Override
        """
        name = self.base_widget.ui_name_edit.text()
        side = self.base_widget.ui_side_cbox.currentText()
        return [name, side]


class ChainFKItem(BaseItem):
    def __init__(self, name='chain-fk'):
        super(ChainFKItem, self).__init__(name)
        self.extra_ui = 'chain.ui'
        self.extra_widget = QtWidgets.QWidget()
        _loadUi(os.path.join(constant.UI_DIR, self.extra_ui), self.extra_widget)

    def build_guide(self, *args, **kwargs):
        """Override"""
        self._obj = chainFK.ChainFK(*args, **kwargs)
        self._obj.build_guide()

    def init_extra(self):
        """Override"""
        pass

    def parse_extra(self):
        seg = self.widget.ui_seg_sbox.value()
        length = self.widget.ui_len_sbox.value()
        direction = self.widget.ui_dir_cbox.currentText()

        return [seg, length, direction]
