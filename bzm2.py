import bitaxeraw
import time

BZ2_OP_WRITEJOB = 0x00
BZ2_OP_READRESULT = 0x10
BZ2_OP_WRITEREG = 0x20
BZ2_OP_READREG = 0x30
BZ2_OP_MULTIWRITE = 0x40
BZ2_OP_VOLTAGE = 0xC0 #this might be a typo and it's actually BZ2_OP_TSVSREAD?
BZ2_OP_TSVSREAD = 0xD0
BZ2_OP_LOOPBACK = 0xE0
BZ2_OP_NOOP = 0xF0

def BZM_readreg(ser, asic, engine_id, offset, count, debug=False):
    """
    BZM_readreg reads from a register on the BZM
    
    Args:
        ser: Serial port object
        asic: ASIC address (0xFA is the default)
        engine_id: Engine ID (0xFFF is the default)
        offset: Register address
        count: Number of bytes to read
        debug: Enable debug output
    
    Returns:
        List of u16 response values, or None if failed
    """
    buf = []
    
    # ASIC address first, with 9th bit high
    buf.append(0x0100 | asic)
    
    # Data next, with 9th bit low
    buf.append(0x0000 | BZ2_OP_READREG | ((engine_id & 0x0F00) >> 8))  # BZ2_OP_READREG and high 4 bytes of engine_id
    buf.append(0x0000 | (engine_id & 0xFF))  # engineID low byte
    buf.append(0x0000 | offset)  # offset (register address)
    buf.append(count-1)  # byte count
    buf.append(0x0000)  # TAR (turnaround)
    
    if debug:
        print("Send readreg: ", end='')
    
    # Send the command
    bitaxeraw.asic_write(ser, buf, debug)
    
    # Read the response - expecting count+4 bytes back
    response = bitaxeraw.asic_read(ser, count+2, debug=debug)
    
    # if len(response) == 0:
    #     print("BZM_readreg failed - no response")
    #     return None
    
    return response

def BZM_writereg(ser, asic, engine_id, offset, write_data, debug=False):
    """
    BZM_writereg writes to a register on the BZM
    
    Args:
        ser: Serial port object
        asic: ASIC address (0xFA is the default)
        engine_id: Engine ID (0xFFF is the default)
        offset: Register address
        write_data: List of u8 data bytes to write
        count: Number of bytes to write
        debug: Enable debug output
    
    Returns:
        True if successful, False otherwise
    """
    buf = []

    count = len(write_data)
    
    # ASIC address first, with 9th bit high
    buf.append(0x0100 | asic)
    
    # Data next, with 9th bit low
    buf.append(0x0000 | BZ2_OP_WRITEREG | ((engine_id & 0x0F00) >> 8))  # BZ2_OP_WRITEREG and high 4 bytes of engine_id
    buf.append(0x0000 | (engine_id & 0xFF))  # engineID low byte
    buf.append(0x0000 | offset)  # offset (register address)
    buf.append(count - 1)  # byte count (N-1, where N is the number of data bytes)
    
    # Copy write_data to buf (convert u8 to u16 with 9th bit low)
    for i in range(count):
        buf.append(0x0000 | write_data[i])
    
    # Set the terminating character at the end
    buf.append(0x0000)
    
    if debug:
        print("Send writereg: ", end='')
    
    # Send the write data
    bitaxeraw.asic_write(ser, buf, debug=True)
    
    return True

def BZM_sendnoop(ser, asic=0xFA, debug=False):
    asic = 0x100 | asic
    bitaxeraw.asic_write(ser, [asic, 0x0F0], debug=debug)
    bitaxeraw.asic_read(ser, 5, debug=debug)
    time.sleep(0.1)

def BZM_loopback(ser, asic, data, debug=False):
    """
    BZM_loopback sends data to the BZM and receives it back (loopback test)
    
    Args:
        ser: Serial port object
        asic: ASIC address (0xFA is the default)
        data: List of u8 data bytes to send
        debug: Enable debug output
    
    Returns:
        List of u16 response values, or None if failed
    """
    buf = []
    count = len(data)
    
    # ASIC address first, with 9th bit high
    buf.append(0x0100 | asic)
    
    # Data next, with 9th bit low
    buf.append(0x0000 | BZ2_OP_LOOPBACK)  # BZ2_OP_LOOPBACK
    buf.append(count)  # byte count
    buf.append(0x0000)  # TAR (turnaround)
    
    # Copy data to buf (convert u8 to u16 with 9th bit low)
    for i in range(count):
        buf.append(0x0000 | data[i])
    
    if debug:
        print("Send Loopback: ", end='')
    
    # Send the command
    bitaxeraw.asic_write(ser, buf, debug)
    
    # Read the response - expecting all sent bytes back (count + 3 header bytes)
    response = bitaxeraw.asic_read(ser, count + 3, debug=debug)
    
    # if len(response) == 0:
    #     print("BZM_loopback failed - no response")
    #     return None
    
    return response
