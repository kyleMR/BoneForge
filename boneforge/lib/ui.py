"""my.lib.ui
Maya UI framework and utilities.
"""

from PySide2 import QtGui, QtCore, QtWidgets
import shiboken2

import maya.OpenMayaUI as OpenMayaUI

class MayaToolWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        parent = kwargs.pop("parent", mayaMainWindow())
        super(MayaToolWindow, self).__init__(parent=parent, **kwargs)

def mayaMainWindow():
    """Returns the main Maya window as a QtGui.QMainWindow instance."""
    ptr = OpenMayaUI.MQtUtil.mainWindow()
    if ptr is not None:
        return wrapinstance(long(ptr))

def wrapinstance(ptr, base=None):
    """Convert a pointer to Qt Class instance.
    
    Default base class is QObject.
    """
    if ptr is None:
        return None
    ptr = long(ptr)
    if base is None:
        qObj = shiboken2.wrapInstance(ptr, QtCore.QObject)
        metaObj = qObj.metaObject()
        cls = metaObj.className()
        superCls = metaObj.superClass().className()
        if hasattr(QtWidgets, cls):
            base = getattr(QtWidgets, cls)
        elif hasattr(QtWidgets, superCls):
            base = getattr(QtWidgets, superCls)
        else:
            base = QtWidgets.QWidget
    return shiboken2.wrapInstance(ptr, base)