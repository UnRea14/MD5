import socket


def create_message(size, s):
    s = str(int(s) + 1)
    s = s.zfill(size)
    return s


def main():
    print("Connecting...")
    sock = socket.socket()
    sock.connect(('127.0.0.1', 8820))
    print("Connected!")
    length = sock.recv(3).decode()
    data = sock.recv(int(length)).decode()
    size = int(data.split("Size of string is - ")[1])
    s = "0" * size
    while data == "wrong" or " - " in data:
        print(data)
        s = create_message(size, s)
        length = str(len(s))
        message = length.zfill(3) + s
        sock.send(message.encode())
        length = sock.recv(3).decode()
        data = sock.recv(int(length)).decode()
    print(data)


if __name__ == "__main__":
    main()
