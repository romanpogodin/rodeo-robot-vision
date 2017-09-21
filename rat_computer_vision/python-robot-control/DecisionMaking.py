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
    

def make_decision2(rodeo_circles, obstacle_circles, target_circles, image):
    dx = 0
    dy = 0

    if len(rodeo_circles)>1:
#        fC, bC = find_rodeo_vector(rodeo_circles, ind)
        fC = rodeo_circles[1][0]
        bC = rodeo_circles[0][0]
     # find front and back coordinates of robot
    
    cv2.line(image, (fC[0], fC[1]), (bC[0], bC[1]), (0, 0, 0), 2) 
    
    # find center coordinates of robot
    mC = find_mid(fC, bC)
    cv2.circle(image, mC, int(2), (255, 0, 0), 2)
       
    obst_distances = []
    for i in range(len(obstacle_circles)):
        obst_distances.append(find_dist(mC,obstacle_circles[i][0]))
        
    targ_distances = []
    for i in range(len(target_circles)):
        targ_distances.append(find_dist(mC,target_circles[i][0]))
        
        
    closest_Oind = np.argmin(obst_distances)
    closest_Tind = np.argmin(targ_distances)

    tC = target_circles[closest_Tind][0]
    
    oC = obstacle_circles[closest_Oind][0]
    
    
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
    dx = tar_dist*np.cos(ang)
    dy = tar_dist*np.sin(ang)
    
    cv2.circle(image, tC, int(2), (255, 0, 0), 2)
    
    cv2.circle(image, oC, int(2), (255, 255, 0), 2)
    cv2.putText(image, str(obstacle),oC, cv2.FONT_HERSHEY_SIMPLEX, 0.2,(0,0,0),2) 
    
    cv2.putText(image, str(int(dx)),(30, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2) 
    cv2.putText(image, str(int(dy)),(100, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,0),2) 


    return (dx, dy), image

            

