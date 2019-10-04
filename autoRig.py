from PySide2 import QtWidgets, QtCore, QtGui
import locator
reload(locator)
import joint
reload(joint)
import controller
reload(controller)
import constraint
reload(constraint)

class AutoRiggerWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(270, 460)
        MainWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 0, 251, 451))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(2)
        self.layout.setObjectName("layout")
        self.locatorLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.locatorLabel.setMinimumSize(QtCore.QSize(0, 25))
        self.locatorLabel.setMaximumSize(QtCore.QSize(16777215, 25))
        self.locatorLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.locatorLabel.setObjectName("locatorLabel")
        self.layout.addWidget(self.locatorLabel)
        self.spineLayout = QtWidgets.QHBoxLayout()
        self.spineLayout.setObjectName("spineLayout")
        self.spineLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.spineLabel.setMinimumSize(QtCore.QSize(60, 25))
        self.spineLabel.setMaximumSize(QtCore.QSize(16777215, 25))
        self.spineLabel.setObjectName("spineLabel")
        self.spineLayout.addWidget(self.spineLabel)
        self.spineSlider = QtWidgets.QSlider(self.verticalLayoutWidget)
        self.spineSlider.setMinimum(2)
        self.spineSlider.setMaximum(10)
        self.spineSlider.setSliderPosition(4)
        self.spineSlider.setOrientation(QtCore.Qt.Horizontal)
        self.spineSlider.setObjectName("spineSlider")
        self.spineLayout.addWidget(self.spineSlider)
        self.spineValueLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.spineValueLabel.setMinimumSize(QtCore.QSize(20, 0))
        self.spineValueLabel.setMaximumSize(QtCore.QSize(16777215, 25))
        self.spineValueLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spineValueLabel.setObjectName("spineValue")
        self.spineLayout.addWidget(self.spineValueLabel)
        self.layout.addLayout(self.spineLayout)
        self.sliderLayout = QtWidgets.QHBoxLayout()
        self.sliderLayout.setObjectName("sliderLayout")
        self.fingerLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.fingerLabel.setMinimumSize(QtCore.QSize(60, 25))
        self.fingerLabel.setMaximumSize(QtCore.QSize(16777215, 25))
        self.fingerLabel.setObjectName("fingerLabel")
        self.sliderLayout.addWidget(self.fingerLabel)
        self.fingerSlider = QtWidgets.QSlider(self.verticalLayoutWidget)
        self.fingerSlider.setMinimum(2)
        self.fingerSlider.setMaximum(5)
        self.fingerSlider.setSliderPosition(5)
        self.fingerSlider.setOrientation(QtCore.Qt.Horizontal)
        self.fingerSlider.setObjectName("fingerSlider")
        self.sliderLayout.addWidget(self.fingerSlider)
        self.fingerValueLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.fingerValueLabel.setMinimumSize(QtCore.QSize(20, 0))
        self.fingerValueLabel.setMaximumSize(QtCore.QSize(16777215, 25))
        self.fingerValueLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fingerValueLabel.setObjectName("fingerValue")
        self.sliderLayout.addWidget(self.fingerValueLabel)
        self.layout.addLayout(self.sliderLayout)
        self.createLocBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.createLocBtn.setObjectName("createLocBtn")
        self.layout.addWidget(self.createLocBtn)
        self.secLocBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.secLocBtn.setObjectName("secLocBtn")
        self.layout.addWidget(self.secLocBtn)
        self.mirrorLayout = QtWidgets.QHBoxLayout()
        self.mirrorLayout.setObjectName("mirrorLayout")
        self.mirrorLRBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.mirrorLRBtn.setMaximumSize(QtCore.QSize(16777215, 25))
        self.mirrorLRBtn.setObjectName("mirrorLR")
        self.mirrorLayout.addWidget(self.mirrorLRBtn)
        self.mirrorRLBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.mirrorRLBtn.setMaximumSize(QtCore.QSize(16777215, 25))
        self.mirrorRLBtn.setObjectName("mirrorRL")
        self.mirrorLayout.addWidget(self.mirrorRLBtn)
        self.layout.addLayout(self.mirrorLayout)
        self.deleteLocBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.deleteLocBtn.setObjectName("deleteLocBtn")
        self.layout.addWidget(self.deleteLocBtn)
        self.line = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.layout.addWidget(self.line)
        self.jointLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.jointLabel.setMinimumSize(QtCore.QSize(0, 25))
        self.jointLabel.setMaximumSize(QtCore.QSize(16777215, 25))
        self.jointLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.jointLabel.setObjectName("jointLabel")
        self.layout.addWidget(self.jointLabel)
        self.createJntBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.createJntBtn.setObjectName("createJntBtn")
        self.layout.addWidget(self.createJntBtn)
        self.createIKBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.createIKBtn.setObjectName("createIKBtn")
        self.layout.addWidget(self.createIKBtn)
        self.deleteJntBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.deleteJntBtn.setObjectName("deleteJntBtn")
        self.layout.addWidget(self.deleteJntBtn)
        self.line_2 = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.layout.addWidget(self.line_2)
        self.controllerLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.controllerLabel.setMinimumSize(QtCore.QSize(0, 25))
        self.controllerLabel.setMaximumSize(QtCore.QSize(16777215, 25))
        self.controllerLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.controllerLabel.setObjectName("controllerLabel")
        self.layout.addWidget(self.controllerLabel)
        self.createCtrlBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.createCtrlBtn.setObjectName("createCtrlBtn")
        self.layout.addWidget(self.createCtrlBtn)
        self.constraintBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.constraintBtn.setObjectName("constraintBtn")
        self.layout.addWidget(self.constraintBtn)
        self.line_3 = QtWidgets.QFrame(self.verticalLayoutWidget)
        self.line_3.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_3.setObjectName("line_3")
        self.layout.addWidget(self.line_3)
        self.skinLabel = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.skinLabel.setMinimumSize(QtCore.QSize(0, 25))
        self.skinLabel.setMaximumSize(QtCore.QSize(16777215, 25))
        self.skinLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.skinLabel.setObjectName("skinLabel")
        self.layout.addWidget(self.skinLabel)
        self.bindSkinBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.bindSkinBtn.setObjectName("bindSkinBtn")
        self.layout.addWidget(self.bindSkinBtn)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.linkFunc()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AutoRigger v1.0"))
        self.locatorLabel.setText(_translate("MainWindow", "---Joint Placement---"))
        self.spineLabel.setText(_translate("MainWindow", "Spine Num:"))
        self.spineValueLabel.setText(_translate("MainWindow", "4"))
        self.fingerLabel.setText(_translate("MainWindow", "Finger Num:"))
        self.fingerValueLabel.setText(_translate("MainWindow", "5"))
        self.createLocBtn.setText(_translate("MainWindow", "Create Locator"))
        self.secLocBtn.setText(_translate("MainWindow", "Secondary Locator"))
        self.mirrorLRBtn.setText(_translate("MainWindow", "Mirror L-> R"))
        self.mirrorRLBtn.setText(_translate("MainWindow", "Mirror R-> L"))
        self.deleteLocBtn.setText(_translate("MainWindow", "Delete Locator"))
        self.jointLabel.setText(_translate("MainWindow", "---Joint & IK---"))
        self.createJntBtn.setText(_translate("MainWindow", "Create Joint"))
        self.createIKBtn.setText(_translate("MainWindow", "Create IK"))
        self.deleteJntBtn.setText(_translate("MainWindow", "Delete Joint"))
        self.controllerLabel.setText(_translate("MainWindow", "---Controller---"))
        self.createCtrlBtn.setText(_translate("MainWindow", "Create Controller"))
        self.constraintBtn.setText(_translate("MainWindow", "Add Constraint"))
        self.skinLabel.setText(_translate("MainWindow", "---Skin---"))
        self.bindSkinBtn.setText(_translate("MainWindow", "Bind Skin"))

    def linkFunc(self):

        self.spineSlider.valueChanged.connect(self.sliderUpdate)
        self.fingerSlider.valueChanged.connect(self.sliderUpdate)

        self.createLocBtn.clicked.connect(self.createLoc)

        self.secLocBtn.clicked.connect(self.createSecLoc)

        self.mirrorLRBtn.clicked.connect(self.mirrorLR)
        self.mirrorRLBtn.clicked.connect(self.mirrorRL)

        self.deleteLocBtn.clicked.connect(self.deleteLoc)

        self.createJntBtn.clicked.connect(self.createJnt)

        self.createIKBtn.clicked.connect(self.createIK)

        self.deleteJntBtn.clicked.connect(self.deleteJnt)

        self.createCtrlBtn.clicked.connect(self.createCtrl)

        self.constraintBtn.clicked.connect(self.constraint)

        self.bindSkinBtn.clicked.connect(self.bindSkin)

    def sliderUpdate(self):
        spineValue = self.spineSlider.value()
        fingerValue = self.fingerSlider.value()

        self.spineValueLabel.setText(str(spineValue))
        self.fingerValueLabel.setText(str(fingerValue))

    def createLoc(self):
        self.spineValue = self.spineSlider.value()
        self.fingerValue = self.fingerSlider.value()

        locator.createLocators(self.spineValue, self.fingerValue)

    def createSecLoc(self):
        self.spineValue = self.spineSlider.value()
        locator.secondaryLocators(self.spineValue)

    def mirrorLR(self):
        locator.mirror('left')

    def mirrorRL(self):
        locator.mirror('right')

    def deleteLoc(self):
        locator.deleteLocators()

    def createJnt(self):
        self.spineValue = self.spineSlider.value()
        self.fingerValue = self.fingerSlider.value()
        joint.createJoints(self.fingerValue)
        joint.orientJoints()
        joint.IKFKLayer()

    def createIK(self):
        controller.createIK()

    def deleteJnt(self):
        joint.deleteJoints()

    def createCtrl(self):
        controller.createController(self.spineValue, self.fingerValue)
        self.deleteLoc()

    def constraint(self):
        constraint.buildConstraint(self.spineValue, self.fingerValue)

    def bindSkin(self):
        #constraint.bindSkin()
        constraint.deleteLayer()

    # Function Not In Use
    def lockMode(self):
        locator.lockAll(locator.lockMode)

MainWindow = QtWidgets.QMainWindow()
ui = AutoRiggerWindow()
ui.setupUi(MainWindow)
MainWindow.show()
