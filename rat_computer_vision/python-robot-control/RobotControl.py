import numpy as np
import cv2
import serial
from time import sleep
from pynput import keyboard

from ObjectRecognition import *
from DecisionMaking import *

def send_decision(ser, command):
    # print("Sending %s" % command)
    if type(command) == str:
        ser.write(bytes(command, 'utf-8'))
    elif type(command) == int:
        ser.write(bytes([command]))
    
def run_rodeo(max_time=1000, min_perimeter=15):
    # Connect to the transmitter
    ser = serial.Serial('COM9', 9600)
    
    # Connect to a webcam
    cam = cv2.VideoCapture(0)
    if (cam.isOpened() == False):
        print("Error opening video stream or file")
    
    # Process video
    for curr_time in range(max_time):
        if not cam.isOpened():
            print("Camera is not opened")
            break
            
        ret, rodeo_circles, obstacle_circles = \
            process_frame(cam, min_perimeter=min_perimeter)
        
        if ret:
            break
        
        command = make_decision(rodeo_circles, obstacle_circles)

        # A temporary thing for flexible speed
        
        if command == 'w':
            command = 1
        elif command == 'c':
            command = 0
        elif command == 's':
            command = 2
        elif command == 'a':
            command = 3
        elif command == 'd':
            command = 6

        send_decision(ser, command)
        
    cam.release()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    run_rodeo(max_time=1000, min_perimeter=30)
    

