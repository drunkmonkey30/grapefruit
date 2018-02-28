# creates uuids for both client and server, and writes them to a file
# that will be stored on both client and server devices. this is to prevent
# the devices from connecting to anything else
# for now, these create random uuids via the uuid4 function (see python 3.6 documentation)

import uuid

PING_TO_CLIENT = "Ping?"
PING_TO_SERVER = "Pong!"

def create_client_uuid():
    return uuid.uuid4()


def create_server_uuid():
    return uuid.uuid4()


def write_uuid_file(filename, server, client):
    with open(filename, 'wb') as file:
        file.write(server.bytes)
        file.write(client.bytes)


def read_uuid_file(filename):
    server = None
    client = None
    try:
        with open(filename, 'rb') as file:
            server = uuid.UUID(bytes = file.read(16))
            client = uuid.UUID(bytes = file.read(16))
    except:
        print("*** ERROR:read_uuid_file:" + filename + ": error reading uuid file")

    return server, client



if __name__ == "__main__":
    print("testing uuid system")
    server = create_server_uuid()
    client = create_client_uuid()

    print("these uuids were written to friends.uuid")
    print("server:" + str(server.hex))
    print("client:" + str(client.hex))
    write_uuid_file("friends.uuid", server, client)

    server = None
    client = None

    print("\nthese uuids were read from the uuid file")
    server, client = read_uuid_file("friends.uuid")
    print("server:" + str(server.hex))
    print("client:" + str(client.hex))