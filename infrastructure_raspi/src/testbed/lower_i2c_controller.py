from time import sleep
import smbus2 as smbus

# Author: Ryan Roberts
#
# lowerController() is used as the master controller for i2c communication with slave
# device for the lower reset of the grasping reset mechanism.

class lowerController():
    def __init__(self, bus):
        """
        initializes lowerController object for interacting with arduino slave device for lower reset
        
        Parameters:
            bus: smbus2 object that represents shared i2c bus for grasping reset mechanism
        """
        self.__I2c_bus = bus
        self.__addr = 15 # 0x0f = 15
        self.__ls_mode = 3 # limit switch mode
        self.__cb_mode = 4 # cone button mode
        self.__he_mode = 5 # hall effect mode
        self.__count_mode = 6 # counting mode
        self.__default_mode = 7 # default mode + reset counter
    
    def __send_transmission(self,val):
        """
        sends i2c write message with 1 data frame to device at specified address
        
        Parameters:
            val: byte to be sent to slave device in data frame
        
        Returns:
            none
        """
        sleep(0.01)
        self.__I2c_bus.write_byte(self.__addr, val)
    
    def get_data(self):
        """
        sends i2c read message  to device at specified address.
        requests to read 2 data frames.

        Parameters:
            none
        
        Returns:
            integer value of data received from message
        """
        sleep(0.01)
        # using i2c_msg object to use it's rdwr command to be able to read multiple data frames. 
        # smbus2 read block commands do not work without specifying a register, which we can't do here.
        msg = smbus.i2c_msg.read(self.__addr, 2) 
        self.__I2c_bus.i2c_rdwr(msg)
        raw_list = list(msg)
        val = (raw_list[0] << 8) + raw_list[1]
        return val
    
    def limit_switch_mode(self):
        """
        sets arduino into limit switch mode

        Parameters:
            none 
        
        Returns:
            none
        """
        self.__send_transmission(self.__ls_mode)

    def cone_button_mode(self):
        """
        sets arduino into cone button mode

        Parameters:
            none 
        
        Returns:
            none
        """
        self.__send_transmission(self.__cb_mode)
    
    def hall_effect_mode(self):
        """
        sets arduino into hall effect mode

        Parameters:
            none 
        
        Returns:
            none
        """
        self.__send_transmission(self.__he_mode)
    
    def start_counting(self):
        """
        sets arduino into counting mode and starts encoder

        Parameters:
            none 
        
        Returns:
            none
        """
        self.__send_transmission(self.__count_mode)
    
    def stop_counting(self):
        """
        sets arduino into cone default mode and resets encoder

        Parameters:
            none 
        
        Returns:
            none
        """
        self.__send_transmission(self.__default_mode)