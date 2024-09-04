import math
import numpy as np

THETA_H = 100.0
PHI_N = 10.0
PHI_S = -70.0
P_PHI = 0.2

def generatePhi():
    meanV = (PHI_S + PHI_N) / 2.0
    sigmaV = math.fabs(PHI_S - PHI_N) / 4.0
    randVal = np.random.uniform(0, 1)
    phi = 0.0
    if randVal < P_PHI:
        phi = np.random.normal(meanV, sigmaV)
    return phi

def generatePilotViewingAngles(ticks):
    pilotViewingDirections = []
    sigmaH = THETA_H/2.0

    prevTheta = 0
    prevPhi = 0
    for tickNum in range(ticks):
        theta = np.random.normal(0, sigmaH)
        while math.fabs(theta) > 180:
            theta = np.random.normal(0, sigmaH)
        phi = generatePhi()
        while math.fabs(phi) > 90:
            phi = generatePhi()
        pilotViewingDirections.append([theta, phi])
        #pilotViewingDirections.append([0, 0])
    return pilotViewingDirections