#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Doc String

Description:

    Initialises communication with the edge agents on the network. Catalogues all edge agents on the network and assigns
    a unique identifier to each.

    Modules:

        - comms_init - initialises edge agent communications

Date Last Edited: 15 june 2022
'''
__author__ = "Brandon Colelough"
__copyright__ = "Open Source"
__credits__ = [""]
__license__ = "Open Source"
__version__ = "1.0.1"
__maintainer__ = "Brandon Colelough"
__email__ = "brandon.colelough1234@gmail.com"
__status__ = "Production"

# Imports Go Here!

try:
    from eye import *
    import map_structs
    import sys
    import getopt
except ImportError:
    raise ImportError('Import failed')


"""Initialises communication with the edge agents on the network"""
def comms_init():
    RADIOInit()
    my_id = RADIOGetID()
    LCDPrintf("Control agent - my id is %d\n", my_id)
    [total,IDList] = RADIOStatus()
    while total <=1:
        LCDPrintf("Waiting for other agents to join the network!");
        [total,IDList] = RADIOStatus()
    # the master  this agent, control agent) will now send out a message to let all other agents on the
    # network know that this agents ID is the control agent ID
    OSWait(300) # wait 3 seconds - allows sim time to ensure all edge agents are up and running on the network
    counter = 0 #need a counter as opposed to x so that the control agent doesn't add its own ID
    message = "control_agent"
    agent_ID_Map = {}
    for x in range(0,total):
        if my_id != IDList[x]: # make sure you're not sending a message to yourself
            partner = IDList[x]; # robot 1 --> robot x
            LCDPrintf("Control agent - Sending handshake message to edge agent with ID %d\n", partner);
            RADIOSend(partner, message);
            # also asign each edge agent a local map
            agent_ID_Map[IDList[x]] = counter #that is, the agent with id at IDList[x] is assosciated with map number x
            counter+=1
    return agent_ID_Map




class comms:
    """Initialises communication with the edge agents on the network"""
    def __init__(self, data):
         self.data = data

