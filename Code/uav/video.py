import time
import math
import pandas as pd
import qp_models

# VIDEO_LENGTHS = pd.read_csv(VIDEO_FILE)
frame_num = 1

FR_H = 7680
FR_W = 3840

def capture():
    raw_frame_size = 10000 # kilobytes
    # raw_frame_size = VIDEO_LENGTHS[frame_num]
    return {"raw_frame_size": raw_frame_size, "capture_timestamp": time.time()}

def encode(raw_frame, parameters):
    global frame_num
    # Add delay and get encoded frame size as a function of encoding parameters
    encoder_delay = 15 # milliseconds
    encoded_frame_size = 100 # kiloytes
    encoded_frame = raw_frame
    encoded_frame["frame_num"] = frame_num
    encoded_frame["encode_timestamp"] = raw_frame["capture_timestamp"] + encoder_delay
    encoded_frame["encoded_frame_size"] = encoded_frame_size 
    encoded_frame["parameters"] = parameters
    encoded_frame["pixels_i"] = (2.0 * parameters["theta_h"] * FR_W / 360.0) * (math.fabs(parameters["phi_n"] - parameters["phi_s"]) *FR_H/ 180.0)
    encoded_frame["pixels_o"] = FR_H * FR_W - encoded_frame["pixels_i"]
    # percFrLenI = qpModels.getExpectedValue(qp, "FrameSizes") * (pixelsInside) / (pixelsOutside + pixelsInside) * 8
    frame_num += 1
    return encoded_frame



    