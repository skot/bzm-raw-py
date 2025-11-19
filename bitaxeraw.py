import serial
import time

PAGE_I2C = 0x05
PAGE_GPIO = 0x06
PAGE_ADC = 0x07
PAGE_FAN = 0x09

GPIO_HIGH = 0x01
GPIO_LOW = 0x00

GPIO_PWR_EN = 0x00
GPIO_5V_EN = 0x01
GPIO_ASIC_RST = 0x02
GPIO_ASIC_TRIP = 0x03

ADC_DOMAIN1 = 0x50
ADC_DOMAIN2 = 0x51
ADC_DOMAIN3 = 0x52

FAN_SPEED_CMD = 0x10
FAN_TACH_CMD = 0x20

def prettyHex(data):
    return ' '.join(f'{byte:02X}' for byte in data)

#print a list of u16 values as hex
def prettyHex9(data):
    return ' '.join(f'{byte & 0x1FF:03X}' for byte in data)

def fan_set_speed(ser, id, speed_percent, debug=False):
    packet_len = 7
    packet = bytes([packet_len, 0x00, id, 0x00, PAGE_FAN, FAN_SPEED_CMD, speed_percent])

    if debug:
        print("ctrl fan tx: [%s]" % prettyHex(packet))

    ser.write(packet)

    # wait for the response
    rxdata = ser.read(4)
    if rxdata:
        bytes_read = len(rxdata)
        if bytes_read > 0:
            if debug:
                print("ctrl fan rx: [%s]" % prettyHex(rxdata))
            if rxdata[2] != id:
                print("Error: ID mismatch. Expected %02X, got %02X" % (id, rxdata[2]))
                return
        else:
            print("No data received")
            return
    else:
        print("No data received")
    return

def get_fan_rpm(ser, id, debug=False):
    packet_len = 6
    packet = bytes([packet_len, 0x00, id, 0x00, PAGE_FAN, FAN_TACH_CMD])

    if debug:
        print("ctrl fan rpm tx: [%s]" % prettyHex(packet))

    ser.write(packet)

    # wait for the response
    rxdata = ser.read(5)
    if rxdata:
        bytes_read = len(rxdata)
        if bytes_read > 0:
            if debug:
                print("ctrl fan rpm rx: [%s]" % prettyHex(rxdata))
            if rxdata[2] != id:
                print("Error: ID mismatch. Expected %02X, got %02X" % (id, rxdata[2]))
                return
            rpm = (rxdata[4] << 8) | rxdata[3]
            return rpm
        else:
            print("No data received")
            return
    else:
        print("No data received")
    return

def gpio_set(ser, id, gpio, value, debug=False):
    packet_len = 7
    packet = bytes([packet_len, 0x00, id, 0x00, PAGE_GPIO, gpio, value])

    if debug:
        print("ctrl gpio tx: [%s]" % prettyHex(packet))

    ser.write(packet)

    # wait for the response
    rxdata = ser.read(4)
    if rxdata:
        bytes_read = len(rxdata)
        if bytes_read > 0:
            if debug:
                print("ctrl gpio rx: [%s]" % prettyHex(rxdata))
            if rxdata[2] != id:
                print("Error: ID mismatch. Expected %02X, got %02X" % (id, rxdata[2]))
                return
        else:
            print("No data received")
            return
    else:
        print("No data received")
    return

#asic_write takes an list of u16 values and writes them as u8 bytes to the serial port
# Data is sent/received as pairs of bytes:
# - **First byte**: Lower 8 bits of the 9-bit word (bits 0-7)
# - **Second byte**: Bit 8 (only LSB is used, can be 0 or 1)
def asic_write(ser, data, debug=False):
    packet = []
    for value in data:
        lower_byte = value & 0xFF
        upper_byte = (value >> 8) & 0x01  # Only bit 8 is used
        packet.append(lower_byte)
        packet.append(upper_byte)

    if debug:
        print("asic tx: [%s]" % prettyHex9(data))
        # print("asic tx: [%s]" % prettyHex(packet))

    ser.write(packet)
    return

def asic_read(ser, length, debug=False):
    expected_bytes = length * 2  # Each u16 is sent as 2 bytes
    rxdata = ser.read(expected_bytes)

    #if debug:
        # print("asic rx: [%s]" % prettyHex(rxdata))

    if len(rxdata) != expected_bytes:
        print(f"Error: Expected {expected_bytes} bytes, got {len(rxdata)} bytes")
        return []

    data = []
    for i in range(0, len(rxdata), 2):
        lower_byte = rxdata[i]
        upper_byte = rxdata[i + 1] & 0x01  # Only bit 8 is used
        value = (upper_byte << 8) | lower_byte
        data.append(value)

    if debug:
        print("asic rx: [%s]" % prettyHex9(data))

    return data