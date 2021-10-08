from hashlib import md5
import socket
import select


def main():
    start_string = input("Enter a string: ")
    md5_s = md5(start_string.encode())
    print("hash - " + md5_s.hexdigest())
    size = len(start_string)
    server_socket = socket.socket()
    server_socket.bind(('0.0.0.0', 8820))
    server_socket.listen()
    messages_to_send = []
    client_sockets = []
    data = ""
    while True:
        r_list, w_list, e_list = select.select([server_socket] + client_sockets, [], [], 0.01)
        for sock in r_list:
            if sock == server_socket:
                connection, client_address = sock.accept()
                client_sockets.append(connection)
                s = f"Size of string is + {size}"
                length = str(len(s))
                message = length.zfill(3) + s
                print(message)
                messages_to_send.append((sock, message))

            else:
                try:
                    length = sock.recv(2).decode()
                    try:
                        data = sock.recv(int(length)).decode()
                        
                    except ValueError:
                        client_sockets.remove(sock)
                        sock.close()
                    data = sock.recv(length).decode()
                    if md5(data).hexdigest() == md5_s.hexdigest():
                        s = "correct"
                        length = str(len(s))
                        message = length.zfill(3) + s
                        messages_to_send.append((sock, message))

                except ConnectionResetError:
                    client_sockets.remove(sock)
                    sock.close()

            for message in messages_to_send:
                current_socket, data = message
                for sok in client_sockets:
                    if sok == current_socket:
                        sok.send(data.encode())
            messages_to_send = []

        solve = "0" * size
        while True:
            if md5_s.hexdigest() == md5(solve.encode()).hexdigest():
                print(solve + " is the string!")
                break
            solve = str(int(solve) + 1)
            solve = solve.zfill(size)


if __name__ == "__main__":
    main()
