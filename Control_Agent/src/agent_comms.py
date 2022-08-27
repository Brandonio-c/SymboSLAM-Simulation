#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Doc String

Description: main file communications between edge and control agents

Modules:
    - map_decoder - Decodes received messages
    - agent_comms_main - main loop for this file

TODO -  - Implement a check to ensure message was recieved by control agent - Send again if it was not!
 - having issues with sending / recieving at the same time as ROBIos function locks recieve functionality

Date Last Edited: 15 June 2022
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
    import map_structs as m_s
    import sys
    import getopt
    import concurrent.futures
    import multiprocessing
except ImportError:
    raise ImportError('Import failed')

#include "eyebot++.h"

class agent_comms(object):
    """main file communications between edge and control agents

        Inputs:

            agent_ID_map        maps each edge agent to their associated local map
            m_p_map_list        multi-processing map list - proxy that stores the local maps of each edge agent and allows for multi-processing
            x                   number of processes to start to enable each edge agents communications to be on its own dedicated process
         TODO - name that variable better
    """
    def __init__(self, agent_ID_map,  m_p_map_list, x):
        #m_s.lock.acquire()
        #LCDPrintf("Starting edge agent comms: %d \n", x)
        #m_s.lock.release()
        self.agent_comms_main(agent_ID_map,  m_p_map_list, x)

    """
        communications between edge and control agent are sent and received as text 
        Local maps received from edge agents are encoded to be sent as text files
        note the following operators are used:
         * , - separator comma deliminated)
         * /0 - deliminator for 3 structure types
         * /1 - deliminator for positions in position list (also used in prediction position list)
         * /2 - deliminator for prediciton results list
         * /3 - deliminator for results information
         
         once local maps are decoded, they are used to update the local map stored for that edge agent by the control agent 
         
         Inputs:
         message           the message that was received from the edge agent
         sender            edge agent that sent the message
         agent_ID_map      maps each edge agent to their associated local map
         m_p_map_list      multi-processing map list - proxy that stores the local maps of each edge agent and allows for multi-processing
         
    """
    def map_decoder(self, message, agent_ID_map, sender, m_p_map_list):
        agent_map_assosciation = agent_ID_map.get(sender) # to know which local map we are adding to
        delim_0 = "/0"
        delim_1 = "/1"
        delim_2 = "/2"
        delim_4 = ","

        #split message into three structure types
        map_components = message.split(delim_0)

        #--------------------------------------------------------------------current position
        if len(map_components) > 1:
            #next - make a pos out of the cur pos info - stored in first position of the local map structures
            pos_struct = map_components[0].split(delim_4)
            loc = m_s.position(float(pos_struct[0]), float(pos_struct[1]), float(pos_struct[2]))
            m_s.update_cur_pos(m_p_map_list, agent_map_assosciation, loc)
        else:
            print("Error in prediciton list ")
            #LCDPrintf("ERROR in message received from %d - No current position recieved \n", sender);

        #--------------------------------------------------------------------current position

        #--------------------------------------------------------------------position list
        #check that the message recieved has a position list
        if len(map_components) > 2:
            #next - make a position list out of the info in the second part of the message vector
            # note that the delim is /1
            pos_list_struct = map_components[1].split(delim_1)
            #now make a position for each vector entry and add it to the position list vector in this agents localmap
            for x in range(0, len(pos_list_struct)-1):
                pos_struct = pos_list_struct[x].split(delim_4)
                loc = m_s.position(float(pos_struct[0]), float(pos_struct[1]), float(pos_struct[2]))
                m_s.append_pos_list(m_p_map_list, agent_map_assosciation, loc)

        else:
            print("Error in position list ")
            #LCDPrintf("ERROR in message received from %d - No position list recieved  %d\n", sender);
            #--------------------------------------------------------------------position list

        # --------------------------------------------------------------------feature list
        #check that there is a predictions list to decode
        if len(map_components) > 3:
            predictions_list_vec = map_components[2].split(delim_1)
            if len(predictions_list_vec)>0:
                for x in range (0, len(predictions_list_vec)-1):
                    prediction_result_struct = predictions_list_vec[x].split(delim_2)
                    if len(prediction_result_struct)>=4:
                        position_vec = prediction_result_struct[0].split(delim_4)
                        loc = m_s.position(float(position_vec[0]), float(position_vec[1]), float(position_vec[2]))
                        feature_name = prediction_result_struct[1]
                        confidence = float(prediction_result_struct[2])
                        feature_class = int(prediction_result_struct[3])
                        feature = m_s.detected_feature(loc, confidence, feature_class, feature_name)
                        m_s.append_feat_list(m_p_map_list, agent_map_assosciation, feature)
                    else:
                        print("Error in prediciton list ")
                        #LCDPrintf("ERROR in message received from %d - predictions list has data faults - not enough arguments received!\n", sender)
            else:
                print("Error in prediciton list ")
                #LCDPrintf("ERROR in message received from %d - predictions list has data faults \n", sender)

        # --------------------------------------------------------------------feature list

    """
        Main module for this file. 
        Messages are restricted to 100 characters (100 bytes) so multiple packets may be received for one single message
        an initial message will be received from edge agent indicating how many packets are to be received for the current message.
        module will scan for these packets up to three times on the network before disregarding the current message and moving on 
        
        Inputs: 
         agent_ID_map        maps each edge agent to their associated local map
         m_p_map_list        multi-processing map list - proxy that stores the local maps of each edge agent and allows for multi-processing
         x                   number of processes to start to enable each edge agents communications to be on its own dedicated process 
         TODO - name that variable better
    """
    def agent_comms_main(self, agent_ID_map, m_p_map_list, x):
        m_s.lock.acquire()
        RADIOInit()
        my_id = RADIOGetID()
        [total,IDList] = RADIOStatus()
        m_s.lock.release()
        #create comms log file
        f_name = "../../Sims/comms_log/agent_comms_" + str(x) + ".txt"
        f = open(f_name, "a")
        f.write("this control agent ID: "+ str(my_id) + "\n")
        f.close()
        if total > 1:
            while True: #infinite loop as we're always going to be scanning for comms and sending local map information through
                m_s.lock.acquire()
                full_message = ""
                [partnerid, buf] = RADIOReceive()
                #check wheter the message being recieved is part of another bigger message
                try:
                    if(buf[:1] == 's'):
                        #start of a broken up message
                        mes_info = buf.split('|')
                        packets = mes_info[1]
                        size = mes_info[2]
                        messID = mes_info[3]
                        message_buffer = [None] * int(packets)
                        this_message_parter = partnerid
                        #attempt to take in the message for no more than 3 times the amount of messge data packets taht the header info specifies there are
                        # (as the sender will often (almost always) send the message two times)
                        packets_received = 0
                        idx = 0;
                        while(idx < (3*int(packets)) and (packets_received <int(packets))):
                            [partnerid, buf] = RADIOReceive()
                            if(partnerid == this_message_parter):
                                packet_info =  buf.split('|')
                                #check message isn't just header info and this message ID is the same as the current header message ID
                                if((not (buf[:1] == 's')) and (packet_info[1] == messID)):
                                    if message_buffer[int(packet_info[2])] is None:
                                        message_buffer[int(packet_info[2])] = packet_info[0]
                                        packets_received +=1;
                            idx+=1;

                        #now reconstruct message as a string and check that the string size matches what was sent through in the header '
                        try:
                            rec_message = ""
                            for idx in range(0, int(packets)):
                                rec_message = rec_message + message_buffer[idx]
                            if (len(rec_message) == (int(size)-1)):
                                full_message = rec_message
                            else:
                                f = open(f_name, "a")
                                f.write("Error! - This message: " + rec_message + " Size does not match the information in its header info \n")
                                f.close()
                        except Exception as e:
                            message = "Error with receiving message - Message buffer missing message packet number " + str(idx) + " - " + str(e)
                            print(message)
                            f = open(f_name, "a")
                            f.write(message + "\n")
                            f.close()


                    else:
                        #messages that weren't recieved as packets should not contain | - throw out anything that makes it here that does
                        if not '|' in buf:
                            full_message = buf
                        else:
                            message = "Error with receiving message - message packet received without header -"
                            print (message)
                            f = open(f_name, "a")
                            f.write(message + "\n")
                            f.close()

                except Exception as e:
                    message = "Error with receiving message - " + str(e)
                    print (message)
                    f = open(f_name, "a")
                    f.write(message + "\n")
                    f.close()

                m_s.lock.release()
                f = open(f_name, "a")
                f.write(str(full_message) + " -  Agent #" + str(partnerid) + "\n")
                f.close()
                #send confirmation message to edge agent that their message has been recieved
                #message = "r/" + str(partnerid)
                #RADIOSend(partnerid, message);
                #LCDPrintf("%s received! Thank you edge agent  %d \n",buf, partnerid)
                try:
                    agent_comms.map_decoder(self, full_message, agent_ID_map, partnerid, m_p_map_list)
                except Exception as e:
                    message = "Error decoding the above message! - "  + str(e)
                    print (message)
                    f = open(f_name, "a")
                    f.write(message + "\n")
                    f.close()

                #LCDPrintf("map Decoded \n")
                OSWait(300); #receive comms pings at increments
        else:
            m_s.lock.acquire()
            LCDPrintf("ERROR! Control agent disconnected from network!")
            m_s.lock.release()




if __name__ == "__main__":
   agent_comms.agent_comms_main(sys.argv[1:])
