import video
import brain
import radio
import common
import time
import math

TARGET_FPS = 30
UAV_VELOCITY = 5
UAV_START = [0, 0, 50]
UAV_END = [1000, 1000, 25]
P_UAV = 1

start_time = time.time()


def get3DDist(pt1, pt2):
    dist = math.sqrt(float(pt1[0] - pt2[0])**2.0 + float(pt1[1] - pt2[1])**2.0 + float(pt1[2] - pt2[2])**2.0)
    return dist

def generatePositions():
    currPos = UAV_START
    positions = [currPos]
    endReached = False
    while endReached == False:
        distToEnd = get3DDist(currPos, UAV_END)
        hop = float(UAV_VELOCITY)/TARGET_FPS
        if distToEnd < hop:
            endReached = True
            positions.append(UAV_END)
            continue
        else:
            vecToEnd = [UAV_END[0] - currPos[0], UAV_END[1] - currPos[1], UAV_END[2]- currPos[2]]
            mag = math.sqrt(vecToEnd[0]**2.0 + vecToEnd[1]**2.0 + vecToEnd[2]**2.0)
            normVecToEnd = [vecToEnd[0]/mag, vecToEnd[1]/mag, vecToEnd[2]/mag]
            currPos = [currPos[0] + hop*normVecToEnd[0], currPos[1] + hop*normVecToEnd[1], currPos[2] + hop*normVecToEnd[2]]
        positions.append(currPos)
    return positions

UAV_POSITIONs = generatePositions()

def run():
    tick = 0
    while tick < len(UAV_POSITIONs): 
        # read frame
        raw_frame = video.capture()
        
        # get optimization parameters
        params = brain.get_parameters()
        
        # encode video
        encoded_frames = video.encode(raw_frame, params)

        print("uav transmitted:", encoded_frames)

        # transmit frames
        encoded_frames["uav_position"] = UAV_POSITIONs[tick]
        encoded_frames["p_uav"] = P_UAV
        radio.transmit(encoded_frames, params["m_i"], params["m_o"])

        end_time = time.time()

        elapsed_time = end_time - start_time
        if elapsed_time < 1 / TARGET_FPS:
            time.sleep(1/TARGET_FPS - elapsed_time)

        tick += 1

run()