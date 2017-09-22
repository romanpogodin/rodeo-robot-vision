"""
Robot's behaviour control
"""
import numpy as np
import cv2

def find_mid(rodeo1, rodeo2):
    x = (rodeo1[0] + rodeo2[0])/2
    y = (rodeo1[1] + rodeo2[1])/2
    return int(x), int(y)
    
def find_rodeo_vector(rodeo_circles, back_ind):
    if back_ind == 0:
        bx, by = find_mid(rodeo_circles[0][0],rodeo_circles[1][0])
        fx = rodeo_circles[2][0][0]
        fy = rodeo_circles[2][0][1]
    elif back_ind == 1:
        bx, by = find_mid(rodeo_circles[1][0],rodeo_circles[2][0])
        fx = rodeo_circles[0][0][0]
        fy = rodeo_circles[0][0][1]
    else:
        bx, by = find_mid(rodeo_circles[2][0],rodeo_circles[0][0])
        fx = rodeo_circles[1][0][0]
        fy = rodeo_circles[1][0][1]
    return (int(fx), int(fy)), (int(bx), int(by))


def find_dist(coord1, coord2):
    import numpy as np
    dist = np.sqrt((coord2[0]-coord1[0])**2 + (coord2[1]-coord1[1])**2)
    return int(dist)
    

def closest_distance_rl(rodeo_circles, obstacle_circles, target_circles):
    tar_dist = 1000
    dx = 0
    dy = 0
    fC = (0,0)
    bC = (0,0)
    tC = (0,0)
    oC = (0,0) 
    
    if len(rodeo_circles)>1:
#        fC, bC = find_rodeo_vector(rodeo_circles, ind)
        fC = rodeo_circles[1][0]
        bC = rodeo_circles[0][0]
    mC = find_mid(fC, bC)
      
    obst_distances = []
    for i in range(len(obstacle_circles)):
        obst_distances.append(find_dist(mC,obstacle_circles[i][0]))
        
    targ_distances = []
    for i in range(len(target_circles)):
        targ_distances.append(find_dist(mC,target_circles[i][0]))
      
    if len(targ_distances)>0:   
        # in blue
        closest_Tind = np.argmin(targ_distances)
        tC = target_circles[closest_Tind][0]  
    if len(obst_distances)>0: 
        # in white
        closest_Oind = np.argmin(obst_distances)
        oC = obstacle_circles[closest_Oind][0]
    
    ob_dist = find_dist(oC, mC)

    tar_dist = find_dist(tC, mC) 
    tar_norm_dist = np.sqrt(dx**2 + dy**2)

    return tar_dist, ob_dist

def make_decision2(rodeo_circles, obstacle_circles, target_circles, image):
    
    h, w = image.shape[:2]
    dx = 0
    dy = 0
    fC = (0,0)
    bC = (0,0)
    tC = (0,0)
    oC = (0,0) 
    if len(rodeo_circles)>1:
#        fC, bC = find_rodeo_vector(rodeo_circles, ind)
        fC = rodeo_circles[1][0]
        bC = rodeo_circles[0][0]
        rob_len = find_dist(fC, bC)
     # find front and back coordinates of robot
        cv2.line(image, (fC[0], fC[1]), (bC[0], bC[1]), (0, 0, 0), 3)
        cv2.putText(image, "robot length = " + str(int(rob_len)),(10, 180), \
        cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2) 
    
    # find center coordinates of robot
    mC = find_mid(fC, bC)
#    cv2.circle(image, mC, int(2), (255, 255, 255), 2)
       
    obst_distances = []
    for i in range(len(obstacle_circles)):
        obst_distances.append(find_dist(mC,obstacle_circles[i][0]))
        
    targ_distances = []
    for i in range(len(target_circles)):
        targ_distances.append(find_dist(mC,target_circles[i][0]))
        
    if len(targ_distances)>0:   
        # in blue
        closest_Tind = np.argmin(targ_distances)
        t_sort = np.argsort(targ_distances)
        tC = target_circles[closest_Tind][0]
        cv2.line(image, (mC[0], mC[1]), (tC[0], tC[1]), (255, 0, 0), 1) 
        cv2.circle(image, tC, target_circles[closest_Tind][1], (255, 0, 0), 2)
        for i in range(len(targ_distances)):
            cv2.putText(image, str(t_sort[i]),target_circles[i][0], \
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,0,0),2) 
            
    
    if len(obst_distances)>0: 
        # in white
        closest_Oind = np.argmin(obst_distances)
        o_sort = np.argsort(obst_distances)
        oC = obstacle_circles[closest_Oind][0]
        cv2.line(image, (mC[0], mC[1]), (oC[0], oC[1]), (255, 255, 255), 1)
        cv2.circle(image, oC, obstacle_circles[closest_Oind][1], (255, 255, 255), 1)
        for i in range(len(obst_distances)):
            cv2.putText(image, str(o_sort[i]),obstacle_circles[i][0], \
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),2) 
        
    
    
    dx_rodeo = fC[0]-bC[0]
    dy_rodeo = fC[1]-bC[1]
    
    dx_tar = tC[0]- mC[0]
    dy_tar = tC[1]- mC[1]
    
    dx_ob = oC[0]- mC[0]
    dy_ob = oC[1]- mC[1]
    
    l_angle = np.arctan2(dy_tar,dx_tar)*180/np.pi
    
    ob_angle = np.arctan2(dy_ob,dx_ob)*180/np.pi
    
    s_angle = np.arctan2(dy_rodeo,dx_rodeo)*180/np.pi
    
    ang = l_angle-s_angle
    obang = ob_angle-s_angle
    
    ob_dist = find_dist(oC, mC)
    dxO = ob_dist*np.cos(obang)
    dyO = ob_dist*np.sin(obang)
    
    tar_dist = find_dist(tC, mC)
    
    dx = tar_dist*np.cos(ang)/w
    dy = tar_dist*np.sin(ang)/h

        
    tar_norm_dist = np.sqrt(dx**2 + dy**2) 

    cv2.putText(image, str("F"),fC, cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 255, 0),2) 
    cv2.putText(image, str("B"),bC, cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0, 165, 255),2) 
    
    cv2.putText(image, str("obstacle"),oC, cv2.FONT_HERSHEY_SIMPLEX, 0.8,(255,255,255),2) 
    cv2.putText(image, str("target"),tC, cv2.FONT_HERSHEY_SIMPLEX, 0.8,(255,0,0),2)
    cv2.putText(image, str("robot"),mC, cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0,0,0),2)
    
    cv2.putText(image, "distance to target = " + str(int(tar_dist)),(10, 20), \
                cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2) 
    
    cv2.putText(image, "distance to obstacle = " + str(int(ob_dist)),(10, 50), \
            cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2)
    
    cv2.putText(image, "angle to target = " + str(int(ang)),(10, 80), \
            cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2)

    if ob_dist<60:
        ang = 0.2*ang-0.8*obang    
        cv2.putText(image, "alert!! obstacle approaching!",(50, 110), \
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,255),2)
    if ob_dist<20:
        ang = 0.1*ang-0.9*obang    
        cv2.putText(image, "alert!! obstacle approaching!",(50, 110), \
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,0,255),2)
        
    if tar_dist<60:   
        cv2.putText(image, "nearly there!!",(50, 140), \
            cv2.FONT_HERSHEY_SIMPLEX, 0.7,(0,255,0),2)
        
#    cv2.putText(image, str(int(dx)),(30, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2) 
#    cv2.putText(image, str(int(dy)),(100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2) 
#    cv2.putText(image, str(int(dxO)),(30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2) 
#    cv2.putText(image, str(int(dyO)),(100, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2) 
    

    return (dx, dy), ang,tar_dist, image

            

