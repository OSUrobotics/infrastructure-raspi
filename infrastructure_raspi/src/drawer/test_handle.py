from drawer import Drawer
import RPi.GPIO as gpio
from time import sleep

#init
drawer = Drawer()
try:
    while True:
        print(drawer.read_handle())
        sleep(.5)
except:
    gpio.cleanup()