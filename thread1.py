import threading
import logging
import time


class Worker:
    def __init__(self, num):
        self.num = num
        self.more_work = "wait" # more_work, wait, done

    def print(self):
        while True:
            while self.more_work == "wait":
                time.sleep(1)
            if self.more_work == "done":
                return

            logging.debug(f'Starting {self.num}')
            time.sleep(2)
            logging.debug('Exiting')
            self.more_work = "wait"


threads = []
workers = []
for i in range(5):
    w = Worker(i)
    workers.append(w)
    t = threading.Thread(target=w.print)
    print(threading.currentThread().getName())
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    threads.append(t)
    t.start()


for w in workers:
    logging.info("before sleep")
    time.sleep(0.1)
    if w.more_work == "wait":
        w.more_work = "more_work"

logging.info("send done to workers")
for w in workers:
    logging.info("before sleep")
    time.sleep(0.1)
    if w.more_work == "wait":
        w.more_work = "done"
