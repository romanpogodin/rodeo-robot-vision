import numpy as np
import matplotlib.pyplot as plt
import cv2
import math
import time
import serial
from time import sleep
from pynput import keyboard

def get_hsv_masks(color='red'):
    if color == 'red':
        return [[np.array([0, 80, 0], np.uint8),
                 np.array([10, 255, 255], np.uint8)],
                [np.array([160, 80, 0], np.uint8), 
                 np.array([180, 255, 255], np.uint8)]]

    if color == 'green':
        return [[np.array([40, 100, 0], np.uint8), 
                 np.array([80, 255, 255], np.uint8)]]
        
    print('Color must be green or red')
    return None
    
def clear_binary_from_noise(image_threshed):
    kernel_open = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    kernel_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))

    image_threshed = cv2.morphologyEx(image_threshed, cv2.MORPH_OPEN, kernel_open)
    image_threshed = cv2.morphologyEx(image_threshed, cv2.MORPH_CLOSE, kernel_close)
    
def detect_colored_objects(hsv_img, min_perimeter, clear_noise=True, color='red'):
    height, width = hsv_img.shape[0:2]
    
    image_threshed = np.zeros((height, width), dtype=np.uint8)
    
    hsv_masks = get_hsv_masks(color)
    
    for each_mask in hsv_masks:
        image_threshed += cv2.inRange(hsv_img, each_mask[0], each_mask[1])

    if clear_noise:
        clear_binary_from_noise(image_threshed)

    _, contours, hierarchy = cv2.findContours(image_threshed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    circles = []
    for contour in contours:
        if len(contour) > min_perimeter:
            radius = np.sqrt(np.sum((contour[len(contour) // 2] - contour[0]) ** 2)) / 2
            circles.append([0.5 * (contour[0] + contour[len(contour) // 2]).reshape(2), radius])

    return circles

def process_frame(cam, min_perimeter, show_picture=True, clear_noise=True):
    # Initial processing

    ret, image = cam.read()    
    
    if not ret:
        print("Cannot read a frame")
        return 1, None, None
    
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    rodeo_circles = detect_colored_objects(hsv_img, min_perimeter, 
                                           clear_noise, color='red')
    obstacle_circles = detect_colored_objects(hsv_img, min_perimeter, 
                                              clear_noise, color='green')

    for circle in rodeo_circles:
        cv2.circle(image, tuple(circle[0].astype('int')), 
                   circle[1].astype('int'), (0, 0, 255), 2)
        
    for circle in obstacle_circles:
        cv2.circle(image, tuple(circle[0].astype('int')), 
                   circle[1].astype('int'), (0, 255, 0), 2)
    
    cv2.imshow('Frame', image)
    
    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        return 1, None, None
    
    return 0, rodeo_circles, obstacle_circles

def make_decision(rodeo_circles, obstacle_circles):
    # Assume that we have two rodeo circles
    
    if len(rodeo_circles) < 2 or len(obstacle_circles) < 1:
        return 'c'
    
    rodeo_center = 0.5 * (rodeo_circles[0][0] + rodeo_circles[1][0]).reshape((2, 1))
    rodeo_direction = rodeo_circles[0][0] - rodeo_circles[1][0]
    
    circle_centers = np.zeros((2, len(obstacle_circles)))
    
    for i in range(len(obstacle_circles)):
        circle_centers[:, i] = obstacle_circles[i][0]
    
    circle_centers -= np.repeat(rodeo_center, len(obstacle_circles), axis=1)
    
    distances = np.sum(circle_centers ** 2, axis=0)
    
    closest_ind = np.argmin(distances)
    
    angle = np.arccos(rodeo_direction.dot(circle_centers[:, closest_ind]) / 
                      np.linalg.norm(rodeo_direction) / 
                      np.linalg.norm(circle_centers[:, closest_ind]))
    
    if np.abs(angle - np.pi) > 0.8 * np.pi:
        return 'w'
    else:
        return 'a'

def send_decision(ser, command):
    # print("Sending %s" % command)
    ser.write(bytes(command, 'utf-8'))
    
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
        
        ser = None
        send_decision(ser, command)
        
    cam.release()
    cv2.destroyAllWindows()
    
if __name__ == '__main__':
    run_rodeo(max_time=100, min_perimeter=30)