"""my.lib.transform

Transformation related utilities and operations
Transform channel modifiers (lock/unlock, show/hide)
"""
import contextlib

import maya.api.OpenMaya as OpenMaya
import pymel.core as pm

AXIS_VECTORS = {
    "x": OpenMaya.MVector.kXaxisVector,
    "y": OpenMaya.MVector.kYaxisVector,
    "z": OpenMaya.MVector.kZaxisVector,
    "-x": OpenMaya.MVector.kXnegAxisVector,
    "-y": OpenMaya.MVector.kYnegAxisVector,
    "-z": OpenMaya.MVector.kZnegAxisVector}

class Axis(int):
    
    NAMES = ("x", "y", "z", "-x", "-y", "-z")
    
    def __new__(cls, idx):
        if isinstance(idx, basestring):
            return cls.fromName(idx)
        return int.__new__(cls, idx % 6)
    
    def __neg__(self):
        return Axis(self + 3)
    
    def __abs__(self):
        return Axis(self % 3)
        
    positive = __abs__
    
    @classmethod
    def fromName(cls, name):
        idx = cls.NAMES.index(name.lower())
        return cls(idx)
        
    @classmethod
    def fromVector(cls, vector):
        """Returns closest world space axis to given vector"""
        allVectors = [AXIS_VECTORS[a] for a in cls.NAMES]
        mVector = OpenMaya.MVector(vector)
        idx, val = 0, 0
        for n, v in enumerate(allVectors):
            dot = v * mVector
            if dot > val:
                val = dot
                idx = n
                
        return cls(idx)
    
    @property
    def name(self):
        return self.NAMES[self]
        
    def otherAxes(self):
        axes = [0, 1, 2]
        axes.remove(self % 3)
        return list(map(Axis, axes))
        
    @property
    def isNegative(self):
        return self > 2
        
X_AXIS, Y_AXIS, Z_AXIS = map(Axis, range(3))


def lockTransforms(transform, translate="xyz", rotate="xyz", scale="xyz"):
    """Lock transformation channels on the given object.
    
    Returns a dictionary of transform axes that were locked.
    """
    lockedAttrs = {"translate": "", "rotate": "", "scale": ""}
    
    for axis in translate:
        attr = transform.attr("t{}".format(axis))
        if not attr.isLocked():
            attr.setLocked(True)
            lockedAttrs["translate"] += axis
    for axis in rotate:
        attr = transform.attr("r{}".format(axis))
        if not attr.isLocked():
            attr.setLocked(True)
            lockedAttrs["rotate"] += axis
    for axis in scale:
        attr = transform.attr("s{}".format(axis))
        if not attr.isLocked():
            attr.setLocked(True)
            lockedAttrs["scale"] += axis
            
    return lockedAttrs

def unlockTransforms(transform, translate="xyz", rotate="xyz", scale="xyz"):
    """Unlock transformation channels on the given object.
    
    Returns a dictionary of transform axes that were unlocked.
    """
    unlockedAttrs = {"translate": "", "rotate": "", "scale": ""}
    
    for axis in translate:
        attr = transform.attr("t{}".format(axis))
        if attr.isLocked():
            attr.setLocked(False)
            unlockedAttrs["translate"] += axis
    for axis in rotate:
        attr = transform.attr("r{}".format(axis))
        if attr.isLocked():
            attr.setLocked(False)
            unlockedAttrs["rotate"] += axis
    for axis in scale:
        attr = transform.attr("s{}".format(axis))
        if attr.isLocked():
            attr.setLocked(False)
            unlockedAttrs["scale"] += axis
            
    return unlockedAttrs
    
def hideTransforms(transform, translate="xyz", rotate="xyz", scale="xyz"):
    """Hide and make unkeyable transformation channels on the given object.
    
    Returns a dictionary of transform axes that were hidden.
    """
    hiddenAttrs = {"translate": "", "rotate": "", "scale": ""}
    
    for axis in translate:
        attr = transform.attr("t{}".format(axis))
        attr.setKeyable(False)
        attr.showInChannelBox(False)
        hiddenAttrs["translate"] += axis
    for axis in rotate:
        attr = transform.attr("r{}".format(axis))
        attr.setKeyable(False)
        attr.showInChannelBox(False)
        hiddenAttrs["rotate"] += axis
    for axis in scale:
        attr = transform.attr("s{}".format(axis))
        attr.setKeyable(False)
        attr.showInChannelBox(False)
        hiddenAttrs["scale"] += axis
            
    return hiddenAttrs

def showTransforms(transform, translate="xyz", rotate="xyz", scale="xyz"):
    """Show and make keyable transformation channels on the given object.
    
    Returns a dictionary of transform axes that were shown.
    """
    shownAttrs = {"translate": "", "rotate": "", "scale": ""}
    
    for axis in translate:
        attr = transform.attr("t{}".format(axis))
        attr.setKeyable(True)
        attr.showInChannelBox(True)
        shownAttrs["translate"] += axis
    for axis in rotate:
        attr = transform.attr("r{}".format(axis))
        attr.setKeyable(True)
        attr.showInChannelBox(True)
        shownAttrs["rotate"] += axis
    for axis in scale:
        attr = transform.attr("s{}".format(axis))
        attr.setKeyable(True)
        attr.showInChannelBox(True)
        shownAttrs["scale"] += axis
            
    return shownAttrs
    
def lockHideTransforms(transform, **kwargs):
    """Convenience function to both lock and hide transform channels."""
    lockTransforms(transform, **kwargs)
    hideTransforms(transform, **kwargs)
    
def unlockShowTransforms(transform, **kwargs):
    """Convenience function to both unlock and show transform channels."""
    unlockTransforms(transform, **kwargs)
    showTransforms(transform, **kwargs)
    
@contextlib.contextmanager
def unlockTransformsCtx(transform, **kwargs):
    """Context manager which unlocks the given transform channels only for the scope of its code block."""
    unlocked = unlockTransforms(transform, **kwargs)
    yield
    lockTransforms(transform, **unlocked)
    
def copyTranslation(source, target):
    """Moves the position of the target object to the source object in world space."""
    translation = pm.xform(source, q=True, translate=True, worldSpace=True)
    pm.xform(target, translate=translation, worldSpace=True)
    return translation
    
def copyRotation(source, target):
    """Matches the target object's orientation to the source object in world space.
    
    Does not alter target object's rotateOrder
    """
    rotation = pm.xform(source, q=True, rotate=True, worldSpace=True)
    rotateOrder = target.getRotationOrder()
    pm.xform(target, rotate=rotation, worldSpace=True, rotateOrder=source.getRotationOrder())
    target.setRotationOrder(rotateOrder, True)
    return rotation
    
def copyTransforms(source, target):
    """Matches the target object's position and orientation to the source's in world space."""
    copyTranslation(source, target)
    copyRotation(source, target)

def alignPlanar(objects, aimAxis=X_AXIS, upAxis=Y_AXIS):
    """Align the given objects such that each object aims to the next,
    with each object's secondary axis aiming along the normal of the plane
    formed by the positions of the first 3 objects.
    """
    if len(objects) < 3:
        raise ValueError("AlignPlanar operation requires at least 3 objects, {} given".format(len(objects)))
        
    objectPositions = [OpenMaya.MVector(pm.xform(obj, q=True, worldSpace=True, translation=True)) for obj in objects]
    v1 = objectPositions[1] - objectPositions[0]
    v2 = objectPositions[2] - objectPositions[1]
    planeNormal = OpenMaya.MVector(v1 ^ v2).normal()
    
    lastAimVector = None
    objectCount = len(objects)
    for i, obj in enumerate(objects):
        position = objectPositions[i]
        if i < objectCount - 1:
            nextPosition = objectPositions[i+1]
            aimVector = OpenMaya.MVector(nextPosition - position).normal()
        else:
            aimVector = lastAimVector

        m = constructAimMatrix(
            aimAxis=aimAxis,
            aimVector=aimVector,
            upAxis=upAxis,
            upVector=planeNormal,
            position=position)
        children = pm.listRelatives(obj, children=True)
        for child in children:
            child.setParent(world=True)
        pm.xform(obj, matrix=m, worldSpace=True)
        for child in children:
            child.setParent(obj)
        lastAimVector = aimVector

# Orient to World

# Duplicate Chain

# Flip Axis

def constructAimMatrix(aimAxis, aimVector, upAxis, upVector, position=OpenMaya.MVector.kZeroVector):
    """Returns an normalized orthagonal MMatrix that is oriented using the given vectors"""
    aimAxis = Axis(aimAxis)
    upAxis = Axis(upAxis)
    aimVector = OpenMaya.MVector(aimVector)
    upVector = OpenMaya.MVector(upVector)
    
    axisVector = {X_AXIS: None, Y_AXIS: None, Z_AXIS: None}
    axisVector[aimAxis.positive()] = -aimVector if aimAxis.isNegative else aimVector
    axisVector[upAxis.positive()] = -upVector if upAxis.isNegative else upVector
    
    # Calculate the missing axis using cross product
    # X^Y=Z, Y^Z=X, Z^X=Y
    axisList = (X_AXIS, Y_AXIS, Z_AXIS)
    for axis in axisList:
        if axisVector[axis] is None:
            v1 = axisVector[(axis - 2) % 3]
            v2 = axisVector[(axis - 1) % 3]
            axisVector[axis] = v1 ^ v2
            break
    
    # If the given up vector is not orthagonal to the aim vector, it needs to be recalculated
    i = upAxis.positive()
    v1 = axisVector[(i - 2) % 3]
    v2 = axisVector[(i - 1) % 3]
    axisVector[upAxis.positive()] = v1 ^ v2
    
    x = axisVector[X_AXIS].normal()
    y = axisVector[Y_AXIS].normal()
    z = axisVector[Z_AXIS].normal()
    p = position
    
    m = [[x[0], x[1], x[2], 0.0],
         [y[0], y[1], y[2], 0.0],
         [z[0], z[1], z[2], 0.0],
         [p[0], p[1], p[2], 1.0]]
        
    return OpenMaya.MMatrix(m)