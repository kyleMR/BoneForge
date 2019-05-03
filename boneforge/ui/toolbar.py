"""my.skeleton.boneforge.ui.toolbar
"""
from functools import partial
from PySide2 import QtGui, QtCore, QtWidgets

import boneforge.core as bfcore

class ForgeToolbar(QtWidgets.QWidget):

    ToolbarHeight = 75
    addGuide = QtCore.Signal(object)
    buildSkeleton = QtCore.Signal()

    def __init__(self, parent=None):
        super(ForgeToolbar, self).__init__(parent)

        layout = QtWidgets.QHBoxLayout()
        guideBox = QtWidgets.QGroupBox("Guides")
        guideBoxLayout = QtWidgets.QHBoxLayout()
        self.spineGuideBtn = QtWidgets.QPushButton("Spine")
        self.limbGuideBtn = QtWidgets.QPushButton("Limb")
        self.blockGuideBtn = QtWidgets.QPushButton("Block")
        guideBoxLayout.addWidget(self.spineGuideBtn)
        guideBoxLayout.addWidget(self.limbGuideBtn)
        guideBoxLayout.addWidget(self.blockGuideBtn)
        guideBoxLayout.setContentsMargins(4, 4, 4, 4)
        guideBox.setLayout(guideBoxLayout)

        actionFrame = QtWidgets.QFrame()
        actionLayout = QtWidgets.QGridLayout()
        self.mirrorBtn = QtWidgets.QPushButton("Mirror")
        self.duplicateBtn = QtWidgets.QPushButton("Duplicate")
        self.buildSkeletonBtn = QtWidgets.QPushButton("Build Skeleton")
        actionLayout.addWidget(self.mirrorBtn, 0, 0)
        actionLayout.addWidget(self.duplicateBtn, 1, 0)
        actionLayout.addWidget(self.buildSkeletonBtn, 0, 1, 2, 1)
        actionFrame.setLayout(actionLayout)

        layout.addWidget(guideBox)
        layout.addWidget(actionFrame)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.setFixedHeight(self.ToolbarHeight)

        self._initConnections()

        self.mirrorBtn.setEnabled(False)
        self.duplicateBtn.setEnabled(False)

    def _initConnections(self):
        self.spineGuideBtn.clicked.connect(partial(self.addGuide.emit, bfcore.GuideSpine))
        self.limbGuideBtn.clicked.connect(partial(self.addGuide.emit, bfcore.GuideLimb))
        self.blockGuideBtn.clicked.connect(partial(self.addGuide.emit, bfcore.GuideBlock))
        self.buildSkeletonBtn.clicked.connect(self.buildSkeleton)
