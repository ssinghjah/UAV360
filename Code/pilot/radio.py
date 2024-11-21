import channel
# import config
import json

bLOG = True
RX_FRAMES_PATH = "./rx_frames.jsonl"

def _log(frame):
    if bLOG:
        with open(RX_FRAMES_PATH, "a+") as log_pointer:
            log_pointer.writelines(json.dumps(frame) + "\n")

def receive(frame, channel_sinr):
    # Add decoding and rendering delay
    # Send acknowledgement and channel SINR back to the uav
    decoding_delay = 30 # milliseconds
    rendering_delay = 30 # milliseconds 
    print("pilot received:", frame)
    frame["display_timestamp"] = frame["transmission_timestamp"] + decoding_delay
    _log(frame)
    ack = {"frame_num": frame["frame_num"], "channel_sinr": channel_sinr}
    channel.transmit_to_uav(ack)