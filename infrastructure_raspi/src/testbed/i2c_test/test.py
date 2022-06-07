import smbus2 as smbus
import struct
from time import sleep

with smbus.SMBus(1) as I2Cbus:
    addr = 14 # bus address

    firstObjectHeight = 4366
    firstObjectPos = 0  # destination for first object
    secondObjectHeight = 2201
    secondObjectPos = 1  # pickup for second object

    firstObjectHeightBytes = list(bytearray(struct.pack('<L', firstObjectHeight)))
    secondObjectHeightBytes = list(bytearray(struct.pack('<L', secondObjectHeight)))

    print("firstObjectHeightBytes:", firstObjectHeightBytes)
    
    I2Cbus.write_i2c_block_data(addr, 0x00, [
        0xaa,
        firstObjectHeightBytes[0], firstObjectHeightBytes[1], firstObjectHeightBytes[2], firstObjectHeightBytes[3],
        firstObjectPos,
        secondObjectHeightBytes[0], secondObjectHeightBytes[1], secondObjectHeightBytes[2], secondObjectHeightBytes[3],
        secondObjectPos,
        0xff
    ])

    # while True:
    #     sleep(1)
    # msg = I2Cbus.read_byte_data(addr, 0)
    # print("Data:", hex(msg))
    # if(msg == 0xF0):
    #     break