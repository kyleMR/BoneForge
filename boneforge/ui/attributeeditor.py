"""my.skeleton.boneforge.ui.attributeeditor
"""

from PySide2 import QtGui, QtCore, QtWidgets

class ForgeAttributeEditor(QtWidgets.QFrame):

    def __init__(self, mainWidget, parent=None):
        super(ForgeAttributeEditor, self).__init__(parent)
        self.mainWidget = mainWidget