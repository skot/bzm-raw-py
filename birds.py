import time
import bitaxeraw

def ASIC_reset(ser, debug=False):
    if debug:
        print("RESET low: ", end='')
    bitaxeraw.gpio_set(ser, 0xAB, bitaxeraw.GPIO_ASIC_RST, bitaxeraw.GPIO_LOW, debug)
    time.sleep(0.1)
    if debug:
        print("RESET high: ", end='')
    bitaxeraw.gpio_set(ser, 0xAB, bitaxeraw.GPIO_ASIC_RST, bitaxeraw.GPIO_HIGH, debug)
    time.sleep(0.1)

def enable_5V(ser, debug=False):
    if debug:
        print("Enabling 5V power: ", end='')
    bitaxeraw.gpio_set(ser, 0xAB, bitaxeraw.GPIO_5V_EN, bitaxeraw.GPIO_HIGH, debug)
    time.sleep(0.1)