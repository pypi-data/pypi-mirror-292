import queue
import threading
from abc import ABCMeta


class DBPool(metaclass=ABCMeta):
    def __init__(self):
        self.connectLock = threading.Lock()
        self.releaseLock = threading.Lock()

        self.queue = queue.Queue()
        self.allList = []

    def get_session(self, timeout=1):
        try:
            self.connectLock.acquire()
            dbImpl = self.queue.get(timeout=timeout)
            return dbImpl

        except:
            return None
        
        finally:
            self.connectLock.release()
    
    def release(self, dbImpl):
        if dbImpl is not None:
            self.releaseLock.acquire()
            self.queue.put(dbImpl)
            self.releaseLock.release()
    
    def check_queue_size(self):
        return self.queue.qsize()