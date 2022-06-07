#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Raspberry Pi to Arduino I2C Communication
#i2cdetect -y 1
#library
import sys
import smbus2 as smbus#,smbus2
import time
# Slave Addresses
I2C_SLAVE_ADDRESS = 15 #0x0b ou 11
I2C_SLAVE2_ADDRESS = 14
# This function converts a string to an array of bytes.
# def ConvertStringsToBytes(src):
#     converted = []
#     try:  
#         for b in src:
#             converted.append(ord(b))
#         return converted
#     except:
#         converted.append(ord(src))
def main(args):
    # Create the I2C bus
    I2Cbus = smbus.SMBus(1)
    with smbus.SMBus(1) as I2Cbus:
        slaveSelect = 2
        if slaveSelect == 1:
            slaveAddress = I2C_SLAVE_ADDRESS
        elif slaveSelect == 2:
            slaveAddress = I2C_SLAVE2_ADDRESS
        # elif slaveSelect == "3":
        #     slaveAddress = I2C_SLAVE3_ADDRESS
        else:
            # quit if you messed up
            print(slaveSelect== "1")
            print(type(slaveSelect))
            print("no slave selected")
            quit()

        firstObjectHeight = 4366
        firstObjectPos = 1  # destination for first object
        secondObjectHeight = 2201
        secondObjectPos = 2 # pickup for second object

        # firstObjectHeight = 2201
        # firstObjectPos = 2  # destination for first object
        # secondObjectHeight = 4366
        # secondObjectPos = 1 # pickup for second object

        firstObjectHeightBytes = firstObjectHeight.to_bytes(4, byteorder = 'little')
        secondObjectHeightBytes = secondObjectHeight.to_bytes(4, byteorder = 'little')

        print(f"Slave address: {slaveAddress}")
        I2Cbus.write_i2c_block_data(slaveAddress, 0x00, [
            0xaa,
            firstObjectHeightBytes[0], firstObjectHeightBytes[1], firstObjectHeightBytes[2], firstObjectHeightBytes[3],
            firstObjectPos,
            secondObjectHeightBytes[0], secondObjectHeightBytes[1], secondObjectHeightBytes[2], secondObjectHeightBytes[3],
            secondObjectPos,
            0xff
        ])
    return 0
if __name__ == '__main__':
    try:
        main(sys.argv)
    except KeyboardInterrupt:
        print("program was stopped manually")
