import threading
import logging
import time


class Worker:
    def __init__(self, num):
        self.num = num

    def print(self):
        logging.debug(f'Starting {self.num}')
        time.sleep(2)
        logging.debug('Exiting')


threads = []
for i in range(5):
    t = threading.Thread(target=Worker(i).print, args=(i,))
    print(threading.currentThread().getName())
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    threads.append(t)
    t.start()
