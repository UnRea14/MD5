from hashlib import md5
import socket
import select
import math
import time


class Searcher:
    def __init__(self, id1=-1, sock=None, num_of_cores=-1, area=""):
        self.id1 = id1
        self.sock = sock
        self.area_of_search = area
        self.num_of_cores = num_of_cores


class SearcherList:
    def __init__(self):
        self.lst: [Searcher] = []

    def append(self, searcher: Searcher):
        self.lst.append(searcher)

    def remove(self, searcher: Searcher):
        self.lst.remove(searcher)

    def search_by_sock(self, sock: socket):
        for searcher in self.lst:
            if searcher.sock == sock:
                return searcher
        return None

    def search_by_id(self, id1: int):
        for searcher in self.lst:
            if searcher.id1 == id1:
                return searcher
        return None


class Zone:
    def __init__(self, area):
        self.area = area
        self.state = -1  # -1 = not worked on, 0 = worked on, 1 = finished


class SearchZones:
    def __init__(self, size_of_string):
        self.zones_lst = []
        num = 10 ** size_of_string
        zone_count = int(math.sqrt(num))
        i = 0
        start = "0"
        while i < zone_count:
            end = str(int(start) + zone_count)
            self.zones_lst.append(Zone(start + " - " + end))
            start = end
            i += 1

    def search_in_lst(self, num_of_cores):
        zones = []
        i = 0
        while i < len(self.zones_lst):
            if self.zones_lst[i].state == -1:
                self.zones_lst[i].state = 0
                zones.append(self.zones_lst[i])
                if len(zones) == num_of_cores:
                    break
            i += 1
        return zones

    def remove_zone(self, area):
        for zone in self.zones_lst:
            if zone.area == area:
                self.zones_lst.remove(zone)
                return


def main():
    """
    hash1 = input("Enter hash: ")
    print("hash - " + hash1)
    size = 10
    """
    start_string = input("Enter a string: ")
    hash1 = md5(start_string.encode()).hexdigest()
    print("hash - " + hash1)
    size = len(start_string)
    search_zones = SearchZones(size_of_string=size)
    print("Setting up server...")
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8820))
    server_socket.listen()
    print("Listening...")
    messages_to_send = []
    client_sockets = []
    id1 = 0
    searcher_lst = SearcherList()
    found = False
    while True:
        r_list, w_list, e_list = select.select([server_socket] + client_sockets, client_sockets, [], 0.01)
        for sock in r_list:
            if sock == server_socket:
                connection, client_address = sock.accept()
                client_sockets.append(connection)
                s = f"{hash1}|{size}|{id1}"
                length = str(len(s))
                message = length.zfill(3) + s
                messages_to_send.append((connection, message))
                searcher_lst.append(Searcher(sock=connection, num_of_cores=-1))
                id1 += 1

            else:
                try:
                    length = sock.recv(3).decode()
                    if length == "":  # sock disconnected
                        disconnected_searcher = searcher_lst.search_by_sock(sock=sock)
                        for zone in search_zones.zones_lst:
                            if zone.area == disconnected_searcher.area_of_search:
                                zone.state = -1
                                break
                        searcher_lst.remove(disconnected_searcher)
                        client_sockets.remove(sock)
                        sock.close()

                    try:
                        data = sock.recv(int(length)).decode()
                        while len(data) < int(length):
                            data += sock.recv(int(length) - len(data)).decode()
                            time.sleep(0.000001)
                        print(data)
                        if found and "done" in data:
                            message = "005found"
                            sock.send(message.encode())
                            client_sockets.remove(sock)
                            sock.close()
                            if not client_sockets:
                                server_socket.close()
                                exit()

                        elif ":" in data:
                            split_data = data.split(": ")
                            num_of_cores = int(split_data[1])
                            id1 = int(split_data[0])
                            zones = search_zones.search_in_lst(num_of_cores)
                            start = zones[0].area.split(" - ")[0]
                            end = zones[len(zones) - 1].area.split(" - ")[1]
                            s = start + " - " + end
                            searcher = searcher_lst.search_by_sock(sock)
                            searcher.id1 = id1
                            searcher.area_of_search = s
                            searcher.num_of_cores = num_of_cores
                            length = str(len(s))
                            message = length.zfill(3) + s
                            messages_to_send.append((sock, message))

                        elif "found" in data:
                            client_sockets.remove(sock)
                            sock.close()
                            if not client_sockets:
                                exit()
                            found = True

                        elif "done" in data:
                            id2 = int(data.split(" done")[0])
                            done_searcher = searcher_lst.search_by_id(id2)
                            search_zones.remove_zone(done_searcher.area_of_search)
                            zones = search_zones.search_in_lst(done_searcher.num_of_cores)
                            if not zones:
                                print("clients checked every zone!")
                                exit()
                            start = zones[0].area.split(" - ")[0]
                            end = zones[len(zones) - 1].area.split(" - ")[1]
                            s = start + " - " + end
                            done_searcher.area_of_search = s
                            length = str(len(s))
                            message = length.zfill(3) + s
                            messages_to_send.append((sock, message))
                            break

                    except ValueError:
                        print("Value error")
                        client_sockets.remove(sock)
                        sock.close()

                except ConnectionResetError:
                    print("CRE")
                    disconnected_searcher = searcher_lst.search_by_sock(sock)
                    for zone in search_zones.zones_lst:
                        if zone.area == disconnected_searcher.area_of_search:
                            zone.state = -1
                            break
                    searcher_lst.remove(disconnected_searcher)
                    client_sockets.remove(sock)
                    sock.close()

        for message in messages_to_send:
            current_socket, data = message
            for sok in client_sockets:
                if sok == current_socket:
                    print(data[3:])
                    sok.send(data.encode())
        messages_to_send = []


if __name__ == "__main__":
    main()
