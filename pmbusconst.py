# Standard Core PMBus commands */
PMBUS_OPERATION = 0x01
PMBUS_ON_OFF_CONFIG = 0x02
PMBUS_CLEAR_FAULTS = 0x03
PMBUS_PHASE = 0x04
PMBUS_WRITE_PROTECT = 0x10
PMBUS_STORE_USER_ALL = 0x15
PMBUS_RESTORE_USER_ALL = 0x16
PMBUS_CAPABILITY = 0x19
PMBUS_SMBALERT_MASK = 0x1B
PMBUS_VOUT_MODE = 0x20
PMBUS_VOUT_COMMAND = 0x21
PMBUS_VOUT_TRIM = 0x22
PMBUS_VOUT_MAX = 0x24
PMBUS_VOUT_MARGIN_HIGH = 0x25
PMBUS_VOUT_MARGIN_LOW = 0x26
PMBUS_VOUT_TRANSITION_RATE = 0x27
PMBUS_VOUT_SCALE_LOOP = 0x29
PMBUS_VOUT_MIN = 0x2B
PMBUS_FREQUENCY_SWITCH = 0x33
PMBUS_VIN_ON = 0x35
PMBUS_VIN_OFF = 0x36
PMBUS_INTERLEAVE = 0x37
PMBUS_IOUT_CAL_GAIN = 0x38
PMBUS_IOUT_CAL_OFFSET = 0x39
PMBUS_VOUT_OV_FAULT_LIMIT = 0x40
PMBUS_VOUT_OV_FAULT_RESPONSE = 0x41
PMBUS_VOUT_OV_WARN_LIMIT = 0x42
PMBUS_VOUT_UV_WARN_LIMIT = 0x43
PMBUS_VOUT_UV_FAULT_LIMIT = 0x44
PMBUS_VOUT_UV_FAULT_RESPONSE = 0x45
PMBUS_IOUT_OC_FAULT_LIMIT = 0x46
PMBUS_IOUT_OC_FAULT_RESPONSE = 0x47
PMBUS_IOUT_OC_WARN_LIMIT = 0x4A
PMBUS_OT_FAULT_LIMIT = 0x4F
PMBUS_OT_FAULT_RESPONSE = 0x50
PMBUS_OT_WARN_LIMIT = 0x51
PMBUS_VIN_OV_FAULT_LIMIT = 0x55
PMBUS_VIN_OV_FAULT_RESPONSE = 0x56
PMBUS_VIN_UV_WARN_LIMIT = 0x58
PMBUS_TON_DELAY = 0x60
PMBUS_TON_RISE = 0x61
PMBUS_TON_MAX_FAULT_LIMIT = 0x62
PMBUS_TON_MAX_FAULT_RESPONSE = 0x63
PMBUS_TOFF_DELAY = 0x64
PMBUS_TOFF_FALL = 0x65
PMBUS_STATUS_BYTE = 0x78
PMBUS_STATUS_WORD = 0x79
PMBUS_STATUS_VOUT = 0x7A
PMBUS_STATUS_IOUT = 0x7B
PMBUS_STATUS_INPUT = 0x7C
PMBUS_STATUS_TEMPERATURE = 0x7D
PMBUS_STATUS_CML = 0x7E
PMBUS_STATUS_OTHER = 0x7F
PMBUS_STATUS_MFR_SPECIFIC = 0x80
PMBUS_READ_VIN = 0x88
PMBUS_READ_VOUT = 0x8B
PMBUS_READ_IOUT = 0x8C
PMBUS_READ_TEMPERATURE_1 = 0x8D
PMBUS_REVISION = 0x98
PMBUS_MFR_ID = 0x99
PMBUS_MFR_MODEL = 0x9A
PMBUS_MFR_REVISION = 0x9B
PMBUS_MFR_SERIAL = 0x9E
PMBUS_IC_DEVICE_ID = 0xAD
PMBUS_IC_DEVICE_REV = 0xAE
PMBUS_COMPENSATION_CONFIG = 0xB1
PMBUS_POWER_STAGE_CONFIG = 0xB5

# Manufacturer Specific PMBUS commands used by the TPS546D24A */
PMBUS_TELEMETRY_CONFIG = 0xD0
PMBUS_READ_ALL = 0xDA
PMBUS_STATUS_ALL = 0xDB
PMBUS_SYNC_CONFIG = 0xE4
PMBUS_STACK_CONFIG = 0xEC
PMBUS_MISC_OPTIONS = 0xED
PMBUS_PIN_DETECT_OVERRIDE = 0xEE
PMBUS_SLAVE_ADDRESS = 0xEF
PMBUS_NVM_CHECKSUM = 0xF0
PMBUS_SIMULATE_FAULTS = 0xF1
PMBUS_FUSION_ID0 = 0xFC
PMBUS_FUSION_ID1 = 0xFD

# PMBUS_ON_OFF_CONFIG initialization values */
ON_OFF_CONFIG_PU        = 0x10 # Act on CONTROL. (01h) OPERATION command to start/stop power conversion, or both.
ON_OFF_CONFIG_CMD       = 0x08 # Act on (01h) OPERATION Command (and CONTROL pin if configured by CP) to start/stop power conversion.
ON_OFF_CONFIG_CP        = 0x04 # Act on CONTROL pin (and (01h) OPERATION Command if configured by bit [3]) to start/stop power conversion.
ON_OFF_CONFIG_POLARITY  = 0x02 # CONTROL pin has active high polarity.
ON_OFF_CONFIG_DELAY     = 0x01 # When power conversion is commanded OFF by the CONTROL pin (must be configured to respect the CONTROL pin as above), stop power conversion immediately.

## STATUS_WORD Offsets
TPS546_STATUS_VOUT    = 0x8000 #bit 15
TPS546_STATUS_IOUT    = 0x4000
TPS546_STATUS_INPUT   = 0x2000
TPS546_STATUS_MFR     = 0x1000
TPS546_STATUS_PGOOD   = 0x0800
TPS546_STATUS_OTHER   = 0x0200

TPS546_STATUS_BUSY    = 0x0080
TPS546_STATUS_OFF     = 0x0040
TPS546_STATUS_VOUT_OV = 0x0020
TPS546_STATUS_IOUT_OC = 0x0010
TPS546_STATUS_VIN_UV  = 0x0008
TPS546_STATUS_TEMP    = 0x0004
TPS546_STATUS_CML     = 0x0002
TPS546_STATUS_NONE    = 0x0001

# STATUS_VOUT OFFSETS */
TPS546_STATUS_VOUT_OVF     = 0x80 #bit 7 - Latched flag indicating a VOUT OV fault has occurred.
TPS546_STATUS_VOUT_OVW     = 0x40 #bit 6 - Latched flag indicating a VOUT OV warn has occurred.
TPS546_STATUS_VOUT_UVW     = 0x20 #bit 5 - Latched flag indicating a VOUT UV warn has occurred.
TPS546_STATUS_VOUT_UVF     = 0x10 #bit 4 - Latched flag indicating a VOUT UV fault has occurred.
TPS546_STATUS_VOUT_MIN_MAX = 0x08 #bit 3 - Latched flag indicating a VOUT_MIN_MAX has occurred.
TPS546_STATUS_VOUT_TON_MAX = 0x04 #bit 2 - Latched flag indicating a TON_MAX has occurred.

# STATUS_IOUT OFFSETS */
TPS546_STATUS_IOUT_OCF     = 0x80 #bit 7 - Latched flag indicating IOUT OC fault has occurred.
TPS546_STATUS_IOUT_OCW     = 0x20 #bit 5 - Latched flag indicating IOUT OC warn has occurred.

# STATUS_INPUT OFFSETS */
TPS546_STATUS_VIN_OVF      = 0x80 #bit 7 - Latched flag indicating PVIN OV fault has occurred.
TPS546_STATUS_VIN_UVW      = 0x20 #bit 5 - Latched flag indicating PVIN UV warn has occurred.
TPS546_STATUS_VIN_LOW_VIN  = 0x08 #bit 3 - LIVE (unlatched) status bit. PVIN is OFF.

# STATUS_TEMPERATURE OFFSETS */
TPS546_STATUS_TEMP_OTF     = 0x80 #bit 7 - Latched flag indicating OT fault has occurred.
TPS546_STATUS_TEMP_OTW     = 0x40 #bit 6 - Latched flag indicating OT warn has occurred

# STATUS_CML OFFSETS */
TPS546_STATUS_CML_IVC     = 0x80 #bit 7 - Latched flag indicating an invalid or unsupported command was received.
TPS546_STATUS_CML_IVD     = 0x40 #bit 6 - Latched flag indicating an invalid or unsupported data was received.
TPS546_STATUS_CML_PEC     = 0x20 #bit 5 - Latched flag indicating a packet error check has failed.
TPS546_STATUS_CML_MEM     = 0x10 #bit 4 - Latched flag indicating a memory error was detected.
TPS546_STATUS_CML_PROC    = 0x08 #bit 3 - Latched flag indicating a logic core error was detected.
TPS546_STATUS_CML_COMM    = 0x02 #bit 1 - Latched flag indicating communication error detected.

# STATUS_OTHER */
TPS546_STATUS_OTHER_FIRST       = 0x01 #bit 0 - Latched flag indicating that this device was the first to assert SMBALERT.

# STATUS_MFG */
TPS546_STATUS_MFR_POR     = 0x80 #bit 7 - A Power-On Reset Fault has been detected.
TPS546_STATUS_MFR_SELF    = 0x40 #bit 6 - Power-On Self-Check is in progress. One or more BCX slaves have not responded.
TPS546_STATUS_MFR_RESET   = 0x08 #bit 3 - A RESET_VOUT event has occurred.
TPS546_STATUS_MFR_BCX     = 0x04 #bit 2 - A BCX fault event has occurred.
TPS546_STATUS_MFR_SYNC    = 0x02 #bit 1 - A SYNC fault has been detected.