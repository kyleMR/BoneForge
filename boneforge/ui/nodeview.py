"""my.skeleton.boneforge.ui.nodeview
"""

from PySide2 import QtGui, QtCore, QtWidgets

class ForgeNodeView(QtWidgets.QGraphicsView):

    def __init__(self, parent=None):
        super(ForgeNodeView, self).__init__(parent)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        # FullViewportUpdate is bad for performance,
        # but avoids nasty redraw artifacts on bg grid
        # self.setViewportUpdateMode(QtWidgets.QGraphicsView.FullViewportUpdate)
        self.setViewportUpdateMode(QtWidgets.QGraphicsView.SmartViewportUpdate)
        self.setRenderHints(QtGui.QPainter.Antialiasing)
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.centerOn(0, 0)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self._pan = False
        self._zoom = False
        self._zoomCenter = None
        self._pressPos = None
        self._initialPress = None

    def wheelEvent(self, event):
        '''
        Handle zooming in and out of the QGraphicsView.
        :param QWheelEvent event: Event triggered by mouse wheel scrolling.
        '''
        inFactor = 1.25
        outFactor = 1 / inFactor
        oldPos = self.mapToScene(event.pos())
        if event.delta() > 0:
            zoomFactor = inFactor
        else:
            zoomFactor = outFactor
        self.scale(zoomFactor, zoomFactor)
        newPos = self.mapToScene(event.pos())
        delta = newPos - oldPos
        self.translate(delta.x(), delta.y())

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._pan = True
            self._pressPos = event.pos()
            self.setCursor(QtCore.Qt.ClosedHandCursor)
            event.accept()
        elif event.button() == QtCore.Qt.RightButton and event.modifiers() & QtCore.Qt.AltModifier:
            self._zoom = True
            self._pressPos = event.pos()
            self._initialPress = event.pos()
            self._zoomCenter = self.mapToScene(self._pressPos)
            self.setTransformationAnchor(QtWidgets.QGraphicsView.NoAnchor)
            event.accept()
        else:
            super(ForgeNodeView, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._pan:
            offset = self._pressPos - event.pos()
            self._pressPos = event.pos()
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + offset.y())
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + offset.x())
            event.accept()
        elif self._zoom:
            offset = event.pos() - self._pressPos
            scaleSpeed = .005
            inFactor = 1.0 + scaleSpeed * abs(offset.x())
            outFactor = 1.0 / inFactor
            if offset.x() > 0:
                zoomFactor = inFactor
            else:
                zoomFactor = outFactor
            self.scale(zoomFactor, zoomFactor)
            newPos = self.mapToScene(self._initialPress)
            delta = newPos - self._zoomCenter
            self.translate(delta.x(), delta.y())
            self._pressPos = event.pos()
            event.accept()
        else:
            super(ForgeNodeView, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.MiddleButton:
            self._pan = False
            self.setCursor(QtCore.Qt.ArrowCursor)
            event.accept()
        elif event.button() == QtCore.Qt.RightButton:
            self._zoom = False
            self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
            event.accept()
        else:
            super(ForgeNodeView, self).mouseReleaseEvent(event)