from hashlib import md5

s = input("Enter a string: ")
md5_s = md5(s.encode())
print("hash - " + md5_s.hexdigest())
size = len(s)
solve = "0" * size
while True:
    if md5_s.hexdigest() == md5(solve.encode()).hexdigest():
        print(solve + " is the string!")
        break
    solve = str(int(solve) + 1)
    solve = solve.zfill(size)
