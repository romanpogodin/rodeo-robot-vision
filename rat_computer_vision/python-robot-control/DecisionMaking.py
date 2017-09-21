"""
Robot's behaviour control
"""
import numpy as np

def make_decision(rodeo_circles, obstacle_circles):
    # Assume that we have two rodeo circles
    
    if len(rodeo_circles) < 3 or len(obstacle_circles) < 1:
        return 'c'
    
    rodeo_center = (rodeo_circles[0][0] + rodeo_circles[1][0] + \
                    rodeo_circles[2][0]).reshape((2, 1)) / 3
    
    rodeo_distances = np.zeros(3)
    
    rodeo_distances[0] = np.sum((rodeo_circles[0][0] - rodeo_circles[1][0]) ** 2)
    rodeo_distances[1] = np.sum((rodeo_circles[1][0] - rodeo_circles[2][0]) ** 2)
    rodeo_distances[2] = np.sum((rodeo_circles[2][0] - rodeo_circles[0][0]) ** 2)
    
    ind = np.argmin(rodeo_distances)
    
    if ind == 0:
        rodeo_direction = rodeo_circles[2][0] - \
            0.5 * (rodeo_circles[0][0] + rodeo_circles[1][0])
    elif ind == 1:
        rodeo_direction = rodeo_circles[0][0] - \
            0.5 * (rodeo_circles[1][0] + rodeo_circles[2][0])
    else:
        rodeo_direction = rodeo_circles[1][0] - \
            0.5 * (rodeo_circles[0][0] + rodeo_circles[2][0])
    
    circle_centers = np.zeros((2, len(obstacle_circles)))
    
    for i in range(len(obstacle_circles)):
        circle_centers[:, i] = obstacle_circles[i][0]
    
    circle_centers -= np.repeat(rodeo_center, len(obstacle_circles), axis=1)
    
    distances = np.sum(circle_centers ** 2, axis=0)
    
    closest_ind = np.argmin(distances)
    
    angle = np.arccos(rodeo_direction.dot(circle_centers[:, closest_ind]) / 
                      np.linalg.norm(rodeo_direction) / 
                      np.linalg.norm(circle_centers[:, closest_ind]))
    
    if np.abs(angle - np.pi) > 0.9 * np.pi:
        return 'w'
    else:
        if np.array([rodeo_direction[1], -rodeo_direction[0]]).dot(
                circle_centers[:, closest_ind]) > 0:
            return 'a'
        else:
            return 'd'
            

