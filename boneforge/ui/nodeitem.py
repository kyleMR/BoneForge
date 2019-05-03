"""my.skeleton.boneforge.ui.nodeitem
"""

import os.path
from PySide2 import QtGui, QtCore, QtWidgets

from .util import Orientation
from . import handlewidget

RESOURCE_FOLDER = "G:\\dcc\\resources\\img"
GUIDE_ICONS = {
    "GuideSpine": os.path.join(RESOURCE_FOLDER, "spine.png"),
    "GuideLimb": os.path.join(RESOURCE_FOLDER, "limb.png"),
    "GuideBlock": os.path.join(RESOURCE_FOLDER, "block.png"),
}
ROTATE_ICON = os.path.join(RESOURCE_FOLDER, "rotate_clockwise.png")

class GuideNodeItem(QtWidgets.QGraphicsRectItem):

    def __init__(self, forgeID, dataModel):
        super(GuideNodeItem, self).__init__(parent=None)
        self.forgeID = forgeID
        self.model = dataModel
        self._guideIcon = QtGui.QPixmap(GUIDE_ICONS[self.guideClass])
        self._rotateIcon = QtGui.QPixmap(ROTATE_ICON)

        self.xRadius = 8
        self.yRadius = 8
        self.setRect(QtCore.QRectF(0, 0, 200, 80))
        self._orientation = Orientation.right
        self.handleWidget = handlewidget.HandleWidget(self._orientation, self)
        self.inputPlug = ConnectionPlugItem(ConnectionPlugItem.Input, self._orientation, self)
        self.outputPlug = ConnectionPlugItem(ConnectionPlugItem.Output, self._orientation, self)
        self.auxOutputPlugs = []
        self.setFlags()

        self.iconSize = 16
        self.titleBarHeight = 20
        self.minWidth = 100

        self.updateHandleWidget()

        self._pressPos = None

    def setFlags(self):
        self.setFlag(self.ItemIsMovable, enabled=True)
        self.setFlag(self.ItemIsSelectable, enabled=True)
        self.setFlag(self.ItemSendsGeometryChanges, enabled=True)

    def boundingRect(self):
        penWidth = 5
        extra = penWidth / 2.0
        return self.rect().adjusted(-extra, -extra, extra, extra)

    @property
    def guideData(self):
        return self.model.guideData(self.forgeID)

    @property
    def name(self):
        return self.guideData["name"]

    @property
    def guideClass(self):
        return self.guideData["class"]

    @property
    def handleCount(self):
        return self.guideData["handleCount"]

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        self._orientation = orientation
        self.handleWidget.orientation = orientation
        self.inputPlug.orientation = orientation
        self.outputPlug.orientation = orientation
        self.adjustRect()
        self.updateConnectionPaths()

    def updateHandleWidget(self):
        count = self.handleCount
        self.handleWidget.setHandleCount(count)
        self.adjustRect()
        self.updateAuxOutputPlugList(count)

    def adjustRect(self):
        self.prepareGeometryChange()
        handleRect = self.handleWidget.boundingRect()
        width = max(handleRect.width() + handlewidget.HANDLE_RADIUS*2, self.minWidth)
        height = self.titleBarHeight + handleRect.height() + handlewidget.HANDLE_RADIUS*2
        rect = QtCore.QRectF(0, 0, width, height)
        self.setRect(rect)
        self.handleWidget.setPos(rect.center().x() - handleRect.width()*0.5, rect.top() + self.titleBarHeight + handlewidget.HANDLE_RADIUS)
        self.placeConnectionPlugs()

    def placeConnectionPlugs(self):
        rect = self.rect()
        self._placeInputOutputPlugs(rect)
        self._placeAuxOutputPlugs(rect)

    def _placeInputOutputPlugs(self, rect):
        if self.orientation == Orientation.right:
            self.inputPlug.setPos(rect.left(), (rect.height() + self.titleBarHeight) * 0.5)
            self.outputPlug.setPos(rect.right() + 3, (rect.height() + self.titleBarHeight) * 0.5)
        elif self.orientation == Orientation.down:
            self.inputPlug.setPos(rect.center().x(), rect.top())
            self.outputPlug.setPos(rect.center().x(), rect.bottom() + 3)
        elif self.orientation == Orientation.left:
            self.inputPlug.setPos(rect.right(), (rect.height() + self.titleBarHeight) * 0.5)
            self.outputPlug.setPos(rect.left() - 3, (rect.height() + self.titleBarHeight) * 0.5)
        elif self.orientation == Orientation.up:
            self.inputPlug.setPos(rect.center().x(), rect.bottom())
            self.outputPlug.setPos(rect.center().x(), rect.top() - 3)

    def _placeAuxOutputPlugs(self, rect):
        for index, auxPlugs in enumerate(self.auxOutputPlugs):
            plug1, plug2 = auxPlugs
            if self.orientation == Orientation.right or self.orientation == Orientation.left:
                plug1.setPos(self.handleWidget.handleItemPosition(index).x(), rect.bottom())
                plug1.orientation = Orientation.down
                plug2.setPos(self.handleWidget.handleItemPosition(index).x(), rect.top())
                plug2.orientation = Orientation.up
            elif self.orientation == Orientation.up or self.orientation == Orientation.down:
                plug1.setPos(rect.right(), self.handleWidget.handleItemPosition(index).y())
                plug1.orientation = Orientation.right
                plug2.setPos(rect.left(), self.handleWidget.handleItemPosition(index).y())
                plug2.orientation = Orientation.left

    def paint(self, painter, options, widget):
        brush = painter.brush()
        brush.setStyle(QtCore.Qt.SolidPattern)
        brush.setColor(QtGui.QColor(80, 80, 80, 255))
        painter.setBrush(brush)
        pen = painter.pen()
        pen.setStyle(QtCore.Qt.SolidLine)
        pen.setWidth(3)
        pen.setColor(QtGui.QColor(0, 0, 0, 255))
        if self.isSelected():
            pen.setWidth(5)
            pen.setColor(QtGui.QColor(70, 250, 230, 255))
        painter.setPen(pen)
        rect = self.rect()
        painter.drawRoundedRect(rect, self.xRadius, self.yRadius)

        iconSize = 16
        pen.setColor(QtGui.QColor(0, 0, 0, 100))
        pen.setWidth(2)
        painter.setPen(pen)
        painter.drawLine(QtCore.QLineF(rect.left()+6, rect.top()+20, rect.right()-6, rect.top()+20))
        pen.setColor(QtGui.QColor(220, 220, 220, 255))
        painter.setPen(pen)
        painter.drawText(rect.left()+25, rect.top()+15, self.name)
        painter.drawPixmap(self.rotateIconRect(), self._rotateIcon, self._rotateIcon.rect())
        painter.drawPixmap(rect.left()+4, rect.top()+3, iconSize, iconSize, self._guideIcon)

    def rotateIconRect(self):
        r = self.rect()
        return QtCore.QRectF(r.right() - self.iconSize - 4, r.top() + 3, self.iconSize, self.iconSize)

    def mousePressEvent(self, event):
        self._pressPos = event.scenePos()
        super(GuideNodeItem, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.scenePos() == self._pressPos and self.rotateIconRect().contains(event.pos()):
            self.orientation = self.orientation.next()
        super(GuideNodeItem, self).mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu()
        select = menu.addAction("Select Guide")
        select.triggered.connect(self.selectGuide)
        a = menu.exec_(event.screenPos())
        event.accept()

    def itemChange(self, change, value):
        if change == self.ItemPositionHasChanged:
            self.updateConnectionPaths()
        return super(GuideNodeItem, self).itemChange(change, value)

    def updateConnectionPaths(self):
        for connection in self.connections():
            connection.updatePath()

    def connections(self):
        plugs = [self.inputPlug, self.outputPlug]
        for pair in self.auxOutputPlugs:
            plugs.extend(pair)
        allConnections = []
        for plug in plugs:
            allConnections.extend(plug.connections)
        return list(set(allConnections))

    def updateAuxOutputPlugList(self, handleCount):
        self.auxOutputPlugs = self.auxOutputPlugs[:handleCount]
        for i in range(len(self.auxOutputPlugs), handleCount):
            newPlugs = [
                AuxConnectionPlugItem(i,
                                      self.orientation,
                                      self),
                AuxConnectionPlugItem(i,
                                      self.orientation,
                                      self)
            ]
            self.auxOutputPlugs.append(newPlugs)
        self._placeAuxOutputPlugs(self.rect())

    def setAuxPlugVisibility(self):
        for p1, p2 in self.auxOutputPlugs:
            p1.setVisible(p1.display())
            p2.setVisible(p2.display())

    def getPlugItems(self, role, index=-1):
        if role == ConnectionPlugItem.Input:
            return [self.inputPlug]
        elif role == ConnectionPlugItem.Output:
            if index == -1:
                return [self.outputPlug]
            else:
                return self.auxOutputPlugs[index]

    def addHandle(self):
        self.scene().addHandle(self.forgeID)

    def updateData(self):
        self.updateHandleWidget()
    
    def removeHandle(self, index):
        self.scene().removeHandle(self.forgeID, index)

    def insertHandle(self, index):
        self.scene().insertHandle(self.forgeID, index)

    def selectHandle(self, index):
        self.scene().selectHandle(self.forgeID, index)

    def selectGuide(self):
        self.scene().selectGuide(self.forgeID)


class ConnectionPlugItem(QtWidgets.QGraphicsPolygonItem):

    Input = 0
    Output = 1

    size = 18

    def __init__(self, role, orientation, parent=None):
        super(ConnectionPlugItem, self).__init__(parent)

        self.role = role
        self._orientation = orientation
        self.index = -1
        self.connections = []
        self.aux = False

        self._defaultPoly = QtGui.QPolygonF([
            QtCore.QPointF(-self.size*0.5, self.size*0.5),
            QtCore.QPointF(0, -self.size*0.5),
            QtCore.QPointF(self.size*0.5, self.size*0.5),
        ])

        self.rotatePolygon()

    @property
    def name(self):
        return "{}.{}".format(self.node.name, "Input" if self.role == 0 else "Output")

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, orientation):
        self._orientation = orientation
        self.rotatePolygon()

    def rotatePolygon(self):
        matrix = QtGui.QMatrix()
        matrix.rotate(90 * int(self.orientation))
        self.setPolygon(matrix.map(self._defaultPoly))

    def boundingRect(self):
        penWidth = 2
        extra = penWidth / 2.0
        rect = QtCore.QRectF(-self.size*0.5, -self.size*0.5, self.size, self.size)
        return rect.adjusted(-extra, -extra, extra, extra)

    def paint(self, painter, option, widget):
        brush = painter.brush()
        brush.setStyle(QtCore.Qt.SolidPattern)
        brush.setColor(QtGui.QColor(200, 200, 200, 255))
        painter.setBrush(brush)
        pen = painter.pen()
        pen.setStyle(QtCore.Qt.SolidLine)
        pen.setWidth(2)
        pen.setColor(QtGui.QColor(0, 0, 0, 255))
        painter.setPen(pen)
        painter.drawPolygon(self.polygon())

    def mousePressEvent(self, event):
        if self.scene().inConnectionContext():
            self.scene().endConnectionContext(self.role, self.nodeID, self.index)
        else:
            self.scene().beginConnectionContext(event.scenePos(), self.role, self.nodeID, self.index)

    @property
    def node(self):
        return self.parentItem()

    def plugPos(self):
        return self.scenePos()

    def display(self):
        return True

    @property
    def nodeID(self):
        return self.node.forgeID


class AuxConnectionPlugItem(ConnectionPlugItem):

    def __init__(self, index, orientation, parent=None):
        super(AuxConnectionPlugItem, self).__init__(self.Output, orientation, parent)

        self.index = index

        self._defaultPoly = QtGui.QPolygonF([
            QtCore.QPointF(-self.size*0.5, 0),
            QtCore.QPointF(0, -self.size*0.5),
            QtCore.QPointF(self.size*0.5, 0),
            QtCore.QPointF(0, self.size*0.5),
        ])

        self.aux = True
        self.setPolygon(self._defaultPoly)
        self.setVisible(self.display())

    @property
    def name(self):
        return "{}.Handle{:0<2d}".format(self.node.name, self.index)

    def rotatePolygon(self):
        return

    def display(self):
        return self.scene() is not None and (self.scene().inConnectionContext() or len(self.connections) > 0)