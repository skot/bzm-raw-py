import logging

def i2c_send_bytes(ser, id, address, register, data, debug=False):

    # If data is a list, handle each byte separately
    if isinstance(data, list):
        packet_len = len(data) + 8
        # Create packet with all data bytes
        packet = bytes([packet_len & 0xFF, packet_len >> 8, id, 0x00, 0x05, 0x20, address, register] + data)
    else:
        packet_len = 9
        # Handle single byte case
        packet = bytes([packet_len & 0xFF, packet_len >> 8, id, 0x00, 0x05, 0x20, address, register, data])

    if debug:
        print("ctrl tx: [%s]" % prettyHex(packet))

    ser.write(packet)

    # wait for the response
    data = ser.read(4)
    if data:
        bytes_read = len(data)
        if bytes_read > 0:
            if debug:
                print("ctrl rx: [%s]" % prettyHex(data))
            if data[2] != id:
                print("Error: ID mismatch. Expected %02X, got %02X" % (id, data[2]))
                return
        else:
            print("No data received")
            return
    else:
        print("No data received")
    return

def i2c_read_bytes(ser, id, address, register, size, debug=False):
    ser.reset_input_buffer()
    packet = bytes([0x09, 0x00, id, 0x00, 0x05, 0x40, address, register, size])
    ser.write(packet)
    if debug:
        print("ctrl tx: [%s]" % prettyHex(packet))
    data = ser.read(size+3)
    if data:
        bytes_read = len(data)
        if bytes_read > 0:
            if debug:
                print("ctrl rx: [%s]" % prettyHex(data))
            if data[2] != id:
                logging.error("Error: ID mismatch. Expected %02X, got %02X" % (id, data[2]))
                return None
        else:
            logging.error("No data received")
            return None
    else:
        logging.error("No data received")
        return None

    return data[-size:]

def prettyHex(data):
    return ' '.join(f'{byte:02X}' for byte in data)