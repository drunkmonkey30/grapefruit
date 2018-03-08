# creates and interprets messages intended to be sent over bluetooth connection
# messages are of the following format:

#   packet number   - 2 bytes (unsigned short)  - used to match responses and requests
#
#   total fragments - 1 bytes (unsigned byte)   - used to indicate if the packet has been split into multiple messages,
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
    # defines for packet header fields
    PACKET_NUMBER   = 0
    TOTAL_FRAGMENTS = 1
    FRAGMENT_NUMBER = 2
    PAYLOAD_LENGTH  = 3
    TYPE            = 4

    L2CAP_MTU = 672 # this should be the default value for the bluetooth protocol
    ENCODING = 'utf-8'

    # format string does not include the payload data
    # payload should be tacked on as bytes
    header_maker = struct.Struct("!HBBHB")
    # maximum size for each bluetooth payload
    MAX_PACKET_SIZE = L2CAP_MTU - header_maker.size
    packet_number = 0
    packet_lock = threading.Lock()
    receive_dict = {}

    def __init__(self):
        pass


    # returns a list of packets for sending on bluetooth channel
    # the data argument should be one of three types
    #   1. a string, or str of plain text data
    #   TODO 2. a list of strings
    #   TODO 3. a dictionary of key value pairs, all of which are strings
    def create_bluetooth_message(self, data_string):

        encoded_payload = bytes(data_string, Message.ENCODING)
        payload_length = len(encoded_payload)

        # determine if packet will be fragmented and set number of fragments
        fragmented = payload_length // Message.MAX_PACKET_SIZE

        packets = []
        # lock so we don't increment the packet number from another thread while making this packet
        Message.packet_lock.acquire()
        Message.packet_number += 1
        for p in range(fragmented):
            # make header for the packet
            header = Message.header_maker.pack(Message.packet_number, fragmented, p, Message.MAX_PACKET_SIZE, 0x01)
            packet = header + encoded_payload[p*Message.MAX_PACKET_SIZE:(p+1)*Message.MAX_PACKET_SIZE] #bytes(data_string[p*Message.MAX_PACKET_SIZE:(p+1)*Message.MAX_PACKET_SIZE], Message.ENCODING)
            packets.append(packet)
            payload_length = payload_length - Message.MAX_PACKET_SIZE

        # do last packet
        header = Message.header_maker.pack(Message.packet_number, fragmented, fragmented, payload_length, 0x01)
        Message.packet_lock.release()
        # bytes(data_string[fragmented*Message.MAX_PACKET_SIZE:], Message.ENCODING)
        packet = header + encoded_payload[fragmented*Message.MAX_PACKET_SIZE:]
        packets.append(packet)

        return packets


    def print_header(self, header):
        print("Packet Number . ." + str(header[0]))
        print("Fragments . . . ." + str(header[1]))
        print("Fragment Number ." + str(header[2]))
        print("Payload Length  ." + str(header[3]))
        print("Type . . . . .  ." + str(header[4]))


    # returns a tuple with (header, data) or None if no packet is complete
    # data will be represented as a string
    # header as a tuple with elements defined at the top of this file
    def receive_packet(self, packet):
        # read header from packet
        header = Message.header_maker.unpack(packet[0:Message.header_maker.size])
        # read data from packet
        data = packet[Message.header_maker.size:header[Message.PAYLOAD_LENGTH]+Message.header_maker.size].decode()

        # print debug data
        #self.print_header(header)
        #print(data)

        # now that we have the header and payload data,
        # we create an entry in the receive dictionary that consists of:
        #   key = packet number
        #   value = list[ tuple( header, data ) ]

        pn = header[Message.PACKET_NUMBER]

        # first check if the packet number key exists in the dictionary
        # if it does not exist, then create an entry as an empty list
        if pn not in Message.receive_dict:
            Message.receive_dict[pn] = []

        # append (header, data) of packet to its appropriate dictionary entry
        Message.receive_dict[pn].append((header, data))

        # check that we have all fragments of a message
        if len(Message.receive_dict[pn]) - 1 == header[Message.TOTAL_FRAGMENTS]:
            # if we do, then assemble the full message and return it

            # use sorted function to sort list by fragment number AFTER reception of all packets
            fragment_list = Message.receive_dict.pop(pn)
            fragment_list = sorted(fragment_list, key=lambda p: p[0][Message.FRAGMENT_NUMBER])

            payload = ""
            for d in fragment_list:
                payload += d[1]

            # debug
            #print("Received Packet Number: " + str(pn))
            #print("Full payload:\n" + payload)

            # return completed packet
            return (header, payload)

        # no packet is complete, return none
        return None


if __name__ == "__main__":
    m = Message()

    print("testing creation")
    packets = m.create_bluetooth_message("this is a test message")
    print(packets)

    print("\ntesting decode...")
    for p in packets:
        m.receive_packet(p)

    print('\n')

    s = "X 1 2 3 4 5 6 7 *" * 400
    packets = m.create_bluetooth_message(s)

    print("shuffling packet list")
    from random import shuffle
    shuffle(packets)
    for p in packets:
        print(p)

    print("\ndecode...")
    for p in packets:
        m.receive_packet(p)

    print("\n")
