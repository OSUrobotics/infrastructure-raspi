from time import time, sleep
import RPi.GPIO as gpio
import sys
import smbus2 as smbus#,smbus2

class testbed_test():
    def __init__(self):
        
        # Slave Addresses
        self.I2C_SLAVE_ADDRESS = 15 #0x0b ou 11
        self.I2C_SLAVE2_ADDRESS = 14
        # self.button_pin = 24
        self.button_pin = 14

        self.motor_pwm = 4 # pin 7
        self.motor_in1 = 21 # pin 
        self.motor_in2 = 27 # pin 
        self.motor_en = 13

        # self.hall_effect_pin = 
        self.hall_effect_pin = 23
        gpio.setwarnings(False)
        gpio.setmode(gpio.BCM)
        
        gpio.setup(self.button_pin, gpio.IN, pull_up_down = gpio.PUD_DOWN)
        gpio.setup(self.motor_pwm, gpio.OUT)
        gpio.setup(self.motor_in1, gpio.OUT)
        gpio.setup(self.motor_in2, gpio.OUT)
        gpio.setup(self.motor_en, gpio.OUT)

        gpio.output(self.motor_en, gpio.HIGH)
        gpio.output(self.motor_in1, gpio.LOW)
        gpio.output(self.motor_in2, gpio.LOW)
        self.p = gpio.PWM(self.motor_pwm, 1000)
        self.p.start(75)
        
        gpio.setup(self.hall_effect_pin, gpio.IN, pull_up_down= gpio.PUD_DOWN)

    def ConvertStringsToBytes(self, src):
        self.converted = []
        try:  
            for b in src:
                self.converted.append(ord(b))
            return self.converted
        except:
            self.converted.append(ord(src))
            return self.converted

    def button_test(self):
        i = 0
        while True:
            
            if gpio.input(self.button_pin) == gpio.HIGH:
                print("{} button was pressed!!!!!!!!!!!".format(i))
                i += 1
            # sleep(.01)

    def motor(self, duration=None):
        gpio.output(self.motor_in1, gpio.LOW)
        gpio.output(self.motor_in2, gpio.HIGH)
        if duration == None:

            while True:
                
                # gpio.output(self.motor_in1, gpio.LOW)
                # gpio.output(self.motor_in2, gpio.HIGH)

                sleep(1)
        else:
            gpio.output(self.motor_in1, gpio.LOW)
            gpio.output(self.motor_in2, gpio.HIGH)
            sleep(duration)

            gpio.output(self.motor_in1, gpio.LOW)
            gpio.output(self.motor_in2, gpio.LOW)
            gpio.cleanup()
    
    def motor_with_encoder(self):
        pass

    def talk_with_arduino(self, angle=360):

        self.I2Cbus = smbus.SMBus(1)
        with smbus.SMBus(1) as I2Cbus:
            
            sleep(0.001)
            while True:
                try:
                    sleep(0.1)
                    self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [2])
                    sleep(0.1)
                    self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [2])
                    sleep(0.1)
                    break
                except:
                    sleep(.5)
                    self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [2])
                    sleep(.5)
            while True:
                try:
                    self.I2Cbus.read_byte_data(self.I2C_SLAVE_ADDRESS,1)
                    break
                except:
                    print("remote i/o error")
                    sleep(.1)
            while True:
                try:
                    sleep(0.1)
                    self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [6])
                    sleep(0.1)
                    break
                except:
                    sleep(.5)
                    self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [6])
                    sleep(.5)
            while True:
                try:                    
                    first_byte =self.I2Cbus.read_byte_data(self.I2C_SLAVE_ADDRESS,1)
                    sleep(.01)
                    second_byte =self.I2Cbus.read_byte_data(self.I2C_SLAVE_ADDRESS,1)
                    encoder_value = (first_byte<< 8) + (second_byte)
                    print("recieve from slave:")
                    print(encoder_value)
                    sleep(.01)
                    if encoder_value >= angle:
                        break
                except:
                    print("remote i/o error")
                    while True:
                        try:
                            sleep(0.1)
                            self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [8])
                            sleep(0.1)
                            break
                        except:
                            sleep(.5)
                            self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [8])
                            sleep(.5)
                    while True:
                        try:
                            self.I2Cbus.read_byte_data(self.I2C_SLAVE_ADDRESS,1)
                            break
                        except:
                            print("remote i/o error")
                            sleep(.1)
                    while True:
                        try:
                            sleep(0.1)
                            self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [6])
                            sleep(0.1)
                            break
                        except:
                            sleep(.5)
                            self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [6])
                            sleep(.5)
                    sleep(.1)
            while True:
                try:
                    sleep(0.1)
                    self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [7])
                    sleep(0.1)
                    break
                except:
                    sleep(.5)
                    self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [7])
                    sleep(.5)
            while True:
                try:
                    self.I2Cbus.read_byte_data(self.I2C_SLAVE_ADDRESS,1)
                    break
                except:
                    print("remote i/o error")
                    sleep(.1)
            
        return 0

    def hall_effect(self):
        counter = 0

        while True:
            if gpio.input(self.hall_effect_pin) == False:
                print("{}  magnet is detected".format(counter))
                counter += 1
            # print(gpio.input(self.hall_effect_pin))

            sleep(.01)
    
    def hall_effect_arduino(self):
        self.I2Cbus = smbus.SMBus(1)
        with smbus.SMBus(1) as I2Cbus:
            sleep(0.001)
            # self.BytesToSend = self.ConvertStringsToBytes("5")
            while True:
                    try:
                        sleep(0.05)
                        self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [5])
                        break
                    except:
                        sleep(.2)
                        self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [5])

            while True:
                # while True:
                #     try:
                #         sleep(0.01)
                #         self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [5])
                #         break
                #     except:
                #         sleep(.02)
                #         self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [5])
                try:
                    data=self.I2Cbus.read_byte_data(self.I2C_SLAVE_ADDRESS,1)
                    print("recieve from slave:")
                    print(data)
                    sleep(.05)
                except:
                    print("remote i/o error")
                    sleep(.1)
        return 0

    def button_arduino(self):
        self.I2Cbus = smbus.SMBus(1)
        with smbus.SMBus(1) as I2Cbus:
            sleep(0.001)
            # self.BytesToSend = self.ConvertStringsToBytes("5")
            while True:
                try:
                    sleep(0.05)
                    self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [4])
                    sleep(0.01)
                    break
                except:
                    sleep(.02)
                    self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [4])
                    sleep(.02)

            while True:
                try:
                    sleep(0.05)
                    data=self.I2Cbus.read_byte_data(self.I2C_SLAVE_ADDRESS,1)
                    print("recieve from slave:")
                    print(data)
                    sleep(.01)
                except:
                    print("remote i/o error")
                    sleep(.01)
        return 0

    def limit_switch_aduino(self):
        self.I2Cbus = smbus.SMBus(1)
        with smbus.SMBus(1) as I2Cbus:
            sleep(0.001)
            # self.BytesToSend = self.ConvertStringsToBytes("5")
            while True:
                try:
                    sleep(0.05)
                    self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [3])
                    break
                except:
                    sleep(.2)
                    self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [3])
                    sleep(.2)

            while True:
                # while True:
                    # try:
                    #     sleep(0.01)
                    #     self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [3])
                    #     break
                    # except:
                    #     sleep(.02)
                    #     self.I2Cbus.write_i2c_block_data(self.I2C_SLAVE_ADDRESS, 0x00, [3])
                    #     sleep(.02)
                try:
                    sleep(0.05)
                    data=self.I2Cbus.read_byte_data(self.I2C_SLAVE_ADDRESS,1)
                    print("recieve from slave:")
                    print(data)
                except:
                    print("remote i/o error")
                    sleep(.01)
        return 0
def on_exit(sig, func=None):
        gpio.cleanup()

if __name__ == '__main__':
    gpio.cleanup()
        

    test_num = input("""
    1) button
    2) motor
    3) motor and encoder
    4) stepper motor
    5) Arduino Communication
    6) hall effect sensor
    7) hall effect arduino
    8) button with arduino
    9) limit switch arduino

    What do you want to test? (enter the number)
    """)


    test = testbed_test()

    if test_num == 1:

        test.button_test()

    elif test_num == 5:
        test.talk_with_arduino()
    elif test_num == 6:
        test.hall_effect()
    
    elif test_num == 7:
        test.hall_effect_arduino()

    elif test_num == 8:
        test.button_arduino()
    
    elif test_num == 9:
        test.limit_switch_aduino()
        
    elif test_num == 2:
        
        # try:
        #     duration = input("how long to run motors? \n(Enter None if you want to run indefently)\n")
        # except SyntaxError:
        # if len(duration) == None:
            # print("true")

        # test.motor(duration=duration)
        test.motor()
    else:
        print("not implemented yet")
