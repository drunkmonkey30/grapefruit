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

class Message:
    L2CAP_MTU = 1000
    ENCODING = 'utf-8'
    # format string does not include the payload data
    # payload should be tacked on as bytes
    header_maker = struct.Struct("!HBBHB")
    MAX_PACKET_SIZE = L2CAP_MTU - header_maker.size
    packet_number = 0
    packet_lock = threading.Lock()

    def __init__(self):
        pass

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


    def decode_bluetooth_message(self, message_as_bytes):
        pass


if __name__ == "__main__":
    m = Message()

    packets = m.create_bluetooth_message("this is a test message")
    print(packets)

    print('\n')

    s = "t" * 994
    packets = m.create_bluetooth_message(s)
    for p in packets:
        print(p)

    print("\n")

    s = "test " * 500
    packets = m.create_bluetooth_message(s)
    for p in packets:
        print(p)