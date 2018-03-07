# creates and interprets messages intended to be sent over bluetooth connection
# messages are of the following format:

#   packet number   - 2 bytes (unsigned short)  - used to match responses and requests
#
#   fragmented?     - 1 bytes (unsigned byte)   - used to indicate if the packet has been split into multiple messages,
#                                               - if the packet has been fragmented, this is the total number of fragments
#                                               - we will be expecting
#
#   fragment number - 1 bytes (unsigned byte)   - fragment number for this packet, ignored if not fragmented
#
#   length          - 2 bytes (unsigned short)  - length of payload, not including headers.
#
#   type            - 1 bytes (unsigned byte)   - 1=string, 2=list, 3=dict
#
#   ascii data      - variable length


import struct
import threading
import queue

class Message:
    L2CAP_MTU = 672 # this should be the default value for the bluetooth protocol
    ENCODING = 'utf-8'
    # format string does not include the payload data
    # payload should be tacked on as bytes
    header_maker = struct.Struct("!HBBHB")
    MAX_PACKET_SIZE = L2CAP_MTU - header_maker.size
    packet_number = 0
    packet_lock = threading.Lock()

    def __init__(self):
        self.receive_dict = {}


    # returns a list of packets for sending on bluetooth channel
    # the data argument should be one of three types
    #   1. a string, or str of plain text data
    #   TODO 2. a list of strings
    #   TODO 3. a dictionary of key value pairs, all of which are strings
    def create_bluetooth_message(self, data_string):
        payload_length = len(data_string)
        # determine if packet will be fragmented and set number of fragments
        fragmented = payload_length // Message.MAX_PACKET_SIZE

        packets = []
        # lock so we don't increment the packet number from another thread while making this packet
        Message.packet_lock.acquire()
        Message.packet_number += 1
        for p in range(fragmented):
            # make header for the packet
            header = Message.header_maker.pack(Message.packet_number, fragmented, p, Message.MAX_PACKET_SIZE, 0x01)
            packet = header + bytes(data_string[p*Message.MAX_PACKET_SIZE:(p+1)*Message.MAX_PACKET_SIZE], Message.ENCODING)
            packets.append(packet)
            payload_length = payload_length - Message.MAX_PACKET_SIZE

        # do last packet
        header = Message.header_maker.pack(Message.packet_number, fragmented, fragmented, payload_length, 0x01)
        Message.packet_lock.release()
        packet = header + bytes(data_string[fragmented*Message.MAX_PACKET_SIZE:], Message.ENCODING)
        packets.append(packet)

        return packets


    def print_header(self, header):
        print("Packet Number . ." + str(header[0]))
        print("Fragments . . . ." + str(header[1]))
        print("Fragment Number ." + str(header[2]))
        print("Payload Length  ." + str(header[3]))
        print("Type . . . . .  ." + str(header[4]))


    # returns a tuple with (header, data)
    # data will be represented as a string
    # header as a tuple with elements defined at the top of this file
    def receive_packet(self, packet):
        # read header from packet
        header = self.header_maker.unpack(packet[0:self.header_maker.size])
        # read data from packet
        data = packet[self.header_maker.size:header[3]].decode()

        # TODO left off here
        self.receive_dict

    def decode_bluetooth_message(self, message_as_bytes):
        pass


if __name__ == "__main__":
    m = Message()

    print("testing creation")
    packets = m.create_bluetooth_message("this is a test message")
    print(packets)

    print("\ntesting decode...")
    for p in packets:
        m.receive_packet(p)

    print('\n')

    s = "t" * 994
    packets = m.create_bluetooth_message(s)
    for p in packets:
        print(p)

    print("\ndecode...")
    for p in packets:
        m.receive_packet(p)

    print("\n")

    s = "test " * 500
    packets = m.create_bluetooth_message(s)
    for p in packets:
        print(p)

    print("\ndecode...")
    for p in packets:
        m.receive_packet(p)
