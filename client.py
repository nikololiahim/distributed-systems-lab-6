import socket
import tqdm
import os
import sys

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 4096
host = sys.argv[2]
port = int(sys.argv[3])
filename = sys.argv[1]


filesize = os.path.getsize(filename)


s = socket.socket()

print(f"[+] Connecting to {host}:{port}")
s.connect((host, port))
print("[+] Connected.")

# send the filename and filesize
s.send(f"{filename}{SEPARATOR}{filesize}".encode())

# receiving the file validation message
# if file with such name already exists on the server,
# client will receive the respective message
# otherwise, the message will be "OK".
msg = s.recv(BUFFER_SIZE).decode()
print(msg)

# initializing the progress bar
progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
with open(filename, "rb") as f:
    for _ in progress:
        bytes_read = f.read(BUFFER_SIZE)
        if not bytes_read:
            break
        s.sendall(bytes_read)

        # update the progress bar
        progress.update(len(bytes_read))

s.close()