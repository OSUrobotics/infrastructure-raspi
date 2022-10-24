import smbus2 as smbus
import struct
from time import sleep

with smbus.SMBus(1) as I2Cbus:
    addr = 15 # bus address

    # while True:
    #     sleep(1)
    # I2Cbus.write_byte(addr, 3)

    I2Cbus.write_byte(addr, 7)

    while True:
        sleep(1)
        try:
            msg = I2Cbus.read_byte_data(addr, 6)
            print("Data:", hex(msg))
        except:
            print("i2c read error") # sometimes the read_byte_data fails, so catch it instead of crashing program

    # msg = smbus.i2c_msg.read(addr, 3) 
    # I2Cbus.i2c_rdwr(msg)
    # raw_list = list(msg)
    # val = (raw_list[0] << 8) + raw_list[1]
    # print(val)