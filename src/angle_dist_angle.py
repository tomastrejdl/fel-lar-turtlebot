import math
import numpy as np

def get_intersections(x0, y0, r0, x1, y1, r1):
    # circle 1: (x0, y0), radius r0
    # circle 2: (x1, y1), radius r1

    d = math.sqrt((x1 - x0) * 2 + (y1 - y0) * 2)

    # non intersecting
    if d > r0 + r1:
        return None
    # One circle within other
    if d < abs(r0 - r1):
        return None
    # coincident circles
    if d == 0 and r0 == r1:
        return None
    else:
        a = (r0 * 2 - r1 * 2 + d ** 2) / (2 * d)
        h = math.sqrt(r0 * 2 - a * 2)
        x2 = x0 + a * (x1 - x0) / d
        y2 = y0 + a * (y1 - y0) / d
        x3 = x2 + h * (y1 - y0) / d
        y3 = y2 - h * (x1 - x0) / d

        x4 = x2 - h * (y1 - y0) / d
        y4 = y2 + h * (x1 - x0) / d

        return (x3, y3, x4, y4)

def get_directions(x1,y1,x2,y2,dist_from_gate):
    # = np.sign(a1) * math.sin(math.radians(abs(a1))) * d1
    #x2 = np.sign(a2) * math.sin(math.radians(abs(a2))) * d2
    #y1 = np.sign(a1) * math.cos(math.radians(abs(a1))) * d1
    #y2 = np.sign(a2) * math.cos(math.radians(abs(a2))) * d2
    # print(x1,y1,x2,y2)
    B = [(x1+x2)/2,(y1+y2)/2] # gate center (point between gate poles)
    V = [(y1-y2),-(x1-x2)] # orthogonal vector to vector from one pillar to second pillar
    
    #sets orthogonal vector to given size (distance from gate)
    v0 = (V[0] /  (V[0]**2 + V[1]**2)**(1/2))*dist_from_gate #
    v1 = (V[1] /  (V[0]**2 + V[1]**2)**(1/2))*dist_from_gate
    V[0] = v0
    V[1] = v1
    
    c1 = [B[0]+V[0],B[1]+V[1]] # First or second point we want to get to (in front of or behind gate)
    c2 = [B[0]-V[0],B[1]-V[1]] # First or second point we want to get to (in front of or behind gate)
    if c1[0]**2+c1[1]**2>c2[0]**2+c2[1]**2:
        C = c2
    else:
        C = c1
    # C is the point in front of the gate
    
    # creates vector between point C in front of the gate and the one behind it
    # compares z coordinates to ensure correct orientation of vector
    if c1[1] > c2[1]:
        v = [c1[0]-c2[0],c1[1]-c2[1]]
    else:
        v = [c2[0]-c1[0],c2[1]-c1[1]]
     # angle of first rotation (robot is then supposed to be facing in the direction of point C (the one in front of the gate))
    angle1 = math.degrees(math.atan2(C[1],C[0]))
    vector_angle = math.degrees(math.atan2(v[1],v[0])) # support vector (gate inclination)

    distance = math.sqrt(C[0] ** 2 + C[1] ** 2) # distance to be traveled in straight line from origin to C
    
   
    angle1 = -(angle1 - 90) # adjust angle to be compatible with rest of the program
    vector_angle = vector_angle -90 

    final_angle = -(vector_angle + angle1) # angle of second rotation (robot is supposed to be facing center of the gate after that)


    return math.radians(angle1), distance, math.radians(final_angle)
