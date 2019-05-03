import sys

import maya.api.OpenMaya as OpenMaya
import maya.api.OpenMayaUI as OpenMayaUI
import maya.api.OpenMayaAnim as OpenMayaAnim
import maya.api.OpenMayaRender as OpenMayaRender

import boneforgecomponents.spine as spine
import boneforgecomponents.limb as limb
import boneforgecomponents.block as block
import boneforgecomponents.handle as handle

def maya_useNewAPI():
    """
    The presence of this function tells Maya that the plugin produces, and
    expects to be passed, objects created using the Maya Python API 2.0.
    """
    pass


def initializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj)

    # SPINE #
    try:
        plugin.registerNode(
            "skeletonGuideSpine",
            spine.SkeletonGuideSpine.id,
            spine.SkeletonGuideSpine.creator,
            spine.SkeletonGuideSpine.initialize,
            OpenMaya.MPxNode.kLocatorNode,
            spine.SkeletonGuideSpine.drawDbClassification)
    except RuntimeError:
        sys.stderr.write("Failed to register SkeletonGuideSpine node\n")
        raise

    try:
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator(
            spine.SkeletonGuideSpine.drawDbClassification,
            spine.SkeletonGuideSpine.drawRegistrantId,
            spine.SkeletonGuideSpineDrawOverride.creator)
    except RuntimeError:
        sys.stderr.write("Failed to register SkeletonGuideSpineDrawOverride override\n")
        raise

    # LIMB #
    try:
        plugin.registerNode("skeletonGuideLimb",
                            limb.SkeletonGuideLimb.id,
                            limb.SkeletonGuideLimb.creator,
                            limb.SkeletonGuideLimb.initialize,
                            OpenMaya.MPxNode.kLocatorNode,
                            limb.SkeletonGuideLimb.drawDbClassification)
    except RuntimeError:
        sys.stderr.write("Failed to register SkeletonGuideLimb node\n")
        raise

    try:
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator(
            limb.SkeletonGuideLimb.drawDbClassification,
            limb.SkeletonGuideLimb.drawRegistrantId,
            limb.SkeletonGuideLimbDrawOverride.creator)
    except RuntimeError:
        sys.stderr.write("Failed to register SkeletonGuideLimbDrawOverride override\n")
        raise

    # BLOCK #
    try:
        plugin.registerNode("skeletonGuideBlock",
                            block.SkeletonGuideBlock.id,
                            block.SkeletonGuideBlock.creator,
                            block.SkeletonGuideBlock.initialize,
                            OpenMaya.MPxNode.kLocatorNode,
                            block.SkeletonGuideBlock.drawDbClassification)
    except RuntimeError:
        sys.stderr.write("Failed to register SkeletonGuideBlock node\n")
        raise

    try:
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator(
            block.SkeletonGuideBlock.drawDbClassification,
            block.SkeletonGuideBlock.drawRegistrantId,
            block.SkeletonGuideBlockDrawOverride.creator)
    except RuntimeError:
        sys.stderr.write("Failed to register SkeletonGuideBlockDrawOverride override\n")
        raise

    # HANDLE #
    try:
        plugin.registerNode(
            "guideHandle",
            handle.GuideHandle.id,
            handle.GuideHandle.creator,
            handle.GuideHandle.initialize,
            OpenMaya.MPxNode.kLocatorNode,
            handle.GuideHandle.drawDbClassification)
    except RuntimeError:
        sys.stderr.write("Failed to register GuideHandle node\n")
        raise

    try:
        OpenMayaRender.MDrawRegistry.registerDrawOverrideCreator(
            handle.GuideHandle.drawDbClassification,
            handle.GuideHandle.drawRegistrantId,
            handle.GuideHandleDrawOverride.creator)
    except RuntimeError:
        sys.stderr.write("Failed to register GuideHandleDrawOverride override\n")
        raise


def uninitializePlugin(obj):
    plugin = OpenMaya.MFnPlugin(obj)

    # SPINE #
    try:
        plugin.deregisterNode(spine.SkeletonGuideSpine.id)
    except RuntimeError:
        sys.stderr.write("Failed to deregister SkeletonGuideSpine node\n")
        pass

    try:
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator(
            spine.SkeletonGuideSpine.drawDbClassification,
            spine.SkeletonGuideSpine.drawRegistrantId)
    except RuntimeError:
        sys.stderr.write("Failed to deregister SkeletonGuideSpineDrawOverride override\n")
        pass

    # LIMB #
    try:
        plugin.deregisterNode(limb.SkeletonGuideLimb.id)
    except RuntimeError:
        sys.stderr.write("Failed to deregister SkeletonGuideLimb node\n")
        pass

    try:
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator(
            limb.SkeletonGuideLimb.drawDbClassification,
            limb.SkeletonGuideLimb.drawRegistrantId)
    except RuntimeError:
        sys.stderr.write("Failed to deregister SkeletonGuideLimbDrawOverride override\n")
        pass

    # BLOCK #
    try:
        plugin.deregisterNode(block.SkeletonGuideBlock.id)
    except RuntimeError:
        sys.stderr.write("Failed to deregister SkeletonGuideBlock node\n")
        pass

    try:
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator(
            block.SkeletonGuideBlock.drawDbClassification,
            block.SkeletonGuideBlock.drawRegistrantId)
    except RuntimeError:
        sys.stderr.write("Failed to deregister SkeletonGuideBlockDrawOverride override\n")
        pass

    # HANDLE #
    try:
        plugin.deregisterNode(handle.GuideHandle.id)
    except RuntimeError:
        sys.stderr.write("Failed to deregister GuideHandle node\n")
        pass

    try:
        OpenMayaRender.MDrawRegistry.deregisterDrawOverrideCreator(
            handle.GuideHandle.drawDbClassification,
            handle.GuideHandle.drawRegistrantId)
    except RuntimeError:
        sys.stderr.write("Failed to deregister GuideHandleDrawOverride override\n")
        pass