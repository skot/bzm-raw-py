import serial
import time
import TPS546D24

# Configure the serial ports
try:
    serial_port_asic = serial.Serial(
        port='/dev/tty.usbmodeme3e4967a3',  # Update this to your serial port
        baudrate=115200,
        timeout=2
    )
except serial.SerialException as e:
    print(f"Error opening ASIC serial port: {e}")
    exit(1)

try:
    serial_port_ctrl = serial.Serial(
        port='/dev/tty.usbmodeme3e4967a1',  # Update this to your serial port
        baudrate=115200,
        timeout=1
    )
except serial.SerialException as e:
    print(f"Error opening Control serial port: {e}")
    exit(1)

def prettyHex(data):
    return ' '.join(f'{byte:02X}' for byte in data)


# TPS546D24.get_device_id(serial_port_ctrl)
# TPS546D24.read_current_settings(serial_port_ctrl)
# TPS546D24.read_manf_settings(serial_port_ctrl)

TPS546D24.Init(serial_port_ctrl)

# time.sleep(1)

# TPS546D24.test_write_read(serial_port_ctrl)

print("\n\n----reading settings:")
TPS546D24.read_settings(serial_port_ctrl)

TPS546D24.read_current_settings(serial_port_ctrl)
TPS546D24.read_manf_settings(serial_port_ctrl)