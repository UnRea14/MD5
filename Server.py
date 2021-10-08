from hashlib import md5
import socket
import select


def main():
    start_string = input("Enter a string: ")
    md5_s = md5(start_string.encode())
    print("hash - " + md5_s.hexdigest())
    size = len(start_string)
    print("Setting up server...")
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8820))
    server_socket.listen()
    print("Listening...")
    messages_to_send = []
    client_sockets = []
    while True:
        r_list, w_list, e_list = select.select([server_socket] + client_sockets, [], [], 0.01)
        for sock in r_list:
            if sock == server_socket:
                connection, client_address = sock.accept()
                client_sockets.append(connection)
                s = f"Size of string is - {size}"
                length = str(len(s))
                message = length.zfill(3) + s
                messages_to_send.append((connection, message))
            else:
                try:
                    length = sock.recv(3).decode()
                    try:
                        data = sock.recv(int(length))
                        if md5(data).hexdigest() == md5_s.hexdigest():
                            s = "correct"
                            length = str(len(s))
                            message = length.zfill(3) + s
                            messages_to_send.append((sock, message))
                        else:
                            s = "wrong"
                            length = str(len(s))
                            message = length.zfill(3) + s
                            messages_to_send.append((sock, message))

                    except ValueError:
                        client_sockets.remove(sock)
                        sock.close()

                except ConnectionResetError:
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
