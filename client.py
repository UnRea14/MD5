from hashlib import md5
import threading
import multiprocessing
import logging
import time
import socket
import select


class Zone:
    def __init__(self, area, state=-1):
        self.area = area
        self.state = state


class ZoneList:
    def __init__(self):
        self.zone_list: list[Zone] = []

    def __getitem__(self, item):
        return self.zone_list[item]

    def append(self, zone: Zone):
        self.zone_list.append(zone)

    def remove(self, zone: Zone):
        self.zone_list.remove(zone)

    def search_searchable_zone(self):
        for zone in self.zone_list:
            if zone.state == -1:
                zone.state = 1
                return zone
        return None


class Worker:
    def __init__(self, zone, num, hash1):
        self.num = num
        self.zone: Zone = zone
        self.state = "wait"
        self.hash1 = hash1
        self.found = ""

    def work(self):
        while True:
            while self.state == "wait":
                time.sleep(0.001)
            if self.state == "done":
                return

            split = self.zone.area.split(" - ")
            start = int(split[0])
            end = int(split[1])
            while start <= end and self.state != "done":
                start += 1
                s = str(start)
                s = s.zfill(3)
                if md5(s.encode()).hexdigest() == self.hash1:
                    self.found = s
                    print("thread " + str(self.num) + " found it!")
                    self.state = "done"
            if self.state != "done":
                self.state = "wait"


def fill_zone_list(end, start, num_of_cores, zones):
    """
    fills the zones list
    """
    print("----------------------zones----------------------")
    i = 0
    a = int((end - start) / num_of_cores)
    while i < num_of_cores:
        b = start + (a * i)
        zone = str(b) + " - " + str(b + a)
        zones.append(Zone(area=zone))
        print(zones[i].area)
        i += 1
    print("-------------------------------------------------")


def start_threads(workers, zones):
    """
    starts the work of the threads
    """
    i = 0
    while i < len(workers):
        zone = zones.search_searchable_zone()
        if zone is not None:
            workers[i].zone = zone
            if workers[i].state == "wait":
                workers[i].state = "work"
        i += 1


def check_if_found(workers, sock, sok):
    """
    checks if the string is found
    return: True if found, false else
    """
    i = 0
    while i < len(workers):
        for w in workers:
            if w.found != "":
                s = w.found
                message = "found - " + s
                print(message)
                length = str(len(message))
                sok.send((length.zfill(3) + message).encode())
                sock.close()
                return True
            elif w.state == "wait":
                i += 1
    return False


def main():
    print("Connecting...")
    sock = socket.socket()
    sock.connect(('127.0.0.1', 8820))
    print("Connected!")
    size = 0
    s = ""
    threads = []
    workers = []
    zones = ZoneList()
    num_of_cores = multiprocessing.cpu_count()
    for i in range(num_of_cores):
        w = Worker("", i, "")
        workers.append(w)
        t = threading.Thread(target=w.work)
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        threads.append(t)
        t.start()

    while True:
        r_list, w_list, e_list = select.select([sock], [], [])
        for sok in r_list:
            try:
                length = sok.recv(3).decode()
                try:
                    data = sok.recv(int(length)).decode()
                    while len(data) < int(length):
                        data += sok.recv(int(length)-len(data)).decode()
                        time.sleep(0.000001)
                    print("data = " + data)
                    if data == "found":
                        for w in workers:
                            w.state = "done"
                        exit()

                    if "|" in data:  # hash|chars in string|client number
                        split_data = data.split("|")
                        hash1 = split_data[0]
                        for w in workers:
                            w.hash1 = hash1
                        size = int(split_data[1])
                        message = "nof " + str(num_of_cores)
                        length = str(len(message))
                        sok.send((length.zfill(3) + message).encode())

                    elif " - " in data:  # num - num
                        split_data = data.split(" - ")
                        start = int(split_data[0])
                        end = int(split_data[1])
                        if len(s) < size:
                            s = str(start).zfill(size)
                        else:
                            s = str(start)
                        fill_zone_list(end, start, num_of_cores, zones)
                        start_threads(workers, zones)
                        found = check_if_found(workers, sock, sok)
                        if found:
                            for w in workers:
                                w.state = "done"
                            exit()
                        zones = ZoneList()
                        message = "done"
                        length = str(len(message))
                        sok.send((length.zfill(3) + message).encode())

                except ValueError:
                    print("ValueError")
                    exit()

            except ConnectionAbortedError:
                print("CAE")
                exit()


if __name__ == "__main__":
    main()
