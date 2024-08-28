import sys
import pilot

def transmit(frames):
    # Drop or pass according to the channel SNR and bit rate
    # Call the pilot / ground receiver with the frames
    pilot.radio.receive(frames)
    