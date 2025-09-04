#include <stdint.h>

#define PMBUS_VOUT_MODE 0

/**
 * @brief Convert an SLINEAR11 value into an int
 * @param value The SLINEAR11 value to convert
 */
static int slinear11_2_int(uint16_t value)
{
    int exponent, mantissa;
    float result;

    // First 5 bits is exponent in twos-complement
    // check the first bit of the exponent to see if its negative
    if (value & 0x8000) {
        // exponent is negative
        exponent = -1 * (((~value >> 11) & 0x001F) + 1);
    } else {
        exponent = (value >> 11);
    }
    // last 11 bits is the mantissa in twos-complement
    // check the first bit of the mantissa to see if its negative
    if (value & 0x400) {
        // mantissa is negative
        mantissa = -1 * ((~value & 0x03FF) + 1);
    } else {
        mantissa = (value & 0x03FF);
    }

    // calculate result (mantissa * 2^exponent)
    result = mantissa * powf(2.0, exponent);
    return (int)result;
}

/**
 * @brief Convert an SLINEAR11 value into an int
 * @param value The SLINEAR11 value to convert
 */
static float slinear11_2_float(uint16_t value)
{
    int exponent, mantissa;
    float result;

    // First 5 bits is exponent in twos-complement
    // check the first bit of the exponent to see if its negative
    if (value & 0x8000) {
        // exponent is negative
        exponent = -1 * (((~value >> 11) & 0x001F) + 1);
    } else {
        exponent = (value >> 11);
    }
    // last 11 bits is the mantissa in twos-complement
    // check the first bit of the mantissa to see if its negative
    if (value & 0x400) {
        // mantissa is negative
        mantissa = -1 * ((~value & 0x03FF) + 1);
    } else {
        mantissa = (value & 0x03FF);
    }

    // calculate result (mantissa * 2^exponent)
    result = mantissa * powf(2.0, exponent);
    return result;
}

/**
 * @brief Convert an int value into an SLINEAR11
 * @param value The int value to convert
 */
static uint16_t int_2_slinear11(int value)
{
    int mantissa;
    int exponent = 0;
    uint16_t result = 0;
    int i;

    // First see if the exponent is positive or negative
    if (value >= 0) {
        // exponent is positive
        for (i=0; i<=15; i++) {
            mantissa = value / powf(2.0, i);
            if (mantissa < 1024) {
                exponent = i;
                break;
            }
        }
        if (i == 16) {
            printf("Could not find a solution");
            return 0;
        }
    } else {
        // value is negative
        printf("No negative numbers at this time");
        return 0;
    }

    result = ((exponent << 11) & 0xF800) + mantissa;

    return result;
}

/**
 * @brief Convert a float value into an SLINEAR11
 * @param value The float value to convert
 */
static uint16_t float_2_slinear11(float value)
{
    int mantissa;
    int exponent = 0;
    uint16_t result = 0;
    int i;

    // First see if the exponent is positive or negative
    if (value > 0) {
        // exponent is negative
        for (i=0; i<=15; i++) {
            mantissa = value * powf(2.0, i);
            if (mantissa >= 1024) {
                exponent = i-1;
                mantissa = value * powf(2.0, exponent);
                break;
            }
        }
        if (i == 16) {
            printf("Could not find a solution");
            return 0;
        }
    } else {
        // value is negative
        printf("No negative numbers at this time");
        return 0;
    }

    result = (( (~exponent + 1) << 11) & 0xF800) + mantissa;

    return result;
}

/**
 * @brief Convert a ULINEAR16 value into a float
 * the exponent comes from the VOUT_MODE bits[4..0]
 * stored in twos-complement
 * The mantissa occupies the full 16-bits of the value
 * @param value The ULINEAR16 value to convert
 */
static float ulinear16_2_float(uint16_t value)
{
    uint8_t voutmode;
    int exponent;
    float result;

    smb_read_byte(PMBUS_VOUT_MODE, &voutmode);

    if (voutmode & 0x10) {
        // exponent is negative
        exponent = -1 * ((~voutmode & 0x1F) + 1);
    } else {
        exponent = (voutmode & 0x1F);
    }
    result = (value * powf(2.0, exponent));
    return result;
}

/**
 * @brief Convert a float value into a ULINEAR16
 * the exponent comes from the VOUT_MODE bits[4..0]
 * stored in twos-complement
 * The mantissa occupies the full 16-bits of the result
 * @param value The float value to convert
*/
static uint16_t float_2_ulinear16(float value)
{
    uint8_t voutmode;
    float exponent;
    uint16_t result;

    smb_read_byte(PMBUS_VOUT_MODE, &voutmode);
    if (voutmode & 0x10) {
        // exponent is negative
        exponent = -1 * ((~voutmode & 0x1F) + 1);
    } else {
        exponent = (voutmode & 0x1F);
    }

    result = (value / powf(2.0, exponent));

    return result;
}