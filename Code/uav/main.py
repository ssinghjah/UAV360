import video
import brain
import radio

TARGET_FPS = 30

def run():
    while True: 
        # read frame
        raw_frame = video.capture()
        
        # get optimization parameters
        params = brain.get_parameters()
        
        # encode video
        encoded_frames = video.encode(raw_frame, params["theta_h"], params["phi_n"], params["phi_s"], params["qp_i"], params["qp_o"])

        # transmit frames
        radio.transmit(encoded_frames, params["m_i"], params["m_o"])