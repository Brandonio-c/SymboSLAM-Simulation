#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Doc String

Description:

    Global map takes the local map structures stored by the control agent and places them ona  globally referenced plane
    This is done by:

    1. Amending the local maps
        This is done by using the known starting location of each edge agent and either subtracting it / adding it so that
        a common zero can be used on one plane

    2. Merging the local maps in the global map structure
        This is done by taking landmarks that are spatially close and comparing their feature class. If the feature classes
        are the same and they are within some tolerance then the features are merged into one

        TODO - incorporate semantic similarity through the use of an ontology


        TODO - Update the mapping structure data structure so it is stored spatially and not grouped by feature type
            - update data structure so it is stored on a pose graph


    Modules:

    1. Ammend_maps - ammends the maps to place on a global plane
    2. merge maps - merges features within a global map data structure


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

try:
    from eye import *
    import map_structs as m_s
    import sys
    import math
    import concurrent.futures
    import multiprocessing
except ImportError:
    raise ImportError('Import failed')


class global_map:
    """Global map takes the local map structures stored by the control agent and places them ona  globally referenced plane

        Inputs:
            agent_num              : number of agents on network
            agent_ID_map           : maps each edge agent to their associated local map
            agent_start_location   : dictionary that stores the starting location of each edge agent using their unique ID
            map_name               : not needed anymore TODO - prune
            class_name_map         : maps the feature classes (found by YOLO) to their assosciated unique ID (can be found in third party - YOLO - imagenet.names, coco.names
            m_p_map_list           : multi-processing local map list - proxy that stores the local maps of each edge agent and allows for multi-processing
            m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
    """
    def __init__(self, agent_num, agent_ID_map, agent_start_location, map_name, class_name_map, m_p_map_list, m_p_global_map):
        #m_s.lock.acquire()
        #LCDPrintf("Starting global map process \n")
        #m_s.lock.release()
        self.global_map_main(agent_num, agent_ID_map, agent_start_location, map_name, class_name_map,m_p_map_list, m_p_global_map)

    '''
    Amends the local maps of the edge agents stored by the control agent to place them on a globally referenced plane 
    This is done by using the known starting location of each edge agent and either subtracting it / adding it so that
    a common zero can be used on one plane
    
    
    
    Inputs: 
            agent_num               : number of agents on network
            position_list_tracker   : Used to keep track of the length of the position list data structure for each edge agent local map structure 
            predictions_list_tracker: Used to keep track of the length of the prediction list data structure for each edge agent local map structure 
            agent_start_location    : dictionary that stores the starting location of each edge agent using their unique ID
            m_p_map_list            : multi-processing local map list - proxy that stores the local maps of each edge agent and allows for multi-processing
            m_p_global_map          : multi-processing global map list - proxy that stores the global map of the control agent
            
    '''
    def ammend_maps(self, agent_num, position_list_tracker, predictions_list_tracker, agent_start_location, m_p_map_list, m_p_global_map):
        map_bounds = m_s.get_global_bounds(m_p_global_map)
        for x in range (0, int(agent_num)):
            #ammend position list
            pos_list_size = m_s.pos_list_size(m_p_map_list, x)
            for y in range (int(position_list_tracker[x]), pos_list_size):
                old_pos = m_s.pos_fm_list(m_p_map_list, x, y)
                posx =old_pos.x + agent_start_location[x][0].x
                posy = old_pos.y+ agent_start_location[x][0].y
                posphi = old_pos.phi + agent_start_location[x][0].phi
                new_pos = m_s.position(posx, posy, posphi)
                m_s.update_pos_list(m_p_map_list, x, y, new_pos)

                #Global map boundaries -----------------------------------------

                ''' - Not currently working - 
                - due to error building up - map mounds get waaaay too large 
                TODO - FIX!
                if(posx > map_bounds[2]):
                     map_bounds[2] = posx
                elif(posx < map_bounds[0]):
                    map_bounds[0] = posx

                if(posy >  map_bounds[3]):
                      map_bounds[3] = posy
                elif(posy <  map_bounds[1]):
                      map_bounds[1] = posy
                '''

            position_list_tracker[x] = pos_list_size

            #do the same as above but for predictions lists

            feat_list_size = m_s.feat_list_size(m_p_map_list, x)
            for z in range(int(predictions_list_tracker[x]), feat_list_size):
                old_pos = m_s.pos_fm_feat_list(m_p_map_list, x, z)
                posx =old_pos.x + agent_start_location[x][0].x
                posy = old_pos.y+ agent_start_location[x][0].y
                posphi = old_pos.phi + agent_start_location[x][0].phi
                new_pos = m_s.position(posx, posy, posphi)
                m_s.update_feat_list(m_p_map_list, x, z, new_pos)

                 #Global map boundaries -----------------------------------------
                if(posx > map_bounds[2]):
                     map_bounds[2] = posx
                elif(posx < map_bounds[0]):
                    map_bounds[0] = posx

                if(posy >  map_bounds[3]):
                      map_bounds[3] = posy
                elif(posy <  map_bounds[1]):
                      map_bounds[1] = posy

            #predictions_list_tracker[x] = len(map_list[x].prediction_list)
            #self.lock.acquire()
            #LCDPrintf("map no: %d ammended\n", x)
            #self.lock.release()

        m_s.set_global_bounds(m_p_global_map, map_bounds)

    '''
    Merges all of the edge agent local map structures onto one global map data structure
        This is done by taking landmarks that are spatially close and comparing their feature class. If the feature classes
        are the same and they are within some tolerance then the features are merged into one
    
    Inputs: 
            agent_num               : number of agents on network
            agent_ID_map            : maps each edge agent to their associated local map
            predictions_list_tracker: Used to keep track of the length of the prediction list data structure for each edge agent local map structure 
            m_p_map_list            : multi-processing local map list - proxy that stores the local maps of each edge agent and allows for multi-processing
            m_p_global_map          : multi-processing global map list - proxy that stores the global map of the control agent
       
    '''
    def merge_maps(self, agent_num, predictions_list_tracker, agent_ID_map, m_p_map_list, m_p_global_map):
        tolerance = 500 # 300mm = .3m tolerance TODO - change this so its taken in from CLI
        try:
            for x in range(0, int(agent_num)):
                agent_map_assosciation = list(agent_ID_map.keys())[list(agent_ID_map.values()).index(x)]
                #go through all of the new found features
                feat_list_size = m_s.feat_list_size(m_p_map_list, x)
                for y in range(int(predictions_list_tracker[x]), feat_list_size):
                    feature_class = m_s.get_feature_class(m_p_map_list, x, y)
                    feature_found = False
                    # find all other features within the tolerance range that match this feature
                    # match using class types first
                    #note - feature class numbers are used as keys in global map dictionary
                    if(m_s.find_global_key(m_p_global_map, feature_class)):
                        feat_pos = m_s.pos_fm_feat_list(m_p_map_list, x, y)
                        new_feature_x  = feat_pos.x
                        new_feature_y =feat_pos.y
                        z = 0
                        while (feature_found is False) and (z < m_s.glob_map_feat_list_size(m_p_global_map, feature_class) -1):
                            cur_feat = m_s.pos_fm_glob_feat_list(m_p_global_map,feature_class, z)
                            cur_feature_x = cur_feat.x
                            cur_feature_y = cur_feat.y
                            distance = math.sqrt(pow((cur_feature_x - new_feature_x),2) + pow((cur_feature_y - new_feature_y),2) );
                            if distance < tolerance:
                                m_s.append_agent(m_p_global_map, feature_class, z, agent_map_assosciation)
                                #change the location of this feature so it's the average between these two assertions
                                updated_x = (cur_feature_x + new_feature_x)/2
                                updated_y = (cur_feature_y + new_feature_y)/2
                                updated_phi = (cur_feat.phi + feat_pos.phi)/2
                                new_pos = m_s.position(updated_x, updated_y, updated_phi)
                                m_s.update_feat_list(m_p_map_list, x, z, new_pos)
                                feature_found = True
                            z +=1
                    else:
                        #new feature - add it to the global map
                        agent_IDs = [agent_map_assosciation]
                        detected_features = m_s.det_feature(m_p_map_list, x, y)
                        global_feature = m_s.global_map_detected_feature(detected_features.position, detected_features.confidence, detected_features.feature_class, detected_features.name, agent_IDs)
                        global_map_entry = [m_s.global_map_entry(global_feature)]
                        m_s.add_map_entry(m_p_global_map, global_map_entry, feature_class)
                        feature_found = True

                    if not feature_found:
                        #feature was not found but this is not a new class
                        #add this feature at its assosciated class key
                        agent_IDs = [agent_map_assosciation]
                        detected_features = m_s.det_feature(m_p_map_list, x, y)
                        global_feature = m_s.global_map_detected_feature(detected_features.position, detected_features.confidence, detected_features.feature_class, detected_features.name, agent_IDs)
                        global_map_entry = m_s.global_map_entry(global_feature)
                        m_s.append_map_entry(m_p_global_map, global_map_entry, feature_class)
                    #m_s.lock.acquire()
                    #LCDPrintf("agent map %d merged with global map\n", int(agent_map_assosciation))
                    #m_s.lock.release()
                predictions_list_tracker[x] = feat_list_size
        except Exception as e:
            message = "Error: unable to merge local maps - " + str(e)
            print (message)



    '''
    Main Loop 
    
    Note that position_list_tracker and  predictions_list_tracker are used to keep track of the length of these data structures in their local map structures
    
    Inputs:
            agent_num              : number of agents on network
            agent_ID_map           : maps each edge agent to their associated local map
            agent_start_location   : dictionary that stores the starting location of each edge agent using their unique ID
            map_name               : not needed anymore TODO - prune
            class_name_map         : maps the feature classes (found by YOLO) to their assosciated unique ID (can be found in third party - YOLO - imagenet.names, coco.names
            m_p_map_list           : multi-processing local map list - proxy that stores the local maps of each edge agent and allows for multi-processing
            m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
            
            map_name and class_name_map are no longer needed 
            TODO Prune that 
    '''
    def global_map_main(self, agent_num, agent_ID_map, agent_start_location, map_name, class_name_map, m_p_map_list, m_p_global_map):
        position_list_tracker = [0]* int(agent_num)
        predictions_list_tracker = [0]* int(agent_num)
        while True:
            OSWait(500);
            m_s.lock.acquire()
            self.ammend_maps(agent_num, position_list_tracker, predictions_list_tracker, agent_start_location, m_p_map_list, m_p_global_map)
            self.merge_maps(agent_num, predictions_list_tracker, agent_ID_map, m_p_map_list, m_p_global_map)
            m_s.lock.release()



