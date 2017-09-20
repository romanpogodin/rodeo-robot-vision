"""
Object recognition using OpenCV
"""
import numpy as np
import cv2

def get_hsv_masks(color='red'):
    if color == 'red':
        return [[np.array([0, 80, 0], np.uint8),
                 np.array([10, 255, 255], np.uint8)],
                [np.array([160, 80, 0], np.uint8), 
                 np.array([180, 255, 255], np.uint8)]]

    if color == 'orange':
        return [[np.array([10, 150, 0], np.uint8), 
                 np.array([30, 235, 255], np.uint8)]]
    
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
                                           clear_noise, color='orange')
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
    

