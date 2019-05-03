import pymel.core as pm
from .handle import Handle, isHandleType

import lib.transform

class Guide(object):
    """Base class for all guide nodes."""

    def __init__(self, guideNode):
        if pm.nodeType(guideNode) == "transform":
            guideNode = guideNode.getShape()
        self.guide = guideNode

    def __new__(cls, guideNode=None):
        if guideNode:
            nodeType = pm.nodeType(guideNode)
            if nodeType == "transform":
                guideNode = guideNode.getShape()
                nodeType = pm.nodeType(guideNode)
            guideClass = GUIDE_NODE_CLASS[nodeType]
            instance = guideClass.__new__(guideClass)
        else:
            instance = super(Guide, cls).__new__(cls)
        return instance

    def __repr__(self):
        return "{}.{}({!r})".format(__name__,
                                  self.__class__.__name__,
                                  self.transform.name())

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.guide == self.guide

    @property
    def name(self):
        return self.transform.name()

    @name.setter
    def name(self, name):
        self.transform.rename(name)

    @property
    def transform(self):
        return self.guide.getParent()

    @property
    def forgeID(self):
        return self.guide.forgeID.get()

    @property
    def provideAimVector(self):
        return self.guide.provideAimVector.get()

    @provideAimVector.setter
    def provideAimVector(self, value):
        self.guide.provideAimVector.set(value)

    def handleCount(self):
        """Returns the number of handles associated with this guide."""
        count = 0
        for handle in self.guide.handle:
            if handle.isConnected():
                count += 1
        return count

    def handleAtIndex(self, index):
        """Returns the Handle at the given index."""
        return list(self.handles())[index]

    def indexOf(self, handle):
        """Returns the index of the given Handle."""
        for i, h in enumerate(self.handles()):
            if h == handle:
                return i
        else:
            return -1

    def addHandle(self, name="joint", position=(0, 0, 0)):
        """Append a new handle to the end of the chain."""
        self._consolidateSparseHandleArray()
        numHandles = self.handleCount()
        handle = self._addNewHandleAtIndex(numHandles, name, position)
        return handle

    def _addNewHandleAtIndex(self, index, name, position):
        """Internal helper method for creating handles."""
        pm.select(clear=True)
        handle = Handle.create(self.guide, name)
        handle.transform.setParent(self.transform)
        handle.transform.setTranslation(position)
        handle.node.message.connect(self.guide.handle[index])
        self._refreshHandleHierarchicalConnections()
        return handle

    def insertHandle(self, index, name="joint", position=(0, 0, 0)):
        """Insert a new handle at the given index."""
        if index >= self.handleCount():
            handle = self.addHandle(name, position)
        else:
            handleList = list(self.handles())
            for i in reversed(xrange(index, self.handleCount())):
                # If a handle after the insert point has a child in
                # another guide, that guide needs to have its parentHandleIndex
                # increased by 1
                h = handleList[i]
                for child in h.children():
                    if child.guideNode != self.guide:
                        g = Guide(child.guideNode)
                        g.setParentGuideHandleIndex(g.parentGuideHandleIndex() + 1)
                self._changeHandleIndex(i, i + 1)
            handle = self._addNewHandleAtIndex(index, name, position)
        return handle

    def removeHandle(self, index):
        """Remove and delete the handle at the given index."""
        self._consolidateSparseHandleArray()
        handle = self.handleAtIndex(index)
        # If the handle being removed has children in other guides,
        # Set those guides to have no parent
        for child in handle.children():
            if child.guideNode != self.guide:
                Guide(child.guideNode).setParentGuide(None)
        handleList = list(self.handles())
        for i in xrange(index + 1, self.handleCount()):
            # If a handle after the removal point has a child in
            # another guide, that guide needs to have its parentHandleIndex
            # decreased by 1
            h = handleList[i]
            for child in h.children():
                if child.guideNode != self.guide:
                    g = Guide(child.guideNode)
                    g.setParentGuideHandleIndex(g.parentGuideHandleIndex() - 1)
            self._changeHandleIndex(i, i - 1)
        pm.removeMultiInstance(
            self.guide.handle[self.guide.handle.numElements() - 1], b=True)
        pm.delete(handle.transform)
        self._refreshHandleHierarchicalConnections()

    def handles(self):
        """Return an ordered iterator of the handles managed by this guide."""
        for handle in self.guide.handle:
            if handle.isConnected():
                yield Handle(handle.inputs()[0])

    def sanitize(self):
        """Sanitize handles attribute and update hierarchy connections."""
        self._consolidateSparseHandleArray()
        self._refreshHandleHierarchicalConnections()

    def _refreshHandleHierarchicalConnections(self):
        """Re-set parent/child relationship connections on the handles of this guide."""
        handleIter = self.handles()
        prevHandle = next(handleIter)
        # Set the first handle's parent to the handle at parentHandleIndex of parentHandle
        if self.parentGuide() is not None:
            parentHandle = self.parentGuide().handleAtIndex(self.parentGuideHandleIndex())
            prevHandle.setParent(parentHandle)
            if self.parentGuideHandleIndex() == -1:
                parentHandle.setOrientTarget(prevHandle)
        for handle in handleIter:
            handle.setParent(prevHandle)
            prevHandle.setOrientTarget(handle)
            prevHandle = handle
        # Set the final handle's orient target if there is a child guide
        if self.childGuide() is not None:
            nextHandle = self.childGuide().handleAtIndex(0)
            lastHandle = self.handleAtIndex(-1)
            nextHandle.setParent(lastHandle)
            lastHandle.setOrientTarget(nextHandle)
        else:
            lastHandle = self.handleAtIndex(-1)
            lastHandle.setOrientTarget(None)

    def _consolidateSparseHandleArray(self):
        """Remove unconnected handle array entries.

        Pushes all connections to occupy consecutive indices starting from 0.
        """
        i = 0
        for handle in self.guide.handle:
            if not handle.isConnected():
                continue
            if handle.index() == i:
                i += 1
                continue
            self._changeHandleIndex(handle.index(), i)
            i += 1

    def _changeHandleIndex(self, fromIndex, toIndex):
        """Moves the handle connection from one index to another."""
        sourceHandle = self.guide.handle[fromIndex]
        destinationHandle = self.guide.handle[toIndex]
        handlePlug = sourceHandle.inputs(plugs=True)[0]
        destinationHandle.disconnect()
        handlePlug.connect(destinationHandle)
        sourceHandle.disconnect()

    def parentGuide(self):
        """Returns the parent guide."""
        guide = self.guide.parentGuide.listConnections(shapes=True)
        if guide:
            return Guide(guide[0])
        return None

    def setParentGuide(self, guide, index=-1):
        """Set the parent guide and guide handle index.
        
        An index of -1 means that the guide is connected directly
        to the previous guide, and the previous guide's end handle
        will orient to this guide's first handle.
        
        Other index values represent which handle on the previous guide
        is the parent of the first handle of this guide.
        """
        baseHandle = self.handleAtIndex(0)
        baseHandle.setParent(None)
        currentParent = self.parentGuide()
        if currentParent and currentParent.childGuide() == self:
            currentParent.guide.childGuide.disconnect()
            currentParent.handleAtIndex(-1).setOrientTarget(None)
        self.guide.parentGuide.disconnect()
        if guide is not None:
            guide.guide.message.connect(self.guide.parentGuide)
            baseHandle.setParent(guide.handleAtIndex(index))
            # If this guide is a direct child of the given guide (follows the last handle)
            # Then set as the child of that guide
            if index == -1:
                guide.setChildGuide(self)
            self.setParentGuideHandleIndex(index)

    def parentGuideHandleIndex(self):
        return self.guide.parentGuideHandleIndex.get()

    def setParentGuideHandleIndex(self, index):
        self.guide.parentGuideHandleIndex.set(index)

    def childGuide(self):
        guide = self.guide.childGuide.listConnections(shapes=True)
        if guide:
            return Guide(guide[0])
        return None

    def setChildGuide(self, guide):
        currentChild = self.childGuide()
        if currentChild is not None:
            currentChild.setParentGuide(None)
            self.guide.childGuide.disconnect()
            self.handleAtIndex(-1).setOrientTarget(None)
        if guide is not None:
            guide.guide.message.connect(self.guide.childGuide)
            self.handleAtIndex(-1).setOrientTarget(guide.handleAtIndex(0))

    def _pynodeIsGuidePart(self, node):
        isGuideShape = node == self.guide
        isHandle = isHandleType(node) and Handle(node).guideNode == self.guide
        return isGuideShape or isHandle

    def remove(self):
        for child in self.transform.getChildren():
            if self._pynodeIsGuidePart(child):
                continue
            child.setParent(self.transform.getParent())
        pm.delete(self.transform)

    def handleColor(self):
        return self.guide.handleColor.get()

    def setHandleColor(self, color):
        self.guide.handleColor.set(color)

    def getGuideData(self):
        data = {}
        data["guideNodeType"] = self.nodetype
        data["className"] = self.__class__.__name__
        data["forgeID"] = self.forgeID
        data["name"] = self.name()
        parentGuide = self.parentGuide()
        parentGuideHandleIndex = self.parentGuideHandleIndex()
        if parentGuide is not None:
            parentGuideID = parentGuide.forgeID
        else:
            parentGuideID = None
        data["parentGuideID"] = parentGuideID
        data["parentGuideHandleIndex"] = parentGuideHandleIndex

        data["handleCount"] = self.handleCount()

        ## Handle Data
        handleData = []
        for handle in self.handles():
            hd = {}
            hd["forgeID"] = handle.forgeID
            hd["name"] = handle.name
            hd["rotateOrder"] = handle.rotateOrder
            hd["translation"] = tuple(pm.xform(handle.transform, q=True, translation=True, worldSpace=True))
            hd["rotation"] = tuple(pm.xform(handle.transform, q=True, rotation=True, worldSpace=True))
            hd["radius"] = handle.transform.radius.get()

        data["handleColor"] = self.handleColor()

        data["translation"] = tuple(pm.xform(self.transform, q=True, translation=True, worldSpace=True))
        data["rotation"] = tuple(pm.xform(self.transform, q=True, rotation=True, worldSpace=True))
        data["scale"] = tuple(pm.xform(self.transform, q=True, scale=True, worldSpace=True))
        return data

    @staticMethod
    def fromGuideData(data, idMap=None):
        nodeType = data["guideNodeType"]
        cls = GUIDE_NODE_CLASS[nodeType]
        guide = cls.create(name=data["name"])
        cls._setValuesFromGuideData(guide, data, idMap)
        return guide
    
    @classmethod
    def _setValuesFromGuideData(cls, guide, data, idMap=None):
        pm.xform(guide.transform, translation=data["translation"], worldSpace=True)
        pm.xform(guide.transform, rotation=data["rotation"], worldSpace=True)
        pm.xform(guide.transform, scale=data["scale"], worldSpace=True)
        guide.setHandleColor(data.get("handleColor", (0.0, 0.0, 0.0)))
        ## Get parent guide from given id
        ## I think this needs to be in the import template script to ensure the parent
        ## exists by the time we set it
        #parentGuide = data["parentGuideID"]
        #parentGuideHandleIndex = data["parentGuideHandleIndex"]
        #guide.setParentGuide(parentGuide, parentGuideHandleIndex)


class GuideSpine(Guide):
    """Control Class for planar spine guide object."""

    nodetype = "skeletonGuideSpine"

    @classmethod
    def create(cls, name="guideSpine"):
        """Create a new guide object with a single handle."""
        guideNode = pm.createNode("skeletonGuideSpine")
        guide = cls(guideNode)
        guide.transform.worldMatrix[0].connect(guide.guide.guideMatrix)
        guide.name = name
        guide.addHandle()
        pm.select(guide.transform)
        return guide

    def addHandle(self, name="joint", position=(0, 0, 0)):
        """Append a new handle to the end of the chain."""
        handle = super(GuideSpine, self).addHandle(name, position)
        handle.transform.translateX.setLocked(True)
        return handle

    def insertHandle(self, index, name="joint", position=(0, 0, 0)):
        """Insert a new handle at the given index."""
        handle = super(GuideSpine, self).addHandle(index, name, position)
        handle.transform.translateX.setLocked(True)


class GuideLimb(Guide):
    """Control Class for limb guide object."""

    nodetype = "skeletonGuideLimb"

    @classmethod
    def create(cls, name="guideLimb"):
        """Create a new guide object with 3 initial handles."""
        guideNode = pm.createNode("skeletonGuideLimb")
        guide = cls(guideNode)
        guide.transform.worldMatrix[0].connect(guide.guide.guideMatrix)
        guide.name = name
        orientGroup = pm.createNode("transform")
        orientGroup.setParent(guide.transform)
        orientGroup.message.connect(guide.guide.orientGroup)
        guide.guide.orientGroupTranslate.connect(orientGroup.translate)
        guide.guide.orientGroupRotate.connect(orientGroup.rotate)
        base = guide._addNewHandleAtIndex(0, "joint", (0, 0, 0))
        mid = guide._addNewHandleAtIndex(1, "joint", (2, 0, 0))
        end = guide._addNewHandleAtIndex(2, "joint", (4, 0, 0))
        guide.setBaseHandle(base)
        guide.setHingeHandle(mid)
        guide.setEndHandle(end)
        pm.select(guide.transform)
        return guide

    @property
    def orientGroup(self):
        grp = self.guide.orientGroup.listConnections()
        if not grp:
            orientGroup = pm.createNode("transform")
            orientGroup.setParent(self.transform)
            orientGroup.message.connect(self.guide.orientGroup)
            self.guide.orientGroupTranslate.connect(orientGroup.translate)
            self.guide.orientGroupRotate.connect(orientGroup.rotate)
            return orientGroup
        return grp[0]

    @property
    def useChildBaseAsEnd(self):
        return self.guide.useChildBaseAsEnd.get()

    @useChildBaseAsEnd.setter
    def useChildBaseAsEnd(self, value):
        if value:
            child = self.childGuide()
            if child is not None:
                self.guide.useChildBaseAsEnd.set(True)
                self.setEndHandle(child.handleAtIndex(0))
            else:
                raise RuntimeError("Guide {!r} has no child to use as limb end".format(self.name))
        else:
            if self.handleCount() >= 3:
                self.guide.useChildBaseAsEnd.set(False)
                self.setEndHandle(self.handleAtIndex(-1))
            else:
                raise RuntimeError("Cannot stop using child as limb end unless guide {!r} has 3 or more handles".format(self.name))

    def baseHandle(self):
        handle = self.guide.baseMatrix.listConnections(shapes=True)
        if handle:
            return Handle(handle[0])
        return None

    def hingeHandle(self):
        handle = self.guide.hingeMatrix.listConnections(shapes=True)
        if handle:
            return Handle(handle[0])
        return None

    def endHandle(self):
        handle = self.guide.endMatrix.listConnections(shapes=True)
        if handle:
            return Handle(handle[0])
        return None

    def setBaseHandle(self, handle):
        existingHandle = self.baseHandle()
        pm.disconnectAttr(self.guide.baseMatrix)
        self.removeFromOrientGroup(handle)
        handle.transform.worldMatrix[0].connect(self.guide.baseMatrix)
        if existingHandle and existingHandle != handle:
            self.moveToOrientGroup(existingHandle)
        self.snapOrientGroupHandlesToPlane()

    def setHingeHandle(self, handle):
        existingHandle = self.hingeHandle()
        pm.disconnectAttr(self.guide.hingeMatrix)
        self.removeFromOrientGroup(handle)
        handle.transform.worldMatrix[0].connect(self.guide.hingeMatrix)
        if existingHandle and existingHandle != handle:
            self.moveToOrientGroup(existingHandle)

    def setEndHandle(self, handle):
        existingHandle = self.endHandle()
        pm.disconnectAttr(self.guide.endMatrix)
        existingHandleGuide = existingHandle.guideNode
        newEndGuide = handle.guideNode
        if newEndGuide == self.guide:
            self.removeFromOrientGroup(handle)
        handle.transform.worldMatrix[0].connect(self.guide.endMatrix)
        if existingHandle and existingHandle != handle and existingHandleGuide == self.guide:
            self.moveToOrientGroup(existingHandle)
        self.snapOrientGroupHandlesToPlane()

    def moveToOrientGroup(self, handle):
        handle.transform.setParent(self.orientGroup)
        handle.transform.rotate.set([0, 0, 0])
        handle.transform.translateY.setLocked(True)

    def removeFromOrientGroup(self, handle):
        if handle.transform.getParent() == self.orientGroup:
            lib.transform.unlockTransforms(handle.transform, rotate="", scale="")
            handle.transform.setParent(self.transform)
            handle.transform.rotate.set([0, 0, 0])

    def snapOrientGroupHandlesToPlane(self):
        for transform in self.orientGroup.getChildren():
            with lib.transform.unlockTransformsCtx(transform):
                transform.translateY.set(0)

    def addHandle(self, name="joint", position=(0, 0, 0)):
        """Append a new handle to the end of the chain.
        
        This extends the base class to set the new handle as the End Handle."""
        handle = super(GuideLimb, self).addHandle(name, position)
        self.setEndHandle(handle)
        return handle

    def insertHandle(self, index, name="joint", position=(0, 0, 0)):
        """Insert a new handle at the given index.
        
        This extends the base class to set the new handle as the Base Handle
        if it becomes the new first handle (inserted at index 0).
        """
        handle = super(GuideLimb, self).insertHandle(index, name, position)
        if index == 0:
            self.setBaseHandle(handle)
        else:
            self.moveToOrientGroup(handle)
        return handle

    def _pynodeIsGuidePart(self, node):
        return (super(GuideLimb, self)._pynodeIsGuidePart(node)
                or node == self.orientGroup)


class GuideBlock(Guide):
    """Control Class for block guide object."""

    nodetype = "skeletonGuideBlock"

    @classmethod
    def create(cls, name="guideBlock"):
        """Create a new guide object with its handle."""
        guideNode = pm.createNode("skeletonGuideBlock")
        guide = cls(guideNode)
        guide.transform.worldMatrix[0].connect(guide.guide.guideMatrix)
        guide.name = name
        handle = guide.addHandle()
        pm.select(guide.transform)
        return guide


GUIDE_NODE_TYPES = (GuideSpine.nodetype, GuideLimb.nodetype, GuideBlock.nodetype)
GUIDE_NODE_CLASS = {
    GuideSpine.nodetype: GuideSpine,
    GuideLimb.nodetype: GuideLimb,
    GuideBlock.nodetype: GuideBlock,
}

def isGuideType(obj):
    if pm.nodeType(obj) == "transform":
        obj = obj.getShape()
    return obj is not None and pm.nodeType(obj) in GUIDE_NODE_TYPES