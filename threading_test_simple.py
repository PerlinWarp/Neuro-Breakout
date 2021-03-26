# one dimension of the 2d array which is shared
dim = 5000

import numpy as np
from multiprocessing import shared_memory, Process, Lock
from multiprocessing import cpu_count, current_process
import time

lock = Lock()

def add_one(shr_name):
    existing_shm = shared_memory.SharedMemory(name=shr_name)
    np_array = np.ndarray((dim, dim,), dtype=np.int64, buffer=existing_shm.buf)
    lock.acquire()
    np_array[:] = np_array[0] + 1
    lock.release()
    time.sleep(10) # pause, to see the memory usage in top
    print('added one')
    existing_shm.close()

def create_shared_block():

    a = np.ones(shape=(dim, dim), dtype=np.int64)  # Start with an existing NumPy array

    shm = shared_memory.SharedMemory(create=True, size=a.nbytes)
    # # Now create a NumPy array backed by shared memory
    np_array = np.ndarray(a.shape, dtype=np.int64, buffer=shm.buf)
    np_array[:] = a[:]  # Copy the original data into shared memory
    return shm, np_array


print("creating shared block")
shr, np_array = create_shared_block()

_process = Process(target=add_one, args=(shr.name,))
_process.start()


_process.join()

print("Final array")
print(np_array[:10])
print(np_array[10:])

shr.close()
shr.unlink()