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

        self.done = threading.Event
        self.done.clear()

        self.send_queue = None
        self.recv_queue = None

        self.uuid, self.client_uuid = provision.read_uuid_file("friends.uuid")
        if self.uuid is None or self.client_uuid is None:
            print("*** ERROR: unable to read bluetooth uuids from file")
            exit(1)


    # spawns a new thread that waits to connect to the client device
    # ie our dual screen child device
    #
    # returns a threading.Event that will be set when we have established a good
    # connection with the intended child device and can begin sending data
    def connect_to_client(self):
        # create event object that our threads will use
        # we will also use it for internal state
        self.is_connected = threading.Event
        # set flag to false (not connected to correct client)
        self.is_connected.clear()

        self.send_queue = queue.Queue(10)
        self.recv_queue = queue.Queue(10)

        self.recv_thread = threading.Thread(target=self.recv_func, name="bluetooth-server-recv")
        self.comm_thread = threading.Thread(target=self.start_comms, name="bluetooth-server-comms")
        self.comm_thread.start()

        return self.is_connected


    def start_comms(self):
        self.socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.socket.bind(("", 0xBEEF))
        self.socket.listen(1)
        bluetooth.advertise_service(self.socket, "grapefruit-server", str(self.uuid))

        # this should loop until we should stop all bluetooth communications
        # for instance, if we need to shutdown the game
        while not self.done.is_set():

            # perform this until we get a valid connection with our intended client
            while not self.is_connected.is_set():
                self.client_sock, address = self.socket.accept()
                print("Bluetooth: connection from: " + str(address))

                # we got a connection, now verify the client
                # client should send their uuid first, and we check that it matches what was in
                # our friends.uuid file from the provisioning script
                c_uuid = self.client_sock.recv(1024).strip()
                c_uuid = uuid.UUID(bytes=c_uuid)

                # check that our only allowed uuid matches
                if c_uuid == self.client_uuid:
                    self.is_connected.set()
                    bluetooth.stop_advertising(self.socket)
                else:
                    print("BlueServer: bad uuid attempted connection: " + str(c_uuid))
                    self.client_sock.close()

            # the following loop is the communications part of the server
            # it sends messages added to a queue via the interface of BlueServer
            # it will also periodically ping the child to make sure our connection is good
            #
            # this should loop for:
            #   as long as we have a connection OR
            #   application requests that we die
            missed_pings = 0
            while self.is_connected.is_set() and not self.done.is_set():
                message = None
                try:
                    message = self.send_queue.get_nowait()
                    self.socket.send(message)
                except queue.Empty:
                    # no message is available for sending, ping the child instead
                    self.socket.send(provision.PING_TO_CLIENT)
                    response = self.socket.recv(1024).strip()

                    if provision.PING_TO_SERVER in response:
                        missed_pings = 0
                    else:
                        missed_pings += 1

                    if missed_pings > 5:
                        print("*** ERROR: BlueServer: client missed > 5 pings")
                        # clear the connected flag and try to reconnect
                        self.is_connected.clear()

        # TODO should probably do a clean up to get any data that should be commited to database before killing connection

        # all done with our bluetooth connection, shut everything down
        self.client_sock.close()
        self.socket.close()

    # listens for incoming messages from the bluetooth socker
    def recv_func(self):
        while self.is_connected.wait() and not self.done.is_set():
            pass


if __name__ == "__main__":
    print("a test has not yet been written for the BlueServer")