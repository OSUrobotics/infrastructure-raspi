#!/usr/bin/env python
#
# Author: Ryan Roberts
#
# General class for interfacing with the AS5047P rotary sensor.
# Currently only has read functionalities for each register.
# 
# TODO:
# add write capabilities for non-volatile registers (PROG)

import spidev
from time import sleep


class AS5047P:
    #read command frames for each register
    __NOP_RCF = [0,0]
    __ERRFL_RCF = [0b01000000, 0b00000001]
    __PROG_RCF = [0b11000000, 0b00000011]
    __DIAAGC_RCF = [0b11111111, 0b11111100]
    __MAG_RCF = [0b01111111, 0b11111101]
    __ANGLEUNC_RCF = [0b01111111, 0b11111110]
    __ANGLECOM_RCF = [0b11111111, 0b11111111]

    def __init__(self, bus, device, speed):
        self.dev = spidev.SpiDev()
        self.dev.open(bus, device)
        self.dev.max_speed_hz = speed
        self.dev.mode = 0b01
        self.error_flag = 0
        self.latest_err_msg = 0
    
    def __read_reg(self, reg_rcf):
        self.dev.xfer2(reg_rcf)
        sleep(0.00002)
        res = self.dev.xfer2(tuple(self.__NOP_RCF))
        self.error_flag = (res[0] & 0b01000000) >> 6
        raw_data = ((res[0] & 0b00111111) << 8) + res[1]
        return raw_data
    
    def get_error(self):
        res = self.__read_reg(tuple(self.__ERRFL_RCF))
        self.latest_err_msg = res & 7
        return self.latest_err_msg
    
    def get_diagnostics(self):
        #returns dict of all diagnostic features for the rotary sensor.
        #see chip documentation for more
        res = self.__read_reg(tuple(self.__DIAAGC_RCF))
        if(self.error_flag):
            self.get_error()
        diagnostics = {
            "MAGL" : (res & 2048) >> 11,
            "MAGH" : (res & 1024) >> 10,
            "COF" : (res & 512) >> 9,
            "LF" : (res & 256) >> 8,
            "AGC" : (res & 255)
        }
        return diagnostics
        
    def get_CORDIC_mag(self):
        #returns magnitude of CORDIC value
        res = self.__read_reg(tuple(self.__MAG_RCF))
        if(self.error_flag):
            self.get_error()
        return res
        
    def print_latest_err_msg(self):
        print("Raw Error Message: {}".format(self.latest_err_msg))
        print("Meaning:")
        if(self.latest_err_msg == 0):
            print(" - There is no error detected in ERRFL register")
        else:
            if(self.latest_err_msg & 0b001):
                print(" - Framing error: a non-compliant SPI frame is detected")
            if(self.latest_err_msg & 0b010):
                print(" - Invalid command error: reading or writing an invalid register address")
            if(self.latest_err_msg & 0b100):
                print(" - Parity error: There must be an even number of 1's and 0's in command frame")
    
    def get_angle(self, comp = True):
        cf = [0,0]
        if(comp):
            cf = self.__ANGLECOM_RCF
        else:
            cf = self.__ANGLEUNC_RCF
        raw_angle = self.__read_reg(tuple(cf))
        if(self.error_flag):
            self.get_error()
        angle = (float(raw_angle)/16384)*360
        return round(angle,1)
    
    def __del__(self):
        self.dev.close()

#test code for class
if __name__ == "__main__":
    test = AS5047P(0,0,1000000)
    print(test.get_diagnostics())
    print("CORDIC MAG: {}".format(test.get_CORDIC_mag()))
    try:
        start_pos = test.get_angle()
        while(not test.error_flag):
            print(start_pos - test.get_angle())
        test.print_latest_err_msg()
    except:
        pass