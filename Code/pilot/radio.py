def receive(frame, channel_sinr):
    # Add decoding and rendering delay
    # Send acknowledgement and channel SINR back to the uav
    decoding_delay = 30 # milliseconds
    rendering_delay = 30 # milliseconds 
    ack = {"frame_num": frame["frame_num"], "channel_sinr": channel_sinr}
    # channel.transmit(ack)