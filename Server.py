from hashlib import md5
import socket
import select
import math


class Searcher:
    def __init__(self, id1, sock, area=""):
        self.id1 = id1
        self.sock = sock
        self.area_of_search = area


class Zone:
    def __init__(self, area):
        self.area = area
        self.state = -1  # -1 = not worked on, 0 = worked on, 1 = finished


class Search_Zones:
    def __init__(self, size_of_string):
        self.zones_lst = []
        num = 10**size_of_string
        zone_count = int(math.sqrt(num))
        i = 0
        start = "0"
        while i < zone_count:
            end = str(int(start) + zone_count)
            self.zones_lst.append(Zone(start + " - " + end))
            start = end
            i += 1

    def search_in_lst(self):
        for zone in self.zones_lst:
            if zone.state == -1:
                return zone

    def remove_zone(self, area):
        for zone in self.zones_lst:
            if zone.area == area:
                self.zones_lst.remove(zone)
                return

    def str(self):
        s = "["
        for zone in self.zones_lst:
            s += ",area=" + zone.area + " and " + "state=" + str(zone.state)
        s += "]"
        return s


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
    search_zones = Search_Zones(size_of_string=size)
    print(search_zones.str())
    print("Setting up server...")
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8820))
    server_socket.listen()
    print("Listening...")
    messages_to_send = []
    client_sockets = []
    id1 = 0
    searcher_lst = []
    found = False
    while True:
        r_list, w_list, e_list = select.select([server_socket] + client_sockets, [], [], 0.01)
        for sock in r_list:
            if sock == server_socket:
                connection, client_address = sock.accept()
                client_sockets.append(connection)
                s = f"{hash1}|{size}|{id1}"
                length = str(len(s))
                message = length.zfill(3) + s
                messages_to_send.append((connection, message))
                zone = search_zones.search_in_lst()
                zone.state = 0
                searcher_lst.append(Searcher(id1=id1, sock=connection, area=zone.area))
                s = zone.area
                length = str(len(s))
                message = length.zfill(3) + s
                messages_to_send.append((connection, message))
                id1 += 1

            else:
                try:
                    length = sock.recv(3).decode()
                    if length == "":  # sock disconnected
                        for searcher in searcher_lst:
                            if searcher.sock == sock:
                                for zone in search_zones.zones_lst:
                                    if zone.area == searcher.area_of_search:
                                        zone.state = -1
                                        break
                                searcher_lst.remove(searcher)
                                break
                        client_sockets.remove(sock)
                        sock.close()
                    try:
                        data = sock.recv(int(length)).decode()
                        print(data)
                        if found and "done" in data:
                            message = "005found"
                            sock.send(message.encode())
                            client_sockets.remove(sock)
                            sock.close()
                            if not client_sockets:
                                server_socket.close()
                                exit()

                        elif "found" in data:
                            client_sockets.remove(sock)
                            sock.close()
                            found = True

                        elif "done" in data:
                            id2 = int(data.split(" done")[0])
                            for searcher in searcher_lst:
                                if searcher.id1 == id2:
                                    search_zones.remove_zone(searcher.area_of_search)
                                    zone = search_zones.search_in_lst()
                                    zone.state = 0
                                    s = zone.area
                                    searcher.area_of_search = s
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
                    for searcher in searcher_lst:
                        if searcher.sock == sock:
                            for zone in search_zones.zones_lst:
                                if zone.area == searcher.area_of_search:
                                    zone.state = -1
                                    break
                            searcher_lst.remove(searcher)
                            break
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
