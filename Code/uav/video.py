import time

def capture():
    raw_frame_size = 10000 # kilobytes
    return {"raw_frame_size": raw_frame_size, "capture_timestamp": time.time()}

def encode(raw_frame, parameters):
    # Add delay and get encoded frame size as a function of encoding parameters
    encoder_delay = 15 # milliseconds
    encoded_frame_size = 100 # kiloytes
    encoded_frame = raw_frame
    encoded_frame["encode_timestamp"] = raw_frame["capture_timestamp"] + encoder_delay
    encoded_frame["encoded_frame_size"] = encoded_frame_size 
    encoded_frame["parameters"] = parameters
    return encoded_frame



    