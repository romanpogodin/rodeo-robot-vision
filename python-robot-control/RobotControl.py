import numpy as np
import cv2
import serial
from time import sleep
from pynput import keyboard
import imutils

from ObjectRecognition import *
from DecisionMaking import *
#from ReinforcementLearning import *
def send_decision(ser, command):
    # print("Sending %s" % command)
    if type(command) == str:
        ser.write(bytes(command, 'utf-8'))
    elif type(command) == int:
        ser.write(bytes([command]))
    
    
def run_rodeo(max_time=10000, min_perimeter=15):
    Ser = False
    Ser2 = False
    if Ser == True or Ser2 == True:
    # Connect to the transmitter
        cname = '/dev/cu.usbmodem1431' # COM9
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
        

        command, ang,tar_dist, image2 = make_decision2(rodeo_circles, 
                                                       obstacle_circles, 
                                                       target_circles, 
                                                       image)

        
        aT = [(-10, 10), (10, 35), (-35, -10), (35, 80), 
              (-80, -35),(80, 150) ,(-150, -80), (150, 185), (-185, -150)]        
        instr = [1, 3, 6, 4, 7, 5, 8, 2, 0, 9]
        
        aT2 = [(-45, 45), (45, 135), (-135, -45), (180, 135) , (-180, -135)]
        
        cS = -1
        if Ser2 == True:
            if ang>aT2[0][0] and ang<aT2[0][1]:
                cS = 1
                send_decision(ser, 1)
            elif ang>aT2[1][0] and ang<aT2[1][1]:
                cS = 4
                send_decision(ser, cS)
            elif ang>aT2[2][0] and ang<aT2[2][1]:
                cS = 3
                send_decision(ser, cS)    
            elif ang>aT2[3][0] and ang<aT2[3][1]:
                cS = 2
                send_decision(ser, cS)
            elif ang>aT2[4][0] and ang<aT2[4][1]:
                cS = 2
                send_decision(ser, cS)
            sleep(0.2)
          
            
        if Ser == True:
            if ang>aT[0][0] and ang<aT[0][1]:
                if tar_dist>100:
                    send_decision(ser, instr[0])
                    cS = instr[0]
                else:
                    send_decision(ser, instr[-1])
                    cS = instr[-1]     
            elif ang>aT[1][0] and ang<aT[1][1]:
                send_decision(ser, instr[1])
                cS = instr[1]
    
            elif ang>aT[2][0] and ang<aT[2][1]:
                send_decision(ser, instr[2])
                cS = instr[2]           
            elif ang>aT[3][0] and ang<aT[3][1]:
                send_decision(ser, instr[3])
                cS = instr[3]
    
            elif ang>aT[4][0] and ang<aT[4][1]:
                send_decision(ser, instr[4])
                cS = instr[4]
                
            elif ang>aT[5][0] and ang<aT[5][1]:
                send_decision(ser, instr[5])
                cS = instr[5]
                
            elif ang>aT[6][0] and ang<aT[6][1]:
                send_decision(ser, instr[6])
                cS = instr[6]
                
            elif ang>aT[7][0] and ang<aT[7][1]:
                send_decision(ser, instr[7])
                cS = instr[7]
                
            elif ang>aT[8][0] and ang<aT[8][1]:
                send_decision(ser, instr[8])
                cS = instr[8]
            elif ang>190:
                send_decision(ser, instr[9])
                cS = "attack!"
            sleep(0.2)
            
            
        cv2.putText(image2, "sending" + str(cS),(20,300), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,0,255),2)
        cv2.imshow('Frame', image2)
               
    cam.release()
    cv2.destroyAllWindows()
    
#def run_rodeo_rl(max_time=10000, min_perimeter=15):
#    # Connect to the transmitter
#    ser = serial.Serial('COM9', 9600)
#    
#    # Connect to a webcam
#    cam = cv2.VideoCapture(0)
#    if (cam.isOpened() == False):
#        print("Error opening video stream or file")
#    
#    ret, image = cam.read()    
#    image = imutils.resize(image, width=600)
#    
#    state = np.ndarray.flatten(np.zeros_like(image))
#    
#    print(len(state))
#    
#    # Create a NN
#    network = DeepRLNetwork()
#    network.init_network(len(state), 6, (500, 500))
#    reward = 0
#    
#    old_reward = 0
#    
#    # Process video
#    for curr_time in range(max_time):
#        # MAKE ACTION BASED ON PREVIOUS SOLUTION
#        action = network.choose_action(state)
#    
#        send_decision(ser, action)
#        
#        # LOOK AT THE RESULT
#        
#        if not cam.isOpened():
#            print("Camera is not opened")
#            break
#            
#        ret, rodeo_circles, obstacle_circles, target_circles, image, new_state = \
#            process_frame(cam, min_perimeter=min_perimeter)
#        
#        if ret:
#            break  
#        
#        print(len(np.ndarray.flatten(new_state)))
#        
#        tar_dist, ob_dist = closest_distance_rl(rodeo_circles, 
#                                                obstacle_circles, 
#                                                target_circles)
#        
#        reward = 1 / (1 + tar_dist) - 1 / (1 + ob_dist)
#        
#        if old_reward - reward > 0.3: # if we popped a baloon
#            reward = 0.5
#        
#        new_state = np.ndarray.flatten(new_state)
#        
#        network.report_action(reward, new_state)
#        network.update_weights()
#        
#        state = new_state
#        
#    cam.release()
#    cv2.destroyAllWindows()
#    
    
if __name__ == '__main__':
    run_rodeo(max_time=1000, min_perimeter=30)
    
