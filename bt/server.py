# server side of bluetooth communications
# to be run on the game board

import threading
import uuid
import queue
import bluetooth
from provision import *
from message_maker import *

try:
    import bluetooth
except:
    print("*** ERROR:bluetooth: failed to import bluetooth library, exiting")
    exit(1)

# TODO lots of common code between client and server, make common code a base class and extend client and server
class BlueServer:
    def __init__(self):
        self.server_socket = None
        self.client_socket = None
        self.is_connected = None
        self.comm_thread = None
        self.recv_thread = None

        self.pings_sent = 0
        self.pongs_recv = 0

        self.done = threading.Event()
        self.done.clear()

        self.send_queue = queue.Queue(10)
        self.recv_queue = queue.Queue(10)

        self.server_uuid, self.client_uuid = read_uuid_file("friends.uuid")
        if self.server_uuid is None or self.client_uuid is None:
            print("*** ERROR: unable to read bluetooth uuids from file")
            exit(1)

        print("***BlueServer: server uuid: " + str(self.server_uuid))
        print("***BlueServer: client uuid: " + str(self.client_uuid))


    # send a message via the blueserver to client device
    # this will take a raw message and packet-ize it
    def send_message(self, message):
        packets = Message.create_bluetooth_message(Message, message)
        for p in packets:
            self.send_queue.put_nowait(p)


    # stop the bluetooth server
    def stop_server(self):
        self.done.set()


    # spawns a new thread that waits to connect to the client device
    # ie our dual screen child device
    #
    # returns a threading.Event that will be set when we have established a good
    # connection with the intended child device and can begin sending data
    def start_server(self):
        # create event object that our threads will use
        # we will also use it for internal state
        self.is_connected = threading.Event()
        # set flag to false (not connected to correct client)
        self.is_connected.clear()

        # start receiver thread
        self.recv_thread = threading.Thread(target=self.recv_func, name="bluetooth-server-recv")
        self.recv_thread.start()
        # start connector and sender thread
        self.comm_thread = threading.Thread(target=self.start_send_thread, name="bluetooth-server-send")
        self.comm_thread.start()

        return self.is_connected


    def start_send_thread(self):
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
        self.server_socket.bind(("", 0xBEEF))
        self.server_socket.listen(1)


        bluetooth.advertise_service(self.server_socket, "grapefruit-server", str(self.server_uuid))
        
        # this should loop until we should stop all bluetooth communications
        # for instance, if we need to shutdown the game
        while not self.done.is_set():
            print("start of connection loop")

            # perform this until we get a valid connection with our intended client
            while not self.is_connected.is_set():
                self.client_socket, address = self.server_socket.accept()
                print("Bluetooth: connection from: " + str(address))

                # we got a connection, now verify the client
                # client should send their uuid first, and we check that it matches what was in
                # our friends.uuid file from the provisioning script

                # uuid is 16 bytes, so only receive that many
                c_uuid = self.client_socket.recv(16)
                #print("DEBUG: BlueServer received:",c_uuid)
                c_uuid = uuid.UUID(bytes=c_uuid[0:16])
                print("DEBUG: BlueServer client UUID: " + str(c_uuid))

                # check that our only allowed uuid matches
                if c_uuid == self.client_uuid:
                    self.client_socket.send("OK")
                    #bluetooth.stop_advertising(self.server_socket)
                    self.is_connected.set()
                else:
                    print("BlueServer: bad uuid attempted connection: " + str(c_uuid))
                    self.client_socket.close()


            # set mtu of l2cap socket to larger than 672 bytes
            # update 3/26/18 Message.L2CAP_MTU is set to 672, so no change from default value
            bluetooth.set_l2cap_mtu(self.server_socket, Message.L2CAP_MTU)
            #bluetooth.set_l2cap_mtu(self.client_socket, Message.L2CAP_MTU)


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
                    self.client_socket.send(message)

                except queue.Empty:
                    # no message is available for sending, ping the child instead
                    #ping = Message.create_bluetooth_message(Message, PING_TO_CLIENT)
                    #self.server_socket.send(ping)
                    self.send_message(PING_TO_CLIENT)
                    self.pings_sent += 1

                    print("***BlueServer: sent ping #: " + str(self.pings_sent))

                except bluetooth.btcommon.BluetoothError:
                    self.is_connected.clear()


        # TODO should probably do a clean up to get any data that should be commited to database before killing connection

        # all done with our bluetooth connection, shut everything down
        self.client_socket.close()
        self.server_socket.close()

    # listens for incoming messages from the bluetooth socket
    def recv_func(self):
        # loop until done is set
        while not self.done.is_set():
            # wait() will wait until the event is set, then will always return True immediately
            # UNLESS we lose connection, so that it will continue waiting
            while self.is_connected.wait():
                print("receive thread: waiting for data")
                try:
                    # read data from client socket
                    data = self.client_socket.recv(Message.L2CAP_MTU)
                    # pass if off to message packet receiver
                    packet = Message.receive_packet(Message, data)
                except:
                    self.is_connected.clear()
                    continue

                if packet is not None:
                    # check for pong
                    if packet[1] == PING_TO_SERVER:
                        self.pongs_recv += 1
                        print("BlueServer: got pong #: " + str(self.pongs_recv))
                    else:
                        # if we have a full packet (packet not None)
                        if packet is not None:
                            self.recv_queue.put_nowait(packet)



if __name__ == "__main__":
    server = BlueServer()
    server.start_bluetooth()