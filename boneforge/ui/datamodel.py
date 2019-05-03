"""my.skeleton.boneforge.ui.datamodel
"""

from PySide2 import QtGui, QtCore, QtWidgets
import pymel.core as pm

import boneforge.core as bfcore

class GuideDataModel(QtCore.QObject):

    guidesAdded = QtCore.Signal(list)
    guidesRemoved = QtCore.Signal(list)
    guidesUpdated = QtCore.Signal(list)
    connectionsUpdated = QtCore.Signal()
    guideDataUpdated = QtCore.Signal()

    def __init__(self):
        super(GuideDataModel, self).__init__()
        self.guideNodes = {}
        self.connections = []
        self.gatherDataFromScene()

    def gatherDataFromScene(self):
        guides = bfcore.guidesFromScene()
        self.guideNodes.clear()
        for guide in guides:
            self.guideNodes[guide.forgeID] = guide
        self.gatherConnectionsFromScene(guides)
        self.guideDataUpdated.emit()

    def gatherConnectionsFromScene(self, guides=None):
        if guides is None:
            guides = bfcore.guidesFromScene()
        self.connections[:] = []
        for guide in guides:
            if guide.parentGuide():
                output = guide.parentGuide()
                outputIndex = guide.parentGuideHandleIndex()
                input = guide
                self.connections.append((output.forgeID, outputIndex, input.forgeID))

    def guideIDs(self):
        return self.guideNodes.iterkeys()

    def addGuide(self, guideClass):
        guide = guideClass.create()
        self.guideNodes[guide.forgeID] = guide
        self.guidesAdded.emit([guide.forgeID])

    def removeGuides(self, ids):
        for gID in ids:
            guide = self.guideNodes.pop(gID)
            if guide:
                guide.remove()
        self.guidesRemoved.emit(ids)
        self.gatherConnectionsFromScene()
        self.connectionsUpdated.emit()

    def connectGuides(self, outputID, outputIndex, inputID):
        outputGuide = self.guideNodes[outputID]
        inputGuide = self.guideNodes[inputID]
        inputGuide.setParentGuide(outputGuide, outputIndex)
        self.gatherConnectionsFromScene()
        self.connectionsUpdated.emit()

    def disconnectGuides(self, inputIDs):
        for inputID in inputIDs:
            inputGuide = self.guideNodes[inputID]
            inputGuide.setParentGuide(None)
        self.gatherConnectionsFromScene()
        self.connectionsUpdated.emit()

    def duplicateGuides(self, ids):
        pass

    def changeHandleIndex(self, id, sourceIndex, targetIndex):
        pass

    def addHandle(self, id):
        guide = self.guideNodes[id]
        bfcore.addGuideHandle(guide)
        self.guidesUpdated.emit([id])

    def insertHandle(self, id, index):
        guide = self.guideNodes[id]
        bfcore.insertGuideHandle(guide, index)
        self.guidesUpdated.emit([id])
        self.gatherConnectionsFromScene()
        self.connectionsUpdated.emit()

    def removeHandle(self, id, index):
        guide = self.guideNodes[id]
        guide.removeHandle(index)
        self.guidesUpdated.emit([id])
        self.gatherConnectionsFromScene()
        self.connectionsUpdated.emit()

    def renameGuide(self, id, name):
        pass

    def selectGuides(self, ids):
        transforms = []
        for id in ids:
            transforms.append(self.guideNodes[id].transform)
        pm.select(transforms)

    def selectHandle(self, id, index):
        guide = self.guideNodes[id]
        handle = guide.handleAtIndex(index)
        pm.select(handle.transform)

    def guideData(self, id):
        guide = self.guideNodes.get(id, None)
        if guide is None:
            raise RuntimeError("Model has no reference to guide with ID: {!r}".format(id))

        data = {
            "name": guide.name,
            "class": guide.__class__.__name__,
            "handleCount": guide.handleCount()
        }
        return data

    def getGuideRoots(self):
        guides = self.guideNodes.values()
        roots = []
        for guide in guides:
            if guide.parentGuide() is None:
                roots.append(guide)
        return roots

    def buildSkeleton(self):
        for root in self.getGuideRoots():
            bfcore.buildSkeleton(root)


