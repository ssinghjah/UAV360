import sys
import pilot.radio as pilot_radio
import uav.radio as uav_radio
import math
import numpy as np

SCENARIO = "scenario_1"
P_UAV = 1
CENTER_FREQ = 28*(10.0**9.0)
NOISE_SPECTRAL_DENSITY = 1.380649*10.0**(-23.0)*298
B = float(400*10e6)

def _getBER5GNR(snr, M):
    ber = 1
    deltaX = 0.4
    deltaY = -3.7

    if snr < -2:
        ber = 1
    else:
        if M == 4:
            xStart = -2.1
        if M == 16:
            xStart = 4
        if M == 64:
            xStart = 7.5 
        if M == 256:
            xStart = 12
    
        exponent = (snr - xStart)*(deltaY)/deltaX
        ber = math.pow(10.0, exponent)    
    return ber

def initialize_scenario_1():
    BS_X_SPACING = 50
    BS_Y_SPACING = 50
    BS_HEIGHT = 10
    
    SIM_X_END = 1000
    SIM_Y_END = 1000
    bsX = 0
    bsY = 0

    bs_locations = []
    while bsX <= SIM_X_END:
        bsY = 0
        while bsY <= SIM_Y_END:
            bs_locations.append([bsX, bsY, BS_HEIGHT])
            bsY += BS_Y_SPACING
        bsX += BS_X_SPACING

    return bs_locations


def _calculateSNR(pathLoss, txPower):
    noise = B*(NOISE_SPECTRAL_DENSITY)
    signal = float(txPower/pathLoss)
    snr = signal / noise
    return snr

def _get_path_loss(uavPosition):
    uavHeight = uavPosition[2]
    minPl = math.inf
    bsIndex = 0
    assocBS = 0
    global BS_LOCATIONS
    for bsLocation in BS_LOCATIONS:
        k1 = max(294.05*math.log10(uavHeight) - 432.94, 18)
        k2 = 233.98*math.log10(uavHeight) - 0.95
        l2d = math.sqrt(float(uavPosition[0] - bsLocation[0])**2.0 + float(uavPosition[1] - bsLocation[1])**2.0)
 
        if l2d < k1:
            losProb = 1
        else:
            losProb = k1/l2d + (1 - 1/l2d)*math.exp(-l2d/k2)
        randVal = np.random.uniform(0, 1)
        if randVal < losProb:
            # calculate path loss using LoS params
            A = 2.0
            B = 0.0
            SIGMA = 1.44
        else:
            # calculate path loss using reflection and diffraction params
            A = 2.999 
            B = -0.067
            SIGMA = 3.60
        d = math.sqrt(float(uavPosition[0] - bsLocation[0])**2.0 + float(uavPosition[1] - bsLocation[1])**2.0 + float(uavPosition[2] - bsLocation[2])**2.0)

        # d = get3DDist(uavPosition, bsLocation)
        pl = 32.4 + 20*math.log10(CENTER_FREQ/1e9) + 10*A*(uavHeight**B)*math.log10(d)
        xFading = np.random.uniform(0, SIGMA)
        pl += xFading
        if pl < minPl:
            minPl = pl
            assocBS = bsIndex
        bsIndex += 1
    
    minPl = 10.0**(0.1*minPl)
    return minPl, assocBS

def transmit(frame):
    # Drop or pass according to the channel SNR and bit rate
    # Call the pilot / ground receiver with the frames
    sinr = 10
    ber_i = _getBER5GNR(sinr, frame["parameters"]["m_i"])
    ber_o = _getBER5GNR(sinr, frame["parameters"]["m_o"])
    pl, assoc_bs = _get_path_loss(frame["uav_position"])
    sinr = _calculateSNR(pl, frame["p_uav"])
    frame["ber_i"] = ber_i
    frame["ber_o"] = ber_o
    frame["sinr"] = sinr
    frame["associated_bs"] = assoc_bs
    pilot_radio.receive(frame, sinr)
    
def transmit_to_uav(frame):
    # Drop or pass according to the channel SNR and bit rate
    # Call the pilot / ground receiver with the frames
    sinr = 10
    uav_radio.receive(frame, sinr)

if SCENARIO == "scenario_1":
    BS_LOCATIONS = initialize_scenario_1()

    