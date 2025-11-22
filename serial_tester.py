import serial
import time

# Configure the ASIC serial port
try:
    serial_port = serial.Serial(
        port='/dev/tty.usbmodemb310cc523',  # ASIC serial port
        baudrate=5000000,
        timeout=0.5
    )
except serial.SerialException as e:
    print(f"Error opening ASIC serial port: {e}")
    exit(1)

def prettyHex(data):
    return ' '.join(f'{byte:02X}' for byte in data)

def prettyHex9(data):
    """Format 9-bit values (u16) as 3-digit hex"""
    return ' '.join(f'{value:03X}' for value in data)

def write_9bit(ser, data_9bit):
    """
    Write 9-bit data to serial port.
    data_9bit: list of u16 values (9-bit words)
    Converts to pairs: [lower_8_bits, bit_8]
    """
    packet = []
    for value in data_9bit:
        lower_byte = value & 0xFF
        upper_byte = (value >> 8) & 0x01
        packet.append(lower_byte)
        packet.append(upper_byte)
    ser.write(bytes(packet))
    return packet

def read_9bit(ser, length, timeout=1.0):
    """
    Read 9-bit data from serial port.
    length: number of 9-bit words to read
    timeout: maximum time to wait for data (seconds)
    Returns: list of u16 values (9-bit words), raw bytes
    """
    expected_bytes = length * 2
    rx_data = bytearray()
    
    # Wait for data to arrive, checking periodically
    start_time = time.time()
    while len(rx_data) < expected_bytes and (time.time() - start_time) < timeout:
        bytes_available = ser.in_waiting
        if bytes_available > 0:
            chunk = ser.read(bytes_available)
            rx_data.extend(chunk)
        else:
            time.sleep(0.001)  # Small sleep to avoid busy-waiting
    
    data_9bit = []
    for i in range(0, len(rx_data), 2):
        if i + 1 < len(rx_data):
            lower_byte = rx_data[i]
            upper_byte = rx_data[i + 1] & 0x01
            value = (upper_byte << 8) | lower_byte
            data_9bit.append(value)
    
    return data_9bit, bytes(rx_data)
    return data_9bit, rx_data

print("=== 9-Bit Serial Loopback Test ===")
print("Testing if TX data appears on RX (loopback or echo)")
print("Format: Each 9-bit word is sent as [lower_8_bits, bit_8]\n")

# Clear any existing data in buffers
serial_port.reset_input_buffer()
serial_port.reset_output_buffer()
time.sleep(0.1)

# Test patterns (9-bit values)
test_patterns_9bit = [
    [0x155, 0x0AA],                    # 9-bit: 101010101, 010101010
    [0x1FF, 0x000],                    # 9-bit: 111111111, 000000000
    [0x001, 0x002, 0x004, 0x008],      # Low bits
    [0x100, 0x101, 0x102, 0x103],      # High bit set
    [0x042, 0x05A, 0x069, 0x096],      # Random 9-bit
]

for test_num, pattern in enumerate(test_patterns_9bit, 1):
    print(f"Test {test_num}: Sending {len(pattern)} 9-bit words")
    print(f"  TX (9-bit): [{prettyHex9(pattern)}]")
    
    # Clear input buffer before sending
    serial_port.reset_input_buffer()
    
    # Send the pattern
    tx_bytes = write_9bit(serial_port, pattern)
    print(f"  TX (bytes): [{prettyHex(tx_bytes)}]")
    serial_port.flush()
    
    # Wait for any echo/loopback
    time.sleep(0.1)
    
    # Read back
    rx_9bit, rx_bytes = read_9bit(serial_port, len(pattern))
    
    if len(rx_9bit) > 0:
        print(f"  RX (bytes): [{prettyHex(rx_bytes)}]")
        print(f"  RX (9-bit): [{prettyHex9(rx_9bit)}]")
        
        # Compare
        if pattern == rx_9bit:
            print(f"  ✓ PERFECT MATCH - Exact 9-bit loopback!")
        elif len(rx_9bit) == len(pattern):
            print(f"  ✗ MISMATCH - Received same count but different values")
            for i, (tx, rx) in enumerate(zip(pattern, rx_9bit)):
                if tx != rx:
                    print(f"    Word {i}: TX=0x{tx:03X}, RX=0x{rx:03X}")
        else:
            print(f"  ✗ PARTIAL - Received {len(rx_9bit)}/{len(pattern)} words")
    else:
        print(f"  RX: No data received")
    
    print()

# Test with longer 9-bit data - WITH PACING
print("Extended test: Sending 20 9-bit words WITH PACING")
long_pattern = [i for i in range(0x100, 0x114)]  # 0x100 to 0x113
print(f"  TX (9-bit): [{prettyHex9(long_pattern)}...] ({len(long_pattern)} words)")

serial_port.reset_input_buffer()

# Send in smaller chunks with delays to avoid buffer overflow
chunk_size = 5  # Send 5 words at a time
all_tx_bytes = []
for i in range(0, len(long_pattern), chunk_size):
    chunk = long_pattern[i:i+chunk_size]
    tx_bytes = write_9bit(serial_port, chunk)
    all_tx_bytes.extend(tx_bytes)
    serial_port.flush()
    time.sleep(0.05)  # Small delay between chunks

print(f"  TX (bytes): {len(all_tx_bytes)} bytes sent in {len(range(0, len(long_pattern), chunk_size))} chunks")

# Wait for all data to arrive
time.sleep(0.3)

# Check how many bytes are waiting
bytes_waiting = serial_port.in_waiting
print(f"  Bytes waiting in RX buffer: {bytes_waiting}/{len(all_tx_bytes)}")

rx_9bit, rx_bytes = read_9bit(serial_port, len(long_pattern), timeout=2.0)
print(f"  RX (bytes): {len(rx_bytes)} bytes received")
print(f"  RX (9-bit): [{prettyHex9(rx_9bit)}...] ({len(rx_9bit)} words)")

if len(rx_9bit) > 0:
    print(f"\n  Detailed byte comparison:")
    print(f"    TX bytes: [{prettyHex(all_tx_bytes[:20])}...]")
    print(f"    RX bytes: [{prettyHex(rx_bytes[:20])}...]")
    
    if long_pattern == rx_9bit:
        print(f"  ✓ PERFECT MATCH - Complete loopback of all {len(rx_9bit)} words!")
    elif len(rx_9bit) == len(long_pattern):
        print(f"  ✗ MISMATCH - Received same length but different data")
    else:
        print(f"  ✗ PARTIAL - Received {len(rx_9bit)}/{len(long_pattern)} words")
        if len(rx_bytes) % 2 != 0:
            print(f"  ⚠ WARNING: Odd number of bytes received ({len(rx_bytes)}) - data misaligned!")
else:
    print(f"  RX: No data received")

print("\n=== Test Complete ===")
print("\nConclusion:")
print("If you see perfect matches, the serial port has loopback enabled.")
print("This explains why reset_input_buffer() might trigger echoes.")
serial_port.close()
