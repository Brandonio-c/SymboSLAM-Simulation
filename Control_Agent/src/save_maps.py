#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Doc String

saves and loads global / local maps

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

try:
    from eye import *
    import map_structs as m_s
    import sys
    import os
    import multiprocessing
    import pickle
except ImportError:
    raise ImportError('Import  failed')

''''''
def load_local_map(map_name):
    with open(map_name + '/local_maps.data', 'rb') as config_dictionary_file:
        config_dictionary = pickle.load(config_dictionary_file)
        return config_dictionary

''''''
def load_global_map(map_name):
     with open(map_name + '/global_map.data', 'rb') as config_dictionary_file:
        config_dictionary = pickle.load(config_dictionary_file)
        return config_dictionary

''''''
class save_maps:
    """Class Description"""
    def __init__(self, map_name, m_p_map_list, m_p_global_map):
        #m_s.lock.acquire()
        #LCDPrintf("saving maps \n")
        #m_s.lock.release()
        self.save_main(map_name, m_p_map_list, m_p_global_map)

    ''''''
    def save_local_map(self, map_name, m_p_map_list):
        local_maps = m_s.get_maps(m_p_map_list)
        with open(map_name + '/local_maps.data', 'wb') as config_dictionary_file:
            pickle.dump(local_maps, config_dictionary_file)

    ''''''
    def save_global_map(self, map_name, m_p_global_map):
        global_map = m_s.get_global_map(m_p_global_map)
        with open(map_name + '/global_map.data', 'wb') as config_dictionary_file:
            pickle.dump(global_map, config_dictionary_file)


    def save_main(self, map_name, m_p_map_list, m_p_global_map):
        if not os.path.exists(map_name):
            os.mkdir(map_name)
            print("Directory '% s' created \n" % map_name)
        while True:
            OSWait(10000);
            m_s.lock.acquire()
            self.save_local_map(map_name, m_p_map_list)
            self.save_global_map(map_name, m_p_global_map)
            m_s.lock.release()




