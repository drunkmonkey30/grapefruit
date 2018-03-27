# client side of bluetooth connection

import threading
import queue
import bluetooth

from bluetooth.message_maker import Message

# TODO lots of common code between client and server, make common code a base class and extend client and server
class BlueClient:
    def __init__(self):
        self.client_socket = None
        self.is_connected = threading.Event()
        self.done = threading.Event()
        self.send_queue = queue.Queue(10)
        self.recv_queue = queue.Queue(10)

        self.comm_thread = None
        self.recv_thread = None

        self.server_uuid = None
        self.client_uuid = None

        self.pong_sent = 0


    def send_message(self, message):
        packets = Message.create_bluetooth_message(Message, message)
        for p in packets:
            self.send_queue.put_nowait(p)


    def stop_client(self):
        self.done.set()


    def start_client(self):
        self.is_connected.clear()
        self.done.clear()

        self.server_uuid, self.client_uuid = bluetooth.provision.read_uuid_file("friends.uuid")
        if self.server_uuid is None or self.client_uuid is None:
            print("*** ERROR: unable to read bluetooth uuids from file")
            exit(1)

        self.recv_thread = threading.Thread(target=self.recv_thread, name="bluetooth-client-recv")
        self.recv_thread.start()
        self.comm_thread = threading.Thread(target=self.send_thread, name="bluetooth-client-send")
        self.comm_thread.start()

        return self.is_connected


    def send_thread(self):
        # loop until we are told to stop
        while not self.done.is_set():
            # connect to master device (game board)
            while not self.is_connected.is_set():
                # search for our master uuid
                matches = bluetooth.find_service(uuid=str(self.server_uuid))
                if len(matches) == 0:
                    print("*** BlueClient: did not find matching service uuid")
                    continue

                # get info of first match
                port = matches[0]["port"]
                host = matches[0]["host"]
                # create bluetooth socket and connect
                self.client_socket = bluetooth.BluetoothSocket(bluetooth.L2CAP)
                self.client_socket.connect((host, port))
                # send our uuid to the server
                self.client_socket.send(self.client_uuid.bytes)
                # check for ok message
                ok = self.client_socket.recv(2)
                if "OK" in ok:
                    self.is_connected.set()

            # we have a good connection, begin sending
            while self.is_connected.is_set() and not self.done.is_set():
                try:
                    message = self.send_queue.get()
                    self.client_socket.send(message)
                except queue.Empty:
                    pass



    def recv_thread(self):
        while not self.done.is_set():
            while self.is_connected.wait():
                data = self.client_socket.recv(Message.L2CAP_MTU)
                packet = Message.receive_packet(Message, data)

                if packet is not None:
                    # check for pong
                    if bluetooth.provision.PING_TO_CLIENT in packet[1]:
                        pong = Message.create_bluetooth_message(Message, bluetooth.provision.PING_TO_SERVER)
                        self.send_queue.put(pong)
                        self.pong_sent += 1
                        print("***BlueClient sent PONG #" + str(self.pong_sent))
                    else:
                        # if we have a full packet (packet not None)
                        if packet is not None:
                            self.recv_queue.put_nowait(packet)


if __name__ == "__main__":
    print("a test for the BlueClient has not yet been written")