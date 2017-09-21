import numpy as np
import cv2
import serial
from time import sleep
from pynput import keyboard
import imutils

from ObjectRecognition import *
from DecisionMaking import *

def send_decision(ser, command):
    # print("Sending %s" % command)
    if type(command) == str:
        ser.write(bytes(command, 'utf-8'))
    elif type(command) == int:
        ser.write(bytes([command]))
    
    
def run_rodeo(max_time=10000, min_perimeter=15):
    import imutils
    Ser = False
    if Ser == True:
    # Connect to the transmitter
        cname = '/dev/cu.usbmodem14411'
        ser = serial.Serial(cname, 9600)
    
    # Connect to a webcam
    cam = cv2.VideoCapture(0)
    if (cam.isOpened() == False):
        print("Error opening video stream or file")
    
    # Process video
    for curr_time in range(max_time):
        if not cam.isOpened():
            print("Camera is not opened")
            break
        
        ret, rodeo_circles, obstacle_circles, target_circles, image, mask_rl = \
            process_frame(cam, min_perimeter=min_perimeter)
        
        if ret:
            break
        

        command, ang,tar_dist, image2 = make_decision2(rodeo_circles, obstacle_circles, target_circles, image)

        
        aT = [(-10, 10), (10, 35), (-35, -10),(35, 80), (-80, -35),(80, 150),(-150, -80),(150, 185),(-185, -150)]
        instr = [1, 3, 6, 4, 7, 5, 8, 2, 0, 9]
        
        if Ser == True:
            if ang>aT[0][0] and ang<aT[0][1]:
                if tar_dist>100:
                    send_decision(ser, instr[0])
                else:
                    send_decision(ser, instr[-1])
                
            elif ang>aT[1][0] and ang<aT[1][1]:
                send_decision(ser, instr[1])
    
            elif ang>aT[2][0] and ang<aT[2][1]:
                send_decision(ser, instr[2]) 
                
            elif ang>aT[3][0] and ang<aT[3][1]:
                send_decision(ser, instr[3])       
    
            elif ang>aT[4][0] and ang<aT[4][1]:
                send_decision(ser, instr[4]) 
                
            elif ang>aT[5][0] and ang<aT[5][1]:
                send_decision(ser, instr[5])
                
            elif ang>aT[6][0] and ang<aT[6][1]:
                send_decision(ser, instr[6])
                
            elif ang>aT[7][0] and ang<aT[7][1]:
                send_decision(ser, instr[7])
                
            elif ang>aT[8][0] and ang<aT[8][1]:
                send_decision(ser, instr[8])

            elif ang>190:
                send_decision(ser, instr[9])
            sleep(0.2)
            
        cv2.imshow('Frame', image2)
               
    cam.release()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    run_rodeo(max_time=1000, min_perimeter=30)
    

