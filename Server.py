from hashlib import md5
import socket
import select


def main():
    start_string = input("Enter a string: ")
    hash1 = md5(start_string.encode()).hexdigest()
    print("hash - " + hash1)
    size = len(start_string)
    if size < 5:
        end = pow(10, size - 1)
    else:
        end = 1000
    print("Setting up server...")
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8820))
    server_socket.listen()
    print("Listening...")
    messages_to_send = []
    client_sockets = []
    start = 0
    done = 1
    while True:
        r_list, w_list, e_list = select.select([server_socket] + client_sockets, [], [], 0.01)
        for sock in r_list:
            if sock == server_socket:
                connection, client_address = sock.accept()
                client_sockets.append(connection)
                s = f"{hash1}|{size}"
                length = str(len(s))
                message = length.zfill(3) + s
                messages_to_send.append((connection, message))
                s = "-1 - " + str(end)
                length = str(len(s))
                message = length.zfill(3) + s
                messages_to_send.append((connection, message))
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
                                sok.close()
                                exit()

                        elif "done" in data:
                            done += 1
                            start = data.split(" done")[0]
                            s = str(start) + " - " + str(end * done)
                            length = str(len(s))
                            message = length.zfill(3) + s
                            messages_to_send.append((sock, message))

                    except ValueError:
                        print("value error")
                        client_sockets.remove(sock)
                        sock.close()

                except ConnectionResetError:
                    print("CRE error")
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
