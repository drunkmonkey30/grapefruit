# creates and interprets messages intended to be sent over bluetooth connection
# messages are of the following formate:
#   length          - 2 bytes (unsigned short) - length of payload, not including headers. currently capped at 10,000 bytes
#   packet number   - 2 bytes (unsigned short) - used to match responses and requests
#   type            - 1 bytes (unsigned byte). 1 indicates string, 2 indicates list, 3 indicates dict
#   ascii data      - variable length


import struct



# the data argument should be one of three types
#   1. a string, or str of plain text data
#   TODO 2. a list of strings
#   TODO 3. a dictionary of key value pairs, all of which are strings
def create_bluetooth_message(data_string):
    Message.packet_number += 1
    header = Message.header_maker.pack(len(data_string) + Message.header_maker.size, Message.packet_number, 0x01)
    #header.

def decode_bluetooth_message(message_as_bytes):
    pass


class Message:
    packet_number = 0
    header_maker = struct.Struct("!HHb")
