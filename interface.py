from PySide2 import QtCore, QtGui, QtWidgets
import maya.cmds as cmds
from urllib2 import urlopen

import locator
reload(locator)
import joint
reload(joint)
import controller
reload(controller)
import constraint
reload(constraint)

import face
reload(face)

class AutoRiggerUI(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(276, 490)
        MainWindow.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 281, 491))
        self.tabWidget.setObjectName("tabWidget")
        self.bodyTab = QtWidgets.QWidget()
        self.bodyTab.setObjectName("bodyTab")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.bodyTab)
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
        self.spineValue = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.spineValue.setMinimumSize(QtCore.QSize(20, 0))
        self.spineValue.setMaximumSize(QtCore.QSize(16777215, 25))
        self.spineValue.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.spineValue.setObjectName("spineValue")
        self.spineLayout.addWidget(self.spineValue)
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
        self.fingerValue = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.fingerValue.setMinimumSize(QtCore.QSize(20, 0))
        self.fingerValue.setMaximumSize(QtCore.QSize(16777215, 25))
        self.fingerValue.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.fingerValue.setObjectName("fingerValue")
        self.sliderLayout.addWidget(self.fingerValue)
        self.layout.addLayout(self.sliderLayout)
        self.createLocBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.createLocBtn.setObjectName("createLocBtn")
        self.layout.addWidget(self.createLocBtn)
        self.secLocBtn = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.secLocBtn.setObjectName("secLocBtn")
        self.layout.addWidget(self.secLocBtn)
        self.mirrorLayout = QtWidgets.QHBoxLayout()
        self.mirrorLayout.setObjectName("mirrorLayout")
        self.mirrorLR = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.mirrorLR.setMaximumSize(QtCore.QSize(16777215, 25))
        self.mirrorLR.setObjectName("mirrorLR")
        self.mirrorLayout.addWidget(self.mirrorLR)
        self.mirrorRL = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.mirrorRL.setMaximumSize(QtCore.QSize(16777215, 25))
        self.mirrorRL.setObjectName("mirrorRL")
        self.mirrorLayout.addWidget(self.mirrorRL)
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
        self.tabWidget.addTab(self.bodyTab, "")

        self.faceTab = QtWidgets.QWidget()
        self.faceTab.setObjectName("faceTab")
        self.widget = QtWidgets.QWidget(self.faceTab)
        self.widget.setGeometry(QtCore.QRect(10, 13, 251, 271))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.locatorLabel_2 = QtWidgets.QLabel(self.widget)
        self.locatorLabel_2.setMinimumSize(QtCore.QSize(0, 25))
        self.locatorLabel_2.setMaximumSize(QtCore.QSize(16777215, 25))
        self.locatorLabel_2.setAlignment(QtCore.Qt.AlignCenter)
        self.locatorLabel_2.setObjectName("locatorLabel_2")
        self.verticalLayout.addWidget(self.locatorLabel_2)
        self.createFaceLocBtn = QtWidgets.QPushButton(self.widget)
        self.createFaceLocBtn.setObjectName("createFaceLocBtn")
        self.verticalLayout.addWidget(self.createFaceLocBtn)
        self.mirrorLayout_3 = QtWidgets.QHBoxLayout()
        self.mirrorLayout_3.setObjectName("mirrorLayout_3")
        self.mirrorFaceLR = QtWidgets.QPushButton(self.widget)
        self.mirrorFaceLR.setMaximumSize(QtCore.QSize(16777215, 25))
        self.mirrorFaceLR.setObjectName("mirrorFaceLR")
        self.mirrorLayout_3.addWidget(self.mirrorFaceLR)
        self.mirrorFaceRL = QtWidgets.QPushButton(self.widget)
        self.mirrorFaceRL.setMaximumSize(QtCore.QSize(16777215, 25))
        self.mirrorFaceRL.setObjectName("mirrorFaceRL")
        self.mirrorLayout_3.addWidget(self.mirrorFaceRL)
        self.verticalLayout.addLayout(self.mirrorLayout_3)
        self.deleteFaceLocBtn = QtWidgets.QPushButton(self.widget)
        self.deleteFaceLocBtn.setObjectName("deleteFaceLocBtn")
        self.verticalLayout.addWidget(self.deleteFaceLocBtn)
        self.jointLabel_2 = QtWidgets.QLabel(self.widget)
        self.jointLabel_2.setMinimumSize(QtCore.QSize(0, 25))
        self.jointLabel_2.setMaximumSize(QtCore.QSize(16777215, 25))
        self.jointLabel_2.setAlignment(QtCore.Qt.AlignCenter)
        self.jointLabel_2.setObjectName("jointLabel_2")
        self.verticalLayout.addWidget(self.jointLabel_2)
        self.createFaceJntBtn = QtWidgets.QPushButton(self.widget)
        self.createFaceJntBtn.setObjectName("createFaceJntBtn")
        self.verticalLayout.addWidget(self.createFaceJntBtn)
        self.deleteFaceJntBtn = QtWidgets.QPushButton(self.widget)
        self.deleteFaceJntBtn.setObjectName("deleteFaceJntBtn")
        self.verticalLayout.addWidget(self.deleteFaceJntBtn)
        self.connectBtn = QtWidgets.QPushButton(self.widget)
        self.connectBtn.setObjectName("connectBtn")
        self.verticalLayout.addWidget(self.connectBtn)
        self.bindFaceBtn = QtWidgets.QPushButton(self.widget)
        self.bindFaceBtn.setObjectName("bindFaceBtn")
        self.verticalLayout.addWidget(self.bindFaceBtn)
        self.tabWidget.addTab(self.faceTab, "")

        self.bodyPicTab = QtWidgets.QWidget()

        self.facePicTab = QtWidgets.QWidget()


        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        self.tabWidget.setCurrentIndex(0)

        self.linkFunc()
        self.disableBtn()
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "AutoRigger v1.3"))
        self.locatorLabel.setText(_translate("MainWindow", "---Joint Placement---"))
        self.spineLabel.setText(_translate("MainWindow", "Spine Num:"))
        self.spineValue.setText(_translate("MainWindow", "10"))
        self.fingerLabel.setText(_translate("MainWindow", "Finger Num:"))
        self.fingerValue.setText(_translate("MainWindow", "10"))
        self.createLocBtn.setText(_translate("MainWindow", "Create Locator"))
        self.secLocBtn.setText(_translate("MainWindow", "Secondary Locator"))
        self.mirrorLR.setText(_translate("MainWindow", "Mirror L-> R"))
        self.mirrorRL.setText(_translate("MainWindow", "Mirror R-> L"))
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
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.bodyTab), _translate("MainWindow", "Body"))
        self.locatorLabel_2.setText(_translate("MainWindow", "---Joint Placement---"))
        self.createFaceLocBtn.setText(_translate("MainWindow", "Create Locator"))
        self.mirrorFaceLR.setText(_translate("MainWindow", "Mirror L-> R"))
        self.mirrorFaceRL.setText(_translate("MainWindow", "Mirror R-> L"))
        self.deleteFaceLocBtn.setText(_translate("MainWindow", "Delete Locator"))
        self.jointLabel_2.setText(_translate("MainWindow", "---Joint & IK---"))
        self.createFaceJntBtn.setText(_translate("MainWindow", "Create Joint"))
        self.deleteFaceJntBtn.setText(_translate("MainWindow", "Delete Joint"))
        self.connectBtn.setText(_translate("MainWindow", "Connect Joints"))
        self.bindFaceBtn.setText(_translate("MainWindow", "Bind Skin"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.faceTab), _translate("MainWindow", "Face"))

    def disableBtn(self):
        self.secLocBtn.setEnabled(False)
        self.mirrorLR.setEnabled(False)
        self.mirrorRL.setEnabled(False)
        self.deleteLocBtn.setEnabled(False)
        self.createJntBtn.setEnabled(False)
        self.createIKBtn.setEnabled(False)
        self.deleteJntBtn.setEnabled(False)
        self.createCtrlBtn.setEnabled(False)
        self.constraintBtn.setEnabled(False)
        #self.bindSkinBtn.setEnabled(False)

        self.deleteFaceLocBtn.setEnabled(False)
        self.mirrorFaceLR.setEnabled(False)
        self.mirrorFaceRL.setEnabled(False)
        self.createFaceJntBtn.setEnabled(False)
        self.deleteFaceJntBtn.setEnabled(False)
        self.connectBtn.setEnabled(False)
        #self.bindFaceBtn.setEnabled(False)

    def addBodyPickerTab(self):
        url = 'https://upload.wikimedia.org/wikipedia/en/0/0e/Outline-body.png'
        data = urlopen(url).read()

        image = QtGui.QImage()
        image.loadFromData(data)

        self.bodyPicTab.setObjectName("bodyPicTab")
        self.label = QtWidgets.QLabel(self.bodyPicTab)
        self.label.setGeometry(QtCore.QRect(10, 10, 251, 441))
        self.label.setText("")

        bodyPic = QtGui.QPixmap(image)
        self.label.setPixmap(bodyPic)
        self.label.setScaledContents(True)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.tabWidget.addTab(self.bodyPicTab, "Body Picker")

    def addFacePickerTab(self):
        url = 'https://s3.amazonaws.com/peoplepng/wp-content/uploads/2018/08/30090003/Face-PNG-Download-Image.png'
        data = urlopen(url).read()

        image = QtGui.QImage()
        image.loadFromData(data)
        facePic = QtGui.QPixmap(image)

        self.facePicTab = QtWidgets.QWidget()
        self.facePicTab.setObjectName("facePicTab")
        self.picHolder = QtWidgets.QLabel(self.facePicTab)
        self.picHolder.setGeometry(QtCore.QRect(10, 10, 251, 311))
        self.picHolder.setPixmap(facePic)
        self.picHolder.setScaledContents(True)
        self.picHolder.setAlignment(QtCore.Qt.AlignCenter)
        self.picHolder.setObjectName("picHolder")
        self.Jaw = QtWidgets.QPushButton(self.facePicTab)
        self.Jaw.setGeometry(QtCore.QRect(130, 280, 16, 16))
        self.Jaw.setObjectName("Jaw")
        self.RCorner = QtWidgets.QPushButton(self.facePicTab)
        self.RCorner.setGeometry(QtCore.QRect(80, 220, 16, 16))
        self.RCorner.setObjectName("RCorner")
        self.LCorner = QtWidgets.QPushButton(self.facePicTab)
        self.LCorner.setGeometry(QtCore.QRect(180, 220, 16, 16))
        self.LCorner.setObjectName("LCorner")
        self.UpLip = QtWidgets.QPushButton(self.facePicTab)
        self.UpLip.setGeometry(QtCore.QRect(125, 210, 25, 12))
        self.UpLip.setObjectName("UpLip")
        self.LowLip = QtWidgets.QPushButton(self.facePicTab)
        self.LowLip.setGeometry(QtCore.QRect(125, 252, 25, 12))
        self.LowLip.setObjectName("LowLip")
        self.LCheek = QtWidgets.QPushButton(self.facePicTab)
        self.LCheek.setGeometry(QtCore.QRect(190, 170, 16, 16))
        self.LCheek.setObjectName("LCheek")
        self.RCheek = QtWidgets.QPushButton(self.facePicTab)
        self.RCheek.setGeometry(QtCore.QRect(70, 170, 16, 16))
        self.RCheek.setObjectName("RCheek")
        self.LBrow = QtWidgets.QPushButton(self.facePicTab)
        self.LBrow.setGeometry(QtCore.QRect(160, 100, 25, 12))
        self.LBrow.setObjectName("LBrow")
        self.RBrow = QtWidgets.QPushButton(self.facePicTab)
        self.RBrow.setGeometry(QtCore.QRect(90, 100, 25, 12))
        self.RBrow.setObjectName("RBrow")
        self.LLowLid = QtWidgets.QPushButton(self.facePicTab)
        self.LLowLid.setGeometry(QtCore.QRect(168, 148, 18, 10))
        self.LLowLid.setObjectName("LLowLid")
        self.LUpLid = QtWidgets.QPushButton(self.facePicTab)
        self.LUpLid.setGeometry(QtCore.QRect(168, 125, 18, 10))
        self.LUpLid.setObjectName("LUpLid")
        self.RUpLid = QtWidgets.QPushButton(self.facePicTab)
        self.RUpLid.setGeometry(QtCore.QRect(86, 127, 18, 10))
        self.RUpLid.setObjectName("RUpLid")
        self.RLowLid = QtWidgets.QPushButton(self.facePicTab)
        self.RLowLid.setGeometry(QtCore.QRect(86, 149, 18, 10))
        self.RLowLid.setObjectName("RLowLid")

        # set center button to be yellow
        self.Jaw.setStyleSheet("background-color: yellow")
        self.LowLip.setStyleSheet("background-color: yellow")
        self.UpLip.setStyleSheet("background-color: yellow")

        # set left button to be blue
        self.LCheek.setStyleSheet("background-color: blue")
        self.LBrow.setStyleSheet("background-color: blue")
        self.LCorner.setStyleSheet("background-color: blue")
        self.LLowLid.setStyleSheet("background-color: blue")
        self.LUpLid.setStyleSheet("background-color: blue")

        # set right button to be red
        self.RCheek.setStyleSheet("background-color: red")
        self.RBrow.setStyleSheet("background-color: red")
        self.RCorner.setStyleSheet("background-color: red")
        self.RLowLid.setStyleSheet("background-color: red")
        self.RUpLid.setStyleSheet("background-color: red")

        self.tabWidget.addTab(self.facePicTab, "Face Picker")

        self.linkFacePickerFunc()

    def linkFunc(self):
        # add Tabs after binding skin
        self.bindSkinBtn.clicked.connect(self.addBodyPickerTab)
        self.bindFaceBtn.clicked.connect(self.addFacePickerTab)

        #face function
        self.createFaceLocBtn.clicked.connect(self.addFaceLocFunc)
        self.mirrorFaceLR.clicked.connect(self.mirrorFaceLRFunc)
        self.deleteFaceLocBtn.clicked.connect(self.delFaceLocFunc)
        self.createFaceJntBtn.clicked.connect(self.addFaceJntFunc)
        self.deleteFaceJntBtn.clicked.connect(self.delFaceJntFunc)
        self.connectBtn.clicked.connect(self.connectFunc)

        #body function
        self.spineSlider.valueChanged.connect(self.sliderUpdate)
        self.fingerSlider.valueChanged.connect(self.sliderUpdate)

        self.createLocBtn.clicked.connect(self.createLoc)

        self.secLocBtn.clicked.connect(self.createSecLoc)

        self.mirrorLR.clicked.connect(self.mirrorLRFunc)
        self.mirrorRL.clicked.connect(self.mirrorRLFunc)

        self.deleteLocBtn.clicked.connect(self.deleteLoc)

        self.createJntBtn.clicked.connect(self.createJnt)

        self.createIKBtn.clicked.connect(self.createIK)

        self.deleteJntBtn.clicked.connect(self.deleteJnt)

        self.createCtrlBtn.clicked.connect(self.createCtrl)

        self.constraintBtn.clicked.connect(self.constraint)

        self.bindSkinBtn.clicked.connect(self.bindSkin)

    def linkFacePickerFunc(self):
        #face picker function
        # set center button to be yellow
        self.Jaw.clicked.connect(lambda: self.linkCtrl(1))
        self.LowLip.clicked.connect(lambda: self.linkCtrl(2))
        self.UpLip.clicked.connect(lambda: self.linkCtrl(3))

        # set left button to be blue
        self.LCheek.clicked.connect(lambda: self.linkCtrl(4))
        self.LBrow.clicked.connect(lambda: self.linkCtrl(5))
        self.LCorner.clicked.connect(lambda: self.linkCtrl(6))
        self.LLowLid.clicked.connect(lambda: self.linkCtrl(7))
        self.LUpLid.clicked.connect(lambda: self.linkCtrl(8))

        # set right button to be red
        self.RCheek.clicked.connect(lambda: self.linkCtrl(9))
        self.RBrow.clicked.connect(lambda: self.linkCtrl(10))
        self.RCorner.clicked.connect(lambda: self.linkCtrl(11))
        self.RLowLid.clicked.connect(lambda: self.linkCtrl(12))
        self.RUpLid.clicked.connect(lambda: self.linkCtrl(13))

    def addFaceLocFunc(self):
        self.mirrorFaceLR.setEnabled(True)
        self.deleteFaceLocBtn.setEnabled(True)
        self.createFaceJntBtn.setEnabled(True)
        face.Locators()

    def mirrorFaceLRFunc(self):
        face.Mirror()

    def delFaceLocFunc(self):
        self.mirrorFaceLR.setEnabled(False)
        self.deleteFaceLocBtn.setEnabled(False)
        self.createFaceJntBtn.setEnabled(False)
        face.DeleteLoc()

    def addFaceJntFunc(self):
        self.deleteFaceJntBtn.setEnabled(True)
        self.connectBtn.setEnabled(True)
        face.FaceJoint()

    def delFaceJntFunc(self):
        self.createFaceJntBtn.setEnabled(False)
        self.deleteFaceJntBtn.setEnabled(False)

    def connectFunc(self):
        face.ConnectWBody()

    '''Following are body functions'''

    def sliderUpdate(self):
        spineValue = self.spineSlider.value()
        fingerValue = self.fingerSlider.value()

        self.spineLabel.setText(str(spineValue))
        self.fingerLabel.setText(str(fingerValue))

    def createLoc(self):
        self.deleteLocBtn.setEnabled(True)
        self.mirrorLR.setEnabled(True)
        self.mirrorRL.setEnabled(True)
        self.secLocBtn.setEnabled(True)

        self.spineValue = self.spineSlider.value()
        self.fingerValue = self.fingerSlider.value()

        locator.createLocators(self.spineValue, self.fingerValue)

    def createSecLoc(self):
        self.createJntBtn.setEnabled(True)

        self.spineValue = self.spineSlider.value()
        locator.secondaryLocators(self.spineValue)

    def mirrorLRFunc(self):
        locator.mirror('left')

    def mirrorRLFunc(self):
        locator.mirror('right')

    def deleteLoc(self):
        self.secLocBtn.setEnabled(False)
        self.mirrorLR.setEnabled(False)
        self.mirrorRL.setEnabled(False)
        self.deleteLocBtn.setEnabled(False)
        self.createJntBtn.setEnabled(False)
        locator.deleteLocators()

    def createJnt(self):
        self.createIKBtn.setEnabled(True)
        self.deleteJntBtn.setEnabled(True)
        self.spineValue = self.spineSlider.value()
        self.fingerValue = self.fingerSlider.value()
        joint.createJoints(self.fingerValue)
        joint.orientJoints()
        joint.IKFKLayer()

    def createIK(self):
        self.createCtrlBtn.setEnabled(True)
        controller.createIK()

    def deleteJnt(self):
        self.createCtrlBtn.setEnabled(False)
        self.createIKBtn.setEnabled(False)
        self.deleteJntBtn.setEnabled(False)
        joint.deleteJoints()

    def createCtrl(self):
        self.constraintBtn.setEnabled(True)
        controller.createController(self.spineValue, self.fingerValue)
        self.deleteLoc()
        self.createIKBtn.setEnabled(False)
        self.deleteJntBtn.setEnabled(False)

    def constraint(self):
        constraint.buildConstraint(self.spineValue, self.fingerValue)
        self.bindSkinBtn.setEnabled(True)

    def bindSkin(self):
        #constraint.bindSkin()
        constraint.deleteLayer()

    '''Following are face picker functions'''

    def linkCtrl(self, value):
        if value is 1:
            cmds.select('Ctrl_Face_Jaw')
        elif value is 2:
            lips = cmds.ls('Ctrl_Face_*_LowerLip_*')
            cmds.select(lips)
        elif value is 3:
            lips = cmds.ls('Ctrl_Face_*_UpperLip_*')
            cmds.select(lips)
        elif value is 4:
            cmds.select('Ctrl_Face_L_SecondCheek')
        elif value is 5:
            lBrow = cmds.ls('Ctrl_Face_L_EyeBrow_*')
            cmds.select(lBrow)
        elif value is 6:
            cmds.select('Ctrl_Face_L_MouthCorner')
        elif value is 7:
            lLowLid = cmds.ls('Ctrl_Face_L_LowerEyeLid_*')
            cmds.select(lLowLid)
        elif value is 8:
            lUpLid = cmds.ls('Ctrl_Face_L_UpperEyeLid_*')
            cmds.select(lUpLid)
        elif value is 9:
            cmds.select('Ctrl_Face_R_SecondCheek')
        elif value is 10:
            rBrow = cmds.ls('Ctrl_Face_R_EyeBrow_*')
            cmds.select(rBrow)
        elif value is 11:
            cmds.select('Ctrl_Face_R_MouthCorner')
        elif value is 12:
            rLowLid = cmds.ls('Ctrl_Face_R_LowerEyeLid_*')
            cmds.select(rLowLid)
        elif value is 13:
            rUpLid = cmds.ls('Ctrl_Face_R_UpperEyeLid_*')
            cmds.select(rUpLid)


MainWindow = QtWidgets.QMainWindow()
ui = AutoRiggerUI()
ui.setupUi(MainWindow)
MainWindow.show()

