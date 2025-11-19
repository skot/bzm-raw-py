import serial
import time

import bitaxeraw
import bzm2
import birds

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
        baudrate=5000000,
        timeout=2
    )
except serial.SerialException as e:
    print(f"Error opening ASIC serial port: {e}")
    exit(1)


def prettyHex(data):
    return ' '.join(f'{byte:02X}' for byte in data)

serial_port_asic.reset_input_buffer()
serial_port_ctrl.reset_input_buffer()

#enable 5V_EN
birds.enable_5V(serial_port_ctrl, debug=True)

#reset ASIC
birds.ASIC_reset(serial_port_ctrl, debug=True)

#test asic communication

bzm2.BZM_sendnoop(serial_port_asic, asic=0xFA, debug=True)

#write to the ASIC_ID register
# bzm2.BZM_writereg(serial_port_asic, 0xFA, 0xFFF, 0x00, [0x42, 0x01], debug=True)
# time.sleep(0.1)

# bitaxeraw.asic_write(serial_port_asic, [0x142, 0x0B0], debug=True)
# bitaxeraw.asic_read(serial_port_asic, 5, debug=True)
# time.sleep(1)

# bitaxeraw.asic_write(serial_port_asic, [0x1FA, 0x0B0], debug=True)
# bitaxeraw.asic_read(serial_port_asic, 5, debug=True)
# time.sleep(1)