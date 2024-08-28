import video
import brain
import radio
import time

TARGET_FPS = 30

def run():
    while True: 
        start_time = time.time()
        # read frame
        raw_frame = video.capture()
        
        # get optimization parameters
        params = brain.get_parameters()
        
        # encode video
        encoded_frames = video.encode(raw_frame, params)

        # transmit frames
        radio.transmit(encoded_frames, params["m_i"], params["m_o"])

        end_time = time.time()

        elapsed_time = end_time - start_time
        if elapsed_time < 1 / TARGET_FPS:
            time.sleep(1/TARGET_FPS - elapsed_time)

run()