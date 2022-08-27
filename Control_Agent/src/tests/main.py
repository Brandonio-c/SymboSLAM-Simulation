import multiprocessing
from multiprocessing.managers import SyncManager
import mem_struc_t as m_s

m_s.MyManager.register('mem_test', m_s.mem_test)

def update_mem(mem_test_inst):
   #append to list a first time
   loc = m_s.position(1,2,3)
   #m_s.lock.acquire()
   m_s.append_pos_list(mem_test_inst, 0, loc)
   #m_s.lock.release()

   #append to list a second time
   loc = m_s.position(4,5,6)
   #m_s.lock.acquire()
   m_s.append_pos_list(mem_test_inst, 0, loc)
   #m_s.lock.release()

   check = m_s.check(mem_test_inst)

   print(check.get(0).position_list.get(0).x )
   print(check.get(0).position_list.get(0).y )
   print(check.get(0).position_list.get(0).phi )

   print(check.get(0).position_list.get(1).x )
   print(check.get(0).position_list.get(1).y )
   print(check.get(0).position_list.get(1).phi )


def test():
   manager = m_s.Manager()
   mem_test_inst = manager.mem_test()

   m_s.create_map_list(mem_test_inst, 2)

   l = multiprocessing.Lock()
   pool = multiprocessing.Pool(multiprocessing.cpu_count())
   for _ in range(0,2):
        pool.apply_async(func=update_mem, args=(mem_test_inst,))
   pool.close()
   pool.join()

if __name__ == "__main__":
   test()
