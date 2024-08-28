import sys

# import channel

def transmit(encoded_frames, m_i, m_o):
    # Divide encoded frame into network datagrams
    # Transmit to channel at given modulation scheme
    transmission_delay = 30 # milliseconds. Calculate using encoded frame size and modulation schemes
    propagation_delay = 1 # transmission delay. Calculate based on UAV's position
    encoded_frames["transmission_timestamp"] = encoded_frames["encode_timestamp"] + transmission_delay + propagation_delay
    # channel.transmit(encoded_frames)