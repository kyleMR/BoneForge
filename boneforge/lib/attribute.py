"""my.lib.attribute

Utility functions for dealing with various types of Maya attributes
"""
import itertools

import pymel.core as pm

def sanitizeMultiMessageAttribute(attribute):
    """Consolidate all connections to the given attribute to sequential indices from 0."""
    connections = attribute.listConnections(connections=True, plugs=True)
    for index, connection in enumerate(connections):
        thisPlug, incomingPlug = connection
        pm.disconnectAttr(incomingPlug, thisPlug)
        pm.connectAttr(incomingPlug, attribute[index])
        
def firstOpenIndex(attribute):
    """Returns the first open (non-connected) index of the given array attribute."""
    for i in itertools.count():
        entry = attribute[i]
        if not entry.listConnections():
            return i
            
def getMultiMessageAttributeIndex(multiMessageAttr, incomingAttr):
    """Returns the index of the incoming attribute connection to the given multi attribute."""
    connectionList = multiMessageAttr.listConnections(plugs=True)
    for connection in connectionList:
        if connection == incomingAttr:
            return connectionList.index(connection)