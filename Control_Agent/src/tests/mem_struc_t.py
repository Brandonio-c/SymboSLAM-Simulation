try:
    import string
    from dataclasses import dataclass
    import multiprocessing
    from multiprocessing.managers import BaseManager
    from multiprocessing.managers import SyncManager, AutoProxy, MakeProxyType, public_methods
except ImportError:
    raise ImportError('Import test failed')


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
class local_map:
    def __init__(self, pos, pos_list, det_feat_list):
        self.cur_position: position = pos
        self.position_list: list[position] = pos_list

    def append_pos_list(self, pos):
        self.position_list.append(pos)

#----------------------------------------------------------------------------------------------------------

class mem_test(object):
  def __init__(self):
    self.map_list = {}

  def create_map_list(self, agent_num):
    for x in range(0,int(agent_num)):
        pos = position
        ls1 =[]
        ls2 =[]
        self.map_list[x] = (local_map(pos, ls1, ls2))


  def append_pos_list(self, map_list_pos, position):
      self.map_list.get(map_list_pos).append_pos_list(position)


  def check(self):
      return self.map_list


#----------------------------------------------------------------------------------------------------------

def append_pos_list(proxy, map_list_pos, position):
    proxy.append_pos_list(map_list_pos, position)


def create_map_list(proxy, agent_num):
  proxy.create_map_list(agent_num)

def check(proxy):
  return proxy.check()

