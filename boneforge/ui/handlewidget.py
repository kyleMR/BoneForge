"""my.skeleton.boneforge.ui.handlewidget
"""

import os.path
from functools import partial
from PySide2 import QtGui, QtCore, QtWidgets

from .util import Orientation

HANDLE_RADIUS = 15

BASE_ROLE, HANDLE_ROLE, ADD_ROLE = range(3)

class HandleItem(QtWidgets.QGraphicsEllipseItem):

    def __init__(self, index, role=HANDLE_ROLE, parent=None):
        super(HandleItem, self).__init__(parent)
        self.handleWidget = parent
        self.setRect(
            QtCore.QRectF(0, 0, HANDLE_RADIUS * 2, HANDLE_RADIUS * 2))
        self.index = index
        self.role = role
        self.isDown = False

    def boundingRect(self):
        penWidth = 2
        extra = penWidth / 2.0
        return self.rect().adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        brush = painter.brush()
        brush.setStyle(QtCore.Qt.SolidPattern)
        if self.role == BASE_ROLE:
            brush.setColor(QtGui.QColor(60, 60, 60, 255))
            if self.isDown:
                brush.setColor(QtGui.QColor(40, 40, 40, 255))
        # elif self.role == HANDLE_ROLE:
        else:
            brush.setColor(QtGui.QColor(140, 140, 140, 255))
            if self.isDown:
                brush.setColor(QtGui.QColor(100, 100, 100, 255))
        # else:
        # brush.setColor(QtGui.QColor(80, 80, 80, 255))
        painter.setBrush(brush)
        pen = painter.pen()
        if self.role == ADD_ROLE:
            pen.setStyle(QtCore.Qt.DotLine)
        else:
            pen.setStyle(QtCore.Qt.SolidLine)
        pen.setWidth(2)
        pen.setColor(QtGui.QColor(0, 0, 0, 255))
        painter.setPen(pen)
        rect = self.rect()
        painter.drawEllipse(rect)
        pen.setWidth(4)
        pen.setStyle(QtCore.Qt.SolidLine)
        painter.setPen(pen)
        if self.role == ADD_ROLE:
            painter.drawLine(HANDLE_RADIUS*0.5, HANDLE_RADIUS, HANDLE_RADIUS*1.5, HANDLE_RADIUS)
            painter.drawLine(HANDLE_RADIUS, HANDLE_RADIUS*0.5, HANDLE_RADIUS, HANDLE_RADIUS*1.5)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        if self.role == ADD_ROLE:
            menu.addAction("I'm the button to press to add a handle")
        else:
            select = menu.addAction("Select Handle")
            insertBefore = menu.addAction("Insert Handle Before")
            insertAfter = menu.addAction("Insert Handle After")
            remove = menu.addAction("Remove Handle")
            select.triggered.connect(partial(self.handleWidget.selectHandle, self.index))
            insertBefore.triggered.connect(partial(self.handleWidget.insertHandle, self.index))
            insertAfter.triggered.connect(partial(self.handleWidget.insertHandle, self.index + 1))
            remove.triggered.connect(partial(self.handleWidget.removeHandle, self.index))
        a = menu.exec_(event.screenPos())
        event.accept()

    def center(self):
        return self.pos() + self.boundingRect().center()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.isDown = True
            self.update()
            event.accept()

    def mouseReleaseEvent(self, event):    
        if event.button() == QtCore.Qt.LeftButton:
            self.isDown = False
            self.update()
            if self.boundingRect().contains(event.pos()):
                self.handleWidget.handleClicked(self)



class HandleWidget(QtWidgets.QGraphicsRectItem):

    spacing = 5

    def __init__(self, orientation, parent=None):
        super(HandleWidget, self).__init__(parent)
        self.node = parent
        self.handles = []
        self._orientation = orientation

    def handleItemCount(self):
        return len(self.handles)

    def setHandleCount(self, count):
        for handle in self.handles:
            self.scene().removeItem(handle)
        self.handles[:] = []

        i = 0
        for i in xrange(count):
            role = BASE_ROLE if i == 0 else HANDLE_ROLE
            self.handles.append(HandleItem(i, role, self))
        self.handles.append(HandleItem(i+1, ADD_ROLE, self))
        self._layoutHandles()

    def _layoutHandles(self):
        marker = 0
        if self.orientation == Orientation.right:
            for handle in self.handles:
                handle.setPos(marker, 0)
                marker += HANDLE_RADIUS * 2 + self.spacing
        elif self.orientation == Orientation.down:
            for handle in self.handles:
                handle.setPos(0, marker)
                marker += HANDLE_RADIUS * 2 + self.spacing
        elif self.orientation == Orientation.left:
            for handle in reversed(self.handles):
                handle.setPos(marker, 0)
                marker += HANDLE_RADIUS * 2 + self.spacing
        elif self.orientation == Orientation.up:
            for handle in reversed(self.handles):
                handle.setPos(0, marker)
                marker += HANDLE_RADIUS * 2 + self.spacing
        self.prepareGeometryChange()
        self.adjustRect()

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        self._orientation = orientation
        self._layoutHandles()

    def adjustRect(self):
        handleSize = HANDLE_RADIUS * 2
        shortDimension = handleSize
        longDimension = (self.handleItemCount() * handleSize
                         + self.spacing * (self.handleItemCount() - 1))
        if self.orientation == Orientation.up or self.orientation == Orientation.down:
            rect = QtCore.QRectF(0, 0, shortDimension, longDimension)
        else:
            rect = QtCore.QRectF(0, 0, longDimension, shortDimension)
        self.setRect(rect)

    def boundingRect(self):
        return self.rect()

    def paint(self, painter, option, widget):
        # NO OP
        pass

    def handleItemPosition(self, index):
        handle = self.handles[index]
        return self.mapToParent(handle.center())

    def handleClicked(self, handle):
        if handle.role == ADD_ROLE:
            self.node.addHandle()

    def removeHandle(self, index):
        self.node.removeHandle(index)

    def insertHandle(self, index):
        self.node.insertHandle(index)

    def selectHandle(self, index):
        self.node.selectHandle(index)