import pymel.core as pm
import maya.api.OpenMaya as OpenMaya

from . import handle
from . import guide


LOAD_PLUGIN = True
PLUGIN_PATH = "boneforge.py"
if LOAD_PLUGIN:
    if not pm.pluginInfo(PLUGIN_PATH, q=True, loaded=True):
        pm.loadPlugin(PLUGIN_PATH)

from .guide import Guide, GuideSpine, GuideLimb, GuideBlock
from .handle import Handle

def guidesFromScene():
    allGuides = set()
    for nodetype in guide.GUIDE_NODE_TYPES:
        cls = guide.GUIDE_NODE_CLASS[nodetype]
        allGuides.update(map(cls, pm.ls(type=nodetype)))
    return list(allGuides)

def addGuideHandle(guide):
    if guide.handleCount() > 1:
        lastHandle = guide.handleAtIndex(-1)
        secondLastHandle = guide.handleAtIndex(-2)
        lastPos = OpenMaya.MVector(lastHandle.transform.translate.get())
        secondLastPos = OpenMaya.MVector(secondLastHandle.transform.translate.get())
        vector = lastPos - secondLastPos
        newPos = lastPos + vector
    else:
        lastHandle = guide.handleAtIndex(-1)
        lastPos = OpenMaya.MVector(lastHandle.transform.translate.get())
        newPos = lastPos
    print newPos
    guide.addHandle(position=newPos)

def insertGuideHandle(guide, index):
    if index == 0:
        baseHandle = guide.handleAtIndex(0)
        newPos = OpenMaya.MVector(baseHandle.transform.translate.get())
    elif index == guide.handleCount():
        addGuideHandle(guide)
        return
    else:
        after = guide.handleAtIndex(index)
        before = guide.handleAtIndex(index - 1)
        afterPos = OpenMaya.MVector(after.transform.translate.get())
        beforePos = OpenMaya.MVector(before.transform.translate.get())
        vector = (afterPos - beforePos) * 0.5
        newPos = beforePos + vector
    guide.insertHandle(index, position=newPos)

def buildSkeleton(rootGuide):
    stack = [(rootGuide.handleAtIndex(0), None)]
    skeleton, noBind, noExport = [], [], []
    while stack:
        handle, parent = stack.pop()
        jnt = handle.buildJoint()
        if parent:
            jnt.setParent(parent)
            pm.rename(jnt, handle.name)
        skeleton.append(jnt)
        for child in handle.children():
            stack.append((child, jnt))

    pm.makeIdentity(skeleton[0], apply=True)
    pm.select(skeleton[0])
    return skeleton