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
        timeout=1,
        dsrdtr=False,  # Disable DTR/DSR
        rtscts=False   # Disable RTS/CTS
    )
except serial.SerialException as e:
    print(f"Error opening Control serial port: {e}")
    exit(1)

try:
    serial_port_asic = serial.Serial(
        port='/dev/tty.usbmodemb310cc523',  # Update this to your ASIC serial port. usually it's the second one
        baudrate=5000000,
        timeout=2,
        dsrdtr=False,  # Disable DTR/DSR
        rtscts=False   # Disable RTS/CTS
    )
except serial.SerialException as e:
    print(f"Error opening ASIC serial port: {e}")
    exit(1)


def prettyHex(data):
    return ' '.join(f'{byte:02X}' for byte in data)

serial_port_ctrl.reset_input_buffer()

#enable 5V_EN
birds.enable_5V(serial_port_ctrl, debug=True)

#reset ASIC
birds.ASIC_reset(serial_port_ctrl, debug=True)

time.sleep(1)

# enabling power and resetting spams the asic_serial port with junk, so flush it
serial_port_asic.reset_input_buffer()

#test asic communication
print("\n=== Sending NOOP with ASIC ID 0xFA ===")
bzm2.BZM_sendnoop(serial_port_asic, asic=0xFA, debug=True)

# Write to the ASIC_ID register (offset 0xBh per Table 8-3) to change ID from 0xFA to 0x42
# According to datasheet section 8.1.4:
# - Offset 0xBh contains the ASIC_ID register
# - Bits 7:0 = ASIC ID value (default 0xFA)
# - Bit 8 = Chain enable (automatically set to 1 on write)
# - Writing sets the new ID and enables chain for next ASIC
print("\n=== Changing ASIC_ID from 0xFA to 0x42 ===")
# Write 4 bytes: [ID, chain_enable, reserved, reserved]
# 0x42 = new ID, 0x01 = chain enable bit, 0x00, 0x00 for reserved bits
bzm2.BZM_writereg(serial_port_asic, 0xFA, 0xFFF, 0x0B, [0x42, 0x00, 0x00, 0x00], debug=True)
time.sleep(0.5)

# Read back the ASIC_ID register to verify the write
print("\n=== Reading back ASIC_ID register ===")
result = bzm2.BZM_readreg(serial_port_asic, 0x42, 0xFFF, 0x0B, 4, debug=True)
if result:
    print(f"ASIC_ID register contents: {bitaxeraw.prettyHex(result[2:4])}")
    print(f"  ASIC_ID (bits 7:0): 0x{result[2]:02X}")
    print(f"  Chain enable (bit 8): {(result[3] & 0x01)}")
time.sleep(0.5)

# Test with new ID (0x42)
print("\n=== Testing NOOP with new ID 0x42 ===")
bzm2.BZM_sendnoop(serial_port_asic, asic=0x42, debug=True)
time.sleep(0.5)

# # Test that old ID (0xFA) no longer responds
# print("\n=== Verifying old ID 0xFA no longer responds ===")
# bzm2.BZM_sendnoop(serial_port_asic, asic=0xFA, debug=True)
# time.sleep(0.5)

# Loopback test with new ID
print("\n=== Loopback test with new ID 0x42 ===")
bzm2.BZM_loopback(serial_port_asic, asic=0x42, data=[0x55, 0xAA, 0xFF, 0x00, 0x11, 0x22, 0x33, 0x44], debug=True)

# Test if second ASIC in chain now responds to 0xFA
print("\n=== Testing if second ASIC responds to 0xFA (broadcast) ===")
bzm2.BZM_sendnoop(serial_port_asic, asic=0xFA, debug=True)

# If there's a second ASIC, we should be able to program it now
print("\n=== Attempting to set second ASIC to ID 0x43 ===")
bzm2.BZM_writereg(serial_port_asic, 0xFA, 0xFFF, 0x0B, [0x43, 0x01, 0x00, 0x00], debug=True)
time.sleep(0.5)

# Read back the ASIC_ID register to verify the write
print("\n=== Reading back ASIC_ID register ===")
result = bzm2.BZM_readreg(serial_port_asic, 0x43, 0xFFF, 0x0B, 4, debug=True)
if result:
    print(f"ASIC_ID register contents: {bitaxeraw.prettyHex(result[2:4])}")
    print(f"  ASIC_ID (bits 7:0): 0x{result[2]:02X}")
    print(f"  Chain enable (bit 8): {(result[3] & 0x01)}")
time.sleep(0.5)

# Test if second ASIC now responds to 0x43
print("\n=== Testing if second ASIC responds to 0x43 ===")
bzm2.BZM_sendnoop(serial_port_asic, asic=0x43, debug=True)

## 3rd asic
# Test if third ASIC in chain now responds to 0xFA
print("\n=== Testing if second ASIC responds to 0xFA (broadcast) ===")
bzm2.BZM_sendnoop(serial_port_asic, asic=0xFA, debug=True)

# If there's a third ASIC, we should be able to program it now
print("\n=== Attempting to set third ASIC to ID 0x44 ===")
bzm2.BZM_writereg(serial_port_asic, 0xFA, 0xFFF, 0x0B, [0x44, 0x01, 0x00, 0x00], debug=True)
time.sleep(0.5)

# Read back the ASIC_ID register to verify the write
print("\n=== Reading back ASIC_ID register ===")
result = bzm2.BZM_readreg(serial_port_asic, 0x44, 0xFFF, 0x0B, 4, debug=True)
if result:
    print(f"ASIC_ID register contents: {bitaxeraw.prettyHex(result[2:4])}")
    print(f"  ASIC_ID (bits 7:0): 0x{result[2]:02X}")
    print(f"  Chain enable (bit 8): {(result[3] & 0x01)}")
time.sleep(0.5)

# Test if third ASIC now responds to 0x44
print("\n=== Testing if third ASIC responds to 0x44 ===")
bzm2.BZM_sendnoop(serial_port_asic, asic=0x44, debug=True)

## 4th asic
# Test if fourth ASIC in chain now responds to 0xFA
print("\n=== Testing if fourth ASIC responds to 0xFA (broadcast) ===")
bzm2.BZM_sendnoop(serial_port_asic, asic=0xFA, debug=True)

# If there's a fourth ASIC, we should be able to program it now
print("\n=== Attempting to set fourth ASIC to ID 0x45 ===")
bzm2.BZM_writereg(serial_port_asic, 0xFA, 0xFFF, 0x0B, [0x45, 0x01, 0x00, 0x00], debug=True)
time.sleep(0.5)

# Read back the ASIC_ID register to verify the write
print("\n=== Reading back ASIC_ID register ===")
result = bzm2.BZM_readreg(serial_port_asic, 0x45, 0xFFF, 0x0B, 4, debug=True)
if result:
    print(f"ASIC_ID register contents: {bitaxeraw.prettyHex(result[2:4])}")
    print(f"  ASIC_ID (bits 7:0): 0x{result[2]:02X}")
    print(f"  Chain enable (bit 8): {(result[3] & 0x01)}")
time.sleep(0.5)

# Test if fourth ASIC now responds to 0x45
print("\n=== Testing if fourth ASIC responds to 0x45 ===")
bzm2.BZM_sendnoop(serial_port_asic, asic=0x45, debug=True)