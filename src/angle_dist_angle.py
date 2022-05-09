import math
import numpy as np

def pol2cart(r, phi):
    x = r * np.cos(phi)
    y = r * np.sin(phi)
    return(x, y)


def get_directions(x1,y1,x2,y2,dist_from_gate):
    # = np.sign(a1) * math.sin(math.radians(abs(a1))) * d1
    #x2 = np.sign(a2) * math.sin(math.radians(abs(a2))) * d2
    #y1 = np.sign(a1) * math.cos(math.radians(abs(a1))) * d1
    #y2 = np.sign(a2) * math.cos(math.radians(abs(a2))) * d2
    # print(x1,y1,x2,y2)
    B = [(x1+x2)/2,(y1+y2)/2] # gate center (point between gate poles)
    V = [(y1-y2),-(x1-x2)] # orthogonal vector to vector from one pillar to second pillar NORMALIZE THIS SHIT

    #sets orthogonal vector to given size (distance from gate)
    v0 = (V[0] / (V[0]**2 + V[1]**2)**(1/2))*dist_from_gate #
    v1 = (V[1] / (V[0]**2 + V[1]**2)**(1/2))*dist_from_gate
    V[0] = v0
    V[1] = v1

    c1 = [B[0]+V[0],B[1]+V[1]] # First or second point we want to get to (in front of or behind gate)
    c2 = [B[0]-V[0],B[1]-V[1]] # First or second point we want to get to (in front of or behind gate)

    if c1[0]**2+c1[1]**2 >= c2[0]**2+c2[1]**2:
        C = c2
        # creates vector between point C in front of the gate and the one behind it
        # compares z coordinates to ensure correct orientation of vector
        v = [c1[0] - c2[0], c1[1] - c2[1]]
    else:
        C = c1
        v = [c2[0] - c1[0], c2[1] - c1[1]]
    # C is the point in front of the gate

    # angle of first rotation (robot is then supposed to be facing in the direction of point C (the one in front of the gate))
    angle1 = math.degrees(math.atan2(C[1],C[0]))
    #print(angle1)cd R
    if angle1 <= -90:
        angle1 = 270 + angle1
    else:
        angle1 = (angle1 - 90)  # adjust angle to be compatible with rest of the program
    #print(C)
    #print(C[1],C[0])
    #print(angle1)
    #print(math.degrees(math.atan2(1,-10)))
    vector_angle = math.degrees(math.atan2(v[1],v[0])) # support vector (gate inclination)
    distance = math.sqrt(C[0] ** 2 + C[1] ** 2) # distance to be traveled in straight line from origin to C
    #print(angle1)

    #if vector_angle
    if vector_angle <= -90:
        vector_angle = 270 + vector_angle
    else:
        vector_angle = (vector_angle - 90)  # adjust angle to be compatible with rest of the program
    #print(vector_angle)

    #vector_angle = (vector_angle -90)

    #print(vector_angle)
    final_angle = +(vector_angle - angle1) # angle of second rotation (robot is supposed to be facing center of the gate after that)
    if abs(final_angle)>180:
        final_angle = -np.sign(final_angle)*(360-abs(final_angle))

    return math.radians(-angle1), distance, math.radians(-final_angle)
