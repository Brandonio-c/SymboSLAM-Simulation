#!/usr/bin/env python3
# -*- coding: utf-8 -*-
''' Doc String
Description: stores all the structs used in control agent architecture

Two proxies are used to store two separate data structures

m_p_map_list           : multi-processing local map list - proxy that stores the local maps of each edge agent and allows for multi-processing
m_p_global_map         : multi-processing global map list - proxy that stores the global map of the control agent

These proxies are used to enable these data structures to be used in a multi-processing manner over many modules

Note that, to edit these data structures, two functions are required. One that can be called directly from this file and one that is called from within the data structure class

TODO - Update the mapping structure data structure so it is stored spatially and not grouped by feature type
     - update data structure so it is stored on a pose graph

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
    import string
    from eye import *
    from dataclasses import dataclass
    import multiprocessing
    from multiprocessing.managers import BaseManager
    from multiprocessing.managers import SyncManager, AutoProxy, MakeProxyType, public_methods
    import numpy as np
except ImportError:
    raise ImportError('Import failed')


#include "eyebot++.h"

def init(l):
    global lock
    lock = l

class MyManager(BaseManager): pass

def Manager():
    m = MyManager()
    m.start()
    return m

@dataclass
class position:
  def __init__(self, x, y, phi):
    self.x: float = x
    self.y: float = y
    self.phi: float = phi
  def update(self, pos):
    self.x = pos.x
    self.y = pos.y
    self.phi = pos.phi

@dataclass
class detected_feature:
  def __init__(self, pos, conf, feat_class, name):
    self.position: map_list.position = pos
    self.confidence: float = conf
    self.feature_class: int = feat_class
    self.name: string = name
    self.property = None

@dataclass
class local_map:
    def __init__(self, pos, pos_list, det_feat_list):
        self.cur_position: position = pos
        self.position_list: list[position] = pos_list
        self.detected_feature_list: list[map_list.detected_feature] = det_feat_list

    def update_cur_pos(self, pos):
        self.cur_position.update(pos)

    def append_pos_list(self, pos):
        self.position_list.append(pos)

    def append_feat_list(self, pos):
        self.detected_feature_list.append(pos)

class map_list(object): #MapProxy
  def __init__(self):
    self.map_list = {}

  def create_map_list(self, agent_num):
    for x in range(0,int(agent_num)):
        pos = position(0,0,0) #needs a dummy variable so it can be updated
        ls1 =[]
        ls2 =[]
        self.map_list[x] = (local_map(pos, ls1, ls2))


  def update_cur_pos(self, agent_map_assosciation, pos):
      self.map_list.get(agent_map_assosciation).update_cur_pos(pos)

  def append_pos_list(self, agent_map_assosciation, pos):
      self.map_list.get(agent_map_assosciation).append_pos_list(pos)

  def append_feat_list(self, agent_map_assosciation, feat):
      self.map_list.get(agent_map_assosciation).append_feat_list(feat)

  def pos_list_size(self, x):
      return len(self.map_list.get(x).position_list)

  def pos_fm_list(self, x, y):
      return self.map_list.get(x).position_list[y]

  def update_pos_list(self, x, y, pos):
      self.map_list.get(x).position_list[y].update(pos)

  def feat_list_size(self, x):
      return len(self.map_list.get(x).detected_feature_list)

  def pos_fm_feat_list(self, x, y):
      return self.map_list.get(x).detected_feature_list[y].position

  def update_feat_list(self, x, y, pos):
      self.map_list.get(x).detected_feature_list[y].position.update(pos)

  def get_feature_class(self, x, y):
      return self.map_list.get(x).detected_feature_list[y].feature_class

  def det_feature(self, x, y):
      return self.map_list.get(x).detected_feature_list[y]

  def get_maps(self):
      return self.map_list

  def set_map_list(self, map_list_):
      self.map_list = map_list_

#----------------------------------------------------------------------------------------------------------------------

def create_map_list(proxy, agent_num):
   proxy.create_map_list(agent_num)

def update_cur_pos(proxy, agent_map_assosciation, pos):
    proxy.update_cur_pos(agent_map_assosciation, pos)

def append_pos_list(proxy, agent_map_assosciation, pos):
    proxy.append_pos_list(agent_map_assosciation, pos)

def append_feat_list(proxy, agent_map_assosciation, feat):
    proxy.append_feat_list(agent_map_assosciation, feat)

def pos_list_size(proxy, x):
    return proxy.pos_list_size(x)

def pos_fm_list(proxy, x, y):
    return proxy.pos_fm_list(x,y)

def update_pos_list(proxy, x, y, pos):
    proxy.update_pos_list(x, y, pos)

def feat_list_size(proxy, x):
    return proxy.feat_list_size(x)

def pos_fm_feat_list(proxy, x, y):
    return proxy.pos_fm_feat_list(x,y)

def update_feat_list(proxy, x, y, pos):
    proxy.update_feat_list(x, y, pos)

def get_feature_class(proxy, x, y):
    return proxy.get_feature_class(x, y)

def det_feature(proxy, x, y):
    return proxy.det_feature(x, y)

def get_maps(proxy):
    return proxy.get_maps()

def set_map_list(proxy, map_list_):
    proxy.set_map_list(map_list_)

#----------------------------------------------------------------------------------------------------------------------

#TODO - merge global map and local map detected feature ito one dataclass
@dataclass
class global_map_detected_feature:
    def __init__(self, pos, conf, feat_class, name, agent_IDs):
        self.position: position = pos
        self.confidence: float = conf
        self.feature_class: int = feat_class
        self.name: string = name
        self.agent_IDs: list[int] = agent_IDs


# not needed - TODO Prune
@dataclass
class global_map_entry:
        def __init__(self, feat):
            self.global_map_detected_feature: list[global_map_detected_feature] = feat


#----------------------------------------------------------------------------------------------------------------------

@dataclass
class env_feature:
  def __init__(self, detected_feature, prob):
    self.feature: global_map_detected_feature = detected_feature
    self.prob: float = prob


@dataclass
class segmented_map_fragments:
  def __init__(self,seg_ID, index ,features, env_features, env_prob):
    self.seg_ID: string = seg_ID
    self.index: dict= index
    self.features: list = features
    self.env_features: dict = env_features
    self.env_prob: dict = env_prob

  def update_features(self, feature):
      self.features.append(feature)

  def increase_fragment_env_prob(self, env_name, env_feature):
      self.env_features[env_name].append(env_feature)

  def set_env_prob(self, env_name, prob):
      self.env_prob[env_name] = prob





#----------------------------------------------------------------------------------------------------------------------

class global_map_(object):
  def __init__(self):
    self.global_map = {}
    self.bounds = [0,0,0,0]
    self.segmented_map = {}
    self.transformed_feat_map = ""

  def find_global_key(self, feature_class):
      return feature_class in self.global_map

  def glob_map_feat_list_size(self, feature_class):
      return len(self.global_map.get(feature_class))

  def pos_fm_feat_list(self, feature_class, z):
      return self.global_map.get(feature_class)[z].global_map_detected_feature.position

  def append_agent(self, feature_class, z, agent_ID):
      self.global_map.get(feature_class)[z].global_map_detected_feature.agent_IDs.append(agent_ID)

  def add_map_entry(self, map_entry, feature_class):
      self.global_map[feature_class] = map_entry

  def append_map_entry(self, map_entry, feature_class):
      self.global_map.get(feature_class).append(map_entry)

  def get_global_map(self):
      return self

  def set_global_map(self, global_map_):
      self.global_map = global_map_.global_map
      self.bounds     = global_map_.bounds

  def get_global_bounds(self):
      return self.bounds

  def set_global_bounds(self, global_bounds_):
      self.bounds = global_bounds_

  def remove_key(self, key):
      self.global_map.pop(key)

  def update_glob_map(self, key, feature_pos, feature):
      self.global_map.get(key)[feature_pos].global_map_detected_feature.position.update(feature)

  def delfeat_glob_map(self, key, feature_pos):
      del self.global_map.get(key)[feature_pos]

  def add_feature_map(self, feature_map):
      self.transformed_feat_map = feature_map

  def add_fragment(self, seg_ID, seg_map_frag):
      self.segmented_map[seg_ID] = seg_map_frag

  def update_fragment_feat_list(self, seg_ID, feature):
    self.segmented_map.get(seg_ID).update_features(feature)

  def increase_fragment_env_prob(self, seg_ID, env_name, env_feature):
    self.segmented_map.get(seg_ID).increase_fragment_env_prob(env_name, env_feature)

  def get_env_features(self,  seg_ID, env_name):
      return self.segmented_map.get(seg_ID).env_features.get(env_name)

  def set_env_prob(self, seg_ID, env_name, prob):
      self.segmented_map.get(seg_ID).set_env_prob(env_name, prob)

  def get_env_prob(self, seg_ID):
    return self.segmented_map.get(seg_ID).env_prob

  def get_fragment_feat_list(self, seg_ID):
    return self.segmented_map.get(seg_ID).features

  def del_fragment(self, seg_ID):
    self.segmented_map.__delitem__(seg_ID)

#----------------------------------------------------------------------------------------------------------------------

def find_global_key(proxy, feature_class):
    return proxy.find_global_key(feature_class)

def glob_map_feat_list_size(proxy, feature_class,):
    return proxy.glob_map_feat_list_size(feature_class)

def pos_fm_glob_feat_list(proxy, feature_class, z):
    return proxy.pos_fm_feat_list(feature_class, z)

def append_agent(proxy,feature_class, z, agent_ID):
    proxy.append_agent(feature_class, z, agent_ID)

def add_map_entry(proxy, map_entry, feature_class):
    proxy.add_map_entry(map_entry, feature_class)

def append_map_entry(proxy, map_entry, feature_class):
    proxy.append_map_entry(map_entry, feature_class)

def get_global_map(proxy):
    return proxy.get_global_map()

def set_global_map(proxy, global_map_):
    proxy.set_global_map(global_map_)

def get_global_bounds(proxy):
    return proxy.get_global_bounds()

def set_global_bounds(proxy, global_bounds_):
    proxy.set_global_bounds(global_bounds_)

def remove_key(proxy, key):
    proxy.remove_key(key)

def update_glob_map(proxy, key, feature_pos, feature):
    proxy.update_glob_map( key, feature_pos, feature)

def delfeat_glob_map(proxy, key, feature_pos):
    proxy.delfeat_glob_map(key, feature_pos)

def add_feature_map(proxy, feature_map):
    proxy.add_feature_map(feature_map)

def add_fragment(proxy, seg_ID, seg_map_frag):
    proxy.add_fragment(seg_ID, seg_map_frag)

def update_fragment_feat_list(proxy, seg_ID, feature):
    proxy.update_fragment_feat_list(seg_ID, feature)

def increase_fragment_env_prob(proxy, seg_ID, env_name, env_feature):
    proxy.increase_fragment_env_prob(seg_ID, env_name, env_feature)

def get_env_features(proxy,  seg_ID, env_name):
    return proxy.get_env_features(seg_ID, env_name)

def set_env_prob(proxy, seg_ID, env_name, prob):
    proxy.set_env_prob(seg_ID, env_name, prob)

def get_env_prob(proxy, seg_ID):
    return proxy.get_env_prob(seg_ID)

def get_fragment_feat_list(proxy, seg_ID):
    return proxy.get_fragment_feat_list(seg_ID)

def del_fragment(proxy, seg_ID):
    proxy.del_fragment(seg_ID)
#----------------------------------------------------------------------------------------------------------------------





