# server side of bluetooth communications
# to be run on the game board

import threading
import uuid
import time
import queue
from provision import *

try:
    import bluetooth
except:
    print("*** ERROR:bluetooth: failed to import bluetooth library, exiting")
    exit(1)


class BlueServer:
    def __init__(self):
        self.socket = None
        self.client_sock = None
        self.is_connected = None
        self.comm_thread = None

        self.consecutive_pings_sent = 0
        self.consecutive_pings_recv = 0

        self.done = threading.Event
        self.done.clear()

        self.send_queue = queue.Queue(10)
        self.recv_queue = queue.Queue(10)

        self.uuid, self.client_uuid = provision.read_uuid_file("friends.uuid")
        if self.uuid is None or self.client_uuid is None:
            print("*** ERROR: unable to read bluetooth uuids from file")
            exit(1)


    # stop the bluetooth server
    def stop_bluetooth(self):
        self.done.set()

    # spawns a new thread that waits to connect to the client device
    # ie our dual screen child device
    #
    # returns a threading.Event that will be set when we have established a good
    # connection with the intended child device and can begin sending data
    def start_bluetooth(self):
        # create event object that our threads will use
        # we will also use it for internal state
        self.is_connected = threading.Event
        # set flag to false (not connected to correct client)
        self.is_connected.clear()

        # start receiver thread
        self.recv_thread = threading.Thread(target=self.recv_func, name="bluetooth-server-recv")
        self.recv_thread.start()
        # start connector and sender thread
        self.comm_thread = threading.Thread(target=self.start_comms, name="bluetooth-server-comms")
        self.comm_thread.start()

        return self.is_connected


    def start_comms(self):
        self.socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.socket.bind(("", 0xBEEF))
        self.socket.listen(1)

        # this should loop until we should stop all bluetooth communications
        # for instance, if we need to shutdown the game
        while not self.done.is_set():
            bluetooth.advertise_service(self.socket, "grapefruit-server", str(self.uuid))

            # perform this until we get a valid connection with our intended client
            while not self.is_connected.is_set():
                self.client_sock, address = self.socket.accept()
                print("Bluetooth: connection from: " + str(address))

                # we got a connection, now verify the client
                # client should send their uuid first, and we check that it matches what was in
                # our friends.uuid file from the provisioning script
                c_uuid = self.client_sock.recv(1024)
                print("DEBUG: BlueServer received:",c_uuid)
                c_uuid = uuid.UUID(bytes=c_uuid[0:16])
                print("DEBUG: BlueServer client UUID: " + str(c_uuid))

                # check that our only allowed uuid matches
                if c_uuid == self.client_uuid:
                    bluetooth.stop_advertising(self.socket)
                    self.is_connected.set()
                else:
                    print("BlueServer: bad uuid attempted connection: " + str(c_uuid))
                    self.client_sock.close()


            # set mtu of l2cap socket to larger than 672 bytes
            bluetooth.set_l2cap_mtu(self.socket, 10000)
            bluetooth.set_l2cap_mtu(self.client_sock, 10000)


            # the following loop is the communications part of the server
            # it sends messages added to a queue via the interface of BlueServer
            # it will also periodically ping the child to make sure our connection is good
            #
            # this should loop for:
            #   as long as we have a connection OR
            #   application requests that we die
            while self.is_connected.is_set() and not self.done.is_set():
                message = None
                try:
                    message = self.send_queue.get(True, 10.0)
                    self.socket.send(message)
                    self.consecutive_pings_sent = 0

                except queue.Empty:
                    # no message is available for sending, ping the child instead
                    self.socket.send(provision.PING_TO_CLIENT)
                    self.consecutive_pings_sent += 1


        # TODO should probably do a clean up to get any data that should be commited to database before killing connection

        # all done with our bluetooth connection, shut everything down
        self.client_sock.close()
        self.socket.close()

    # listens for incoming messages from the bluetooth socket
    def recv_func(self):
        while not self.done.is_set():
            while self.is_connected.wait():
                data = self.client_sock.recv(1024)
                self.recv_queue.put(data)



if __name__ == "__main__":
    print("a test has not yet been written for the BlueServer")