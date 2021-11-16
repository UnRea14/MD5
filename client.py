from hashlib import md5
import threading
import multiprocessing
import logging
import time
import socket
import select


class Worker:
    def __init__(self, zone, num, hash1):
        self.num = num
        self.zone = zone
        self.state = "wait"
        self.hash1 = hash1
        self.found = ""

    def work(self):
        while True:
            while self.state == "wait":
                time.sleep(0.001)
            if self.state == "done":
                return

            logging.debug(f'Starting thread {self.num}')
            start = self.zone.split(" - ")[0]
            end = self.zone.split(" - ")[1]
            while start < end and self.state != "done":
                start += 1
                s = str(start)
                s = s.zfill(3)
                if md5(s.encode()).hexdigest() == self.hash1:
                    self.found = s
            if self.state != "done":
                self.state = "wait"
            logging.debug(f'Exiting thread {self.num}')


def main():
    print("Connecting...")
    sock = socket.socket()
    sock.connect(('127.0.0.1', 8820))
    print("Connected!")
    size = 0
    s = ""
    id1 = "0"
    found = False
    threads = []
    workers = []
    zones = []
    num_of_cores = multiprocessing.cpu_count()
    for i in range(5):
        w = Worker("", i, "")
        workers.append(w)
        t = threading.Thread(target=w.work)
        print(threading.currentThread().getName())
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        threads.append(t)
        t.start()

    while True:
        r_list, w_list, e_list = select.select([sock], [sock], [])
        for sok in r_list:
            try:
                length = sok.recv(3).decode()
                try:
                    data = sok.recv(int(length)).decode()
                    while len(data) < int(length):
                        data += sok.recv(int(length)-len(data)).decode()
                        time.sleep(0.000001)
                    print(data)
                    if data == "found":
                        quit()
                    if "|" in data:  # hash|chars in string|client number
                        hash1 = data.split("|")[0]
                        for w in workers:
                            w.hash1 = hash1
                        size = int(data.split("|")[1])
                        id1 = data.split("|")[2]
                        message = id1 + ": " + str(num_of_cores)
                        length = str(len(message))
                        sok.send((length.zfill(3) + message).encode())

                    elif " - " in data:  # num - num
                        splitted_data = data.split(" - ")
                        start = int(splitted_data[0])
                        end = int(splitted_data[1])
                        if len(s) < size:
                            s = str(start).zfill(size)
                        else:
                            s = str(start)

                        #  fill zones list
                        i = 0
                        a = (end - start) / num_of_cores
                        while i < num_of_cores:
                            b = start + a * i
                            zones.append(str(b) + " - " + str(b + a))

                        #  start work of threads
                        i = 0
                        logging.info("start work")
                        while i < len(workers):
                            workers[i].zone = zones[i]
                            if workers[i].state == "wait":
                                workers[i].state = "work"

                        #  check if string is found
                        for w in workers:
                            if w.found != "":
                                s = w.found
                                logging.info("send done to workers")
                                w.state = "done"
                                message = "found - " + s
                                print(message)
                                length = str(len(message))
                                sok.send((length.zfill(3) + message).encode())
                                sok.close()
                                found = True
                            elif found:
                                w.state = "done"
                        if found:
                            exit()
                        message = id1 + " done"
                        length = str(len(message))
                        sok.send((length.zfill(3) + message).encode())

                except ValueError:
                    print("ValueError")
                    quit()

            except ConnectionAbortedError:
                print("CAE")
                quit()


if __name__ == "__main__":
    main()
