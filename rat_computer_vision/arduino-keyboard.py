"""
Gets keyboard signals with pynput and send them with pyserial
"""
from time import sleep
import serial
from pynput import keyboard

ser = serial.Serial('COM9', 115200)

def on_press(key):
    try:
        # ser.write(b'{0}'.format(key)[1]) # should be more effecient
        if 'w' == '{0}'.format(key)[1]:
            ser.write(bytes([1]))
            #sleep(0.00001)        
        elif 'a' == '{0}'.format(key)[1]:
            ser.write(bytes([3]))
            #sleep(0.00001)
        elif 's' == '{0}'.format(key)[1]:
            ser.write(bytes([2]))
            #sleep(0.00001)
        elif 'd' == '{0}'.format(key)[1]:
            ser.write(bytes([6]))
            #sleep(0.00001)  
        elif 'c' == '{0}'.format(key)[1]:
            ser.write(bytes([0]))
            sleep(0.0001)
    except AttributeError:
        print('special key {0} pressed'.format(key))

def on_release(key):
#     print('{0} released'.format(key))
    if key == keyboard.Key.esc:
        # Stop listener
        return False

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()
    
ser.close()
