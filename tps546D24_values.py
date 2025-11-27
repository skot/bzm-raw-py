TPS546_CONFIG_BIRDS = {
    "ON_OFF_CONFIG": None,
    "PHASE": 0xFF, # Phase addressing - 0xFF is all phases as single entity
    "CAPABILITY": 0xD0,
    "SMBALERT_MASK": [0x0200, 0x1800, 0xE800, 0x0000, 0x0000, 0x0100, 0x4200], #Vout, Iout, Input, Temp, CML, Other, MFR_SPECIFIC

    "FREQUENCY_SWITCH": 325, #kHz

    "SYNC_CONFIG": 0x00, # Enable Auto Detect SYNC
    "STACK_CONFIG": 0x0000, # 1 module
    "INTERLEAVE": 0x0010, # GROUPID = 0, NUM_GROUP = 1, ORDER = 0. Sets phase Position to 0º
    "MISC_OPTIONS": 0x0000,
    "PIN_DETECT_OVERRIDE": 0x0000, #use NVM values
    "DEVICE_ADDRESS": 0x24,

    "MFR_ID": [0x00, 0x00, 0x00],
    "MFR_MODEL": [0x00, 0x00, 0x00],
    "MFR_REVISION": [0x00, 0x00, 0x00],
    "MFR_SERIAL": [0x00, 0x00, 0x00],

    "COMPENSATION_CONFIG": [0x13, 0x11, 0x8C, 0x1D, 0x06], # calculated with TPS546x24A_Compensation_Pinstrap_Calculator_Release20200120.xlsx
    "POWER_STAGE_CONFIG": 0x70,
    "TELEMETRY_CONFIG": [0x03, 0x03, 0x03, 0x03, 0x03, 0x00],
    
    "VOUT_MODE": None,
    "VOUT_COMMAND": 2.8, #ULINEAR16
    "VOUT_TRIM": 0x0000, 
    "VOUT_MAX": 3.5, #ULINEAR16
    "VOUT_MARGIN_HIGH": 1.1, # %/100 above VOUT
    "VOUT_MARGIN_LOW": 0.90, # %/100 below VOUT
    "VOUT_TRANSITION_RATE": 0xE010,
    "VOUT_SCALE_LOOP": 0.125,
    "VOUT_MIN": 2.1,
    
    "VIN_ON": 11.0,
    "VIN_OFF": 10.5,
    
    "IOUT_CAL_GAIN": 0xC880,
    "IOUT_CAL_OFFSET": 0xE000,
    
    "VOUT_OV_FAULT_LIMIT": 1.25, # % above VOUT_COMMAND
    "VOUT_OV_FAULT_RESPONSE": 0xBD,
    "VOUT_OV_WARN_LIMIT": 1.16, # % above VOUT_COMMAND
    "VOUT_UV_WARN_LIMIT": 0.90, # % below VOUT_COMMAND
    "VOUT_UV_FAULT_LIMIT": 0.75, # % below VOUT_COMMAND
    "VOUT_UV_FAULT_RESPONSE": 0xBE, #TODO
    
    "IOUT_OC_FAULT_LIMIT": 55.00, # A
    "IOUT_OC_FAULT_RESPONSE": 0xC0, #TODO
    "IOUT_OC_WARN_LIMIT": 50.00, # A
    
    "OT_FAULT_LIMIT": 145, # degrees C
    "OT_FAULT_RESPONSE": 0xFF, #TODO
    "OT_WARN_LIMIT": 105, # degrees C
    
    "VIN_OV_FAULT_LIMIT": 14.0,
    "VIN_OV_FAULT_RESPONSE": 0xB7, #TODO
    "VIN_UV_WARN_LIMIT": 11.0,
    
    "TON_DELAY": 0,
    "TON_RISE": 3,
    "TON_MAX_FAULT_LIMIT": 0,
    "TON_MAX_FAULT_RESPONSE": 0x3B, #TODO
    "TOFF_DELAY": 0,
    "TOFF_FALL": 0,
}

## these need to be converted into the complete format like BIRDS above
# TPS546_CONFIG_BONANZA = {
#     # vin voltage
#     "VIN_ON": 11.0,
#     "VIN_OFF": 10.5,
#     "VIN_UV_WARN_LIMIT": 11.0,
#     "VIN_OV_FAULT_LIMIT": 14.0,
#     # vout voltage
#     "SCALE_LOOP": 0.25,
#     "VOUT_MIN": 2.1,
#     "VOUT_MAX": 3.5,
#     "VOUT_COMMAND": 2.8,
#     # iout current
#     "IOUT_OC_WARN_LIMIT": 50.00, # A
#     "IOUT_OC_FAULT_LIMIT": 55.00, # A
#     # config
#     "STACK_CONFIG": 0x0001, # 2 modules
#     "SYNC_CONFIG": 0xF0, # Enable Auto Detect SYNC
#     "CMD_PHASE": 0xFF, # Phase addressing - 0xFF is all phases as single entity
#     "COMPENSATION_CONFIG": [0x12, 0x20, 0x42, 0x24, 0x42], # Default compensation config
#     "FREQUENCY": 1500,
#     "PIN_DETECT_OVERRIDE": 0x0000 #use NVM values
# }

# TPS546_CONFIG_EVM = {
#     # vin voltage
#     "VIN_ON": 11.0,
#     "VIN_OFF": 10.5,
#     "VIN_UV_WARN_LIMIT": 11.0,
#     "VIN_OV_FAULT_LIMIT": 14.0,
#     # vout voltage
#     "SCALE_LOOP": 0.25,
#     "VOUT_MIN": 2.1,
#     "VOUT_MAX": 3.5,
#     "VOUT_COMMAND": 2.8,
#     # iout current
#     "IOUT_OC_WARN_LIMIT": 50.00, # A
#     "IOUT_OC_FAULT_LIMIT": 55.00, # A
#     # config
#     "STACK_CONFIG": 0x0001, # 2 modules
#     "SYNC_CONFIG": 0xD0, # Enable Auto Detect SYNC
#     "CMD_PHASE": 0xFF, # Phase addressing - 0xFF is all phases as single entity
#     "COMPENSATION_CONFIG": [0x12, 0x70, 0x42, 0x10, 0x48], # Default compensation config
#     "FREQUENCY": 650,
#     "PIN_DETECT_OVERRIDE": 0x0000 #use NVM values
# }