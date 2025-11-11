import serial
import time

import bitaxeraw

# Configure the serial ports
try:
    serial_port_ctrl = serial.Serial(
        port='/dev/tty.usbmodemb310cc521',  # Update this to your control serial port. usually it's the first one
        baudrate=115200,
        timeout=1
    )
except serial.SerialException as e:
    print(f"Error opening Control serial port: {e}")
    exit(1)

try:
    serial_port_asic = serial.Serial(
        port='/dev/tty.usbmodemb310cc523',  # Update this to your ASIC serial port. usually it's the second one
        baudrate=115200,
        timeout=2
    )
except serial.SerialException as e:
    print(f"Error opening ASIC serial port: {e}")
    exit(1)


def prettyHex(data):
    return ' '.join(f'{byte:02X}' for byte in data)

#enable 5V_EN
bitaxeraw.gpio_set(serial_port_ctrl, 0xAB, bitaxeraw.GPIO_5V_EN, bitaxeraw.GPIO_HIGH, debug=True)
time.sleep(0.1)
