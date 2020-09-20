import socket
import tqdm
import os


server_host = "0.0.0.0"
server_port = 8800
buffer_size = 4096
separator = "<SEPARATOR>"

# path to the data directory
data_directory = "received data"


def get_internal_filename(ext_name):
    return os.path.join(data_directory, ext_name)


def resolve_name_collisions(ext_filename):
    int_filename = get_internal_filename(ext_filename)
    if int_filename in fileset:

        # if file with such name already exists,
        # rename it to <filename>_copy<number>.<extension>
        filename_split = os.path.splitext(ext_filename)
        name = filename_split[0]  # extracting the name
        ext = filename_split[1]   # extracting extension
        i = 1
        ext_filename = f"{name}_copy{i}{ext}"
        temp_int_filename = get_internal_filename(ext_filename)

        # if the file with a new name already exists,
        # cycle through the names until we find the one that doesn't exist yet
        lookup = temp_int_filename in fileset
        while lookup:
            i += 1
            ext_filename = f"{name}_copy{i}{ext}"
            temp_int_filename = get_internal_filename(ext_filename)
            lookup = temp_int_filename in fileset

        # if the new name has been found,
        # create an entry for it in the set
        if temp_int_filename not in fileset:
            fileset.add(temp_int_filename)

        # send the warning message to the client
        client_socket.send(f"File with a given name already exists on the server!"
                           f" A name {ext_filename} has been given to it instead.".encode())

        # changing the internal name to be returned
        int_filename = temp_int_filename
    else:
        # if file does not exist
        # create an entry for it in the map
        fileset.add(int_filename)

        # ... and send the success message to the client
        client_socket.send("OK".encode())

    # returning the generated names
    return ext_filename, int_filename


# a set that contains all the filenames in the data directory
fileset = set()

# creating the data directory if it does not exist
if not os.path.exists(data_directory):
    os.makedirs(data_directory)

# populating the file counter with the contents of the data directory
for file in os.listdir(data_directory):
    fileset.add(os.path.join(data_directory, file))

# create the server socket
s = socket.socket()

# bind the socket to our local address
s.bind((server_host, server_port))

print(f"[*] Listening as {server_host}:{server_port}")

while True:
    s.listen(5)
    client_socket, address = s.accept()
    print(f"[+] {address} is connected.")

    received = client_socket.recv(buffer_size).decode()
    filename, filesize = received.split(separator)

    filename = os.path.basename(filename)

    external_filename, internal_filename = resolve_name_collisions(filename)

    filesize = int(filesize)
    progress = tqdm.tqdm(range(filesize), f"Receiving {external_filename}", unit="B", unit_scale=True,
                         unit_divisor=1024)
    with open(internal_filename, "wb") as f:
        for _ in progress:
            bytes_read = client_socket.recv(buffer_size)
            if not bytes_read:
                break
            f.write(bytes_read)
            progress.update(len(bytes_read))

    client_socket.close()
