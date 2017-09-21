"""
Object recognition using OpenCV
"""
import numpy as np
import cv2

def create_mask(hsv, colorLower, colorUpper):
    import cv2
    mask = cv2.inRange(hsv, colorLower, colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    return mask


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
    cnts = sorted(contours, key=cv2.contourArea)[0:2]
    for i in range(len(cnts)):
        ((x_g, y_g), radius_g) = cv2.minEnclosingCircle(cnts[i])
        circles.append([(int(x_g), int(y_g)), int(radius_g)])
        
    

    return circles
#    return cnts

def process_frame(cam, min_perimeter, show_picture=True, clear_noise=True):
    import imutils

    ret, image = cam.read()    
    image = imutils.resize(image, width=600)
    
    if not ret:
        print("Cannot read a frame")
        return 1, None, None, None, None, None
    
    hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


    # back orange
    oLower = (0, 35, 30)
    oUpper = (30, 255, 255)
    
    # front green
    fLower = (30, 10, 10)
    fUpper = (90, 255, 255)
    
    #obstacle color    
    gLower = (0, 0, 200)
    gUpper = (180, 95, 255)

    #target color
    bLower = (94, 45, 40)
    bUpper = (110, 255, 255)
    
    # front
    f_thresh = [fLower, fUpper]   
    # back
    o_thresh = [oLower, oUpper]

    #obstacle color    
    g_thresh = [gLower, gUpper]
    #target color
    b_thresh = [bLower, bUpper]
    
    mask_f = create_mask(hsv_img, f_thresh[0], f_thresh[1])
    mask_o = create_mask(hsv_img, o_thresh[0], o_thresh[1])
    mask_g = create_mask(hsv_img, g_thresh[0], g_thresh[1])
    mask_b = create_mask(hsv_img, b_thresh[0], b_thresh[1])
    

    
    
    cv2.imshow('mask_green', mask_f)
    cv2.imshow('mask_orange', mask_o)
    cv2.imshow('mask_white', mask_g)
    cv2.imshow('mask_blue', mask_b)
    
    
    rodeo_circles = []
    obstacle_circles = []
    target_circles = []
    
    cnts_o = cv2.findContours(mask_o.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]  
    cnts_f = cv2.findContours(mask_f.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]

    cnts_b = cv2.findContours(mask_b.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnts_b =sorted(cnts_b, key=cv2.contourArea, reverse=True)
    
    cnts_g = cv2.findContours(mask_g.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
    cnts_g = sorted(cnts_g, key=cv2.contourArea, reverse=True)
#    cnts_g = sorted(cnts_g, key=cv2.contourArea)

    mask_rl = np.zeros(mask_f.shape)
    mask_rl[mask_g>100] = 1
    mask_rl[mask_b>100] = 2
    
    
    # find robot
    if len(cnts_o)>0:
        cnts_o1 = max(cnts_o, key=cv2.contourArea)
        ((x_g, y_g), radius_g) = cv2.minEnclosingCircle(cnts_o1)
        rodeo_circles.append([(int(x_g), int(y_g)), int(radius_g)])
        cv2.circle(image, (int(x_g), int(y_g)), int(radius_g), (0, 0, 255), 2)
#        mask_rl[int(x_g), int(y_g)] = 3
        
    if len(cnts_f)>0:
        cnts_f1 = max(cnts_f, key=cv2.contourArea)
        ((x_g, y_g), radius_g) = cv2.minEnclosingCircle(cnts_f1)
        rodeo_circles.append([(int(x_g), int(y_g)), int(radius_g)])
        cv2.circle(image, (int(x_g), int(y_g)), int(radius_g), (0, 0, 255), 2)
#        mask_rl[int(x_g), int(y_g)] = 3
        
    
    # find obstacles in white
    if len(cnts_g)>0:       
        for i in range(min(len(cnts_g), 4)):
            ((x_g, y_g), radius_g) = cv2.minEnclosingCircle(cnts_g[i])
            obstacle_circles.append([(int(x_g), int(y_g)), int(radius_g)])
            cv2.circle(image, (int(x_g), int(y_g)), int(radius_g), (255, 255, 255), 2)
            
    # find target in blue
    if len(cnts_b)>0:       
        for i in range(min(len(cnts_b), 4)):
            ((x_g, y_g), radius_g) = cv2.minEnclosingCircle(cnts_b[i])
            target_circles.append([(int(x_g), int(y_g)), int(radius_g)])
            cv2.circle(image, (int(x_g), int(y_g)), int(radius_g), (255, 0, 0), 2)


    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        return 1, None, None, None, None, None
    
    return 0, rodeo_circles, obstacle_circles, target_circles, image, mask_rl
    

