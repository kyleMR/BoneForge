import maya.api.OpenMaya as OpenMaya

# Define plugin IDs
# From Autodesk Maya API Guide:
# For local testing of nodes you can use any identifier between 0x00000000 and 0x0007ffff,
# but for any node that you plan to use for more permanent purposes, you should get a
# universally unique id from Autodesk Technical Support. You will be assigned a unique
# range that you can manage on your own.
GUIDEHANDLE = OpenMaya.MTypeId(0x00011717)
GUIDESPINE = OpenMaya.MTypeId(0x00011718)
GUIDELIMB = OpenMaya.MTypeId(0x00011719)
GUIDEBLOCK = OpenMaya.MTypeId(0x00011720)