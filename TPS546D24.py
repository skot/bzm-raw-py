import rawi2c
import struct
import time
from pmbusconst import *
from TPS546helpers import *

TPS546_CONFIG_BONANZA = {
    # vin voltage
    "VIN_ON": 11.0,
    "VIN_OFF": 10.5,
    "VIN_UV_WARN_LIMIT": 11.0,
    "VIN_OV_FAULT_LIMIT": 14.0,
    # vout voltage
    "SCALE_LOOP": 0.25,
    "VOUT_MIN": 1,
    "VOUT_MAX": 3.5,
    "VOUT_COMMAND": 2.8,
    # iout current
    "IOUT_OC_WARN_LIMIT": 50.00, # A
    "IOUT_OC_FAULT_LIMIT": 55.00, # A
    # config
    "STACK_CONFIG": 0x0001, # 2 modules
    "SYNC_CONFIG": 0xF0, # Enable Auto Detect SYNC
    "CMD_PHASE": 0xFF, # Phase addressing - 0xFF is all phases as single entity
    "COMPENSATION_CONFIG": [0xFF, 0xFF, 0xFF, 0xFF, 0xFF], # Default compensation config
    "FREQUENCY": 1500
}

W_CMD_ID = 0xAA # arbitrary write command ID
R_CMD_ID = 0xBB # arbitrary read command ID

DEVICE_ID1 = [0x54, 0x49, 0x54, 0x6B, 0x24, 0x41] # TPS546D24A
DEVICE_ID2 = [0x54, 0x49, 0x54, 0x6D, 0x24, 0x41] # TPS546D24A
DEVICE_ID3 = [0x54, 0x49, 0x54, 0x6D, 0x24, 0x62] # TPS546D24S

TPS546_I2CADDR         = 0x24  # TPS546 i2c address
TPS546_I2CADDR_ALERT   = 0x0C  # TPS546 SMBus Alert address
TPS546_MANUFACTURER_ID = 0xFE  # Manufacturer ID
TPS546_REVISION        = 0xFF  # Chip revision

OPERATION_OFF = 0x00
OPERATION_ON  = 0x80

# These are the inital values for the voltage regulator configuration

TPS546_INIT_INTERLEAVE = 0x0010 # GROUPID = 0, NUM_GROUP = 1, ORDER = 0. Sets phase Position to 0º

#VIN_OV_FAULT_RESPONSE pg98
#= 0xB7 -> 1011 0111
#10 -> Immediate Shutdown. Shut down and restart according to VIN_OV_RETRY.
#110 -> After shutting down, wait one HICCUP period, and attempt to restart up to 6 times. After 6 failed restart attempts, do not attempt to restart (latch off).
#111 -> Shutdown delay of seven PWM_CLK, HICCUP equal to 7 times TON_RISE
TPS546_INIT_VIN_OV_FAULT_RESPONSE = 0xB7

# vout voltage
#TPS546_INIT_SCALE_LOOP 0.25  # Voltage Scale factor --> In device-specific config
#TPS546_INIT_VOUT_MAX 3 # V --> In device-specific config
TPS546_INIT_VOUT_OV_FAULT_LIMIT = 1.25 # %/100 above VOUT_COMMAND
TPS546_INIT_VOUT_OV_WARN_LIMIT  = 1.16 # %/100 above VOUT_COMMAND
TPS546_INIT_VOUT_MARGIN_HIGH = 1.1 # %/100 above VOUT
#TPS546_INIT_VOUT_COMMAND 1.2  # V absolute value --> In device-specific config
TPS546_INIT_VOUT_MARGIN_LOW = 0.90 # %/100 below VOUT
TPS546_INIT_VOUT_UV_WARN_LIMIT = 0.90  # %/100 below VOUT_COMMAND
TPS546_INIT_VOUT_UV_FAULT_LIMIT = 0.75 # %/100 below VOUT_COMMAND
#TPS546_INIT_VOUT_MIN 1 # v

# iout current
# TPS546_INIT_IOUT_OC_WARN_LIMIT  50.00 # A --> In device-specific config
# TPS546_INIT_IOUT_OC_FAULT_LIMIT 55.00 # A --> In device-specific config

#IOUT_OC_FAULT_RESPONSE - pg91
#= 0xC0 -> 1100 0000
#11 -> Shutdown Immediately
#000 -> Do not attempt to restart (latch off).
#000 -> Shutdown delay of one PWM_CLK, HICCUP equal to TON_RISE
TPS546_INIT_IOUT_OC_FAULT_RESPONSE = 0xC0  # shut down, no retries

# temperature
# It is better to set the temperature warn limit for TPS546 more higher than Ultra 
TPS546_INIT_OT_WARN_LIMIT  = 105 # degrees C
TPS546_INIT_OT_FAULT_LIMIT = 145 # degrees C

#OT_FAULT_RESPONSE - pg94
#= 0xFF -> 1111 1111
#11 -> Shutdown until Temperature is below OT_WARN_LIMIT, then restart according to OT_RETRY*.
#111 -> After shutting down, wait one HICCUP period, and attempt to restart indefinitely, until commanded OFF or a successful start-up occurs.
#111 -> Shutdown delay of 7 ms, HICCUP equal to 4 times TON_RISE
TPS546_INIT_OT_FAULT_RESPONSE = 0xFF # wait for cooling, and retry

# timing
TPS546_INIT_TON_DELAY = 0
TPS546_INIT_TON_RISE = 3
TPS546_INIT_TON_MAX_FAULT_LIMIT = 0
TPS546_INIT_TON_MAX_FAULT_RESPONSE = 0x3B
TPS546_INIT_TOFF_DELAY = 0
TPS546_INIT_TOFF_FALL = 0

INIT_PIN_DETECT_OVERRIDE = 0xFFFF #use pin values

## SMBus Commands
def smb_write_word(ser, command, data, debug=False):
    # Write a word (2 bytes) to the SMBus
    rawi2c.i2c_send_bytes(ser, R_CMD_ID, TPS546_I2CADDR, command, [data & 0xFF, data >> 8], debug)

def smb_write_byte(ser, command, data, debug=False):
    # Write a byte (1 byte) to the SMBus
    rawi2c.i2c_send_bytes(ser, R_CMD_ID, TPS546_I2CADDR, command, [data], debug)

def smb_write_block(ser, command, data, length, debug=False):
    # Write a block of data to the SMBus
    rawi2c.i2c_send_bytes(ser, R_CMD_ID, TPS546_I2CADDR, command, [length] + data, debug)

def smb_read_word(ser, command, debug=False):
    # Read a word (2 bytes) from the SMBus
    response = rawi2c.i2c_read_bytes(ser, W_CMD_ID, TPS546_I2CADDR, command, 2, debug)
    if response and len(response) == 2:
        return (response[1] << 8) | response[0]
    return None

def smb_read_byte(ser, command, debug=False):
    # Read a byte (1 byte) from the SMBus
    response = rawi2c.i2c_read_bytes(ser, W_CMD_ID, TPS546_I2CADDR, command, 1, debug)
    if response and len(response) == 1:
        return response[0]
    return None

def smb_read_block(ser, command, length, debug=False):
    length = length + 1
    # Read a block of data from the SMBus
    response = rawi2c.i2c_read_bytes(ser, W_CMD_ID, TPS546_I2CADDR, command, length, debug)
    if response and len(response) == length:
        #return the response minus the first element in the list
        return response[1:]
    return None

#-------------------------*/


def get_device_id(ser):
  response = rawi2c.i2c_read_bytes(ser, R_CMD_ID, TPS546_I2CADDR, PMBUS_IC_DEVICE_ID, 7)
  print(f"[{ ' '.join(f'{b:02X}' for b in response) }]" )
  if response:
    resp_list = list(response)[1:]  # drop the first integer
    if resp_list == DEVICE_ID1:
      print("TPS546D24A found")
      return True
    elif resp_list == DEVICE_ID2:
      print("TPS546D24A found")
      return True
    elif resp_list == DEVICE_ID3:
      print("TPS546D24S found")
      return True
    else:
      print(f"Unknown device ID: [{ ' '.join(f'{b:02X}' for b in response) }]")
  return False

def read_current_settings(ser):
    response = rawi2c.i2c_read_bytes(ser, R_CMD_ID, TPS546_I2CADDR, PMBUS_READ_ALL, 15)
    if response:
        print(f"[{ ' '.join(f'{b:02X}' for b in response) }]" )
        results = struct.unpack('>HHHHHHH', response[1:])  # drop the first integer
        print(f"PMBUS_READ_ALL: [{ ' '.join(f'{value:04X}' for value in results) }]")
        return results
    return None

def read_manf_settings(ser):
    response = rawi2c.i2c_read_bytes(ser, R_CMD_ID, TPS546_I2CADDR, PMBUS_STATUS_ALL, 8)
    if response:
        print(f"[{ ' '.join(f'{b:02X}' for b in response) }]" )
        results = struct.unpack('>BBBBBBB', response[1:])  # drop the first integer
        print(f"PMBUS_STATUS_ALL: [{ ' '.join(f'{value:04X}' for value in results) }]")
        return results
    return None

def Init(ser):
    # Establish communication with regulator
    get_device_id(ser)

    # configure the bootup behavior regarding pin detect values vs NVM values
    print("Setting PIN_DETECT_OVERRIDE: %04X" % INIT_PIN_DETECT_OVERRIDE)
    smb_write_word(ser, PMBUS_PIN_DETECT_OVERRIDE, INIT_PIN_DETECT_OVERRIDE)

    # Make sure power is turned off until commanded
    u8_value = (ON_OFF_CONFIG_DELAY | ON_OFF_CONFIG_POLARITY | ON_OFF_CONFIG_CMD | ON_OFF_CONFIG_PU)
    print("Setting ON_OFF_CONFIG: %02X" % u8_value)
    smb_write_byte(ser, PMBUS_ON_OFF_CONFIG, u8_value)

    # Stack Config
    print("Setting STACK_CONFIG: %04X" % TPS546_CONFIG_BONANZA["STACK_CONFIG"])
    smb_write_word(ser, PMBUS_STACK_CONFIG, TPS546_CONFIG_BONANZA["STACK_CONFIG"])

    # Interleave -- only works in multi-phased stack
    # print("Setting INTERLEAVE: %04X" % TPS546_INIT_INTERLEAVE)
    # smb_write_word(ser, PMBUS_INTERLEAVE, TPS546_INIT_INTERLEAVE)

    # Sync Config
    print("Setting SYNC_CONFIG: %02X" % TPS546_CONFIG_BONANZA["SYNC_CONFIG"])
    smb_write_byte(ser, PMBUS_SYNC_CONFIG, TPS546_CONFIG_BONANZA["SYNC_CONFIG"])

    # Command Phase
    print("Setting CMD_PHASE: %02X" % TPS546_CONFIG_BONANZA["CMD_PHASE"])
    smb_write_byte(ser, PMBUS_PHASE, TPS546_CONFIG_BONANZA["CMD_PHASE"])

    # Switch frequency
    print("Setting FREQUENCY: %dMHz" % TPS546_CONFIG_BONANZA["FREQUENCY"])
    smb_write_word(ser, PMBUS_FREQUENCY_SWITCH, int_2_slinear11(TPS546_CONFIG_BONANZA["FREQUENCY"]))

    # Compensation Config
    print("Setting COMPENSATION_CONFIG: [%s]" % ' '.join(f'{b:02X}' for b in TPS546_CONFIG_BONANZA["COMPENSATION_CONFIG"]))
    smb_write_block(ser, PMBUS_COMPENSATION_CONFIG, TPS546_CONFIG_BONANZA["COMPENSATION_CONFIG"], 5)
    time.sleep(0.1)

    # vin voltage
    #deal with the UV_WARN_LIMIT bug
    if (TPS546_CONFIG_BONANZA["VIN_UV_WARN_LIMIT"] > 0):
        print("Setting VIN_UV_WARN_LIMIT: %.2f" % TPS546_CONFIG_BONANZA["VIN_UV_WARN_LIMIT"])
        smb_write_word(ser, PMBUS_VIN_UV_WARN_LIMIT, float_2_slinear11(TPS546_CONFIG_BONANZA["VIN_UV_WARN_LIMIT"]))

    print("Setting VIN_ON: %.2fV" % TPS546_CONFIG_BONANZA["VIN_ON"])
    smb_write_word(ser, PMBUS_VIN_ON, float_2_slinear11(TPS546_CONFIG_BONANZA["VIN_ON"]))

    print("Setting VIN_OFF: %.2fV" % TPS546_CONFIG_BONANZA["VIN_OFF"])
    smb_write_word(ser, PMBUS_VIN_OFF, float_2_slinear11(TPS546_CONFIG_BONANZA["VIN_OFF"]))

    print("Setting VIN_OV_FAULT_LIMIT: %.2fV" % TPS546_CONFIG_BONANZA["VIN_OV_FAULT_LIMIT"])
    smb_write_word(ser, PMBUS_VIN_OV_FAULT_LIMIT, float_2_slinear11(TPS546_CONFIG_BONANZA["VIN_OV_FAULT_LIMIT"]))

    print("Setting VIN_OV_FAULT_RESPONSE: %02X" % TPS546_INIT_VIN_OV_FAULT_RESPONSE)
    smb_write_byte(ser, PMBUS_VIN_OV_FAULT_RESPONSE, TPS546_INIT_VIN_OV_FAULT_RESPONSE)

    # vout voltage
    print("Setting VOUT SCALE: %.2f" % TPS546_CONFIG_BONANZA["SCALE_LOOP"])
    smb_write_word(ser, PMBUS_VOUT_SCALE_LOOP, float_2_slinear11(TPS546_CONFIG_BONANZA["SCALE_LOOP"]))

    print("Setting VOUT_COMMAND: %.2fV" % TPS546_CONFIG_BONANZA["VOUT_COMMAND"])
    smb_write_word(ser, PMBUS_VOUT_COMMAND, float_2_ulinear16(TPS546_CONFIG_BONANZA["VOUT_COMMAND"]))

    print("Setting VOUT_MAX: %.2fV" % TPS546_CONFIG_BONANZA["VOUT_MAX"])
    smb_write_word(ser, PMBUS_VOUT_MAX, float_2_ulinear16(TPS546_CONFIG_BONANZA["VOUT_MAX"]))

    print("Setting VOUT_MIN: %.2fV" % TPS546_CONFIG_BONANZA["VOUT_MIN"])
    smb_write_word(ser, PMBUS_VOUT_MIN, float_2_ulinear16(TPS546_CONFIG_BONANZA["VOUT_MIN"]))

    print("Setting VOUT_OV_FAULT_LIMIT: %.2f%% (%.2fV)" % (TPS546_INIT_VOUT_OV_FAULT_LIMIT, TPS546_CONFIG_BONANZA["VOUT_COMMAND"] * TPS546_INIT_VOUT_OV_FAULT_LIMIT))
    smb_write_word(ser, PMBUS_VOUT_OV_FAULT_LIMIT, float_2_ulinear16(TPS546_INIT_VOUT_OV_FAULT_LIMIT))

    print("Setting VOUT_OV_WARN_LIMIT: %.2f%% (%.2fV)" % (TPS546_INIT_VOUT_OV_WARN_LIMIT, TPS546_CONFIG_BONANZA["VOUT_COMMAND"] * TPS546_INIT_VOUT_OV_WARN_LIMIT))
    smb_write_word(ser, PMBUS_VOUT_OV_WARN_LIMIT, float_2_ulinear16(TPS546_INIT_VOUT_OV_WARN_LIMIT))

    print("Setting VOUT_MARGIN_HIGH: %.2f%% (%.2fV)" % (TPS546_INIT_VOUT_MARGIN_HIGH, TPS546_CONFIG_BONANZA["VOUT_COMMAND"] * TPS546_INIT_VOUT_MARGIN_HIGH))
    smb_write_word(ser, PMBUS_VOUT_MARGIN_HIGH, float_2_ulinear16(TPS546_INIT_VOUT_MARGIN_HIGH))

    print("Setting VOUT_MARGIN_LOW: %.2f%% (%.2fV)" % (TPS546_INIT_VOUT_MARGIN_LOW, TPS546_CONFIG_BONANZA["VOUT_COMMAND"] * TPS546_INIT_VOUT_MARGIN_LOW))
    smb_write_word(ser, PMBUS_VOUT_MARGIN_LOW, float_2_ulinear16(TPS546_INIT_VOUT_MARGIN_LOW))

    print("Setting VOUT_UV_WARN_LIMIT: %.2f%% (%.2fV)" % (TPS546_INIT_VOUT_UV_WARN_LIMIT, TPS546_CONFIG_BONANZA["VOUT_COMMAND"] * TPS546_INIT_VOUT_UV_WARN_LIMIT))
    smb_write_word(ser, PMBUS_VOUT_UV_WARN_LIMIT, float_2_ulinear16(TPS546_INIT_VOUT_UV_WARN_LIMIT))

    print("Setting VOUT_UV_FAULT_LIMIT: %.2f%% (%.2fV)" % (TPS546_INIT_VOUT_UV_FAULT_LIMIT, TPS546_CONFIG_BONANZA["VOUT_COMMAND"] * TPS546_INIT_VOUT_UV_FAULT_LIMIT))
    smb_write_word(ser, PMBUS_VOUT_UV_FAULT_LIMIT, float_2_ulinear16(TPS546_INIT_VOUT_UV_FAULT_LIMIT))

    # iout current
    print("----- IOUT")
    print("Setting IOUT_OC_WARN_LIMIT: %.2fA" % TPS546_CONFIG_BONANZA["IOUT_OC_WARN_LIMIT"])
    smb_write_word(ser, PMBUS_IOUT_OC_WARN_LIMIT, float_2_slinear11(TPS546_CONFIG_BONANZA["IOUT_OC_WARN_LIMIT"]))

    print("Setting IOUT_OC_FAULT_LIMIT: %.2fA" % TPS546_CONFIG_BONANZA["IOUT_OC_FAULT_LIMIT"])
    smb_write_word(ser, PMBUS_IOUT_OC_FAULT_LIMIT, float_2_slinear11(TPS546_CONFIG_BONANZA["IOUT_OC_FAULT_LIMIT"]))

    print("Setting IOUT_OC_FAULT_RESPONSE: %02x" % TPS546_INIT_IOUT_OC_FAULT_RESPONSE)
    smb_write_byte(ser, PMBUS_IOUT_OC_FAULT_RESPONSE, TPS546_INIT_IOUT_OC_FAULT_RESPONSE)

    # temperature
    print("----- TEMPERATURE")
    print("Setting OT_WARN_LIMIT: %dC" % TPS546_INIT_OT_WARN_LIMIT)
    smb_write_word(ser, PMBUS_OT_WARN_LIMIT, int_2_slinear11(TPS546_INIT_OT_WARN_LIMIT))
    print("Setting OT_FAULT_LIMIT: %dC" % TPS546_INIT_OT_FAULT_LIMIT)
    smb_write_word(ser, PMBUS_OT_FAULT_LIMIT, int_2_slinear11(TPS546_INIT_OT_FAULT_LIMIT))
    print("Setting OT_FAULT_RESPONSE: %02x" % TPS546_INIT_OT_FAULT_RESPONSE)
    smb_write_byte(ser, PMBUS_OT_FAULT_RESPONSE, TPS546_INIT_OT_FAULT_RESPONSE)

    # timing
    print("----- TIMING")
    print("Setting TON_DELAY: %dms" % TPS546_INIT_TON_DELAY)
    smb_write_word(ser, PMBUS_TON_DELAY, int_2_slinear11(TPS546_INIT_TON_DELAY))
    print("Setting TON_RISE: %dms" % TPS546_INIT_TON_RISE)
    smb_write_word(ser, PMBUS_TON_RISE, int_2_slinear11(TPS546_INIT_TON_RISE))
    print("Setting TON_MAX_FAULT_LIMIT: %dms" % TPS546_INIT_TON_MAX_FAULT_LIMIT)
    smb_write_word(ser, PMBUS_TON_MAX_FAULT_LIMIT, int_2_slinear11(TPS546_INIT_TON_MAX_FAULT_LIMIT))
    print("Setting TON_MAX_FAULT_RESPONSE: %02x" % TPS546_INIT_TON_MAX_FAULT_RESPONSE)
    smb_write_byte(ser, PMBUS_TON_MAX_FAULT_RESPONSE, TPS546_INIT_TON_MAX_FAULT_RESPONSE)
    print("Setting TOFF_DELAY: %dms" % TPS546_INIT_TOFF_DELAY)
    smb_write_word(ser, PMBUS_TOFF_DELAY, int_2_slinear11(TPS546_INIT_TOFF_DELAY))
    print("Setting TOFF_FALL: %dms" % TPS546_INIT_TOFF_FALL)
    smb_write_word(ser, PMBUS_TOFF_FALL, int_2_slinear11(TPS546_INIT_TOFF_FALL))

def read_settings(ser):
    # Simple registers, no conversion needed
    val = smb_read_word(ser, PMBUS_PIN_DETECT_OVERRIDE)
    print(f"PIN_DETECT_OVERRIDE: {val:04X}")

    val = smb_read_byte(ser, PMBUS_ON_OFF_CONFIG)
    print(f"ON_OFF_CONFIG: {val:02X}")

    val = smb_read_word(ser, PMBUS_STACK_CONFIG)
    print(f"STACK_CONFIG: {val:04X}")

    val = smb_read_word(ser, PMBUS_INTERLEAVE)
    print(f"INTERLEAVE: {val:04X}")

    val = smb_read_byte(ser, PMBUS_SYNC_CONFIG)
    print(f"SYNC_CONFIG: {val:02X}")

    val = smb_read_byte(ser, PMBUS_PHASE)
    print(f"CMD_PHASE: {val:02X}")

    # Frequency uses int_2_slinear11 when writing
    val = smb_read_word(ser, PMBUS_FREQUENCY_SWITCH)
    freq = slinear11_2_int(val)
    print(f"FREQUENCY: {freq}MHz (raw: {val:04X})")

    val = smb_read_block(ser, PMBUS_COMPENSATION_CONFIG, 5)
    print(f"COMPENSATION_CONFIG: [{ ' '.join(f'{b:02X}' for b in val) }]" )

    # VIN voltage settings use float_2_slinear11
    val = smb_read_word(ser, PMBUS_VIN_UV_WARN_LIMIT)
    vin = slinear11_2_float(val)
    print(f"VIN_UV_WARN_LIMIT: {vin:.2f}V (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VIN_ON)
    vin = slinear11_2_float(val)
    print(f"VIN_ON: {vin:.2f}V (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VIN_OFF)
    vin = slinear11_2_float(val)
    print(f"VIN_OFF: {vin:.2f}V (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VIN_OV_FAULT_LIMIT)
    vin = slinear11_2_float(val)
    print(f"VIN_OV_FAULT_LIMIT: {vin:.2f}V (raw: {val:04X})")

    val = smb_read_byte(ser, PMBUS_VIN_OV_FAULT_RESPONSE)
    print(f"VIN_OV_FAULT_RESPONSE: {val:02X}")

    # VOUT settings use float_2_slinear11 or float_2_ulinear16
    val = smb_read_word(ser, PMBUS_VOUT_SCALE_LOOP)
    vout = slinear11_2_float(val)
    print(f"VOUT_SCALE_LOOP: {vout:.2f} (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_COMMAND)
    vout = ulinear16_2_float(val)
    print(f"VOUT_COMMAND: {vout:.2f}V (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_MAX)
    vout = ulinear16_2_float(val)
    print(f"VOUT_MAX: {vout:.2f}V (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_MIN)
    vout = ulinear16_2_float(val)
    print(f"VOUT_MIN: {vout:.2f}V (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_OV_FAULT_LIMIT)
    vout = ulinear16_2_float(val)
    print(f"VOUT_OV_FAULT_LIMIT: {vout:.2f}% (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_OV_WARN_LIMIT)
    vout = ulinear16_2_float(val)
    print(f"VOUT_OV_WARN_LIMIT: {vout:.2f}% (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_MARGIN_HIGH)
    vout = ulinear16_2_float(val)
    print(f"VOUT_MARGIN_HIGH: {vout:.2f}% (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_MARGIN_LOW)
    vout = ulinear16_2_float(val)
    print(f"VOUT_MARGIN_LOW: {vout:.2f}% (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_UV_WARN_LIMIT)
    vout = ulinear16_2_float(val)
    print(f"VOUT_UV_WARN_LIMIT: {vout:.2f}% (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_UV_FAULT_LIMIT)
    vout = ulinear16_2_float(val)
    print(f"VOUT_UV_FAULT_LIMIT: {vout:.2f}% (raw: {val:04X})")

    # IOUT settings use float_2_slinear11
    val = smb_read_word(ser, PMBUS_IOUT_OC_WARN_LIMIT)
    iout = slinear11_2_float(val)
    print(f"IOUT_OC_WARN_LIMIT: {iout:.2f}A (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_IOUT_OC_FAULT_LIMIT)
    iout = slinear11_2_float(val)
    print(f"IOUT_OC_FAULT_LIMIT: {iout:.2f}A (raw: {val:04X})")

    val = smb_read_byte(ser, PMBUS_IOUT_OC_FAULT_RESPONSE)
    print(f"IOUT_OC_FAULT_RESPONSE: {val:02X}")

    # Temperature settings use int_2_slinear11
    val = smb_read_word(ser, PMBUS_OT_WARN_LIMIT)
    temp = slinear11_2_int(val)
    print(f"OT_WARN_LIMIT: {temp}°C (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_OT_FAULT_LIMIT)
    temp = slinear11_2_int(val)
    print(f"OT_FAULT_LIMIT: {temp}°C (raw: {val:04X})")

    val = smb_read_byte(ser, PMBUS_OT_FAULT_RESPONSE)
    print(f"OT_FAULT_RESPONSE: {val:02X}")

    # Timing settings use int_2_slinear11
    val = smb_read_word(ser, PMBUS_TON_DELAY)
    time = slinear11_2_int(val)
    print(f"TON_DELAY: {time}ms (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_TON_RISE)
    time = slinear11_2_int(val)
    print(f"TON_RISE: {time}ms (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_TON_MAX_FAULT_LIMIT)
    time = slinear11_2_int(val)
    print(f"TON_MAX_FAULT_LIMIT: {time}ms (raw: {val:04X})")

    val = smb_read_byte(ser, PMBUS_TON_MAX_FAULT_RESPONSE)
    print(f"TON_MAX_FAULT_RESPONSE: {val:02X}")

    val = smb_read_word(ser, PMBUS_TOFF_DELAY)
    time = slinear11_2_int(val)
    print(f"TOFF_DELAY: {time}ms (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_TOFF_FALL)
    time = slinear11_2_int(val)
    print(f"TOFF_FALL: {time}ms (raw: {val:04X})")

def test_write_read(ser):
    print("Setting OT_WARN_LIMIT (0x%02X): %dC (%04X)" % (PMBUS_OT_WARN_LIMIT, TPS546_INIT_OT_WARN_LIMIT, int_2_slinear11(TPS546_INIT_OT_WARN_LIMIT)))
    smb_write_word(ser, PMBUS_OT_WARN_LIMIT, int_2_slinear11(TPS546_INIT_OT_WARN_LIMIT), True)
    time.sleep(0.5)

    print("Reading OT_WARN_LIMIT (0x%02X)" % PMBUS_OT_WARN_LIMIT)
    val = smb_read_word(ser, PMBUS_OT_WARN_LIMIT, True)
    temp = slinear11_2_int(val)
    print(f"OT_WARN_LIMIT: {temp}°C (raw: {val:04X})")