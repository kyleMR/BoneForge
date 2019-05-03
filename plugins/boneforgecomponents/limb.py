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


class SkeletonGuideLimb(OpenMayaUI.MPxLocatorNode):
    id = typeid.GUIDELIMB
    drawDbClassification = "drawdb/geometry/skeletonGuideLimb"
    drawRegistrantId = "SkeletonGuideLimbPlugin"

    # Attributes
    boundingBoxCorner1 = None
    boundingBoxCorner2 = None

    forgeID = None

    guideMatrix = None
    handleInverseScale = None

    aimAxis = None
    upAxis = None
    aimVector = None
    upVector = None
    provideAimVector = None

    baseMatrix = None
    hingeMatrix = None
    endMatrix = None
    useChildBaseAsEnd = None

    handle = None

    handleColor = None

    orientGroup = None
    orientGroupTranslateX = None
    orientGroupTranslateY = None
    orientGroupTranslateZ = None
    orientGroupTranslate = None
    orientGroupRotateX = None
    orientGroupRotateY = None
    orientGroupRotateZ = None
    orientGroupRotate = None

    parentGuide = None
    parentGuideHandleIndex = None
    childGuide = None

    borderPad = 1.0

    @staticmethod
    def creator():
        return SkeletonGuideLimb()

    @classmethod
    def initialize(cls):
        nAttr = OpenMaya.MFnNumericAttribute()
        tAttr = OpenMaya.MFnTypedAttribute()
        uAttr = OpenMaya.MFnUnitAttribute()
        enumAttr = OpenMaya.MFnEnumAttribute()
        compAttr = OpenMaya.MFnCompoundAttribute()
        matrixAttr = OpenMaya.MFnMatrixAttribute()
        messageAttr = OpenMaya.MFnMessageAttribute()

        cls.forgeID = tAttr.create("forgeID",
                                   "fid",
                                   OpenMaya.MFnData.kString,
                                   OpenMaya.MObject.kNullObj)
        cls.addAttribute(cls.forgeID)

        cls.guideMatrix = matrixAttr.create("guideMatrix",
                                            "gm",
                                            OpenMaya.MFnMatrixAttribute.kDouble)
        cls.addAttribute(cls.guideMatrix)

        cls.handleInverseScale = nAttr.create("handleInverseScale",
                                              "his",
                                              OpenMaya.MFnNumericData.k3Double,
                                              1.0)
        cls.addAttribute(cls.handleInverseScale)

        cls.boundingBoxCorner1 = nAttr.create("boundingBoxCorner1",
                                              "bb1",
                                              OpenMaya.MFnNumericData.k3Double,
                                              0)
        nAttr.keyable = False
        cls.addAttribute(cls.boundingBoxCorner1)
        cls.boundingBoxCorner2 = nAttr.create("boundingBoxCorner2",
                                              "bb2",
                                              OpenMaya.MFnNumericData.k3Double,
                                              0)
        nAttr.keyable = False
        cls.addAttribute(cls.boundingBoxCorner2)

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

        cls.provideAimVector = nAttr.create("provideAimVector", "pav", OpenMaya.MFnNumericData.kBoolean, 0)
        cls.addAttribute(cls.provideAimVector)

        cls.baseMatrix = matrixAttr.create("baseMatrix",
                                           "base",
                                           OpenMaya.MFnMatrixAttribute.kDouble)
        cls.addAttribute(cls.baseMatrix)

        cls.hingeMatrix = matrixAttr.create("hingeMatrix",
                                            "hng",
                                            OpenMaya.MFnMatrixAttribute.kDouble)
        cls.addAttribute(cls.hingeMatrix)

        cls.endMatrix = matrixAttr.create("endMatrix",
                                          "end",
                                          OpenMaya.MFnMatrixAttribute.kDouble)
        cls.addAttribute(cls.endMatrix)

        cls.useChildBaseAsEnd = nAttr.create("useChildBaseAsEnd", "ucb", OpenMaya.MFnNumericData.kBoolean, 0)
        cls.addAttribute(cls.useChildBaseAsEnd)

        cls.handle = messageAttr.create("handle", "hndl")
        messageAttr.array = True
        cls.addAttribute(cls.handle)

        cls.handleColor = nAttr.createColor("handleColor", "hc")
        cls.addAttribute(cls.handleColor)

        cls.orientGroup = messageAttr.create("orientGroup", "ogrp")
        cls.addAttribute(cls.orientGroup)

        cls.orientGroupTranslateX = uAttr.create("orientGroupTranslateX", "ogtx", OpenMaya.MFnUnitAttribute.kDistance, 0.0)
        cls.orientGroupTranslateY = uAttr.create("orientGroupTranslateY", "ogty", OpenMaya.MFnUnitAttribute.kDistance, 0.0)
        cls.orientGroupTranslateZ = uAttr.create("orientGroupTranslateZ", "ogtz", OpenMaya.MFnUnitAttribute.kDistance, 0.0)
        cls.orientGroupTranslate = nAttr.create("orientGroupTranslate",
                                             "ogt",
                                             cls.orientGroupTranslateX,
                                             cls.orientGroupTranslateY,
                                             cls.orientGroupTranslateZ)
        cls.addAttribute(cls.orientGroupTranslate)

        cls.orientGroupRotateX = uAttr.create("orientGroupRotateX", "ogrx", OpenMaya.MFnUnitAttribute.kAngle, 0.0)
        cls.orientGroupRotateY = uAttr.create("orientGroupRotateY", "ogry", OpenMaya.MFnUnitAttribute.kAngle, 0.0)
        cls.orientGroupRotateZ = uAttr.create("orientGroupRotateZ", "ogrz", OpenMaya.MFnUnitAttribute.kAngle, 0.0)
        cls.orientGroupRotate = nAttr.create("orientGroupRotate",
                                             "ogr",
                                             cls.orientGroupRotateX,
                                             cls.orientGroupRotateY,
                                             cls.orientGroupRotateZ)
        cls.addAttribute(cls.orientGroupRotate)

        cls.parentGuide = messageAttr.create("parentGuide", "pg")
        cls.addAttribute(cls.parentGuide)

        cls.parentGuideHandleIndex = nAttr.create("parentGuideHandleIndex", "pghi", OpenMaya.MFnNumericData.kShort, -1)
        cls.addAttribute(cls.parentGuideHandleIndex)

        cls.childGuide = messageAttr.create("childGuide", "cg")
        cls.addAttribute(cls.childGuide)

        cls.attributeAffects(cls.guideMatrix, cls.boundingBoxCorner1)
        cls.attributeAffects(cls.guideMatrix, cls.boundingBoxCorner2)
        # cls.attributeAffects(cls.baseMatrix, cls.boundingBoxCorner1)
        # cls.attributeAffects(cls.baseMatrix, cls.boundingBoxCorner2)
        cls.attributeAffects(cls.baseMatrix, cls.orientGroupTranslate)
        cls.attributeAffects(cls.baseMatrix, cls.orientGroupRotate)
        cls.attributeAffects(cls.baseMatrix, cls.aimVector)
        cls.attributeAffects(cls.baseMatrix, cls.upVector)
        # cls.attributeAffects(cls.hingeMatrix, cls.boundingBoxCorner1)
        # cls.attributeAffects(cls.hingeMatrix, cls.boundingBoxCorner2)
        cls.attributeAffects(cls.hingeMatrix, cls.orientGroupTranslate)
        cls.attributeAffects(cls.hingeMatrix, cls.orientGroupRotate)
        cls.attributeAffects(cls.hingeMatrix, cls.aimVector)
        cls.attributeAffects(cls.hingeMatrix, cls.upVector)
        # cls.attributeAffects(cls.endMatrix, cls.boundingBoxCorner1)
        # cls.attributeAffects(cls.endMatrix, cls.boundingBoxCorner2)
        cls.attributeAffects(cls.endMatrix, cls.orientGroupTranslate)
        cls.attributeAffects(cls.endMatrix, cls.orientGroupRotate)
        cls.attributeAffects(cls.endMatrix, cls.aimVector)
        cls.attributeAffects(cls.endMatrix, cls.upVector)
        cls.attributeAffects(cls.guideMatrix, cls.handleInverseScale)
        cls.attributeAffects(cls.provideAimVector, cls.aimVector)

    def __init__(self):
        super(SkeletonGuideLimb, self).__init__()

    def postConstructor(self):
        nodeFn = OpenMaya.MFnDependencyNode(self.thisMObject())
        nodeFn.setName("skeletonGuideLimbShape#")
        plug = nodeFn.findPlug("forgeID", False)
        plug.setString(util.generateID())

    def compute(self, plug, dataBlock):
        boundsRelatedPlugs = (self.boundingBoxCorner1,
                              self.boundingBoxCorner2,
                              self.orientGroupRotate,
                              self.aimVector,
                              self.upVector)
        if plug == self.handleInverseScale:
            self.computeInverseScale(plug, dataBlock)
        elif plug in boundsRelatedPlugs:
            self.computeBounds(plug, dataBlock)

    def computeBounds(self, plug, dataBlock):
        guideMatrix = OpenMaya.MMatrix(dataBlock.inputValue(self.guideMatrix).asMatrix())
        guideInverse = guideMatrix.inverse()
        guidePosition = OpenMaya.MVector(
            OpenMaya.MTransformationMatrix(guideMatrix).translation(
                OpenMaya.MSpace.kPostTransform))


        # projectedPoints = OpenMaya.MPointArray()
        # projectionAxis = OpenMaya.MVector([1.0, 0.0, 0.0]) * guideMatrix
        # projectionAxis.normalize()

        # while not handles.isDone():
        #     currentHandle = handles.inputValue()
        #     inMatrix = OpenMaya.MMatrix(currentHandle.asMatrix())
        #     handlePosition = OpenMaya.MVector(
        #         OpenMaya.MTransformationMatrix(inMatrix).translation(
        #             OpenMaya.MSpace.kPostTransform))
        #     localPosition = handlePosition - guidePosition
        #     length = localPosition * projectionAxis
        #     projectedPoint = OpenMaya.MPoint(handlePosition - (projectionAxis * length))
        #     localPosition = projectedPoint * guideInverse
        #     projectedPoints.append(localPosition)
        #     handles.next()

        # Bounds
        lowerHandle = dataBlock.outputValue(self.boundingBoxCorner1)
        upperHandle = dataBlock.outputValue(self.boundingBoxCorner2)

        xValues = []
        yValues = []
        zValues = []

        # for pt in projectedPoints:
        #     xValues.append(pt.x)
        #     yValues.append(pt.y)
        #     zValues.append(pt.z)

        if not xValues:
            xValues = yValues = zValues = [0.0]

        minPoint = OpenMaya.MPoint([min(xValues), min(yValues), min(zValues)])
        maxPoint = OpenMaya.MPoint([max(xValues), max(yValues), max(zValues)])
        minPoint -= self.borderPad * OpenMaya.MVector([0.0, 1.0, 1.0])
        maxPoint += self.borderPad * OpenMaya.MVector([0.0, 1.0, 1.0])

        lowerHandle.set3Double(minPoint[0], minPoint[1], minPoint[2])
        upperHandle.set3Double(maxPoint[0], maxPoint[1], maxPoint[2])
        lowerHandle.setClean()
        upperHandle.setClean()

        # Orient Group
        baseMatrix = OpenMaya.MMatrix(dataBlock.inputValue(self.baseMatrix).asMatrix())
        hingeMatrix = OpenMaya.MMatrix(dataBlock.inputValue(self.hingeMatrix).asMatrix())
        endMatrix = OpenMaya.MMatrix(dataBlock.inputValue(self.endMatrix).asMatrix())
        basePos = OpenMaya.MTransformationMatrix(baseMatrix).translation(OpenMaya.MSpace.kPostTransform)
        midPos = OpenMaya.MTransformationMatrix(hingeMatrix).translation(
            OpenMaya.MSpace.kPostTransform)
        endPos = OpenMaya.MTransformationMatrix(endMatrix).translation(OpenMaya.MSpace.kPostTransform)

        upperVec = midPos - basePos
        lowerVec = endPos - midPos
        upVector = (upperVec ^ lowerVec).normal()
        aimVector = (endPos - basePos).normal()

        if upVector == OpenMaya.MVector.kZeroVector:
            # Set a default up vector in case all 3 handles are in a perfect line
            upVector = OpenMaya.MVector([guideMatrix[8], guideMatrix[9], guideMatrix[10]])

        lastVector = aimVector ^ upVector
        transformMatrix = OpenMaya.MMatrix([
            aimVector.x, aimVector.y, aimVector.z, 0.0,
            upVector.x, upVector.y, upVector.z, 0.0,
            lastVector.x, lastVector.y, lastVector.z, 0.0,
            basePos.x, basePos.y, basePos.z, 1.0
        ])

        xformMatrix = transformMatrix * guideInverse
        t = OpenMaya.MTransformationMatrix(xformMatrix).translation(OpenMaya.MSpace.kPostTransform)
        r = OpenMaya.MTransformationMatrix(xformMatrix).rotation()
        transHandle = dataBlock.outputValue(self.orientGroupTranslate)
        transHandle.set3Double(t.x, t.y, t.z)
        rotXHandle = dataBlock.outputValue(self.orientGroupRotateX)
        rotYHandle = dataBlock.outputValue(self.orientGroupRotateY)
        rotZHandle = dataBlock.outputValue(self.orientGroupRotateZ)
        rotXHandle.setMAngle(OpenMaya.MAngle(r.x, OpenMaya.MAngle.kRadians))
        rotYHandle.setMAngle(OpenMaya.MAngle(r.y, OpenMaya.MAngle.kRadians))
        rotZHandle.setMAngle(OpenMaya.MAngle(r.z, OpenMaya.MAngle.kRadians))
        dataBlock.setClean(self.orientGroupTranslate)
        dataBlock.setClean(self.orientGroupRotate)

        upHandle = dataBlock.outputValue(self.upVector)
        aimHandle = dataBlock.outputValue(self.aimVector)
        upHandle.set3Double(*upVector)
        aimHandle.set3Double(*aimVector)
        upHandle.setClean()
        aimHandle.setClean()

    def computeInverseScale(self, plug, dataBlock):
        guideMatrix = OpenMaya.MMatrix(dataBlock.inputValue(self.guideMatrix).asMatrix())
        invScaleMatrix = OpenMaya.MTransformationMatrix(guideMatrix).asMatrixInverse()
        scale = OpenMaya.MTransformationMatrix(invScaleMatrix).scale(
            OpenMaya.MSpace.kPostTransform)

        outPlug = dataBlock.outputValue(self.handleInverseScale)
        outPlug.set3Double(*scale)
        outPlug.setClean()

    def isBounded(self):
        return True

    def boundingBox(self):
        block = self.forceCache()
        lowerHandle = block.inputValue(self.boundingBoxCorner1)
        upperHandle = block.inputValue(self.boundingBoxCorner2)
        corner1 = OpenMaya.MPoint(*lowerHandle.asDouble3())
        corner2 = OpenMaya.MPoint(*upperHandle.asDouble3())
        return OpenMaya.MBoundingBox(corner1, corner2)


# Viewport 2.0 Draw Override
class GuideLimbData(OpenMaya.MUserData):
    def __init__(self):
        super(GuideLimbData, self).__init__(False)  # deleteAfterUse=False
        self.boundingBoxCorner1 = None
        self.boundingBoxCorner2 = None
        self.basePosition = None
        self.midPosition = None
        self.endPosition = None

class SkeletonGuideLimbDrawOverride(OpenMayaRender.MPxDrawOverride):

    GuideClass = SkeletonGuideLimb

    def __init__(self, obj):
        super(SkeletonGuideLimbDrawOverride,
              self).__init__(obj,
                             SkeletonGuideLimbDrawOverride.draw)

    @staticmethod
    def creator(obj):
        return SkeletonGuideLimbDrawOverride(obj)

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
        if not isinstance(data, GuideLimbData):
            data = GuideLimbData()

        controlNode = objPath.node()

        controlNode = objPath.node()
        plug = OpenMaya.MPlug(controlNode, self.GuideClass.boundingBoxCorner1)
        plugData = OpenMaya.MFnNumericData(plug.asMObject())
        corner1 = plugData.getData()
        plug = OpenMaya.MPlug(controlNode, self.GuideClass.boundingBoxCorner2)
        plugData.setObject(plug.asMObject())
        corner2 = plugData.getData()
        data.boundingBoxCorner1 = OpenMaya.MPoint(corner1[0], corner1[1], corner1[2])
        data.boundingBoxCorner2 = OpenMaya.MPoint(corner2[0], corner2[1], corner2[2])

        plug.setAttribute(self.GuideClass.guideMatrix)
        guideMatrix = OpenMaya.MFnMatrixData(plug.asMObject()).matrix()
        guideInverse = guideMatrix.inverse()

        plug.setAttribute(self.GuideClass.baseMatrix)
        baseMatrix = OpenMaya.MFnMatrixData(plug.asMObject()).matrix()
        baseMatrix *= guideInverse
        data.basePosition = OpenMaya.MPoint(
            OpenMaya.MTransformationMatrix(baseMatrix).translation(OpenMaya.MSpace.kPostTransform)
        )

        plug.setAttribute(self.GuideClass.hingeMatrix)
        hingeMatrix = OpenMaya.MFnMatrixData(plug.asMObject()).matrix()
        hingeMatrix *= guideInverse
        data.midPosition = OpenMaya.MPoint(
            OpenMaya.MTransformationMatrix(hingeMatrix).translation(
                OpenMaya.MSpace.kPostTransform))

        plug.setAttribute(self.GuideClass.endMatrix)
        endMatrix = OpenMaya.MFnMatrixData(plug.asMObject()).matrix()
        endMatrix *= guideInverse
        data.endPosition = OpenMaya.MPoint(
            OpenMaya.MTransformationMatrix(endMatrix).translation(OpenMaya.MSpace.kPostTransform)
        )

        return data

    def hasUIDrawables(self):
        return True

    def addUIDrawables(self, objPath, drawManager, frameContext, data):
        if not isinstance(data, GuideLimbData):
            return

        normalVector = OpenMaya.MVector([1.0, 0.0, 0.0])
        bounding = OpenMaya.MBoundingBox(data.boundingBoxCorner1, data.boundingBoxCorner2)
        up = OpenMaya.MVector.kYaxisVector
        width = bounding.depth / 2.0
        height = bounding.height / 2.0

        dormantBorderColor = OpenMaya.MColor([0.0, 0.0, 0.8, 1.0])
        leadBorderColor = OpenMaya.MColor([1.0, 1.0, 1.0, 1.0])
        activeBorderColor = OpenMaya.MColor([0.4, 0.8, 1.0, 1.0])
        lineColor = OpenMaya.MColor([1.0, 1.0, 1.0, 1.0])
        fillColor = OpenMaya.MColor([0.0, 0.0, 1.0, 1.0])
        fillColor.a = 0.4
        borderWidth = 1.0
        lineWidth = 2.0

        displayStatus = OpenMayaRender.MGeometryUtilities.displayStatus(objPath)
        selected = True
        if displayStatus == util.DisplayStatus.Lead:
            borderColor = leadBorderColor
            borderWidth = 2.0
        elif displayStatus == util.DisplayStatus.Active:
            borderColor = activeBorderColor
            borderWidth = 2.0
        else:
            # kActiveAffected, kDormant, kHilite.
            borderColor = dormantBorderColor
            borderWidth = 1.0
            selected = False

        drawManager.beginDrawable()

        drawManager.setColor(borderColor)
        drawManager.setLineWidth(borderWidth)
        drawManager.rect(bounding.center, up, normalVector, width, height, filled=False)
        # drawManager.setColor(fillColor)
        # drawManager.rect(bounding.center, up, normalVector, width, height, filled=True)

        drawManager.setColor(OpenMaya.MColor([1.0, 1.0, 0.0, 1.0]))
        drawManager.sphere(data.basePosition, 1.5, filled=False)
        drawManager.sphere(data.midPosition, 1.5, filled=False)
        drawManager.sphere(data.endPosition, 1.5, filled=False)

        drawManager.endDrawable()
