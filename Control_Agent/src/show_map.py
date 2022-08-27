#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Doc String

Description:

File used to show the global map to teh operator

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
    import matplotlib.pyplot as plt
    from matplotlib.offsetbox import OffsetImage, AnnotationBbox
    #from matplotlib._png import read_png
    import matplotlib.image as mpimg
    import random
    import matplotlib.patches as mpatches
    import math
except ImportError:
    raise ImportError('Import failed')


'''
Uses MatPlotLib to plot the global map data structure 
Inputs:
        
         m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
         classname_map          : the file containing all of the class names used by YOLO - used to generate a dictionary storing all the possible features extracted adn assigning unique ID's
         oracle                 : Boolean - Use oracle or not?
         landmark_map           : stores the ground truth of environment features from the oracle file
         images_path            : stores the path for images used to represent features on 2d Topo map
'''
class show_map:
    def __init__(self, m_p_global_map, class_name_map, oracle, landmark_map, images_path):
        #m_s.lock.acquire()
        #LCDPrintf("generating global \n")
        #m_s.lock.release()
        self.show_map_main(m_p_global_map, class_name_map, oracle, landmark_map, images_path)


    '''
    
    Uses MatPlotLib to plot the global map data structure 
    
    Features are currently drawn with a scatter plot and boxes are drawn over segmented parts of the classified environment 
    
    Moving towards using pictures to represent features but this is not currnelty working 
    
    TODO - Fix that 
    
    Inputs:
        
         m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
        class_name_map          : the file containing all of the class names used by YOLO - used to generate a dictionary storing all the possible features extracted adn assigning unique ID's
         images_path            : stores the path for images used to represent features on 2d Topo map
         fig                    : MatPlotLib figure subfigure
         ax                     : MatPlotLib figure subfigure
         color_map              :color map used to link specific colours to label environments
    
    '''
    def show_plot(self, m_p_global_map, class_name_map, images_path, fig, ax,  color_map):
        try:
            gmap = m_s.get_global_map(m_p_global_map)
            bounds = gmap.bounds
            map = gmap.global_map
            segmented_map = gmap.segmented_map
        except Exception as e:
            message = "Error: Unable to load global map  " + str(e)
            print(message)
        try:
            legend = []
            plt.title("Global Map")
            plt.xlabel("X-axis (m)")
            plt.ylabel("Y-axis (m)")
            plt.grid()
            plt.xlim(bounds[0] , bounds[2])
            plt.ylim(bounds[1] , bounds[3])
            plt.subplots_adjust(right=0.75)
            plt.subplots_adjust(top=0.75)
            plt.ion()
            plt.show()


            # load the images up
            #stop_sign = mpimg.imread(images_path + "Stop_sign.png")
            #imagebox = OffsetImage(stop_sign, zoom=0.2)
            #ab = AnnotationBbox(imagebox, (0.4, 0.6))
            #ax.add_artist(ab)

            #add features to map
            for key in map:
                legend.append(class_name_map.get(key))
                x = []
                y = []
                for idx in range (0, len(map.get(key))):
                    if(map.get(key)[idx].global_map_detected_feature.confidence > 60):
                        x.append(map.get(key)[idx].global_map_detected_feature.position.x)
                        y.append(map.get(key)[idx].global_map_detected_feature.position.y)
                        #ab = AnnotationBbox(imagebox, (map.get(key)[idx].global_map_detected_feature.position.x, map.get(key)[idx].global_map_detected_feature.position.y))
                        #ax.add_artist(ab)

                #plt.grid()
                plt.scatter(x, y)
                plt.legend(legend, bbox_to_anchor=(1.04, 0.5), loc="center left", borderaxespad=0)
            plt.draw()
            plt.pause(0.001)


            #now that all that is drawn, draw the segmented areas and assign the stuff
            for fragment in segmented_map:
                #first, get the most likely env type
                env_type = max(segmented_map[fragment].env_prob, key=segmented_map[fragment].env_prob.get)
                # get the color for that environment
                prob = int(segmented_map[fragment].env_prob[env_type] * 100)
                #if the probability is 0 then that means the env type could not be determined
                #this will because no inferences could be made between any of the features within the environment
                if prob == 0:
                    color = 'grey'
                    env_type = "Unknown!"
                else:
                    color =  color_map[env_type]
                #draw the square
                left = (segmented_map[fragment].index['start'].x)
                bottom = (segmented_map[fragment].index['start'].y)
                width = (segmented_map[fragment].index['end'].x - segmented_map[fragment].index['start'].x)
                height = (segmented_map[fragment].index['end'].y - segmented_map[fragment].index['start'].y)
                rect=mpatches.Rectangle((left,bottom),width,height,
                           fill=True,
                           color=color,
                           linewidth=2,
                           zorder = 100,
                           alpha=0.1)
                           #facecolor="red")
                plt.gca().add_patch(rect)
                plt.text(left, bottom, (env_type + ", " + str(prob) + "%"), fontsize=12, color=color, weight="bold")
                plt.draw()
                plt.pause(0.001)
        except Exception as e:
            message = "Error: Unable to show global map - error with drawing process " + str(e)
            print(message)




    '''
    Uses the oracle file to match the landmarks found by the edge agents and place them in the places they are actually meant to be
    Incorporated into the project due to error with measurements cascading and causing issues 
    
        TO BE REMOVED BEFORE DEPLOYMENT - DO NOT USE FOR DEPLOYMENT 
    
    Go through all of the landmarks in the global feature map and align them to the oracle map 
    
    Note that this method should only be used in testing - Oracle help should not be required on the funcitoning system for 
    map generation / place recognition  
    
    Inputs:
    
         m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
         landmark_map           : stores the ground truth of environment features from the oracle file
    
    '''
    def reveal_landmarks(self, m_p_global_map,  landmark_map):
        map_bounds = m_s.get_global_bounds(m_p_global_map)
        if(map_bounds[2]> 10000):
            map_bounds[2] = 10000
        elif(map_bounds[0] <0):
            map_bounds[0] = 0
    
        if(map_bounds[3] > 10000):
              map_bounds[3] = 10000
        elif( map_bounds[1]<0):
              map_bounds[1] = 0
        m_s.set_global_bounds(m_p_global_map, map_bounds)

        try:
            gmap = m_s.get_global_map(m_p_global_map)
            bounds = gmap.bounds
            map = gmap.global_map
        except Exception as e:
            message = "Error: Unable to load global map  " + str(e)
            print(message)

        for key in map:
            #first - check that the landmark type exists in the oracle file - if it foes not then get rid of it
            try:
                if(key in landmark_map):
                    feature_list = map.get(key)
                    fsize = len(map.get(key))
                    for idx in range (0, fsize):
                        #go through and find the closest land mark given in the oracles map
                        feat_pos = feature_list[idx].global_map_detected_feature.position
                        new_feature_x  = feat_pos.x
                        new_feature_y =feat_pos.y
                        # now go through and match the features
                        tolerance = 100
                        feature_found = False
                        while (feature_found is False):
                            idy = 0
                            while idy in range (0, len(landmark_map.get(key)) -1) and feature_found is False:
                                cur_feat = landmark_map.get(key)[idy]
                                cur_feature_x = cur_feat.x
                                cur_feature_y = cur_feat.y
                                distance = math.sqrt(pow((cur_feature_x - new_feature_x),2) + pow((cur_feature_y - new_feature_y),2) );
                                if distance == 0:
                                    feature_found = True
                                elif distance < tolerance:
                                    #m_s.append_agent(m_p_global_map, feature_class, z, agent_map_assosciation)
                                    #If the two are within tolerance then change the feature position int he global map to align with the oracle map
                                    m_s.update_glob_map(m_p_global_map, key, idx, landmark_map.get(key)[idy])
                                    feature_found = True
                                idy +=1
                            if not (feature_found):
                                tolerance +=100
                                #if the feature was not found, delete it
                                if(tolerance > 1500):
                                    feature_found = True
                                    m_s.delfeat_glob_map(m_p_global_map, key, idx)
                                    fsize -=1;
                                    message = "Feature deleted from global map"
                                    print(message)

                else:
                    m_p_global_map.remove_key(key)
                    #Error: Unable to show global map  'builtin_function_or_method' object does not support item deletion
                    message = "Feature deleted from global map"
                    print(message)
            except Exception as e:
                        message = "Error: Issue with oracle -  " + str(e)
                        print(message)

    '''
    Used in production only! Do not use for release of demonstrations
    
    def reveal_landmarks_v2(self, m_p_global_map,  landmark_map):
        try:
            
            map_bounds = m_s.get_global_bounds(m_p_global_map)
            if(map_bounds[2]> 10000):
                map_bounds[2] = 10000
            elif(map_bounds[0] <0):
                map_bounds[0] = 0

            if(map_bounds[3] > 10000):
                  map_bounds[3] = 10000
            elif( map_bounds[1]<0):
                  map_bounds[1] = 0
          
            m_s.set_global_bounds(m_p_global_map, map_bounds)
                
            key = random.choice(list(landmark_map))
            fsize = len(landmark_map.get(key))-1
            pos = random.randint(0, fsize)
            feat_pos_x = landmark_map.get(key)[pos].x
            feat_pos_y = landmark_map.get(key)[pos].y
            feat_phi = landmark_map.get(key)[pos].phi
            new_pos = m_s.position(feat_pos_x, feat_pos_y, feat_phi)
            global_feature = m_s.global_map_detected_feature(new_pos, 100, key, "Tree", [1])
            if(m_s.find_global_key(m_p_global_map, key)):
                global_map_entry = m_s.global_map_entry(global_feature)
                m_s.append_map_entry(m_p_global_map,global_map_entry, key)
            else:
                global_map_entry = [m_s.global_map_entry(global_feature)]
                m_s.add_map_entry(m_p_global_map, global_map_entry, key)

        except Exception as e:
            message = "Error: Issue with oracle -  " + str(e)
            print(message)
    '''

    '''
    Used in production when DEVELOPING SEMANTICS ENGINE for separation of production purposes
    reveals all the landmarks on the map using the oracle system 
    
    Uses the oracle file to match the landmarks found by the edge agents and place them in the places they are actually meant to be
    Incorporated into the project due to error with measurements cascading and causing issues 
    
        TO BE REMOVED BEFORE DEPLOYMENT - DO NOT USE FOR DEPLOYMENT 
    
    Go through all of the landmarks in the global feature map and align them to the oracle map 
    
    Note that this method should only be used in testing - Oracle help should not be required on the funcitoning system for 
    map generation / place recognition  
    
    Inputs:
    
         m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
         landmark_map           : stores the ground truth of environment features from the oracle file
    '''
    def reveal_landmarks_v2(self, m_p_global_map,  landmark_map, class_name_map):
        try:
            for key in landmark_map:
                fsize = len(landmark_map.get(key))
                name = class_name_map[key]
                for idx in range(0, fsize):
                    feat_pos_x = landmark_map.get(key)[idx].x
                    feat_pos_y = landmark_map.get(key)[idx].y
                    feat_phi = landmark_map.get(key)[idx].phi
                    new_pos = m_s.position(feat_pos_x, feat_pos_y, feat_phi)
                    global_feature = m_s.global_map_detected_feature(new_pos, 100, key, name, [1])
                    if(m_s.find_global_key(m_p_global_map, key)):
                        global_map_entry = m_s.global_map_entry(global_feature)
                        m_s.append_map_entry(m_p_global_map,global_map_entry, key)
                    else:
                        global_map_entry = [m_s.global_map_entry(global_feature)]
                        m_s.add_map_entry(m_p_global_map, global_map_entry, key)

        except Exception as e:
            message = "Error: Issue with oracle -  " + str(e)
            print(message)


    '''
        Used with oracle and reveal_landmarks functions to keep map bounds constrained
    '''
    def set_bounds(self, m_p_global_map):
         map_bounds = m_s.get_global_bounds(m_p_global_map)
         map_bounds[2] = 25000
         map_bounds[0] = 0
         map_bounds[3] = 25000
         map_bounds[1] = 0
         m_s.set_global_bounds(m_p_global_map, map_bounds)

    '''
        Main function for this file 
        
        Inputs:
        
         m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
         classname_map          : the file containing all of the class names used by YOLO - used to generate a dictionary storing all the possible features extracted adn assigning unique ID's
         oracle                 : Boolean - Use oracle or not?
         landmark_map           : stores the ground truth of environment features from the oracle file
         images_path            : stores the path for images used to represent features on 2d Topo map
        
    '''
    def show_map_main(self, m_p_global_map, class_name_map, oracle, landmark_map, images_path):
        try:
            #color map used to label environments
            color_map = {"Residential": "orange", "Commercial": "blue", "Industrial": "purple", "CommunityFacility": "yellow", "ParksAndRecreation": "green", "TransportAndServices": "grey", "NonUrban": "green", "Empty": "black", "Military": "red"}
            if(oracle == "T"):
                m_s.lock.acquire()
                self.set_bounds(m_p_global_map)
                self.reveal_landmarks_v2(m_p_global_map, landmark_map, class_name_map)
                m_s.lock.release()

            fig = plt.figure()
            ax = fig.add_subplot(111)


            while True:
                OSWait(1000);
                plt.figure().clear()
                plt.close()
                plt.cla()
                plt.clf()
                self.show_plot(m_p_global_map, class_name_map, images_path, fig, ax, color_map)

                '''
                if(oracle == "T"):
                    m_s.lock.acquire()
                    #self.reveal_landmarks(m_p_global_map, landmark_map)
                    m_s.lock.release()
                '''

        except Exception as e:
            message = "Error: Unable to show global map  " + str(e)
            print(message)





