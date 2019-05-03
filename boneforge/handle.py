import pymel.core as pm

import lib.transform
import lib.attribute


class Handle(object):
    """Control class for handle objects."""

    def __init__(self, handle):
        if pm.nodeType(handle) == "transform":
            handle = handle.getShape()
        self.node = handle

    @classmethod
    def create(cls, guideNode, name=None):
        """Create a new Handle object."""
        handle = pm.createNode("guideHandle")
        transform = handle.getParent()
        if name:
            transform.rename(name)
        transform.worldMatrix[0].connect(handle.handleMatrix)
        transform.scaleY.connect(transform.scaleX)
        transform.scaleY.connect(transform.scaleZ)
        pm.aliasAttr("radius", transform.scaleY)
        lib.transform.lockHideTransforms(transform,
                                          translate="",
                                          rotate="",
                                          scale="xz")
        connectGuideToHandle(guideNode, handle)
        pm.select(transform)
        return cls(handle)

    def __repr__(self):
        return "{}.{}({!r})".format(__name__,
                                  self.__class__.__name__,
                                  self.transform.name())

    def __eq__(self, other):
        return isinstance(other, self.__class__) and other.node == self.node

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.node)

    @property
    def name(self):
        return self.transform.name()

    @name.setter
    def name(self, name):
        self.transform.rename(name)

    @property
    def transform(self):
        return self.node.getParent()

    @property
    def guideNode(self):
        guide = self.node.guide.listConnections(shapes=True)
        if guide:
            return guide[0]
        return None

    @property
    def forgeID(self):
        return self.node.forgeID.get()

    @property
    def rotateOrder(self):
        return self.node.jointRotateOrder.get()

    @rotateOrder.setter
    def rotateOrder(self, order):
        self.node.jointRotateOrder.set(order)

    def parent(self):
        """Returns the parent Handle."""
        parentNode = self.node.parentHandle.listConnections(shapes=True)
        if parentNode:
            return self.__class__(parentNode[0])
        return None

    def setParent(self, other):
        """Set the parent Handle."""
        parentHandle = self.parent()
        if parentHandle:
            pm.disconnectAttr(self.node.parentHandle)
            parentHandle.removeChild(self)
        if other is not None:
            other.node.message.connect(self.node.parentHandle)
            other.transform.worldMatrix[0].connect(self.node.parentHandleMatrix)
            other.addChild(self)

    def childCount(self):
        """Returns the number of child Handles."""
        return len(self.node.childHandle.listConnections())

    def addChild(self, child):
        """Add a Handle as a child of this Handle."""
        idx = lib.attribute.firstOpenIndex(self.node.childHandleMatrix)
        child.node.message.connect(self.node.childHandle[idx])
        child.transform.worldMatrix[0].connect(self.node.childHandleMatrix[idx])

        # If the child is part of the same guide, this handle should orient towards it
        # (If not part of the same guide, it may or may not,
        # depending on how the child guide is connected)
        if child.guideNode == self.guideNode:
            self.setOrientTarget(child)

    def removeChild(self, child):
        """Remove the Handle as a child of this Handle."""
        children = self.children()
        children.remove(child)
        for subAttr in self.node.childHandle:
            pm.removeMultiInstance(subAttr, b=True)
        for subAttr in self.node.childHandleMatrix:
            pm.removeMultiInstance(subAttr, b=True)
        orientTarget = self.orientTarget()
        self.setOrientTarget(None)
        for handle in children:
            self.addChild(handle)
        if orientTarget != child:
            self.setOrientTarget(orientTarget)
        pm.disconnectAttr(child.node.parentHandle)
        pm.disconnectAttr(child.node.parentHandleMatrix)

    def children(self):
        """Return a list of child Handles."""
        return map(self.__class__,
                   self.node.childHandle.listConnections(shapes=True))

    def orientTarget(self):
        """Returns the Handle that this Handle will orient towards."""
        target = self.node.orientTarget.listConnections(shapes=True)
        if target:
            return self.__class__(target[0])
        return None

    def setOrientTarget(self, target):
        """Set the Handle that this Handle will orient towards."""
        if target == self.orientTarget():
            return
        if target and target not in self.children():
            raise RuntimeError(
                "Cannot set {} as the orient target, as it is not a child of {}"
                .format(target, self))

        pm.disconnectAttr(self.node.orientTarget)
        pm.disconnectAttr(self.node.orientTargetMatrix)

        if target:
            target.node.message.connect(self.node.orientTarget)
            target.transform.worldMatrix[0].connect(self.node.orientTargetMatrix)

    def jointMatrix(self):
        return self.node.jointMatrix.get()

    def buildJoint(self):
        pm.select(clear=True)
        jnt = pm.joint(name=self.name)
        jnt.rotateOrder.set(self.rotateOrder)
        #jnt.side.set(self.side)
        matrix = self.jointMatrix()
        pm.xform(jnt, matrix=matrix)
        return jnt


def connectGuideToHandle(guideNode, handle):
    guideNode.message.connect(handle.guide)
    guideNode.provideAimVector.connect(handle.useGuideAim)
    guideNode.aimVector.connect(handle.aimVector)
    guideNode.upVector.connect(handle.upVector)
    guideNode.aimAxis.connect(handle.aimAxis)
    guideNode.upAxis.connect(handle.upAxis)
    guideNode.handleColor.connect(handle.handleColor)

def isHandleType(obj):
    if pm.nodeType(obj) == "transform":
        obj = obj.getShape()
    return obj is not None and pm.nodeType(obj) == "guideHandle"
