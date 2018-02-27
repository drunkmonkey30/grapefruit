# server side of bluetooth communications
# to be run on the game board

import threading
from provision import *

try:
    import bluetooth
except:
    print("*** ERROR:bluetooth: failed to import bluetooth library, exiting")
    exit(1)


class BlueServer:
    def __init__(self):
        self.uuid, self.client_uuid = provision.read_uuid_file("friends.uuid")
        if self.uuid == None or self.client_uuid == None:
            print("*** ERROR: unable to read bluetooth uuids from file")
            exit(1)


    # spawns a new thread that waits to connect to the client device
    # ie our dual screen child device
    def connect_to_client(self):
        # create event object that our threads will use
        # we will also use it for internal state
        self.is_connected = threading.Event
        # set flag to false (not connected to correct client)
        self.is_connected.clear()

        self.connect_thread = threading.Thread(target=self.do_connect, name="bluetooth-server-connect")
        self.handshake_thread = threading.Thread(target=self.do_handshake, name="bluetooth-server-handshake")

    def do_connect(self):
        self.socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.socket.bind(("", 40001))
        self.socket.listen(1)
        bluetooth.advertise_service(self.socket, "grapefruit-server", str(self.uuid))

        while True:
            client_sock, address = self.socket.accept()
            print("Bluetooth: connection from: " + str(address))
            # we got a connection, now verify the client
            # client should send their uuid first, and we check that it matches what was in
            # out friends.uuid file from the provisioning script
            uuid = client_sock.recv

    def do_handshake(self):
        self.is_connected.wait()

if __name__ == "__main__":
    pass