"""my.skeleton.boneforge.ui.main
"""

from PySide2 import QtGui, QtCore, QtWidgets
import lib.ui

from . import attributeeditor
from . import connector
from . import datamodel
from . import handlewidget
from . import nodeitem
from . import nodescene
from . import nodeview
from . import toolbar

class BoneForgeTool(lib.ui.MayaToolWindow):

    DefaultSize = (680, 580)

    def __init__(self):
        super(BoneForgeTool, self).__init__()
        self.setWindowTitle("BoneForge")

        self.bfWidget = BoneForgeWidget()
        self.setCentralWidget(self.bfWidget)

    def sizeHint(self):
        return QtCore.QSize(*self.DefaultSize)

    @classmethod
    def run(cls):
        window = cls()
        window.show()
        return window

class BoneForgeWidget(QtWidgets.QWidget):

    DefaultSplit = (420, 200)

    def __init__(self, parent=None):
        super(BoneForgeWidget, self).__init__(parent)
        verticalLayout = QtWidgets.QVBoxLayout()
        self.toolbar = toolbar.ForgeToolbar()

        self.editorSplitter = QtWidgets.QSplitter()
        self.nodeView = nodeview.ForgeNodeView(self)
        self.nodeScene = nodescene.ForgeNodeScene(self)
        self.nodeView.setScene(self.nodeScene)
        self.attributeEditor = attributeeditor.ForgeAttributeEditor(self)
        self.editorSplitter.addWidget(self.nodeView)
        self.editorSplitter.addWidget(self.attributeEditor)
        self.editorSplitter.setSizes(self.DefaultSplit)

        self.model = datamodel.GuideDataModel()

        verticalLayout.addWidget(self.toolbar)
        verticalLayout.addWidget(self.editorSplitter)

        self.setLayout(verticalLayout)

        self._initConnections()
        self.nodeScene.rebuildFromData()

    def _initConnections(self):
        self.toolbar.addGuide.connect(self.addGuideToScene)
        self.toolbar.buildSkeleton.connect(self.nodeScene.buildSkeleton)
        self.model.guidesAdded.connect(self.nodeScene.addGuideNodes)
        self.model.guidesRemoved.connect(self.nodeScene.removeGuideNodes)
        self.model.guidesUpdated.connect(self.nodeScene.updateGuideNodeData)
        self.model.connectionsUpdated.connect(self.nodeScene.updateConnections)
        self.model.guideDataUpdated.connect(self.nodeScene.rebuildFromData)

    def addGuideToScene(self, guideClass):
        self.model.addGuide(guideClass)