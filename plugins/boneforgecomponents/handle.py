import sys

import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.api.OpenMayaAnim as OpenMayaAnim
import maya.api.OpenMayaRender as OpenMayaRender

from . import typeid
from . import util

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass

class GuideHandle(OpenMayaUI.MPxLocatorNode):
    id = typeid.GUIDEHANDLE
    drawDbClassification = "drawdb/geometry/guideHandle"
    drawRegistrantId = "GuideHandlePlugin"

    # Attributes
    boundingBoxCorner1 = None
    boundingBoxCorner2 = None

    forgeID = None

    handleMatrix = None
    guideInverseScale = None
    guide = None
    parentHandle = None
    parentHandleMatrix = None
    childHandle = None
    childHandleMatrix = None
    orientTarget = None
    orientTargetMatrix = None

    childPosition = None

    jointRotateOrder = None
    jointSide = None
    jointExcludeFromBind = None

    aimAxis = None
    upAxis = None
    aimVector = None
    upVector = None
    useGuideAim = None
    jointMatrix = None

    handleColor = None
    handleStyle = None

    @staticmethod
    def creator():
        return GuideHandle()

    @classmethod
    def initialize(cls):
        nAttr = OpenMaya.MFnNumericAttribute()
        tAttr = OpenMaya.MFnTypedAttribute()
        enumAttr = OpenMaya.MFnEnumAttribute()
        compAttr = OpenMaya.MFnCompoundAttribute()
        matrixAttr = OpenMaya.MFnMatrixAttribute()
        messageAttr = OpenMaya.MFnMessageAttribute()

        cls.boundingBoxCorner1 = nAttr.create("boundingBoxCorner1", "bb1", OpenMaya.MFnNumericData.k3Double, 0)
        nAttr.keyable = False
        cls.addAttribute(cls.boundingBoxCorner1)
        cls.boundingBoxCorner2 = nAttr.create("boundingBoxCorner2", "bb2", OpenMaya.MFnNumericData.k3Double, 0)
        nAttr.keyable = False
        cls.addAttribute(cls.boundingBoxCorner2)

        cls.forgeID = tAttr.create("forgeID", "fid", OpenMaya.MFnData.kString, OpenMaya.MObject.kNullObj)
        cls.addAttribute(cls.forgeID)

        cls.handleMatrix = matrixAttr.create("handleMatrix", "hm", OpenMaya.MFnMatrixAttribute.kDouble)
        cls.addAttribute(cls.handleMatrix)

        cls.guideInverseScale = nAttr.create("guideInverseScale", "gis", OpenMaya.MFnNumericData.k3Double, 1.0)
        cls.addAttribute(cls.guideInverseScale)

        cls.guide = messageAttr.create("guide", "g")
        cls.addAttribute(cls.guide)

        cls.parentHandle = messageAttr.create("parentHandle", "ph")
        cls.addAttribute(cls.parentHandle)

        cls.parentHandleMatrix = matrixAttr.create("parentHandleMatrix", "phm", OpenMaya.MFnMatrixAttribute.kDouble)
        cls.addAttribute(cls.parentHandleMatrix)

        cls.childHandle = messageAttr.create("childHandle", "ch")
        messageAttr.array = True
        cls.addAttribute(cls.childHandle)

        cls.childHandleMatrix = matrixAttr.create("childHandleMatrix", "chm", OpenMaya.MFnMatrixAttribute.kDouble)
        matrixAttr.array = True
        cls.addAttribute(cls.childHandleMatrix)

        cls.orientTarget = messageAttr.create("orientTarget", "ot")
        cls.addAttribute(cls.orientTarget)

        cls.orientTargetMatrix = matrixAttr.create("orientTargetMatrix", "otm", OpenMaya.MFnMatrixAttribute.kDouble)
        cls.addAttribute(cls.orientTargetMatrix)

        cls.childPosition = nAttr.create("childPosition", "cpos", OpenMaya.MFnNumericData.k3Double, 0)
        nAttr.array = True
        nAttr.usesArrayDataBuilder = True
        cls.addAttribute(cls.childPosition)

        cls.jointRotateOrder = enumAttr.create("jointRotateOrder", "jro", 0)
        enumAttr.addField("xyz", 0)
        enumAttr.addField("yzx", 1)
        enumAttr.addField("zxy", 2)
        enumAttr.addField("xzy", 3)
        enumAttr.addField("yxz", 4)
        enumAttr.addField("zyx", 5)
        enumAttr.keyable = False
        cls.addAttribute(cls.jointRotateOrder)

        cls.jointSide = enumAttr.create("jointSide", "js", 0)
        enumAttr.addField("center", 0)
        enumAttr.addField("left", 1)
        enumAttr.addField("right", 2)
        enumAttr.addField("none", 3)
        enumAttr.keyable = True
        cls.addAttribute(cls.jointSide)

        cls.jointExcludeFromBind = nAttr.create("jointExcludeFromBind", "jeb", OpenMaya.MFnNumericData.kBoolean, 0)
        cls.addAttribute(cls.jointExcludeFromBind)

        cls.aimAxis = enumAttr.create("aimAxis", "aa", 0)
        enumAttr.addField("X", 0)
        enumAttr.addField("Y", 1)
        enumAttr.addField("Z", 2)
        enumAttr.addField("-X", 3)
        enumAttr.addField("-Y", 4)
        enumAttr.addField("-Z", 5)
        enumAttr.keyable = False
        cls.addAttribute(cls.aimAxis)

        cls.upAxis = enumAttr.create("upAxis", "ua", 2)
        enumAttr.addField("X", 0)
        enumAttr.addField("Y", 1)
        enumAttr.addField("Z", 2)
        enumAttr.addField("-X", 3)
        enumAttr.addField("-Y", 4)
        enumAttr.addField("-Z", 5)
        enumAttr.keyable = False
        cls.addAttribute(cls.upAxis)

        cls.aimVector = nAttr.create("aimVector", "av", OpenMaya.MFnNumericData.k3Double)
        cls.addAttribute(cls.aimVector)

        cls.upVector = nAttr.create("upVector", "uv", OpenMaya.MFnNumericData.k3Double)
        cls.addAttribute(cls.upVector)

        cls.useGuideAim = nAttr.create("useGuideAim", "uga", OpenMaya.MFnNumericData.kBoolean)
        cls.addAttribute(cls.useGuideAim)

        cls.jointMatrix = matrixAttr.create("jointMatrix", "jm", OpenMaya.MFnMatrixAttribute.kDouble)
        cls.addAttribute(cls.jointMatrix)

        cls.handleColor = nAttr.createColor("handleColor", "hc")
        cls.addAttribute(cls.handleColor)

        cls.handleStyle = enumAttr.create("handleStyle", "hs", 0)
        enumAttr.addField("basic", 0)
        enumAttr.addField("spine", 1)
        enumAttr.addField("limb", 2)
        enumAttr.addField("limb base", 3)
        enumAttr.addField("limb hinge", 4)
        enumAttr.addField("limb end", 5)
        enumAttr.addField("free", 6)
        enumAttr.addField("world", 7)
        cls.addAttribute(cls.handleStyle)

        cls.attributeAffects(cls.handleMatrix, cls.boundingBoxCorner1)
        cls.attributeAffects(cls.handleMatrix, cls.boundingBoxCorner2)
        cls.attributeAffects(cls.handleMatrix, cls.childPosition)
        cls.attributeAffects(cls.childHandleMatrix, cls.boundingBoxCorner1)
        cls.attributeAffects(cls.childHandleMatrix, cls.boundingBoxCorner2)
        cls.attributeAffects(cls.childHandleMatrix, cls.childPosition)
        cls.attributeAffects(cls.handleStyle, cls.boundingBoxCorner1)
        cls.attributeAffects(cls.handleStyle, cls.boundingBoxCorner2)

        cls.attributeAffects(cls.handleMatrix, cls.jointMatrix)
        cls.attributeAffects(cls.orientTargetMatrix, cls.jointMatrix)
        cls.attributeAffects(cls.parentHandleMatrix, cls.jointMatrix)
        cls.attributeAffects(cls.aimAxis, cls.jointMatrix)
        cls.attributeAffects(cls.upAxis, cls.jointMatrix)
        cls.attributeAffects(cls.aimVector, cls.jointMatrix)
        cls.attributeAffects(cls.upVector, cls.jointMatrix)
        cls.attributeAffects(cls.useGuideAim, cls.jointMatrix)

    def __init__(self):
        super(GuideHandle, self).__init__()

    def postConstructor(self):
        nodeFn = OpenMaya.MFnDependencyNode(self.thisMObject())
        nodeFn.setName("guideHandleShape#")
        plug = nodeFn.findPlug("forgeID", False)
        plug.setString(util.generateID())

    def isBounded(self):
        return True

    def boundingBox(self):
        block = self.forceCache()
        lowerHandle = block.inputValue(self.boundingBoxCorner1)
        upperHandle = block.inputValue(self.boundingBoxCorner2)
        corner1 = OpenMaya.MPoint(*lowerHandle.asDouble3())
        corner2 = OpenMaya.MPoint(*upperHandle.asDouble3())
        return OpenMaya.MBoundingBox(corner1, corner2)

    def compute(self, plug, dataBlock):
        boundsRelatedPlugs = self.boundingBoxCorner1, self.boundingBoxCorner2, self.childPosition
        if plug == self.jointMatrix:
            self.computeJointMatrix(plug, dataBlock)
        elif plug in boundsRelatedPlugs:
            self.computeBounds(plug, dataBlock)

    def computeJointMatrix(self, plug, dataBlock):
        matrix = OpenMaya.MMatrix(dataBlock.inputValue(self.handleMatrix).asMatrix())
        position = OpenMaya.MTransformationMatrix(matrix).translation(OpenMaya.MSpace.kPostTransform)

        useGuideAim = dataBlock.inputValue(self.useGuideAim).asBool()
        hasOrientTarget = OpenMaya.MPlug(plug.node(), self.orientTarget).isConnected
        hasParent = OpenMaya.MPlug(plug.node(), self.parentHandleMatrix).isConnected
        if useGuideAim or not (hasParent or hasOrientTarget):
            aimVector = OpenMaya.MVector(dataBlock.inputValue(self.aimVector).asDouble3())
        elif hasParent and not hasOrientTarget:
            parentMatrix = OpenMaya.MMatrix(dataBlock.inputValue(self.parentHandleMatrix).asMatrix())
            parentPosition = OpenMaya.MTransformationMatrix(parentMatrix).translation(OpenMaya.MSpace.kPostTransform)
            aimVector = OpenMaya.MVector(position - parentPosition).normal()
        else:
            orientTargetMatrix = OpenMaya.MMatrix(dataBlock.inputValue(self.orientTargetMatrix).asMatrix())
            targetPosition = OpenMaya.MTransformationMatrix(orientTargetMatrix).translation(OpenMaya.MSpace.kPostTransform)
            aimVector = OpenMaya.MVector(targetPosition - position).normal()

        upVector = OpenMaya.MVector(dataBlock.inputValue(self.upVector).asDouble3())
        aimAxis = dataBlock.inputValue(self.aimAxis).asShort()
        upAxis = dataBlock.inputValue(self.upAxis).asShort()

        aimMatrix = self.buildAimMatrix(aimVector, upVector, aimAxis, upAxis, position)

        outMatrix = dataBlock.outputValue(self.jointMatrix)
        outMatrix.setMMatrix(aimMatrix)
        outMatrix.setClean()

    def buildAimMatrix(self, aimVector, upVector, aimAxis, upAxis, position):
        axisVectors = dict(zip(range(3), [None]*3))
        absAimAxis = aimAxis % 3
        absUpAxis = upAxis % 3
        absAimVector = aimVector if aimAxis < 3 else -aimVector
        absUpVector = upVector if upAxis < 3 else -upVector

        axisVectors[absAimAxis] = absAimVector
        axisVectors[absUpAxis] = absUpVector

        for axis in range(3):
            if axisVectors[axis] is None:
                vec1 = axisVectors[(axis - 2) % 3]
                vec2 = axisVectors[(axis - 1) % 3]
                axisVectors[axis] = vec1 ^ vec2
                break

        # Orthagonalize matrix by recomputing orthagonal up vector
        vec1 = axisVectors[(absUpAxis - 2) % 3]
        vec2 = axisVectors[(absUpAxis - 1) % 3]
        axisVectors[absUpAxis] = vec1 ^ vec2

        x = axisVectors[0].normal()
        y = axisVectors[1].normal()
        z = axisVectors[2].normal()
        p = OpenMaya.MPoint(position)

        m = OpenMaya.MMatrix([x.x, x.y, x.z, 0.0,
                              y.x, y.y, y.z, 0.0,
                              z.x, z.y, z.z, 0.0,
                              p.x, p.y, p.z, 1.0])

        return m

    def computeBounds(self, plug, dataBlock):
        handleMatrix = OpenMaya.MMatrix(dataBlock.inputValue(self.handleMatrix).asMatrix())
        handleMatrixInverse = handleMatrix.inverse()

        projectedPoints = OpenMaya.MPointArray()
        matrices = dataBlock.inputArrayValue(self.childHandleMatrix)
        while not matrices.isDone():
            dataHandle = matrices.inputValue()

            idx = matrices.elementLogicalIndex()
            matrixPlug = OpenMaya.MPlug(plug.node(), self.childHandleMatrix).elementByLogicalIndex(idx)
            if matrixPlug.isConnected:
                childMatrix = OpenMaya.MMatrix(dataHandle.asMatrix())
                local = childMatrix * handleMatrixInverse
                pt = OpenMaya.MTransformationMatrix(local).translation(OpenMaya.MSpace.kPostTransform)
                projectedPoints.append(pt)
            matrices.next()

        outputArray = dataBlock.outputArrayValue(self.childPosition)
        builder = OpenMaya.MArrayDataBuilder(dataBlock, self.childPosition, len(projectedPoints))

        for i, pt in enumerate(projectedPoints):
            handle = builder.addElement(i)
            handle.set3Double(pt.x, pt.y, pt.z)

        outputArray.set(builder)
        dataBlock.setClean(self.childPosition)

        # Compute Bounding box based on child positions
        radius = 1
        bounds = OpenMaya.MBoundingBox(
            OpenMaya.MPoint(-radius, -radius, -radius),
            OpenMaya.MPoint(radius, radius, radius),
            )

        for pt in projectedPoints:
            bounds.expand(pt)

        lowerHandle = dataBlock.outputValue(self.boundingBoxCorner1)
        upperHandle = dataBlock.outputValue(self.boundingBoxCorner2)
        minPt = bounds.min
        maxPt = bounds.max
        lowerHandle.set3Double(minPt.x, minPt.y, minPt.z)
        upperHandle.set3Double(maxPt.x, maxPt.y, maxPt.z)
        lowerHandle.setClean()
        upperHandle.setClean()

    def childPts(self):
        dataBlock = self.forceCache()
        positions = dataBlock.inputArrayValue(self.childPosition)
        pts = OpenMaya.MPointArray()
        while not positions.isDone():
            current = positions.inputValue()
            pos = OpenMaya.MPoint(current.asDouble3())
            pts.append(pos)
            positions.next()
        return pts


# Viewport 2.0 Draw Override
class GuideHandleData(OpenMaya.MUserData):
    def __init__(self):
        super(GuideHandleData, self).__init__(False) # deleteAfterUse=False
        self.childPositions = None
        self.inverseMatrix = None
        self.handleColor = None
        self.jointMatrix = None
        self.hasGuide = None

class GuideHandleDrawOverride(OpenMayaRender.MPxDrawOverride):

    GuideClass = GuideHandle

    def __init__(self, obj):
        super(GuideHandleDrawOverride, self).__init__(obj, GuideHandleDrawOverride.draw)

    @staticmethod
    def creator(obj):
        return GuideHandleDrawOverride(obj)

    @staticmethod
    def draw(context, data):
        pass

    def supportedDrawAPIs(self):
        # Supports both GL and DX
        return OpenMayaRender.MRenderer.kOpenGL | OpenMayaRender.MRenderer.kDirectX11 | OpenMayaRender.MRenderer.kOpenGLCoreProfile

    def isBounded(self, objPath, cameraPath):
        return True

    def boundingBox(self, objPath, cameraPath):
        controlNode = objPath.node()
        c1Plug = OpenMaya.MPlug(controlNode, self.GuideClass.boundingBoxCorner1)
        c2Plug = OpenMaya.MPlug(controlNode, self.GuideClass.boundingBoxCorner2)

        corner1Object = c1Plug.asMObject()
        corner2Object = c2Plug.asMObject()

        fnData = OpenMaya.MFnNumericData()
        fnData.setObject(corner1Object)
        corner1 = fnData.getData()
        fnData.setObject(corner2Object)
        corner2 = fnData.getData()

        corner1Point = OpenMaya.MPoint(corner1[0], corner1[1], corner1[2])
        corner2Point = OpenMaya.MPoint(corner2[0], corner2[1], corner2[2])
        return OpenMaya.MBoundingBox(corner1Point, corner2Point)

    def prepareForDraw(self, objPath, cameraPath, frameContext, oldData):
        data = oldData
        if not isinstance(data, GuideHandleData):
            data = GuideHandleData()

        controlNode = objPath.node()

        data.childPositions = OpenMaya.MPointArray()
        plug = OpenMaya.MPlug(controlNode, self.GuideClass.childPosition)
        fnData = OpenMaya.MFnNumericData()
        for i in xrange(plug.numElements()):
            handle = plug.elementByPhysicalIndex(i)
            fnData.setObject(handle.asMObject())
            pt = OpenMaya.MPoint(fnData.getData())
            data.childPositions.append(pt)

        plug.setAttribute(self.GuideClass.handleMatrix)
        handleMatrix = OpenMaya.MFnMatrixData(plug.asMObject()).matrix()
        data.inverseMatrix = handleMatrix.inverse()

        plug.setAttribute(self.GuideClass.handleColor)
        colorData = OpenMaya.MFnNumericData(plug.asMObject())
        data.handleColor = OpenMaya.MColor(colorData.getData())

        plug.setAttribute(self.GuideClass.jointMatrix)
        jointMatrix = OpenMaya.MFnMatrixData(plug.asMObject()).matrix()
        data.jointMatrix = jointMatrix * data.inverseMatrix

        plug.setAttribute(self.GuideClass.guide)
        data.hasGuide = plug.isConnected

        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, objPath, drawManager, frameContext, data):
        if not isinstance(data, GuideHandleData):
            return

        displayStatus = OpenMayaRender.MGeometryUtilities.displayStatus(objPath)
        selected = displayStatus == util.DisplayStatus.Lead or displayStatus == util.DisplayStatus.Active

        mainColor = data.handleColor
        if selected:
            mainColor = OpenMaya.MColor([1.0, 1.0, 1.0, 1.0])
        connectorColor = OpenMaya.MColor(mainColor)
        connectorColor.a = 0.6

        center = OpenMaya.MPoint(0.0, 0.0, 0.0)
        radius = 1.0
        colorR = OpenMaya.MColor([1.0, 0.0, 0.0, 1.0])
        colorG = OpenMaya.MColor([0.0, 1.0, 0.0, 1.0])
        colorB = OpenMaya.MColor([0.0, 0.0, 1.0, 1.0])

        viewDirection = OpenMaya.MVector(frameContext.getTuple(frameContext.kViewDirection))
        viewDirection *= data.inverseMatrix

        drawManager.beginDrawable()
        drawManager.beginDrawInXray()

        drawManager.setColor(mainColor)
        drawManager.sphere(center, radius, filled=True)

        if data.childPositions:
            self.drawConnectors(drawManager, data.childPositions, viewDirection, connectorColor)

        if data.hasGuide:
            x = OpenMaya.MVector(data.jointMatrix[0], data.jointMatrix[1], data.jointMatrix[2]).normal()
            y = OpenMaya.MVector(data.jointMatrix[4], data.jointMatrix[5], data.jointMatrix[6]).normal()
            z = OpenMaya.MVector(data.jointMatrix[8], data.jointMatrix[9], data.jointMatrix[10]).normal()
            pos = OpenMaya.MPoint(data.jointMatrix[12], data.jointMatrix[13], data.jointMatrix[14])

            drawManager.setColor(colorR)
            drawManager.line(pos, pos + x)
            drawManager.setColor(colorG)
            drawManager.line(pos, pos + y)
            drawManager.setColor(colorB)
            drawManager.line(pos, pos + z)

        drawManager.endDrawInXray()
        drawManager.endDrawable()

    def drawConnectors(self, drawManager, childPositions, viewDirection, color):
        radius = 1.0

        triVerts = OpenMaya.MPointArray([
            OpenMaya.MPoint(0.0, 0.0, -radius),
            OpenMaya.MPoint(0.0, 0.0, radius),
            OpenMaya.MPoint(radius, 0.0, 0.0),
            ])

        upVector = -viewDirection.normal()
        for position in childPositions:
            directionVector = OpenMaya.MVector(position)
            length = directionVector.length()
            directionVector.normalize()

            zVector = (directionVector ^ upVector).normal()
            trueUpVector = (zVector ^ directionVector).normal()
            transformMatrix = OpenMaya.MMatrix([
                directionVector.x, directionVector.y, directionVector.z, 0.0,
                trueUpVector.x, trueUpVector.y, trueUpVector.z, 0.0,
                zVector.x, zVector.y, zVector.z, 0.0,
                0.0, 0.0, 0.0, 1.0,
                ])

            finalVerts = OpenMaya.MPointArray()
            for v in triVerts:
                xformed = OpenMaya.MPoint(v)
                xformed.x *= length
                xformed *= transformMatrix
                finalVerts.append(xformed)

            indices = OpenMaya.MUintArray([0, 1, 2])
            drawManager.setColor(color)
            drawManager.mesh(OpenMayaRender.MUIDrawManager.kTriangles, finalVerts, index=indices)

    def draw3DConnectors(self, drawManager, childPositions, color):
        radius = 1.0

        for position in childPositions:
            directionVector = OpenMaya.MVector(position)
            length = directionVector.length()
            directionVector.normalize()

            thick = min(radius*2, radius + length*0.1)
            triVerts = OpenMaya.MPointArray([
                OpenMaya.MPoint(radius, 0.0, 0.0),
                OpenMaya.MPoint(thick, 0.0, -radius),
                OpenMaya.MPoint(thick, radius, 0.0),
                OpenMaya.MPoint(thick, 0.0, radius),
                OpenMaya.MPoint(thick, -radius, 0.0),
                OpenMaya.MPoint(length, 0.0, 0.0),
                ])

            zVector = directionVector^OpenMaya.MVector.kZaxisVector.normal()
            trueUpVector = (zVector ^ directionVector).normal()
            transformMatrix = OpenMaya.MMatrix([
                directionVector.x, directionVector.y, directionVector.z, 0.0,
                trueUpVector.x, trueUpVector.y, trueUpVector.z, 0.0,
                zVector.x, zVector.y, zVector.z, 0.0,
                0.0, 0.0, 0.0, 1.0,
                ])

            finalVerts = OpenMaya.MPointArray()
            for v in triVerts:
                xformed = OpenMaya.MPoint(v)
                xformed *= transformMatrix
                finalVerts.append(xformed)

            indices = OpenMaya.MUintArray([
                0, 1, 2,
                2, 3, 0,
                0, 3, 4,
                4, 1, 0,
                1, 5, 2,
                2, 5, 3,
                3, 5, 4,
                4, 5, 1,
                ])
            drawManager.setColor(color)
            drawManager.mesh(OpenMayaRender.MUIDrawManager.kTriangles, finalVerts, index=indices)

            color.a = 1.0
            drawManager.setColor(color)
            lineIndices = OpenMaya.MUintArray([
                0, 1,
                0, 2,
                0, 3,
                0, 4,
                1, 2,
                2, 3,
                3, 4,
                4, 1,
                1, 5,
                2, 5,
                3, 5,
                4, 5,
                ])
            drawManager.mesh(OpenMayaRender.MUIDrawManager.kLines, finalVerts, index=lineIndices)