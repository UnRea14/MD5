import socket
import threading
from hashlib import md5
import select


def main():
    print("Connecting...")
    sock = socket.socket()
    sock.connect(('127.0.0.1', 8820))
    print("Connected!")
    data = ""
    size = 0
    hash1 = ""
    end = 0
    s = ""
    start = 0
    while "correct" not in data:
        r_list, w_list, e_list = select.select([sock], [sock], [])
        for sok in r_list:
            length = sok.recv(3).decode()
            try:
                data = sok.recv(int(length)).decode()
                print(data)
                if "|" in data:
                    hash1 = data.split("|")[0]
                    size = int(data.split("|")[1])
                else:
                    if " - " in data:
                        start = int(data.split(" - ")[0])
                        end = int(data.split(" - ")[1])
                        if len(s) < size:
                            s = str(start).zfill(size)
                        else:
                            s = str(start)
                    while start < end:
                        print(s)
                        start += 1
                        s = str(start)
                        s = s.zfill(3)
                        if md5(s.encode()).hexdigest() == hash1:
                            message = "found - " + s
                            print(message)
                            length = str(len(message))
                            sok.send((length.zfill(3) + message).encode())
                            exit()
                    message = str(start) + " done"
                    length = str(len(message))
                    sok.send((length.zfill(3) + message).encode())
            except ValueError:
                print("error - ValueError")
                quit()
    print(data)


if __name__ == "__main__":
    main()
