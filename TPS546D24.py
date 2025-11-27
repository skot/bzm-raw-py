import rawi2c
import struct
import time
from pmbusconst import *
from TPS546helpers import *
from tps546D24_values import *


W_CMD_ID = 0xAA # arbitrary write command ID
R_CMD_ID = 0xBB # arbitrary read command ID

DEVICE_ID1 = [0x54, 0x49, 0x54, 0x6D, 0x24, 0x41] # TPS546D24A
DEVICE_ID2 = [0x54, 0x49, 0x54, 0x6D, 0x24, 0x62] # TPS546D24S

TPS546_I2CADDR         = 0x24  # TPS546 i2c address
TPS546_I2CADDR_ALERT   = 0x0C  # TPS546 SMBus Alert address
TPS546_MANUFACTURER_ID = 0xFE  # Manufacturer ID
TPS546_REVISION        = 0xFF  # Chip revision

OPERATION_OFF = 0x00
OPERATION_ON  = 0x80

def decode_status(status_word):
    """Decode the STATUS_WORD register according to datasheet Figure 7-61 and Table 7-72"""
    
    # High byte - Alert bits
    print("\nAlert Bits (15:8):")
    
    # VOUT (Bit 15)
    vout_fault = bool(status_word & (1 << 15))
    print("VOUT Fault Status:", end=" ")
    if not vout_fault:
        print("OK - No output voltage fault")
    else:
        print("FAULT - Output voltage fault detected, check STATUS_VOUT")
    
    # IOUT (Bit 14)
    iout_fault = bool(status_word & (1 << 14))
    print("IOUT Fault Status:", end=" ")
    if not iout_fault:
        print("OK - No output current fault")
    else:
        print("FAULT - Output current fault detected, check STATUS_IOUT")
    
    # INPUT (Bit 13)
    input_fault = bool(status_word & (1 << 13))
    print("Input Fault Status:", end=" ")
    if not input_fault:
        print("OK - No input fault")
    else:
        print("FAULT - Input fault detected, check STATUS_INPUT")
    
    # MFR (Bit 12)
    mfr_fault = bool(status_word & (1 << 12))
    print("MFR Fault Status:", end=" ")
    if not mfr_fault:
        print("OK - No manufacturer fault")
    else:
        print("FAULT - Manufacturer fault detected, check STATUS_MFR_SPECIFIC")
    
    # PGOOD (Bit 11)
    pgood = bool(status_word & (1 << 11))
    print("Power Good Status:", end=" ")
    if not pgood:
        print("OK - Output voltage within regulation window")
    else:
        print("FAULT - Output voltage outside regulation window")
    
    # Fan (Bit 10) - Not Supported
    print("Fan Status: Not supported on this device")
    
    # OTHER (Bit 9)
    other_status = bool(status_word & (1 << 9))
    print("Other Fault Status:", end=" ")
    if not other_status:
        print("OK - No other faults")
    else:
        print("FAULT - Other fault detected, check STATUS_OTHER")
    
    # Unknown (Bit 8) - Not Supported
    print("Bit 8: Not supported on this device")
    
    # Low byte - Status bits (Figure 7-60 and Table 7-71)
    print("\nSTATUS_BYTE Register Decode (7:0):")
    status_byte = status_word & 0xFF
    print(f"Raw value: 0x{status_byte:02X}")
    
    # BUSY (Bit 7)
    busy = bool(status_byte & (1 << 7))
    print("BUSY Status:", end=" ")
    if not busy:
        print("OK - Device ready to respond")
    else:
        print("BUSY - Device is busy and unable to respond")
    
    # OFF (Bit 6)
    off = bool(status_byte & (1 << 6))
    print("OFF Status:", end=" ")
    if not off:
        print("ON - Unit is enabled and converting power")
    else:
        print("OFF - Unit is not converting power")
    
    # VOUT_OV (Bit 5)
    vout_ov = bool(status_byte & (1 << 5))
    print("VOUT_OV Status:", end=" ")
    if not vout_ov:
        print("OK - No output overvoltage fault")
    else:
        print("FAULT - Output overvoltage fault has occurred")
    
    # IOUT_OC (Bit 4)
    iout_oc = bool(status_byte & (1 << 4))
    print("IOUT_OC Status:", end=" ")
    if not iout_oc:
        print("OK - No output overcurrent fault")
    else:
        print("FAULT - Output overcurrent fault has occurred")
    
    # VIN_UV (Bit 3)
    vin_uv = bool(status_byte & (1 << 3))
    print("VIN_UV Status:", end=" ")
    if not vin_uv:
        print("OK - No input undervoltage fault")
    else:
        print("FAULT - Input undervoltage fault has occurred")
    
    # TEMP (Bit 2)
    temp = bool(status_byte & (1 << 2))
    print("TEMPERATURE Status:", end=" ")
    if not temp:
        print("OK - No temperature fault/warning")
    else:
        print("FAULT - Temperature fault/warning has occurred")
    
    # CML (Bit 1)
    cml = bool(status_byte & (1 << 1))
    print("CML Status:", end=" ")
    if not cml:
        print("OK - No communication/memory/logic fault")
    else:
        print("FAULT - Communication/memory/logic fault has occurred")
    
    # NONE_OF_THE_ABOVE (Bit 0)
    other = bool(status_byte & (1 << 0))
    print("Other Faults:", end=" ")
    if not other:
        print("OK - No other faults")
    else:
        print("FAULT - Other fault has occurred")
    
    # Return decoded status for programmatic use
    return {
        'vout_fault': vout_fault,
        'iout_fault': iout_fault,
        'input_fault': input_fault,
        'mfr_fault': mfr_fault,
        'pgood': pgood,
        'other_status': other_status,
        'status_byte': {
            'raw': status_byte,
            'busy': busy,
            'off': off,
            'vout_ov': vout_ov,
            'iout_oc': iout_oc,
            'vin_uv': vin_uv,
            'temp': temp,
            'cml': cml,
            'other': other
        }
    }

## SMBus Commands
def smb_write_addr(ser, command, debug=False):
    # Write an address and no data
    rawi2c.i2c_write_addr(ser, R_CMD_ID, TPS546_I2CADDR, command, debug)

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

def prettyHex(data):
    return ' '.join(f'{byte:02X}' for byte in data)

def enable_pin(ser, state, debug=False):
    id = 0xAA
    if state:
        value = 0x01  # Enable
    else:
        value = 0x00  # Disable
    packet = bytes([7, 0x00, id, 0x00, 0x06, 0x00, value])
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

def get_device_id(ser):
  response = rawi2c.i2c_read_bytes(ser, R_CMD_ID, TPS546_I2CADDR, PMBUS_IC_DEVICE_ID, 7)
  # print(f"[{ ' '.join(f'{b:02X}' for b in response) }]" )
  if response:
    resp_list = list(response)[1:]  # drop the first integer
    if resp_list == DEVICE_ID1:
      print("TPS546D24A found!")
      return True
    if resp_list == DEVICE_ID2:
      print("TPS546D24S found!")
      return True
    else:
      print(f"Unknown device ID: [{ ' '.join(f'{b:02X}' for b in response) }]")
  return False

def read_all_sensors(ser, debug=False):
    response = rawi2c.i2c_read_bytes(ser, R_CMD_ID, TPS546_I2CADDR, PMBUS_READ_ALL, 15)
    if response:
        # print(f"Raw bytes: [{ ' '.join(f'{b:02X}' for b in response) }]" )
        results = struct.unpack('<HHHHHHH', response[1:])  # drop the first integer
        
        # Extract individual readings
        read_vin = results[4]       # bits 79:64 - Linear format
        read_temp = results[3]      # bits 63:48 - Linear format
        read_iout = results[2]      # bits 47:32 - Linear format
        read_vout = results[1]      # bits 31:16 - ULinear16 format
        status_word = results[0]    # bits 15:0
        
        print("\n\n---------Sensor Readings:")
        
        # Convert VIN using Linear format (slinear11)
        vin = slinear11_2_float(read_vin)
        print(f"READ_VIN : {vin:.3f}V (raw: 0x{read_vin:04X})")
        
        # Convert Temperature using Linear format (slinear11)
        temp = slinear11_2_float(read_temp)
        print(f"READ_TEMP: {temp:.1f}°C (raw: 0x{read_temp:04X})")
        
        # Convert IOUT using Linear format (slinear11)
        iout = slinear11_2_float(read_iout)
        print(f"READ_IOUT: {iout:.3f}A (raw: 0x{read_iout:04X})")
        
        # Convert VOUT using ULinear16 format
        vout = ulinear16_2_float(read_vout)
        print(f"READ_VOUT: {vout:.3f}V (raw: 0x{read_vout:04X})")
        print(f"POWER    : {(vout * iout):.3f}W")

        print(f"\nSTATUS_WORD: (0x{status_word:04X}):")
        
        if debug:
        # Decode STATUS_WORD
            decode_status(status_word)

        # Return the decoded values
        return {
            'raw': results,
            'duty_cycle': None,  # Not supported
            'iin': None,         # Not supported
            'vin': vin,
            'temperature': temp,
            'iout': iout,
            'vout': vout,
            'status_word': status_word
        }
    return None

def init_disable(ser):
    #write operation register to turn off power - note ON_OFF_CONFIG needs to be changed to 0x1B for this to take effect. do that next
    print("Setting OPERATION: %02X" % OPERATION_OFF)
    smb_write_byte(ser, PMBUS_OPERATION, OPERATION_OFF)


    # Make sure power is turned off until commanded
    u8_value = (ON_OFF_CONFIG_DELAY | ON_OFF_CONFIG_POLARITY | ON_OFF_CONFIG_CMD | ON_OFF_CONFIG_PU)
    print("Setting ON_OFF_CONFIG: %02X" % u8_value)
    smb_write_byte(ser, PMBUS_ON_OFF_CONFIG, u8_value)


def Init(ser, TPS546_INIT_CONFIG):
    # Establish communication with regulator
    get_device_id(ser)

def write_settings(ser, TPS546_INIT_CONFIG):
    # ON_OFF_CONFIG
    # if TPS546_INIT_CONFIG["ON_OFF_CONFIG"] is not None:
    #     print("Setting ON_OFF_CONFIG: %02X" % TPS546_INIT_CONFIG["ON_OFF_CONFIG"])
    #     smb_write_byte(ser, PMBUS_ON_OFF_CONFIG, TPS546_INIT_CONFIG["ON_OFF_CONFIG"])

    # Phase addressing
    print("Setting CMD_PHASE: %02X" % TPS546_INIT_CONFIG["PHASE"])
    smb_write_byte(ser, PMBUS_PHASE, TPS546_INIT_CONFIG["PHASE"])

    # CAPABILITY
    # print("Setting CAPABILITY: %02X" % TPS546_INIT_CONFIG["CAPABILITY"])
    # smb_write_byte(ser, PMBUS_CAPABILITY, TPS546_INIT_CONFIG["CAPABILITY"])

    # SMBALERT_MASK
    print("Setting SMBALERT_MASK: (VOUT: %02X," % (TPS546_INIT_CONFIG["SMBALERT_MASK"][0] >> 8), end='')
    smb_write_word(ser, PMBUS_SMBALERT_MASK, TPS546_INIT_CONFIG["SMBALERT_MASK"][0] | PMBUS_STATUS_VOUT)
    print(" IOUT: %02X," % (TPS546_INIT_CONFIG["SMBALERT_MASK"][1] >> 8), end='')
    smb_write_word(ser, PMBUS_SMBALERT_MASK, TPS546_INIT_CONFIG["SMBALERT_MASK"][1] | PMBUS_STATUS_IOUT)
    print(" INPUT: %02X," % (TPS546_INIT_CONFIG["SMBALERT_MASK"][2] >> 8), end='')
    smb_write_word(ser, PMBUS_SMBALERT_MASK, TPS546_INIT_CONFIG["SMBALERT_MASK"][2] | PMBUS_STATUS_INPUT)
    print(" TEMP: %02X," % (TPS546_INIT_CONFIG["SMBALERT_MASK"][3] >> 8), end='')
    smb_write_word(ser, PMBUS_SMBALERT_MASK, TPS546_INIT_CONFIG["SMBALERT_MASK"][3] | PMBUS_STATUS_TEMPERATURE)
    print(" CML: %02X," % (TPS546_INIT_CONFIG["SMBALERT_MASK"][4] >> 8), end='')
    smb_write_word(ser, PMBUS_SMBALERT_MASK, TPS546_INIT_CONFIG["SMBALERT_MASK"][4] | PMBUS_STATUS_CML)
    print(" OTHER: %02X," % (TPS546_INIT_CONFIG["SMBALERT_MASK"][5] >> 8), end='')
    smb_write_word(ser, PMBUS_SMBALERT_MASK, TPS546_INIT_CONFIG["SMBALERT_MASK"][5] | PMBUS_STATUS_OTHER)
    print(" MFR: %02X)" % (TPS546_INIT_CONFIG["SMBALERT_MASK"][6] >> 8))
    smb_write_word(ser, PMBUS_SMBALERT_MASK, TPS546_INIT_CONFIG["SMBALERT_MASK"][6] | PMBUS_STATUS_MFR_SPECIFIC)

    # Switch frequency
    print("Setting FREQUENCY: %dkHz" % TPS546_INIT_CONFIG["FREQUENCY_SWITCH"])
    smb_write_word(ser, PMBUS_FREQUENCY_SWITCH, int_2_slinear11(TPS546_INIT_CONFIG["FREQUENCY_SWITCH"]))

    # Sync Config
    print("Setting SYNC_CONFIG: %02X" % TPS546_INIT_CONFIG["SYNC_CONFIG"])
    smb_write_byte(ser, PMBUS_SYNC_CONFIG, TPS546_INIT_CONFIG["SYNC_CONFIG"])

    # Stack Config
    print("Setting STACK_CONFIG: %04X" % TPS546_INIT_CONFIG["STACK_CONFIG"])
    smb_write_word(ser, PMBUS_STACK_CONFIG, TPS546_INIT_CONFIG["STACK_CONFIG"])

    # Interleave
    print("Setting INTERLEAVE: %04X" % TPS546_INIT_CONFIG["INTERLEAVE"])
    smb_write_word(ser, PMBUS_INTERLEAVE, TPS546_INIT_CONFIG["INTERLEAVE"])

    # MISC_OPTIONS
    print("Setting MISC_OPTIONS: %04X" % TPS546_INIT_CONFIG["MISC_OPTIONS"])
    smb_write_word(ser, PMBUS_MISC_OPTIONS, TPS546_INIT_CONFIG["MISC_OPTIONS"])

    # PIN_DETECT_OVERRIDE
    print("Setting PIN_DETECT_OVERRIDE: %04X" % TPS546_INIT_CONFIG["PIN_DETECT_OVERRIDE"])
    smb_write_word(ser, PMBUS_PIN_DETECT_OVERRIDE, TPS546_INIT_CONFIG["PIN_DETECT_OVERRIDE"])

    # DEVICE_ADDRESS (using SLAVE_ADDRESS register)
    print("Setting DEVICE_ADDRESS: %02X" % TPS546_INIT_CONFIG["DEVICE_ADDRESS"])
    smb_write_byte(ser, PMBUS_SLAVE_ADDRESS, TPS546_INIT_CONFIG["DEVICE_ADDRESS"])

    # MFR_ID (3 bytes)
    if any(b != 0x00 for b in TPS546_INIT_CONFIG["MFR_ID"]):
        print("Setting MFR_ID: [%s]" % ' '.join(f'{b:02X}' for b in TPS546_INIT_CONFIG["MFR_ID"]))
        smb_write_block(ser, PMBUS_MFR_ID, TPS546_INIT_CONFIG["MFR_ID"], 3)

    # MFR_MODEL (3 bytes)
    if any(b != 0x00 for b in TPS546_INIT_CONFIG["MFR_MODEL"]):
        print("Setting MFR_MODEL: [%s]" % ' '.join(f'{b:02X}' for b in TPS546_INIT_CONFIG["MFR_MODEL"]))
        smb_write_block(ser, PMBUS_MFR_MODEL, TPS546_INIT_CONFIG["MFR_MODEL"], 3)

    # MFR_REVISION (3 bytes)
    if any(b != 0x00 for b in TPS546_INIT_CONFIG["MFR_REVISION"]):
        print("Setting MFR_REVISION: [%s]" % ' '.join(f'{b:02X}' for b in TPS546_INIT_CONFIG["MFR_REVISION"]))
        smb_write_block(ser, PMBUS_MFR_REVISION, TPS546_INIT_CONFIG["MFR_REVISION"], 3)

    # MFR_SERIAL (3 bytes)
    if any(b != 0x00 for b in TPS546_INIT_CONFIG["MFR_SERIAL"]):
        print("Setting MFR_SERIAL: [%s]" % ' '.join(f'{b:02X}' for b in TPS546_INIT_CONFIG["MFR_SERIAL"]))
        smb_write_block(ser, PMBUS_MFR_SERIAL, TPS546_INIT_CONFIG["MFR_SERIAL"], 3)

    # Compensation Config
    print("Setting COMPENSATION_CONFIG: [%s]" % ' '.join(f'{b:02X}' for b in TPS546_INIT_CONFIG["COMPENSATION_CONFIG"]))
    smb_write_block(ser, PMBUS_COMPENSATION_CONFIG, TPS546_INIT_CONFIG["COMPENSATION_CONFIG"], 5)
    time.sleep(0.1)

    # POWER_STAGE_CONFIG
    print("Setting POWER_STAGE_CONFIG: %02X" % TPS546_INIT_CONFIG["POWER_STAGE_CONFIG"])
    smb_write_block(ser, PMBUS_POWER_STAGE_CONFIG, [TPS546_INIT_CONFIG["POWER_STAGE_CONFIG"]], 1)

    # TELEMETRY_CONFIG (6 bytes)
    print("Setting TELEMETRY_CONFIG: [%s]" % ' '.join(f'{b:02X}' for b in TPS546_INIT_CONFIG["TELEMETRY_CONFIG"]))
    smb_write_block(ser, PMBUS_TELEMETRY_CONFIG, TPS546_INIT_CONFIG["TELEMETRY_CONFIG"], 6)

    # VOUT_MODE
    if TPS546_INIT_CONFIG["VOUT_MODE"] is not None:
        print("Setting VOUT_MODE: %02X" % TPS546_INIT_CONFIG["VOUT_MODE"])
        smb_write_byte(ser, PMBUS_VOUT_MODE, TPS546_INIT_CONFIG["VOUT_MODE"])

    # VOUT voltage settings
    print("Setting VOUT_COMMAND: %.2fV" % TPS546_INIT_CONFIG["VOUT_COMMAND"])
    smb_write_word(ser, PMBUS_VOUT_COMMAND, float_2_ulinear16(TPS546_INIT_CONFIG["VOUT_COMMAND"]))

    print("Setting VOUT_TRIM: %04X" % TPS546_INIT_CONFIG["VOUT_TRIM"])
    smb_write_word(ser, PMBUS_VOUT_TRIM, TPS546_INIT_CONFIG["VOUT_TRIM"])

    print("Setting VOUT_MAX: %.2fV" % TPS546_INIT_CONFIG["VOUT_MAX"])
    smb_write_word(ser, PMBUS_VOUT_MAX, float_2_ulinear16(TPS546_INIT_CONFIG["VOUT_MAX"]))

    print("Setting VOUT_MARGIN_HIGH: %.2f%% (%.2fV)" % (TPS546_INIT_CONFIG["VOUT_MARGIN_HIGH"], TPS546_INIT_CONFIG["VOUT_COMMAND"] * TPS546_INIT_CONFIG["VOUT_MARGIN_HIGH"]))
    smb_write_word(ser, PMBUS_VOUT_MARGIN_HIGH, float_2_ulinear16(TPS546_INIT_CONFIG["VOUT_MARGIN_HIGH"]))

    print("Setting VOUT_MARGIN_LOW: %.2f%% (%.2fV)" % (TPS546_INIT_CONFIG["VOUT_MARGIN_LOW"], TPS546_INIT_CONFIG["VOUT_COMMAND"] * TPS546_INIT_CONFIG["VOUT_MARGIN_LOW"]))
    smb_write_word(ser, PMBUS_VOUT_MARGIN_LOW, float_2_ulinear16(TPS546_INIT_CONFIG["VOUT_MARGIN_LOW"]))

    print("Setting VOUT_TRANSITION_RATE: %04X" % TPS546_INIT_CONFIG["VOUT_TRANSITION_RATE"])
    smb_write_word(ser, PMBUS_VOUT_TRANSITION_RATE, TPS546_INIT_CONFIG["VOUT_TRANSITION_RATE"])

    print("Setting VOUT SCALE: %.2f" % TPS546_INIT_CONFIG["VOUT_SCALE_LOOP"])
    smb_write_word(ser, PMBUS_VOUT_SCALE_LOOP, float_2_slinear11(TPS546_INIT_CONFIG["VOUT_SCALE_LOOP"]))

    print("Setting VOUT_MIN: %.2fV" % TPS546_INIT_CONFIG["VOUT_MIN"])
    smb_write_word(ser, PMBUS_VOUT_MIN, float_2_ulinear16(TPS546_INIT_CONFIG["VOUT_MIN"]))

    # VIN voltage
    print("Setting VIN_ON: %.2fV" % TPS546_INIT_CONFIG["VIN_ON"])
    smb_write_word(ser, PMBUS_VIN_ON, float_2_slinear11(TPS546_INIT_CONFIG["VIN_ON"]))

    print("Setting VIN_OFF: %.2fV" % TPS546_INIT_CONFIG["VIN_OFF"])
    smb_write_word(ser, PMBUS_VIN_OFF, float_2_slinear11(TPS546_INIT_CONFIG["VIN_OFF"]))

    # IOUT calibration
    print("Setting IOUT_CAL_GAIN: %04X" % TPS546_INIT_CONFIG["IOUT_CAL_GAIN"])
    smb_write_word(ser, PMBUS_IOUT_CAL_GAIN, TPS546_INIT_CONFIG["IOUT_CAL_GAIN"])

    print("Setting IOUT_CAL_OFFSET: %04X" % TPS546_INIT_CONFIG["IOUT_CAL_OFFSET"])
    smb_write_word(ser, PMBUS_IOUT_CAL_OFFSET, TPS546_INIT_CONFIG["IOUT_CAL_OFFSET"])

    # VOUT fault/warn limits
    print("Setting VOUT_OV_FAULT_LIMIT: %.2f%% (%.2fV)" % (TPS546_INIT_CONFIG["VOUT_OV_FAULT_LIMIT"], TPS546_INIT_CONFIG["VOUT_COMMAND"] * TPS546_INIT_CONFIG["VOUT_OV_FAULT_LIMIT"]))
    smb_write_word(ser, PMBUS_VOUT_OV_FAULT_LIMIT, float_2_ulinear16(TPS546_INIT_CONFIG["VOUT_OV_FAULT_LIMIT"]))

    print("Setting VOUT_OV_FAULT_RESPONSE: %02X" % TPS546_INIT_CONFIG["VOUT_OV_FAULT_RESPONSE"])
    smb_write_byte(ser, PMBUS_VOUT_OV_FAULT_RESPONSE, TPS546_INIT_CONFIG["VOUT_OV_FAULT_RESPONSE"])

    print("Setting VOUT_OV_WARN_LIMIT: %.2f%% (%.2fV)" % (TPS546_INIT_CONFIG["VOUT_OV_WARN_LIMIT"], TPS546_INIT_CONFIG["VOUT_COMMAND"] * TPS546_INIT_CONFIG["VOUT_OV_WARN_LIMIT"]))
    smb_write_word(ser, PMBUS_VOUT_OV_WARN_LIMIT, float_2_ulinear16(TPS546_INIT_CONFIG["VOUT_OV_WARN_LIMIT"]))

    print("Setting VOUT_UV_WARN_LIMIT: %.2f%% (%.2fV)" % (TPS546_INIT_CONFIG["VOUT_UV_WARN_LIMIT"], TPS546_INIT_CONFIG["VOUT_COMMAND"] * TPS546_INIT_CONFIG["VOUT_UV_WARN_LIMIT"]))
    smb_write_word(ser, PMBUS_VOUT_UV_WARN_LIMIT, float_2_ulinear16(TPS546_INIT_CONFIG["VOUT_UV_WARN_LIMIT"]))

    print("Setting VOUT_UV_FAULT_LIMIT: %.2f%% (%.2fV)" % (TPS546_INIT_CONFIG["VOUT_UV_FAULT_LIMIT"], TPS546_INIT_CONFIG["VOUT_COMMAND"] * TPS546_INIT_CONFIG["VOUT_UV_FAULT_LIMIT"]))
    smb_write_word(ser, PMBUS_VOUT_UV_FAULT_LIMIT, float_2_ulinear16(TPS546_INIT_CONFIG["VOUT_UV_FAULT_LIMIT"]))

    print("Setting VOUT_UV_FAULT_RESPONSE: %02X" % TPS546_INIT_CONFIG["VOUT_UV_FAULT_RESPONSE"])
    smb_write_byte(ser, PMBUS_VOUT_UV_FAULT_RESPONSE, TPS546_INIT_CONFIG["VOUT_UV_FAULT_RESPONSE"])

    # IOUT current
    print("Setting IOUT_OC_FAULT_LIMIT: %.2fA" % TPS546_INIT_CONFIG["IOUT_OC_FAULT_LIMIT"])
    smb_write_word(ser, PMBUS_IOUT_OC_FAULT_LIMIT, float_2_slinear11(TPS546_INIT_CONFIG["IOUT_OC_FAULT_LIMIT"]))

    print("Setting IOUT_OC_FAULT_RESPONSE: %02x" % TPS546_INIT_CONFIG["IOUT_OC_FAULT_RESPONSE"])
    smb_write_byte(ser, PMBUS_IOUT_OC_FAULT_RESPONSE, TPS546_INIT_CONFIG["IOUT_OC_FAULT_RESPONSE"])

    print("Setting IOUT_OC_WARN_LIMIT: %.2fA" % TPS546_INIT_CONFIG["IOUT_OC_WARN_LIMIT"])
    smb_write_word(ser, PMBUS_IOUT_OC_WARN_LIMIT, float_2_slinear11(TPS546_INIT_CONFIG["IOUT_OC_WARN_LIMIT"]))

    # Temperature
    print("Setting OT_FAULT_LIMIT: %dC" % TPS546_INIT_CONFIG["OT_FAULT_LIMIT"])
    smb_write_word(ser, PMBUS_OT_FAULT_LIMIT, int_2_slinear11(TPS546_INIT_CONFIG["OT_FAULT_LIMIT"]))

    print("Setting OT_FAULT_RESPONSE: %02x" % TPS546_INIT_CONFIG["OT_FAULT_RESPONSE"])
    smb_write_byte(ser, PMBUS_OT_FAULT_RESPONSE, TPS546_INIT_CONFIG["OT_FAULT_RESPONSE"])

    print("Setting OT_WARN_LIMIT: %dC" % TPS546_INIT_CONFIG["OT_WARN_LIMIT"])
    smb_write_word(ser, PMBUS_OT_WARN_LIMIT, int_2_slinear11(TPS546_INIT_CONFIG["OT_WARN_LIMIT"]))

    # VIN OV/UV
    print("Setting VIN_OV_FAULT_LIMIT: %.2fV" % TPS546_INIT_CONFIG["VIN_OV_FAULT_LIMIT"])
    smb_write_word(ser, PMBUS_VIN_OV_FAULT_LIMIT, float_2_slinear11(TPS546_INIT_CONFIG["VIN_OV_FAULT_LIMIT"]))

    print("Setting VIN_OV_FAULT_RESPONSE: %02X" % TPS546_INIT_CONFIG["VIN_OV_FAULT_RESPONSE"])
    smb_write_byte(ser, PMBUS_VIN_OV_FAULT_RESPONSE, TPS546_INIT_CONFIG["VIN_OV_FAULT_RESPONSE"])

    #deal with the UV_WARN_LIMIT bug
    if (TPS546_INIT_CONFIG["VIN_UV_WARN_LIMIT"] > 0):
        print("Setting VIN_UV_WARN_LIMIT: %.2f" % TPS546_INIT_CONFIG["VIN_UV_WARN_LIMIT"])
        smb_write_word(ser, PMBUS_VIN_UV_WARN_LIMIT, float_2_slinear11(TPS546_INIT_CONFIG["VIN_UV_WARN_LIMIT"]))

    # Timing
    print("Setting TON_DELAY: %dms" % TPS546_INIT_CONFIG["TON_DELAY"])
    smb_write_word(ser, PMBUS_TON_DELAY, int_2_slinear11(TPS546_INIT_CONFIG["TON_DELAY"]))

    print("Setting TON_RISE: %dms" % TPS546_INIT_CONFIG["TON_RISE"])
    smb_write_word(ser, PMBUS_TON_RISE, int_2_slinear11(TPS546_INIT_CONFIG["TON_RISE"]))

    print("Setting TON_MAX_FAULT_LIMIT: %dms" % TPS546_INIT_CONFIG["TON_MAX_FAULT_LIMIT"])
    smb_write_word(ser, PMBUS_TON_MAX_FAULT_LIMIT, int_2_slinear11(TPS546_INIT_CONFIG["TON_MAX_FAULT_LIMIT"]))

    print("Setting TON_MAX_FAULT_RESPONSE: %02x" % TPS546_INIT_CONFIG["TON_MAX_FAULT_RESPONSE"])
    smb_write_byte(ser, PMBUS_TON_MAX_FAULT_RESPONSE, TPS546_INIT_CONFIG["TON_MAX_FAULT_RESPONSE"])

    print("Setting TOFF_DELAY: %dms" % TPS546_INIT_CONFIG["TOFF_DELAY"])
    smb_write_word(ser, PMBUS_TOFF_DELAY, int_2_slinear11(TPS546_INIT_CONFIG["TOFF_DELAY"]))

    print("Setting TOFF_FALL: %dms" % TPS546_INIT_CONFIG["TOFF_FALL"])
    smb_write_word(ser, PMBUS_TOFF_FALL, int_2_slinear11(TPS546_INIT_CONFIG["TOFF_FALL"]))

def read_settings(ser):
    # Phase addressing
    val = smb_read_byte(ser, PMBUS_PHASE)
    print(f"Reading CMD_PHASE: {val:02X}")

    # CAPABILITY
    val = smb_read_byte(ser, PMBUS_CAPABILITY)
    print(f"Reading CAPABILITY: {val:02X}")

    # SMBALERT_MASK
    smb_write_block(ser, PMBUS_SMBALERT_MASK, [0x7A], 1)
    SMBALERT_MASK_VOUT = smb_read_block(ser, PMBUS_SMBALERT_MASK, 1)[0]
    smb_write_block(ser, PMBUS_SMBALERT_MASK, [0x7B], 1)
    SMBALERT_MASK_IOUT = smb_read_block(ser, PMBUS_SMBALERT_MASK, 1)[0]
    smb_write_block(ser, PMBUS_SMBALERT_MASK, [0x7C], 1)
    SMBALERT_MASK_INPUT = smb_read_block(ser, PMBUS_SMBALERT_MASK, 1)[0]
    smb_write_block(ser, PMBUS_SMBALERT_MASK, [0x7D], 1)
    SMBALERT_MASK_TEMPERATURE = smb_read_block(ser, PMBUS_SMBALERT_MASK, 1)[0]
    smb_write_block(ser, PMBUS_SMBALERT_MASK, [0x7E], 1)
    SMBALERT_MASK_CML = smb_read_block(ser, PMBUS_SMBALERT_MASK, 1)[0]
    smb_write_block(ser, PMBUS_SMBALERT_MASK, [0x7F], 1)
    SMBALERT_MASK_OTHER = smb_read_block(ser, PMBUS_SMBALERT_MASK, 1)[0]     
    smb_write_block(ser, PMBUS_SMBALERT_MASK, [0x80], 1)
    SMBALERT_MASK_MFR = smb_read_block(ser, PMBUS_SMBALERT_MASK, 1)[0]    

    print(f"Reading SMBALERT_MASK: (VOUT: {SMBALERT_MASK_VOUT:02X}, IOUT: {SMBALERT_MASK_IOUT:02X}, INPUT: {SMBALERT_MASK_INPUT:02X}, TEMP: {SMBALERT_MASK_TEMPERATURE:02X}, CML: {SMBALERT_MASK_CML:02X}, OTHER: {SMBALERT_MASK_OTHER:02X}, MFR: {SMBALERT_MASK_MFR:02X})")

    # Switch frequency
    val = smb_read_word(ser, PMBUS_FREQUENCY_SWITCH)
    freq = slinear11_2_int(val)
    print(f"Reading FREQUENCY: {freq}kHz (raw: {val:04X})")

    # Sync Config
    val = smb_read_byte(ser, PMBUS_SYNC_CONFIG)
    print(f"Reading SYNC_CONFIG: {val:02X}")

    # Stack Config
    val = smb_read_word(ser, PMBUS_STACK_CONFIG)
    print(f"Reading STACK_CONFIG: {val:04X}")

    # Interleave
    val = smb_read_word(ser, PMBUS_INTERLEAVE)
    print(f"Reading INTERLEAVE: {val:04X}")

    # MISC_OPTIONS
    val = smb_read_word(ser, PMBUS_MISC_OPTIONS)
    print(f"Reading MISC_OPTIONS: {val:04X}")

    # PIN_DETECT_OVERRIDE
    val = smb_read_word(ser, PMBUS_PIN_DETECT_OVERRIDE)
    print(f"Reading PIN_DETECT_OVERRIDE: {val:04X}")

    # DEVICE_ADDRESS (using SLAVE_ADDRESS register)
    val = smb_read_byte(ser, PMBUS_SLAVE_ADDRESS)
    print(f"Reading DEVICE_ADDRESS: {val:02X}")

    # MFR_ID (3 bytes)
    val = smb_read_block(ser, PMBUS_MFR_ID, 3)
    print(f"Reading MFR_ID: [{ ' '.join(f'{b:02X}' for b in val) }]")

    # MFR_MODEL (3 bytes)
    val = smb_read_block(ser, PMBUS_MFR_MODEL, 3)
    print(f"Reading MFR_MODEL: [{ ' '.join(f'{b:02X}' for b in val) }]")

    # MFR_REVISION (3 bytes)
    val = smb_read_block(ser, PMBUS_MFR_REVISION, 3)
    print(f"Reading MFR_REVISION: [{ ' '.join(f'{b:02X}' for b in val) }]")

    # MFR_SERIAL (3 bytes)
    val = smb_read_block(ser, PMBUS_MFR_SERIAL, 3)
    print(f"Reading MFR_SERIAL: [{ ' '.join(f'{b:02X}' for b in val) }]")

    # Compensation Config
    val = smb_read_block(ser, PMBUS_COMPENSATION_CONFIG, 5)
    print(f"Reading COMPENSATION_CONFIG: [{ ' '.join(f'{b:02X}' for b in val) }]")

    # POWER_STAGE_CONFIG
    val = smb_read_block(ser, PMBUS_POWER_STAGE_CONFIG, 1)[0]
    print(f"Reading POWER_STAGE_CONFIG: {val:02X}")

    # TELEMETRY_CONFIG (6 bytes)
    val = smb_read_block(ser, PMBUS_TELEMETRY_CONFIG, 6)
    print(f"Reading TELEMETRY_CONFIG: [{ ' '.join(f'{b:02X}' for b in val) }]")

    # VOUT_MODE
    val = smb_read_byte(ser, PMBUS_VOUT_MODE)
    print(f"Reading VOUT_MODE: {val:02X}")

    # VOUT voltage settings
    val = smb_read_word(ser, PMBUS_VOUT_COMMAND)
    vout = ulinear16_2_float(val)
    print(f"Reading VOUT_COMMAND: {vout:.2f}V (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_TRIM)
    print(f"Reading VOUT_TRIM: {val:04X}")

    val = smb_read_word(ser, PMBUS_VOUT_MAX)
    vout = ulinear16_2_float(val)
    print(f"Reading VOUT_MAX: {vout:.2f}V (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_MARGIN_HIGH)
    vout = ulinear16_2_float(val)
    print(f"Reading VOUT_MARGIN_HIGH: {vout:.2f} (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_MARGIN_LOW)
    vout = ulinear16_2_float(val)
    print(f"Reading VOUT_MARGIN_LOW: {vout:.2f} (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_TRANSITION_RATE)
    print(f"Reading VOUT_TRANSITION_RATE: {val:04X}")

    val = smb_read_word(ser, PMBUS_VOUT_SCALE_LOOP)
    vout = slinear11_2_float(val)
    print(f"Reading VOUT_SCALE_LOOP: {vout:.3f} (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_MIN)
    vout = ulinear16_2_float(val)
    print(f"Reading VOUT_MIN: {vout:.2f}V (raw: {val:04X})")

    # VIN voltage
    val = smb_read_word(ser, PMBUS_VIN_ON)
    vin = slinear11_2_float(val)
    print(f"Reading VIN_ON: {vin:.2f}V (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VIN_OFF)
    vin = slinear11_2_float(val)
    print(f"Reading VIN_OFF: {vin:.2f}V (raw: {val:04X})")

    # IOUT calibration
    val = smb_read_word(ser, PMBUS_IOUT_CAL_GAIN)
    print(f"Reading IOUT_CAL_GAIN: {val:04X}")

    val = smb_read_word(ser, PMBUS_IOUT_CAL_OFFSET)
    print(f"Reading IOUT_CAL_OFFSET: {val:04X}")

    # VOUT fault/warn limits
    val = smb_read_word(ser, PMBUS_VOUT_OV_FAULT_LIMIT)
    vout = ulinear16_2_float(val)
    print(f"Reading VOUT_OV_FAULT_LIMIT: {vout:.2f} (raw: {val:04X})")

    val = smb_read_byte(ser, PMBUS_VOUT_OV_FAULT_RESPONSE)
    print(f"Reading VOUT_OV_FAULT_RESPONSE: {val:02X}")

    val = smb_read_word(ser, PMBUS_VOUT_OV_WARN_LIMIT)
    vout = ulinear16_2_float(val)
    print(f"Reading VOUT_OV_WARN_LIMIT: {vout:.2f} (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_UV_WARN_LIMIT)
    vout = ulinear16_2_float(val)
    print(f"Reading VOUT_UV_WARN_LIMIT: {vout:.2f} (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_VOUT_UV_FAULT_LIMIT)
    vout = ulinear16_2_float(val)
    print(f"Reading VOUT_UV_FAULT_LIMIT: {vout:.2f} (raw: {val:04X})")

    val = smb_read_byte(ser, PMBUS_VOUT_UV_FAULT_RESPONSE)
    print(f"Reading VOUT_UV_FAULT_RESPONSE: {val:02X}")

    # IOUT current
    val = smb_read_word(ser, PMBUS_IOUT_OC_FAULT_LIMIT)
    iout = slinear11_2_float(val)
    print(f"Reading IOUT_OC_FAULT_LIMIT: {iout:.2f}A (raw: {val:04X})")

    val = smb_read_byte(ser, PMBUS_IOUT_OC_FAULT_RESPONSE)
    print(f"Reading IOUT_OC_FAULT_RESPONSE: {val:02X}")

    val = smb_read_word(ser, PMBUS_IOUT_OC_WARN_LIMIT)
    iout = slinear11_2_float(val)
    print(f"Reading IOUT_OC_WARN_LIMIT: {iout:.2f}A (raw: {val:04X})")

    # Temperature
    val = smb_read_word(ser, PMBUS_OT_FAULT_LIMIT)
    temp = slinear11_2_int(val)
    print(f"Reading OT_FAULT_LIMIT: {temp}°C (raw: {val:04X})")

    val = smb_read_byte(ser, PMBUS_OT_FAULT_RESPONSE)
    print(f"Reading OT_FAULT_RESPONSE: {val:02X}")

    val = smb_read_word(ser, PMBUS_OT_WARN_LIMIT)
    temp = slinear11_2_int(val)
    print(f"Reading OT_WARN_LIMIT: {temp}°C (raw: {val:04X})")

    # VIN OV/UV
    val = smb_read_word(ser, PMBUS_VIN_OV_FAULT_LIMIT)
    vin = slinear11_2_float(val)
    print(f"Reading VIN_OV_FAULT_LIMIT: {vin:.2f}V (raw: {val:04X})")

    val = smb_read_byte(ser, PMBUS_VIN_OV_FAULT_RESPONSE)
    print(f"Reading VIN_OV_FAULT_RESPONSE: {val:02X}")

    val = smb_read_word(ser, PMBUS_VIN_UV_WARN_LIMIT)
    vin = slinear11_2_float(val)
    print(f"Reading VIN_UV_WARN_LIMIT: {vin:.2f}V (raw: {val:04X})")

    # Timing
    val = smb_read_word(ser, PMBUS_TON_DELAY)
    time_val = slinear11_2_int(val)
    print(f"Reading TON_DELAY: {time_val}ms (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_TON_RISE)
    time_val = slinear11_2_int(val)
    print(f"Reading TON_RISE: {time_val}ms (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_TON_MAX_FAULT_LIMIT)
    time_val = slinear11_2_int(val)
    print(f"Reading TON_MAX_FAULT_LIMIT: {time_val}ms (raw: {val:04X})")

    val = smb_read_byte(ser, PMBUS_TON_MAX_FAULT_RESPONSE)
    print(f"Reading TON_MAX_FAULT_RESPONSE: {val:02X}")

    val = smb_read_word(ser, PMBUS_TOFF_DELAY)
    time_val = slinear11_2_int(val)
    print(f"Reading TOFF_DELAY: {time_val}ms (raw: {val:04X})")

    val = smb_read_word(ser, PMBUS_TOFF_FALL)
    time_val = slinear11_2_int(val)
    print(f"Reading TOFF_FALL: {time_val}ms (raw: {val:04X})")

def clear_faults(ser):
    print("Clearing faults...")
    smb_write_addr(ser, PMBUS_CLEAR_FAULTS)

def enable_regulator(ser):
    print("\n-----> Enabling regulator...\n")
    smb_write_byte(ser, PMBUS_OPERATION, OPERATION_ON)


def TPS546_status(ser):
    TPS_STATUS = {}
    # 1) Top-level
    TPS_STATUS["status_word"] = smb_read_word(ser, PMBUS_STATUS_WORD)

    # 2) Details (read unconditionally so we always have a complete picture)
    TPS_STATUS["st_vout"] = smb_read_byte(ser, PMBUS_STATUS_VOUT)

    TPS_STATUS["st_input"] = smb_read_byte(ser, PMBUS_STATUS_INPUT)

    TPS_STATUS["st_iout"] = smb_read_byte(ser, PMBUS_STATUS_IOUT)
    TPS_STATUS["st_iout"] = smb_read_byte(ser, PMBUS_STATUS_IOUT)

    TPS_STATUS["st_temp"] = smb_read_byte(ser, PMBUS_STATUS_TEMPERATURE)

    TPS_STATUS["st_cml"] = smb_read_byte(ser, PMBUS_STATUS_CML)

    TPS_STATUS["st_mfr"] = smb_read_byte(ser, PMBUS_STATUS_MFR_SPECIFIC)

    TPS_STATUS["st_other"] = smb_read_byte(ser, PMBUS_STATUS_OTHER)

    # 3) Context
    TPS_STATUS["operation"] = smb_read_byte(ser, PMBUS_OPERATION)

    TPS_STATUS["on_off_config"] = smb_read_byte(ser, PMBUS_ON_OFF_CONFIG)

    TPS_STATUS["vout_command"] = ulinear16_2_float(smb_read_word(ser, PMBUS_VOUT_COMMAND))

    TPS_STATUS["read_vout"] = ulinear16_2_float(smb_read_word(ser, PMBUS_READ_VOUT))

    TPS_STATUS["read_vin"] = slinear11_2_float(smb_read_word(ser, PMBUS_READ_VIN))

    TPS_STATUS["read_iout"] = slinear11_2_float(smb_read_word(ser, PMBUS_READ_IOUT))

    TPS_STATUS["read_temp1"] = slinear11_2_int(smb_read_word(ser, PMBUS_READ_TEMPERATURE_1))

    print("================ TPS546 SNAPSHOT ================")
    print("STATUS_WORD: 0x%04X" % TPS_STATUS["status_word"])

    # Top-level flags (only print if set)
    if (TPS_STATUS["status_word"] & TPS546_STATUS_BUSY):
        print("  BUSY")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_OFF):
        print("  OFF")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_VOUT_OV):
        print("  VOUT_OV")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_IOUT_OC):
        print("  IOUT_OC")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_VIN_UV):
        print("  VIN_UV")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_TEMP):
        print("  TEMP")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_CML):
        print("  CML")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_PGOOD):
        print("  PGOOD=NOT IN REGULATION")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_OTHER):
        print("  OTHER")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_VOUT):
        print("  VOUT (detail)")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_IOUT):
        print("  IOUT (detail)")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_INPUT):
        print("  INPUT (detail)")
    if (TPS_STATUS["status_word"] & TPS546_STATUS_MFR):
        print("  MFR_SPECIFIC (detail)")

    # Context (always useful)
    print("OPERATION:     0x%02X  (ON bit: %d)" % (TPS_STATUS["operation"], (1 if (TPS_STATUS["operation"] & 0x80) else 0)))
    print("ON_OFF_CONFIG: 0x%02X" % TPS_STATUS["on_off_config"])
    print("VOUT_COMMAND:  %.3f V" % TPS_STATUS["vout_command"])
    print("READ_VOUT:     %.3f V" % TPS_STATUS["read_vout"])
    print("READ_VIN:      %.3f V" % TPS_STATUS["read_vin"])
    print("READ_IOUT:     %.3f A" % TPS_STATUS["read_iout"])
    print("VR_TEMP:       %d C" % TPS_STATUS["read_temp1"])

    # Detail bytes — print only set bits
    if (TPS_STATUS["status_word"] & TPS546_STATUS_VOUT):
        print("STATUS_VOUT: 0x%02X" % TPS_STATUS["st_vout"])
        if (TPS_STATUS["st_vout"] & TPS546_STATUS_VOUT_OVF):
            print("  VOUT_OV_FAULT")
        if (TPS_STATUS["st_vout"] & TPS546_STATUS_VOUT_OVW):
            print("  VOUT_OV_WARN")
        if (TPS_STATUS["st_vout"] & TPS546_STATUS_VOUT_UVW):
            print("  VOUT_UV_WARN")
        if (TPS_STATUS["st_vout"] & TPS546_STATUS_VOUT_UVF):
            print("  VOUT_UV_FAULT")
        if (TPS_STATUS["st_vout"] & TPS546_STATUS_VOUT_MIN_MAX):
            print("  VOUT_MIN_MAX")
        if (TPS_STATUS["st_vout"] & TPS546_STATUS_VOUT_TON_MAX):
            print("  TON_MAX_EXPIRED")


    if (TPS_STATUS["status_word"] & TPS546_STATUS_INPUT):
        print("STATUS_INPUT: 0x%02X" % TPS_STATUS["st_input"])
        if (TPS_STATUS["st_input"] & TPS546_STATUS_VIN_OVF):
            print("  VIN_OV_FAULT")
        if (TPS_STATUS["st_input"] & TPS546_STATUS_VIN_UVW):
            print("  VIN_UV_WARN")
        if (TPS_STATUS["st_input"] & TPS546_STATUS_VIN_LOW_VIN):
            print("  LOW_VIN (live)")

    if (TPS_STATUS["status_word"] & TPS546_STATUS_IOUT):
        print("STATUS_IOUT: 0x%02X" % TPS_STATUS["st_iout"])
        if (TPS_STATUS["st_iout"] & TPS546_STATUS_IOUT_OCF):
            print("  IOUT_OC_FAULT")
        if (TPS_STATUS["st_iout"] & TPS546_STATUS_IOUT_OCW):
            print("  IOUT_OC_WARN")


    if (TPS_STATUS["status_word"] & TPS546_STATUS_TEMP):
        print("STATUS_TEMPERATURE: 0x%02X" % TPS_STATUS["st_temp"])
        if (TPS_STATUS["st_temp"] & TPS546_STATUS_TEMP_OTF):
            print("  OT_FAULT")
        if (TPS_STATUS["st_temp"] & TPS546_STATUS_TEMP_OTW):
            print("  OT_WARN")

    if (TPS_STATUS["status_word"] & TPS546_STATUS_CML):
        print("STATUS_CML: 0x%02X" % TPS_STATUS["st_cml"])
        if (TPS_STATUS["st_cml"] & TPS546_STATUS_CML_IVC):
            print("  INVALID_COMMAND")
        if (TPS_STATUS["st_cml"] & TPS546_STATUS_CML_IVD):
            print("  INVALID_DATA")
        if (TPS_STATUS["st_cml"] & TPS546_STATUS_CML_PEC):
            print("  PEC_ERROR")
        if (TPS_STATUS["st_cml"] & TPS546_STATUS_CML_MEM):
            print("  MEMORY_ERROR")
        if (TPS_STATUS["st_cml"] & TPS546_STATUS_CML_PROC):
            print("  LOGIC_CORE_ERROR")
        if (TPS_STATUS["st_cml"] & TPS546_STATUS_CML_COMM):
            print("  COMM_ERROR")

    if (TPS_STATUS["status_word"] & TPS546_STATUS_MFR):
        print("STATUS_MFR_SPECIFIC: 0x%02X" % TPS_STATUS["st_mfr"])
        if (TPS_STATUS["st_mfr"] & TPS546_STATUS_MFR_POR):
            print("  POR_OCCURRED")
        if (TPS_STATUS["st_mfr"] & TPS546_STATUS_MFR_SELF):
            print("  SELF_CHECK_IN_PROGRESS")
        if (TPS_STATUS["st_mfr"] & TPS546_STATUS_MFR_RESET):
            print("  RESET_VOUT_OCCURRED")
        if (TPS_STATUS["st_mfr"] & TPS546_STATUS_MFR_BCX):
            print("  BCX_FAULT")
        if (TPS_STATUS["st_mfr"] & TPS546_STATUS_MFR_SYNC):
            print("  SYNC_FAULT")

    if (TPS_STATUS["status_word"] & TPS546_STATUS_OTHER):
        print("STATUS_OTHER: 0x%02X" % TPS_STATUS["st_other"])
        if (TPS_STATUS["st_other"] & TPS546_STATUS_OTHER_FIRST):
            print("  FIRST_TO_ASSERT_SMBALERT")

    print("=================================================")
