"""my.skeleton.boneforge.ui.nodescene
"""

from PySide2 import QtGui, QtCore, QtWidgets


GRID_COLOR = QtGui.QColor(75, 75, 75, 180)
GRID_COLOR_ACCENT = QtGui.QColor(75, 75, 75, 255)

from . import nodeitem
from . import handlewidget
from . import connector

class ForgeNodeScene(QtWidgets.QGraphicsScene):

    DefaultSceneSize = (5000, 5000)

    def __init__(self, mainWidget, parent=None):
        super(ForgeNodeScene, self).__init__(parent)
        self.mainWidget = mainWidget
        self.setSceneSize(*self.DefaultSceneSize)
        self._gridOn = True
        self._gridMinor = 50
        self._gridMajor = 200

        self.connectionCtx = ConnectionContext(self)
        self._minConnectionDrag = 5
        self._connectionInitPos = None
        self._connectionIndicator = None

    def setSceneSize(self, x, y):
        self.setSceneRect(-x*0.5, -y*0.5, x, y)

    def drawBackground(self, painter, rect):
        if not self._gridOn:
            super(ForgeNodeScene, self).drawBackground(painter, rect)
            return

        painter.setWorldMatrixEnabled(True)

        left = int(rect.left()) - (int(rect.left()) % self._gridMinor)
        top = int(rect.top()) - (int(rect.top()) % self._gridMinor)

        minorLinesY = []
        majorLinesY = []
        for y in xrange(left, int(rect.right()), self._gridMinor):
            if y % self._gridMajor == 0:
                majorLinesY.append(QtCore.QLineF(y, rect.top(), y, rect.bottom()))
            else:
                minorLinesY.append(QtCore.QLineF(y, rect.top(), y, rect.bottom()))

        minorLinesX = []
        majorLinesX = []
        for x in xrange(top, int(rect.bottom()), self._gridMinor):
            if x % self._gridMajor == 0:
                majorLinesX.append(QtCore.QLineF(rect.left(), x, rect.right(), x))
            else:
                minorLinesX.append(QtCore.QLineF(rect.left(), x, rect.right(), x))

        coordPen = QtGui.QPen()
        coordPen.setStyle(QtCore.Qt.SolidLine)
        coordPen.setWidth(2)
        coordPen.setColor(GRID_COLOR_ACCENT)
        painter.setPen(coordPen)

        painter.drawLines(majorLinesY)
        painter.drawLines(majorLinesX)

        coordPen.setWidth(1)
        coordPen.setColor(GRID_COLOR)
        painter.setPen(coordPen)

        painter.drawLines(minorLinesY)
        painter.drawLines(minorLinesX)

    def addGuideNodes(self, guideIDs):
        for gID in guideIDs:
            node = nodeitem.GuideNodeItem(gID, self.model)
            self.addItem(node)

    def rebuildFromData(self):
        self.clear()
        self.addGuideNodes(self.model.guideIDs())
        self.updateConnections()
        # TODO: Node layout

    def removeGuideNodes(self, guideIDs):
        guideNodes = self.guideNodeItems(byID=True)
        for gID in guideIDs:
            guide = guideNodes[gID]
            #self.disconnect(guide.connections())
            self.removeItem(guide)

    def contextMenuEvent(self, event):
        if event.modifiers() & QtCore.Qt.AltModifier:
            return
        menu = QtWidgets.QMenu()
        menu.addAction("Hi I'm the scene!")
        item = self.itemAt(event.scenePos(), QtGui.QTransform())
        if not item:
            a = menu.exec_(event.screenPos())
            event.accept()
        else:
            super(ForgeNodeScene, self).contextMenuEvent(event)

    def beginConnectionContext(self, position, role, nodeID, index=-1):
        self._connectionInitPos = position
        node = self.getNodeByID(nodeID)
        plugs = node.getPlugItems(role, index)
        self._connectionIndicator = connector.ConnectionIndicator(plugs, position)
        self.addItem(self._connectionIndicator)
        self.connectionCtx.beginConnectionContext(role, nodeID, index)

    def endConnectionContext(self, role=None, nodeID=None, index=None):
        self.connectionCtx.endConnectionContext(role, nodeID, index)
        self.removeItem(self._connectionIndicator)
        self._connectionIndicator = None
        self._connectionInitPos = None

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), QtGui.QTransform())
        if self.connectionCtx.inConnectionContext() and not isinstance(item, nodeitem.ConnectionPlugItem):
            self.endConnectionContext()
        super(ForgeNodeScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.connectionCtx.inConnectionContext():
            self._connectionIndicator.updateLine(event.scenePos())
        super(ForgeNodeScene, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.connectionCtx.inConnectionContext():
            item = self.itemAt(event.scenePos(), QtGui.QTransform())
            positionDelta = event.scenePos() - self._connectionInitPos
            if positionDelta.manhattanLength() > self._minConnectionDrag:
                if item and isinstance(item, nodeitem.ConnectionPlugItem):
                    self.endConnectionContext(item.role, item.nodeID, item.index)
                else:
                    self.endConnectionContext()
        super(ForgeNodeScene, self).mouseReleaseEvent(event)

    def inConnectionContext(self):
        return self.connectionCtx.inConnectionContext()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            items = self.selectedItems()
            self.disconnect(self.connectorItems(items))
            self.deleteGuides(self.guideNodeItems(items))
        else:
            super(ForgeNodeScene, self).keyPressEvent(event)

    def disconnect(self, connections):
        if isinstance(connections, connector.Connector):
            connections = [connections]
        ids = [connection.inputNodeID for connection in connections]
        self.model.disconnectGuides(ids)

    def deleteGuides(self, guides):
        if isinstance(guides, nodeitem.GuideNodeItem):
            guides = [guides]
        ids = [guide.forgeID for guide in guides]
        self.model.removeGuides(ids)

    @property
    def model(self):
        return self.mainWidget.model

    def guideNodeItems(self, items=None, byID=False):
        if items is None:
            items = self.items()
        guideNodes = filter(lambda x: isinstance(x, nodeitem.GuideNodeItem), items)
        if byID:
            return dict((guide.forgeID, guide) for guide in guideNodes)
        return guideNodes

    def connectorItems(self, items=None, byID=False):
        if items is None:
            items = self.items()
        connectorItems = filter(lambda x: isinstance(x, connector.Connector), items)
        if byID:
            return dict((connector.inputNodeID, connector) for connector in connectorItems)
        return connectorItems

    def getNodeByID(self, gID):
        nodeItems = self.guideNodeItems(byID=True)
        return nodeItems[gID]

    def updateConnections(self):
        for item in self.connectorItems():
            item.prepareToRemove()
            self.removeItem(item)
        for output, index, input in self.model.connections:
            outputNode = self.getNodeByID(output)
            outputPlugs = outputNode.getPlugItems(nodeitem.ConnectionPlugItem.Output, index)
            inputNode = self.getNodeByID(input)
            inputPlug = inputNode.getPlugItems(nodeitem.ConnectionPlugItem.Input)[0]
            connectorItem = connector.Connector(outputPlugs, inputPlug)
            self.addItem(connectorItem)

    def addHandle(self, nodeID):
        self.model.addHandle(nodeID)

    def removeHandle(self, nodeID, handleIndex):
        self.model.removeHandle(nodeID, handleIndex)

    def insertHandle(self, nodeID, handleIndex):
        self.model.insertHandle(nodeID, handleIndex)

    def selectHandle(self, nodeID, handleIndex):
        self.model.selectHandle(nodeID, handleIndex)

    def selectGuide(self, nodeID):
        self.model.selectGuides([nodeID])

    def updateGuideNodeData(self, nodeIDs):
        nodeItems = self.guideNodeItems(byID=True)
        for id in nodeIDs:
            node = nodeItems[id]
            node.updateData()

    def buildSkeleton(self):
        self.model.buildSkeleton()



class ConnectionContext(object):

    PlugRoleInput = nodeitem.ConnectionPlugItem.Input
    PlugRoleOutput = nodeitem.ConnectionPlugItem.Output

    def __init__(self, scene):
        self.scene = scene
        self._connectionCtx = False
        self._connectionInput = None
        self._connectionOutput = None
        self._connectionIndex = None
        self._connectionIndicator = None

    def inConnectionContext(self):
        return self._connectionCtx

    def beginConnectionContext(self, role, nodeID, index=-1):
        self._connectionCtx = True
        if role == self.PlugRoleInput:
            self._connectionInput = nodeID
        else:
            self._connectionOutput = nodeID
            self._connectionIndex = index
        if self.hasInput():
            for node in self.scene.guideNodeItems():
                node.setAuxPlugVisibility()

    def endConnectionContext(self, role=None, nodeID=None, index=None):
        if role == self.PlugRoleInput:
            self._connectionInput = nodeID
        elif role == self.PlugRoleOutput:
            self._connectionOutput = nodeID
            self._connectionIndex = index

        self._connectionCtx = False
        if self.validConnection():
            self.scene.model.connectGuides(self._connectionOutput,
                                           self._connectionIndex,
                                           self._connectionInput)
        self._connectionInput = None
        self._connectionOutput = None
        self._connectionIndex = None
        for node in self.scene.guideNodeItems():
            node.setAuxPlugVisibility()

    def hasInput(self):
        return self._connectionInput is not None

    def hasOutput(self):
        return self._connectionOutput is not None and self._connectionIndex is not None

    def validConnection(self):
        bothPlugs = self.hasInput() and self.hasOutput()
        notSame = bothPlugs and self._connectionInput != self._connectionOutput
        return bothPlugs and notSame