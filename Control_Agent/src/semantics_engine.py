#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Doc String
Description:

This file is used to assign environment types to segmented partitions of the global map data structure

Modules:

Load_Onto               : loads an ontology
assign_properties       : Old module - Prune
build_semantics         : old module - Prune
transform_feat_map      :Transforms the feature map from the old way of storing it (grouped by feature class) into a spatial format
segment_map             : Segments the global map into 9 partitions and generates a data structure within global map proxy for this
context_reasoner        : Determines environment type based on the feature classes found within a map segment, their spatial proximities and semantic proximities

TODO - change the way items on map are stored in array so that they are easier to find by semantcis enigne!
Possibly - store in some sort of pose graph?
TODO - move map segmentation into show map / map merging

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
    from owlready2 import *
    from rdflib import Graph, Literal, BNode, Namespace, RDF, XSD, OWL, RDFS, URIRef
    from rdflib.plugins.sparql import prepareQuery
    import numpy as np
    import math
except ImportError:
    raise ImportError('Import failed')


'''
    Module used to assign environment types to segmented partitions of the global map data structure
    
    Inputs:
         m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
         classname_map          : the file containing all of the class names used by YOLO - used to generate a dictionary storing all the possible features extracted adn assigning unique ID's
         homeloc                : location of main file 
'''
class semantics_engine:
    def __init__(self, m_p_global_map, class_name_map, homeloc):
        #m_s.lock.acquire()
        #LCDPrintf("building relationships \n")
        #m_s.lock.release()
        #load ontologies into memory
        #SymboSLAM_loc = homeloc + "../ontology/SymboSLAM.owl" #for CLI
        SymboSLAM_loc = homeloc + "ontology/SymboSLAM.owl" #for pycharm #TODO - FIX THIS
        OntoSLAM_loc = homeloc + "ontology/third_party/ontoSLAM.owl"
        Onto4MAT_loc = homeloc + "ontology/third_party/Onto4MAT.owl"
        SymboSLAM = self.load_onto(SymboSLAM_loc)
        #OntoSLAM = self.load_onto(OntoSLAM_loc)
        OntoSLAM = "" #OntoSLAM not currently being used
        #Onto4MAT = self.load_onto(Onto4MAT_loc)
        Onto4MAT = "" #Onto4MAT is a bit big to load during dev / testing
        self.semantics_engine_main(m_p_global_map, class_name_map, SymboSLAM, OntoSLAM, Onto4MAT)


    '''
        Loads ontologies into readable formats
    '''
    def load_onto(self, ontology_file):
        #load up the ontology into memory
        try:
            onto = get_ontology(ontology_file).load()
            sync_reasoner(onto)  #reasoner is started and synchronized here
            return onto
        except Exception as e:
            message = "Error: Unable to load ontology - " + str(e)
            print(message)


    '''
        Experimental code to query OntoSLAM ontology 
    '''
    def q1(self, g):
        qpro = prepareQuery("""
        PREFIX ns1:  <http://github.com/Alex23013/slam-up/OntoSLAM.owl#> 
        PREFIX ns2: <http://www.semanticweb.org/ontologies/2013/7/CORA.owl#>  
        SELECT * {?x ?y ?z} 
        }""" )
        pro = g.query(qpro)
        return pro

    '''
    Does not currently work - Cannot query ontology with sparql
    Old code
    TODO - Prune 
    '''
    def assign_properties(self, m_p_global_map, class_name_map, onto, graph):
        # TODO - change this so it's dynamic and only assigns object properties to new things in teh global map feature list
        # TODO - Prune code
        for key in m_s.get_global_map(m_p_global_map).global_map:
            for idx in range (0, len(m_s.get_global_map(m_p_global_map).global_map.get(key))):
                #Class_ID is the smake as key due to the way the global map structure is set up
                class_ID = m_s.get_global_map(m_p_global_map).global_map.get(key)[idx].global_map_detected_feature.feature_class
                class_name = class_name_map.get(class_ID)
                #Base URL of your ontology has to be given here
                try:
                    #classes = onto.classes();
                    #onto_c_list = list(classes)
                    query = """SELECT * WHERE
                               { ?x a owl:Class . }"""
                    result = list(graph.query(query))

                    #result = graph.query_owlready("""select * {?x ?y ?z} """)
                    print(result)
                    #pro = self.q1(g)

                    '''
                    #query is being run
                    #query = """SELECT * WHERE
                    #           { ?x a owl:Class . }"""
                    class_name = "stop_sign"
                    query = """
                               SELECT ?y
                               { 
                                    ?Class rdfs:label "stop_sign" .
                                }
                            """

                    query2 = """
                               SELECT (COUNT(?x) AS ?nb)
                               { ?x a owl:Class . }
                            """
                    query3 = """
                               SELECT ?x
                               { ?x rdfs:label "stop_sign" . }
                            """
                    #        { ?Class name """ + class_name + """ . }"""
                    query4 = """select * {?x ?y ?z} """
                    stat = list(onto.sparql(query4))
                    '''
                    #query = """SELECT * WHERE { ?x a owl:Class . }"""
                    #result = list(graph.query(query))
                    query = """
                               PREFIX ns1: <https://github.com/Brandonio-c/SYMBO-SLAM/blob/main/Ontologies/Ontological_SLAM.owl#>
                               PREFIX ns2: <http://www.semanticweb.org/brandonio/ontologies/2022/3/Ontological_Slam#>
                               SELECT ?s
                               WHERE{ 
                                    ?s  a ns1:stop_sign 
                                }
                            """
                    result = list(graph.query(query))
                except Exception as e:
                    message = "Error running query on ontology- " + str(e)
                    print(message)



    '''
    
    Transforms the feature map from the old way of storing it (grouped by feature class) into a spatial format
    stores output in global map data structure 
    
    Real roudabout way of getting to this 
    TODO - change global mapping module so the feature map is always stored like this!
    
     Inputs:
         m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
       
       Recalling info from memory within loop is too slow - 
       TODO - Fix - recall entire structure from memory once, save locally then query that structure!
       
    '''
    def transform_feat_map(self,m_p_global_map):
        try:
            #Get the dimensions of currently mapped area
            map_bounds = m_s.get_global_bounds(m_p_global_map)
            width = abs(map_bounds[0]) + abs(map_bounds[2])
            height = abs(map_bounds[1]) + abs(map_bounds[3])
            segment_map = np.empty((width, height), dtype=object)
            gbl_map = m_s.get_global_map(m_p_global_map).global_map
            for key in m_s.get_global_map(m_p_global_map).global_map:
                for idx in range (0, len(m_s.get_global_map(m_p_global_map).global_map.get(key))):
                    feat_x = m_s.get_global_map(m_p_global_map).global_map.get(key)[idx].global_map_detected_feature.position.x
                    feat_y = m_s.get_global_map(m_p_global_map).global_map.get(key)[idx].global_map_detected_feature.position.y
                    segment_map[int(feat_x)][int(feat_y)] =  m_s.get_global_map(m_p_global_map).global_map.get(key)[idx].global_map_detected_feature
            m_s.add_feature_map(m_p_global_map, segment_map)
            return segment_map
        except Exception as e:
            message = "Error: Unable to transform feature map - " + str(e)
            print(message)


    '''
    
    Segments the global map into 9 partitions and generates a data structure within global map proxy for this
    TODO -  Incorporate dynamic segmentation if probability of environment is too low!
    
    ODO - completely rewrite so fragment sectoring is done better
    
    Inputs:
         m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
         env_prob               : blank data structure used to store env probabilities    
    '''
    def segment_map(self, m_p_global_map, env_feats, env_prob):
        try:
            #segment this map into 9 areas  - These areas will be increased in fidelity further depending on whether a high enough probability is found for each segment
            # 0 = x1, 1 = y1, 2 = x2, 3 = y2
            #get the segmented env prob from previous run through
            segmented_map = m_s.get_global_map(m_p_global_map).segmented_map
            segmented_map_prob_dict = {}
            for fragment in segmented_map:
                env_type = max(segmented_map[fragment].env_prob, key=segmented_map[fragment].env_prob.get)
                prob = int(segmented_map[fragment].env_prob[env_type] * 100)
                segmented_map_prob_dict[fragment] = prob
            #Get the dimensions of currently mapped area
            map_bounds = m_s.get_global_bounds(m_p_global_map)
            #segment this map into 9 areas  - These areas will be increased in fidelity further depending on whether a high enough probability is found for each segment
            # 0 = x1, 1 = y1, 2 = x2, 3 = y2
            width = abs(map_bounds[0]) + abs(map_bounds[2])
            height = abs(map_bounds[1]) + abs(map_bounds[3])
            seg_width = width/3
            seg_height = height/3
            #create a2d array for segmented map
            segment_map_index = {}
            #hamburger code - TODO - Fix
            # everything from this point onwards is hanburger code - Need to go back and rewrite this module completely
            if len(segmented_map_prob_dict) > 0:
                #hamburger code - TODO - Fix
                for seg_ID in segmented_map_prob_dict:
                    #even more hamburger code!
                    #segmentation module is just crap atm tbh. Can only go down to sector of 4 in fidenity
                    #TODO - rewrite all
                    if not len(seg_ID) > 3:
                        if segmented_map_prob_dict.get(seg_ID) < 55:
                            m_s.del_fragment(m_p_global_map, seg_ID)
                            #if the segment has a prob that's less than 50 then break that segment in 4 quadrants
                            frac_width = seg_width / 2
                            frac_height = seg_height / 2
                            # get idx and idy from segment ID
                            idx = int(seg_ID.split(",")[0])
                            idy = int(seg_ID.split(",")[1])
                            for idxx in range(0, 2):
                                for idyy in range(0,2):
                                    seg_ID = str(idx) + ',' + str(idxx) + ',' + str(idy) + ',' + str(idyy)
                                    seg_x_start = map_bounds[0] + (seg_width * idx) + (frac_width * idxx)
                                    seg_x_end = map_bounds[0] + (seg_width * idx) + (frac_width * (idxx +1))
                                    seg_y_start = map_bounds[1] + (seg_height * idy) + (frac_height * idyy)
                                    seg_y_end= map_bounds[1] + (seg_height * idy) + (frac_height * (idyy +1))
                                    seg_start = m_s.position(seg_x_start, seg_y_start, 0)
                                    seg_end = m_s.position(seg_x_end, seg_y_end, 0)
                                    index = {"start": seg_start, "end": seg_end}
                                    segment_map_index[seg_ID] = index
                                    fragment = m_s.segmented_map_fragments(seg_ID, index, [], env_feats, env_prob)
                                    m_s.add_fragment(m_p_global_map, seg_ID, fragment)

                        else:
                            pass
                            #TODO - add something?
                    else:
                        pass
                        #TODO - write module
            else:
                for idx in range(0,3):
                    for idy in range(0,3):
                        seg_ID = str(idx) + ',' + str(idy)
                        seg_x_start = map_bounds[0] + seg_width * idx
                        seg_x_end = map_bounds[0] + seg_width * (idx+1)
                        seg_y_start = map_bounds[1] + seg_height * idy
                        seg_y_end= map_bounds[1] + seg_height * (idy+1)
                        seg_start = m_s.position(seg_x_start, seg_y_start, 0)
                        seg_end = m_s.position(seg_x_end, seg_y_end, 0)
                        index = {"start": seg_start, "end": seg_end}
                        segment_map_index[seg_ID] = index
                        fragment = m_s.segmented_map_fragments(seg_ID, index, [], env_feats, env_prob)
                        m_s.add_fragment(m_p_global_map, seg_ID, fragment)

            return segment_map_index
        except Exception as e:
            message = "Error: Unable to segment map - " + str(e)
            print(message)

    '''
        blank data structure used to store env features
    '''
    def env_features(self, environments):
        env_feats = {}
        for env in environments:
            env_feats[env] = []
        return env_feats

    '''
        blank data structure used to store env probabilities
    '''
    def env_prob(self, environments):
        env_prob = {}
        for env in environments:
            env_prob[env] = 0
        return env_prob

    '''
        Determines environment type based on the feature classes found within a map segment, their spatial proximities and semantic proximities
        
            Currently - sums the number of found feature superclass (for environment) and takes max - Need to incorporate function to change this to a probability distribution 
        
        TODO - incorporate spatial and semantic probabilities!
        TODO - incorporate function to produce env probability  
        
        Inputs:
         m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
         onto                   : loaded ontology file
         feature_map            : environment feature map represented spatially
         environments           : list of possible environment types (taken from ontology)
         env_prob               : blank data structure used to store env probabilities  
    '''

    def context_reasoner(self, m_p_global_map, onto, feature_map, env_feats, env_prob, environments):
        try:
            segment_map_index = self.segment_map(m_p_global_map, env_feats, env_prob)
            for key in segment_map_index:
                #this_env_prob = self.env_prob(environments)
                #within this segment, get all of the super classes of the features
                seg_x_start = segment_map_index.get(key).get('start').x
                seg_x_end = segment_map_index.get(key).get('end').x
                seg_y_start = segment_map_index.get(key).get('start').y
                seg_y_end = segment_map_index.get(key).get('end').y
                seg_max_distance = math.sqrt(pow((seg_x_end - seg_x_start),2) + pow((seg_y_end - seg_y_start),2) );
                this_segment = feature_map[int(seg_x_start):int(seg_x_end), int(seg_y_start):int(seg_y_end)]
                flat_feats = this_segment.flatten()
                extracted_feats = flat_feats[flat_feats != None]
                #first, assign likely environment probs for all features
                #only do env probability if num features > 0
                if extracted_feats.size > 0:
                    for item in extracted_feats:
                        #get all the environments assosciated with that feature
                        feat_name = (("*" + item.name).replace(" ", "_"))#.lower() - SymboSLAM updated ontology IS CASE SENSITIVE - DESIGN FLAW #TODO FIX
                        m_s.update_fragment_feat_list(m_p_global_map, key, item.name)
                        #query that ontology Boi!
                        res = list(onto.search(iri = feat_name))
                        if res:
                            #get the superclass of this feature
                            env_possibilities = list(res[0].is_a)
                            for env in env_possibilities:
                                #hamburger code - TODO Fix
                                if env.name in environments:
                                #if env.name != "static_objects" and env.name != "dynamic_objects":
                                    #currently no way to determine semantic closeness / proximity - TODO Fix
                                    semantic_proximity = 1
                                    env_feature = m_s.env_feature(item, semantic_proximity)
                                    m_s.increase_fragment_env_prob(m_p_global_map, key, env.name, env_feature)

                    #now, go through each environment in this segments env probability and compute its probability
                    #get the max number of inferences possible
                    #for a segment with x feautes in it, that is x* (x-1)
                    num_features = len(m_s.get_fragment_feat_list(m_p_global_map, key))
                    max_inferences = num_features * (num_features - 1)
                    for env in env_prob:
                        #calculate env likelihood using feature prob, semantic proximity and spatial proximity
                        this_env = m_s.get_env_features(m_p_global_map, key, env)
                        prob_sum = 0
                        num_inferences = 0
                        #TODO - classify for features with only 1 env type
                        for feature_A in this_env:
                            for feature_B in this_env:
                                if(feature_A.feature.position.x != feature_B.feature.position.x or feature_A.feature.position.y != feature_B.feature.position.y):
                                    distance = math.sqrt(pow((feature_A.feature.position.x - feature_B.feature.position.x),2) + pow((feature_A.feature.position.y - feature_B.feature.position.y),2) );
                                    norm_distance = distance / seg_max_distance
                                    #Todo - normalie distance before putting into eqn
                                    #requires knowledge of all distance
                                    prob_sum = prob_sum + (((((feature_A.prob/100) * feature_A.feature.confidence) + ((feature_B.prob/100) * feature_B.feature.confidence)) /2 )* (1 - norm_distance))
                                    num_inferences +=1

                        if num_inferences !=0:
                            prob = prob_sum / num_inferences
                            #lastly, we want to penalise for having less inferences and reward for having more
                            prob = (prob * 0.5) +  ((num_inferences / max_inferences) *0.5)
                        else:
                            prob = 0

                        m_s.set_env_prob(m_p_global_map, key, env, prob)
                else:
                    m_s.set_env_prob(m_p_global_map, key, 'Empty', 1)

                '''
                gmap = m_s.get_global_map(m_p_global_map)
                segmented_map = gmap.segmented_map
                fragment = segmented_map[key]
                
                print("")
                '''



        except Exception as e:
            message = "Error with context reasoner - " + str(e)
            print(message)



    '''
    Main loop for this module
    Returns a probability distribution of possible environmental contexts and stores it in global map data structure proxy
    
    Inputs:
        
         m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent
         classname_map          : the file containing all of the class names used by YOLO - used to generate a dictionary storing all the possible features extracted adn assigning unique ID's
         SymboSlam              : Loaded SymboSlam ontology
         OntoSlam               : Loaded OntoSlam ontology
         Onto4MAT               : Loaded Onto4MAT ontology
    '''
    def semantics_engine_main(self, m_p_global_map, class_name_map, SymboSLAM, OntoSLAM, Onto4MAT ):
        try:
            #graph = SymboSLAM.as_rdflib_graph()
            #get a list of teh possible environments from SymboSLAM
            base_environments = list(SymboSLAM.Environments.subclasses())
            environments = []
            for env in base_environments:
                cur_env = str(env.name)
                environments.append(cur_env)
            env_feats = self.env_features(environments)
            env_prob = self.env_prob(environments)
            #this process was moved out of loop for development
            # feature map transformation much be done at each run through loop as new features are added in
            #TODO - make process more efficient
            #TODO - add back into loop
            feature_map = self.transform_feat_map(m_p_global_map)
            while True:
                m_s.lock.acquire()
                #self.build_semantics(m_p_global_map, class_name_map, onto, graph)
                self.context_reasoner(m_p_global_map, SymboSLAM, feature_map, env_feats, env_prob, environments)
                m_s.lock.release()
                #OSWait(3000);

        except Exception as e:
            message = "Error with semantics engine - " + str(e)
            print(message)

          





