import serial
import time

GPIO_HIGH = 0x01
GPIO_LOW = 0x00

GPIO_PWR_EN = 0x00
GPIO_5V_EN = 0x01
GPIO_ASIC_RST = 0x02
GPIO_ASIC_TRIP = 0x03

ADC_DOMAIN1 = 0x50
ADC_DOMAIN2 = 0x51
ADC_DOMAIN3 = 0x52

def prettyHex(data):
    return ' '.join(f'{byte:02X}' for byte in data)


def gpio_set(ser, id, gpio, value, debug=False):
    packet_len = 7
    packet = bytes([packet_len, 0x00, id, 0x00, 0x06, gpio, value])

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