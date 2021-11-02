from hashlib import md5
import socket
import select


class Searcher:
    def __init__(self, id1, sock, area=""):
        self.id1 = id1
        self.sock = sock
        self.area_of_search = area


def main():
    """
    hash1 = input("Enter hash: ")
    print("hash - " + hash1)
    size = 10
    inc = 100000
    """
    start_string = input("Enter a string: ")
    hash1 = md5(start_string.encode()).hexdigest()
    print("hash - " + hash1)
    size = len(start_string)
    if size < 6:
        inc = pow(10, size - 1)
    else:
        inc = 100000
    print("Setting up server...")
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8820))
    server_socket.listen()
    print("Listening...")
    messages_to_send = []
    client_sockets = []
    id1 = 0
    start = "0"
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
                area = str(start) + " - " + str(int(start) + inc)
                start = int(start) + inc
                length = str(len(area))
                message = length.zfill(3) + area
                messages_to_send.append((connection, message))
                searcher_lst.append(Searcher(id1=id1, sock=connection, area=area))
                id1 += 1

            else:
                try:
                    length = sock.recv(3).decode()
                    try:
                        data = sock.recv(int(length)).decode()
                        print(data)
                        if "found" in data:
                            length = str(len(data))
                            message = length.zfill(3) + data
                            for sok in client_sockets:
                                if sok != sock:
                                    sok.send(message.encode())
                            found = True

                        elif "done" in data:
                            id2 = int(data.split(" done")[0])
                            area = str(start) + " - " + str(int(start) + inc)
                            start = int(start) + inc
                            searcher_lst[id2].area_of_search = area
                            s = searcher_lst[id2].area_of_search
                            length = str(len(s))
                            message = length.zfill(3) + s
                            messages_to_send.append((sock, message))

                    except ValueError:
                        print("value error")
                        client_sockets.remove(sock)
                        sock.close()

                except ConnectionResetError:
                    print("CR error")
                    client_sockets.remove(sock)
                    sock.close()

        if found:
            server_socket.close()
            exit()
        for message in messages_to_send:
            current_socket, data = message
            for sok in client_sockets:
                if sok == current_socket:
                    print(data[3:])
                    sok.send(data.encode())
        messages_to_send = []


if __name__ == "__main__":
    main()
