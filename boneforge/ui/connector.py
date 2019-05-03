"""my.skeleton.boneforge.ui.connector
"""

from PySide2 import QtGui, QtCore, QtWidgets

from .util import Orientation

class Connector(QtWidgets.QGraphicsPathItem):

    def __init__(self, outputPlugs, inputPlug):
        super(Connector, self).__init__(parent=None)
        self.outputItems = outputPlugs
        self.inputItem = inputPlug
        self.outputNode = outputPlugs[0].node
        self.inputNode = inputPlug.node
        self.outputNodeID = self.outputNode.forgeID
        self.inputNodeID = self.inputNode.forgeID
        self._activeOutputItem = None
        self.inputItem.connections.append(self)
        self.updatePath()
        self.setFlag(self.ItemIsSelectable)
        self.setFlag(self.ItemStacksBehindParent)

    def setActiveOutputItem(self, item):
        if self._activeOutputItem is not None:
            self._activeOutputItem.connections.remove(self)
            self._activeOutputItem = None
        if item is not None:
            self._activeOutputItem = item
            self._activeOutputItem.connections.append(self)
        self.outputNode.setAuxPlugVisibility()

    def updatePath(self):
        end = self.inputItem.plugPos()
        endItem = self.inputItem
        minDistance = float("inf")
        start = None
        startItem = None
        self.setActiveOutputItem(None)
        for plug in self.outputItems:
            pos = plug.scenePos()
            dist = (end - pos).manhattanLength()
            if dist < minDistance:
                minDistance = dist
                start = pos
                startItem = plug
        self.setActiveOutputItem(startItem)
        c1Direction = startItem.orientation
        c2Direction = endItem.orientation.opposite()
        vector = end - start
        bezierLengthFactor = .75
        bezierMinLength = 50
        if c1Direction == Orientation.up:
            c1Distance = max(abs(vector.y()) * bezierLengthFactor, bezierMinLength)
            c1 = QtCore.QPointF(start.x(), start.y() - c1Distance)
        elif c1Direction == Orientation.down:
            c1Distance = max(abs(vector.y()) * bezierLengthFactor, bezierMinLength)
            c1 = QtCore.QPointF(start.x(), start.y() + c1Distance)
        elif c1Direction == Orientation.right:
            c1Distance = max(abs(vector.x()) * bezierLengthFactor, bezierMinLength)
            c1 = QtCore.QPointF(start.x() + c1Distance, start.y())
        else:
            c1Distance = max(abs(vector.x()) * bezierLengthFactor, bezierMinLength)
            c1 = QtCore.QPointF(start.x() - c1Distance, start.y())

        if c2Direction == Orientation.up:
            c2Distance = max(abs(vector.y()) * bezierLengthFactor, bezierMinLength)
            c2 = QtCore.QPointF(end.x(), end.y() - c2Distance)
        elif c2Direction == Orientation.down:
            c2Distance = max(abs(vector.y()) * bezierLengthFactor, bezierMinLength)
            c2 = QtCore.QPointF(end.x(), end.y() + c2Distance)
        elif c2Direction == Orientation.right:
            c2Distance = max(abs(vector.x()) * bezierLengthFactor, bezierMinLength)
            c2 = QtCore.QPointF(end.x() + c2Distance, end.y())
        else:
            c2Distance = max(abs(vector.x()) * bezierLengthFactor, bezierMinLength)
            c2 = QtCore.QPointF(end.x() - c2Distance, end.y())

        path = QtGui.QPainterPath(start)
        path.cubicTo(c1, c2, end)
        self.prepareGeometryChange()
        self.setPath(path)

    def mousePressEvent(self, event):
        print "Connection: {} >> {}".format(self.outputItems[0].name, self.inputItem.name)
        super(Connector, self).mousePressEvent(event)

    def paint(self, painter, option, widget):
        pen = painter.pen()
        pen.setWidth(3)
        if self.isSelected():
            pen.setColor(QtGui.QColor(40, 240, 180, 255))
        else:
            pen.setColor(QtGui.QColor(140, 140, 140, 255))
        painter.setPen(pen)
        painter.drawPath(self.path())

    def shape(self):
        stroke = QtGui.QPainterPathStroker()
        stroke.setWidth(12)
        return stroke.createStroke(self.path())

    def prepareToRemove(self):
        self.setActiveOutputItem(None)
        self.inputItem.connections.remove(self)


class ConnectionIndicator(QtWidgets.QGraphicsLineItem):

    def __init__(self, startPlugs, initialPos):
        super(ConnectionIndicator, self).__init__(parent=None)
        self.startPlugs = startPlugs
        self.setZValue(-1)
        self.updateLine(initialPos)

    def updateLine(self, end):
        minDistance = float("inf")
        startPos = None
        for plug in self.startPlugs:
            pos = plug.scenePos()
            dist = (end - pos).manhattanLength()
            if dist < minDistance:
                minDistance = dist
                startPos = pos
        line = QtCore.QLineF(startPos, end)
        self.prepareGeometryChange()
        self.setLine(line)

    def paint(self, painter, option, widget):
        pen = painter.pen()
        pen.setStyle(QtCore.Qt.DotLine)
        pen.setColor(QtGui.QColor(140, 140, 140, 255))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(self.line())
