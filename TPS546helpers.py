import math

VOUTMODE = 0x97

def slinear11_2_int(value):
    """Convert an SLINEAR11 value into an int"""
    # First 5 bits is exponent in twos-complement
    if value & 0x8000:
        # exponent is negative
        exponent = -1 * (((~value >> 11) & 0x1F) + 1)
    else:
        exponent = (value >> 11)
    # last 11 bits is the mantissa in twos-complement
    if value & 0x400:
        # mantissa is negative
        mantissa = -1 * ((~value & 0x3FF) + 1)
    else:
        mantissa = (value & 0x3FF)
    result = mantissa * math.pow(2.0, exponent)
    return int(result)

def slinear11_2_float(value):
    """Convert an SLINEAR11 value into a float"""
    # First 5 bits is exponent in twos-complement
    if value & 0x8000:
        # exponent is negative
        exponent = -1 * (((~value >> 11) & 0x1F) + 1)
    else:
        exponent = (value >> 11)
    # last 11 bits is the mantissa in twos-complement
    if value & 0x400:
        # mantissa is negative
        mantissa = -1 * ((~value & 0x3FF) + 1)
    else:
        mantissa = (value & 0x3FF)
    result = mantissa * math.pow(2.0, exponent)
    return float(result)

def int_2_slinear11(value):
    """Convert an int value into an SLINEAR11"""
    exponent = 0
    mantissa = 0
    # First see if the exponent is positive or negative
    if value >= 0:
        for i in range(16):
            mantissa = value / math.pow(2.0, i)
            if mantissa < 1024:
                exponent = i
                break
        else:  # no break occurred
            print("Could not find a solution")
            return 0
    else:
        print("No negative numbers at this time")
        return 0
    result = ((exponent << 11) & 0xF800) + int(mantissa)
    return result

def float_2_slinear11(value):
    """Convert a float value into an SLINEAR11"""
    exponent = 0
    mantissa = 0
    # First see if the exponent is positive or negative
    if value > 0:
        for i in range(16):
            mantissa = value * math.pow(2.0, i)
            if mantissa >= 1024:
                exponent = i - 1
                mantissa = value * math.pow(2.0, exponent)
                break
        else:  # no break occurred
            print("Could not find a solution")
            return 0
    else:
        print("No negative numbers at this time")
        return 0
    result = ((~exponent + 1) << 11 & 0xF800) + int(mantissa)
    return result

def ulinear16_2_float(value):
    """Convert a ULINEAR16 value into a float
    The exponent comes from the VOUT_MODE bits[4..0] stored in twos-complement
    The mantissa occupies the full 16-bits of the value"""

    if VOUTMODE & 0x10:
        # exponent is negative
        exponent = -1 * ((~VOUTMODE & 0x1F) + 1)
    else:
        exponent = (VOUTMODE & 0x1F)
    result = value * math.pow(2.0, exponent)
    return float(result)

def float_2_ulinear16(value):
    """Convert a float value into a ULINEAR16
    The exponent comes from the VOUT_MODE bits[4..0] stored in twos-complement
    The mantissa occupies the full 16-bits of the result"""

    if VOUTMODE & 0x10:
        # exponent is negative
        exponent = -1 * ((~VOUTMODE & 0x1F) + 1)
    else:
        exponent = (VOUTMODE & 0x1F)
    result = value / math.pow(2.0, exponent)
    return int(result)