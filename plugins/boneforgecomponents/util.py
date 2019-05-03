import string
import random

import maya.api.OpenMayaRender as OpenMayaRender

class DisplayStatus(object):
    """A convenience class for shorter access to MGeometryUtilities DisplayStatus constants."""
    Active = OpenMayaRender.MGeometryUtilities.kActive
    ActiveAffected = OpenMayaRender.MGeometryUtilities.kActiveAffected
    ActiveComponent = OpenMayaRender.MGeometryUtilities.kActiveComponent
    ActiveTemplate = OpenMayaRender.MGeometryUtilities.kActiveTemplate
    DefaultCube = OpenMayaRender.MGeometryUtilities.kDefaultCube
    DefaultPlane = OpenMayaRender.MGeometryUtilities.kDefaultPlane
    DefaultSphere = OpenMayaRender.MGeometryUtilities.kDefaultSphere
    Dormant = OpenMayaRender.MGeometryUtilities.kDormant
    Hilite = OpenMayaRender.MGeometryUtilities.kHilite
    IntermediateObject = OpenMayaRender.MGeometryUtilities.kIntermediateObject
    Invisible = OpenMayaRender.MGeometryUtilities.kInvisible
    Lead = OpenMayaRender.MGeometryUtilities.kLead
    Live = OpenMayaRender.MGeometryUtilities.kLive
    NoStatus = OpenMayaRender.MGeometryUtilities.kNoStatus
    Template = OpenMayaRender.MGeometryUtilities.kTemplate

def generateID(size=6, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    """Return a random ID string."""
    ID = ""
    for c in xrange(size):
        ID += random.choice(chars)
    return ID