from hashlib import md5
import threading
import socket
import select


def main():
    print("Connecting...")
    sock = socket.socket()
    sock.connect(('127.0.0.1', 8820))
    print("Connected!")
    size = 0
    hash1 = ""
    s = ""
    id1 = "0"
    threads = []
    while True:
        r_list, w_list, e_list = select.select([sock], [sock], [])
        for sok in r_list:
            try:
                length = sok.recv(3).decode()
                try:
                    data = sok.recv(int(length)).decode()
                    print(data)
                    if data == "found":
                        quit()
                    if "|" in data:  # hash|chars in string|client number
                        hash1 = data.split("|")[0]
                        size = int(data.split("|")[1])
                        id1 = data.split("|")[2]

                    elif " - " in data:  # num - num
                        start = int(data.split(" - ")[0])
                        end = int(data.split(" - ")[1])
                        if len(s) < size:
                            s = str(start).zfill(size)
                        else:
                            s = str(start)
                        while start < end:
                            start += 1
                            s = str(start)
                            s = s.zfill(3)
                            if md5(s.encode()).hexdigest() == hash1:
                                message = "found - " + s
                                print(message)
                                length = str(len(message))
                                sok.send((length.zfill(3) + message).encode())
                                sok.close()
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
