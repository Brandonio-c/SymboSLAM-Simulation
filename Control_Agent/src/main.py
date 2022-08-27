#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Doc String

Description: main file control agent algorithm used to conduct ontological SLAM

 TODO
- hange the CLI way of taking in information - Make a GUI?

- Add CLI functionality to train or test on this with semantics engine

- fix the multi-processing display issue
    LCD display on simulated robot willnot updated when run through multi processing
    !!!!! - issue with robios X11 functionality - error code

    [xcb] Unknown sequence number while processing queue
    [xcb] Most likely this is a multi-threaded client and XInitThreads has not been called
    [xcb] Aborting, sorry about that.
window: ../../src/xcb_io.c:274: poll_for_event: Assertion `!xcb_xlib_threads_sequence_lost' failed.

every other RobIos function works with python multi-rpocessing except for this one
- possibly use spawn method to fix?

ISSUE - not currently working with more than 4 robots - TODO investigate


TODO - wall detection
TODO - prune imports
TODO - further segmentation in semantics engine module

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
    import sys
    import getopt
    import concurrent.futures
    import multiprocessing
    from multiprocessing import Process, Manager
    from multiprocessing.managers import BaseManager
    from multiprocessing.managers import SyncManager, AutoProxy, MakeProxyType, public_methods
    from multiprocessing import set_start_method
    from multiprocessing import get_context
    from functools import partial
    import ctypes
    import map_structs as m_s
    import comms as c
    import read_file as r_f
    import agent_comms as a_c
    import global_map as g_m
    import save_maps as sa_m
    import show_map as sh_m
    import logging
    from inspect import signature
    from functools import wraps
    from multiprocessing import managers
    import semantics_engine as s_e
except ImportError:
    raise ImportError('Import test failed')

'''
This C++ module is required for multi threading with RobIOS functions (used by EyeSim software)
'''
try:
    x11 = ctypes.cdll.LoadLibrary('libX11.so')
    x11.XInitThreads()
except:
    print("Warning: failed to XInitThreads()")

m_s.MyManager.register('map_list', m_s.map_list)
m_s.MyManager.register('global_map', m_s.global_map_)
mutex = multiprocessing.Lock()

'''
Monkeypatch to fix multi processing shared memory with object issues (bug in python)

    REQUIRED for python version <= 3.6 
    
'''
# Backport of https://github.com/python/cpython/pull/4819
# Improvements to the Manager / proxied shared values code
# broke handling of proxied objects without a custom proxy type,
# as the AutoProxy function was not updated.
#
# This code adds a wrapper to AutoProxy if it is missing the
# new argument.


logger = logging.getLogger(__name__)
orig_AutoProxy = managers.AutoProxy
@wraps(managers.AutoProxy)
def AutoProxy(*args, incref=True, manager_owned=False, **kwargs):
    # Create the autoproxy without the manager_owned flag, then
    # update the flag on the generated instance. If the manager_owned flag
    # is set, `incref` is disabled, so set it to False here for the same
    # result.
    autoproxy_incref = False if manager_owned else incref
    proxy = orig_AutoProxy(*args, incref=autoproxy_incref, **kwargs)
    proxy._owned_by_manager = manager_owned
    return proxy
def apply():
    if "manager_owned" in signature(managers.AutoProxy).parameters:
        return

    logger.debug("Patching multiprocessing.managers.AutoProxy to add manager_owned")
    managers.AutoProxy = AutoProxy

    # re-register any types already registered to SyncManager without a custom
    # proxy type, as otherwise these would all be using the old unpatched AutoProxy
    SyncManager = managers.SyncManager
    registry = managers.SyncManager._registry
    for typeid, (callable, exposed, method_to_typeid, proxytype) in registry.items():
        if proxytype is not orig_AutoProxy:
            continue
        create_method = hasattr(managers.SyncManager, typeid)
        SyncManager.register(
            typeid,
            callable=callable,
            exposed=exposed,
            method_to_typeid=method_to_typeid,
            create_method=create_method,
        )

'''
Main function to be called from CLI

TODO - Add GUI

Inputs:
0   : this file locaiton
1   : number of agents
2   : agents starting location file
3   : name of the map - used to save the map generated from this architecture
4   : the file containing all of the class names used by YOLO - used to generate a dictionary storing all the possible features extracted adn assigning unique ID's
5   : boolean - Load a previous run or not
6   : map name 
7   : map name 
8   : run type for semantics engine - train or test
6-8 no longer required - TODO Prune 
9   :  Boolean - Use oracle or not
10  :   oracle file - contains the ground truth for features and their lcoations within the env
11  : images used to etter represent found features in show map module

'''
def main(argv):
    #apply monkey patch
    apply()

    #------------------------------------------------ get params from CLI
    homeloc = sys.argv[0]
    homeloc = homeloc.replace('./main.py', '')
    homeloc = homeloc.replace('main.py', '')
    homeloc = homeloc.replace('src/', '')
    agent_num = sys.argv[1]
    location_file = homeloc + sys.argv[2]
    map_name = homeloc + sys.argv[3]
    class_name_file = homeloc + sys.argv[4]
    load            = sys.argv[5]
    run_type        = sys.argv[8]
    oracle          = sys.argv[9]
    oraclefile      = homeloc + sys.argv[10]
    images_path      = homeloc + sys.argv[11]
    #------------------------------------------------ get params from CLI

    #initialise data taken in from CLI
    #landmark_map stores the ground truth of environment features from the oracle file
    landmark_map = {}
    if(oracle == "T"):
        landmark_map = r_f.read_oraclefile(oraclefile)
    agent_start_location = r_f.read_agent_loc(location_file)
    class_name_map = r_f.read_class_names(class_name_file)
    #TODO - uncomment this!
    #agent_ID_map = c.comms_init()
    #TODO - uncomment this!

    #initialise proxies for multi-processing data structures
    manager = m_s.Manager()
    m_p_map_list = manager.map_list()
    manager = m_s.Manager()
    m_p_global_map = manager.global_map()

    if load == "T":
        try:
            local_map_file = homeloc + sys.argv[6]
            global_map_file = homeloc + sys.argv[7]
            map_list_load = sa_m.load_local_map(local_map_file)
            global_map_load = sa_m.load_global_map(global_map_file)
            m_s.set_map_list(m_p_map_list, map_list_load)
            m_s.set_global_map(m_p_global_map, global_map_load)
        except Exception as e:
            message = "Error: Unable to load map list- " + str(e)
            print(message)
            m_s.create_map_list(m_p_map_list, agent_num)
    else:
        m_s.create_map_list(m_p_map_list, agent_num)


    #start the multi-processing pool and add submodules
    pool = multiprocessing.Pool(processes=(5), initializer=m_s.init, initargs=(mutex,)) #(int(agent_num) + 3)


    try:

        #start the semantics engine
        #with get_context("spawn").Pool() as pool: - ?Doesn't work? - just use the regular pool and don't mess with the spawn method

        #Issues are caused by having multiple processes with the same control agent
        #TODO - fix this
        # opt 1 - receive all comms from a single control agent ID and then split processing up from there
        # opt2 - somehow assign multiple ID's for one control agent
        #for x in range(0,int(agent_num)):
        #x = 1
        #pool.apply_async(func=a_c.agent_comms, args=[agent_ID_map,  m_p_map_list, x])

        #Add global map process to the pool
        #pool.apply_async(func=g_m.global_map, args=[agent_num, agent_ID_map, agent_start_location, map_name, class_name_map,m_p_map_list, m_p_global_map])

        #Add save maps process to the pool
        #pool.apply_async(func=sa_m.save_maps, args=[map_name, m_p_map_list, m_p_global_map, ])

        #Show the global map
        pool.apply_async(func=sh_m.show_map, args=[m_p_global_map, class_name_map, oracle, landmark_map, images_path])

        #Add semantics engine process to the pool
        pool.apply_async(func=s_e.semantics_engine, args=[m_p_global_map, class_name_map, homeloc])

        pool.close()
        pool.join()
    except Exception as e:
        message = "Error: unable to start thread - "  + str(e)
        print (message)


    #main loop to keep this file running continuously
    while True:
        OSWait(300)
        ####m_s.lock.acquire()   # lock
        key = KEYGet()
        if key==KEY4:
            break
            exit()
        ####m_s.lock.release ()  # unlock


#function run when called from CLI
if __name__ == "__main__":
   #set_start_method("spawn")
   #multiprocessing.set_start_method('fork')
   LCDMenu("", "", "", "END")
   main(sys.argv[1:])
