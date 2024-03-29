import math
from scipy import special
import random
import numpy as np
import sys
import qpModels
import time
import csv
import os

CENTER_FREQ = 28*(10.0**9.0)
BS_LOCATIONs = []
#NOISE_SIGMA = 
FPS = 30 # frames per second
VELOCITY = 5 # meters per second
UAV_START = [0, 0, 50]
UAV_END = [1000, 1000, 25]
THETA_H = 100.0
PHI_N = 10.0
PHI_S = -70.0
P_PHI = 0.2
BS_X_SPACING = 50
BS_Y_SPACING = 50
BS_HEIGHT = 10
SIM_X_END = 1000
SIM_Y_END = 1000

bsX = 0
bsY = 0

BS_LOCATIONs = []
while bsX <= SIM_X_END:
    bsY = 0
    while bsY <= SIM_Y_END:
        BS_LOCATIONs.append([bsX, bsY, BS_HEIGHT])
        bsY += BS_Y_SPACING
    bsX += BS_X_SPACING

#BS_LOCATIONs = [ [500, 250, 0],  [500, 250, 0], [500, 500, 0],  [500, 750, 0]]
# BS_LOCATIONs = [[0, 250, 10], [0, 500, 10], [0, 750, 10], [0, 1000, 10],
#                 [250, 250, 10], [250, 500, 10], [250, 750, 10], [250, 1000, 10],
#                 [500, 250, 10], [500, 500, 10], [500, 750, 10], [500, 1000, 10],
#                 [750, 250, 10], [750, 500, 10], [750, 750, 10], [750, 1000, 10],
#                 [1000, 250, 10],  [1000, 250, 10], [1000, 500, 10], [1000, 750, 10]]
QPs = [10, 20, 40, 50]
#QPs = [50]
Ms = [4, 16, 64, 256]
#Ms = [256]
FNAME_SUFFIX = "LakeHibara_Adaptive"


ALPHA = 0.95
NOISE_SPECTRAL_DENSITY = 1.380649*10.0**(-23.0)*298;
B = float(400*10e6)
P_UAV = 1

FR_H = 7680
FR_W = 3840

# FOV_THETA = 190
# FOV_PHI = 120

GOP = 50
FOV_CENTRAL_THETA_E = 30
FOV_CENTRAL_THETA_W = -30
FOV_CENTRAL_PHI_N = 30
FOV_CENTRAL_PHI_S = -30
FOV_PERIPHERAL_THETA_E = 60
FOV_PERIPHERAL_THETA_W = -60
FOV_PERIPHERAL_PHI_N = 60
FOV_PERIPHERAL_PHI_S = -75

CENTRAL_WEIGHT = 0.75
PERIPHERAL_WEIGHT = 0.20
OUTSIDE_PERIPHERAL_WEIGHT = 0.05

METRIC_FOV_WEIGHT = 0.95
GAUSSIAN_MINIMUM = 100
MAX_VIEWING_ANGLE_CHANGE = 120 # per second

THETA_H_PRIMES = np.arange(15, 180, 15)
PHI_N_PRIMES = np.arange(15, 90, 15)
PHI_S_PRIMES = np.arange(-90, -15, 15)
CODE_RATE = 1/3

# THETA_H_PRIMES = [60]
# PHI_N_PRIMES = [60]
# PHI_S_PRIMES = [-75]


def getQPABR(prevGoPDR):
    chosenQP = 50
    for qp in QPs:
        # get qpDR
        qpDR = qpModels.getExpectedValue(qp, "FrameSizes")
        # if qpDR < prevGoPDR, return
        if qpDR < prevGoPDR:
            chosenQP = qp
            break
    return chosenQP



def qFunc(arg):
    qVal = 0.5*special.erfc(arg/math.sqrt(2))
    return qVal

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

def evaluate(qualI, qualO, phiSPrime, phiNPrime, thetaHPrime, thetaP, phiP):
    nonPeripheralArea = FOV_PHI*FOV_THETA
    viewPortPrimeArea = 2*thetaHPrime*(phiNPrime - phiSPrime)
    fovCentralArea =  (FOV_CENTRAL_PHI_N - FOV_CENTRAL_PHI_S)*(FOV_CENTRAL_THETA_E - FOV_CENTRAL_THETA_W)
    fovPeripheralArea = (FOV_PERIPHERAL_PHI_N - FOV_PERIPHERAL_PHI_S)*(FOV_PERIPHERAL_THETA_E - FOV_PERIPHERAL_THETA_W)


    viewPortPrimeAreaInsideCentral = getAreaInside([-thetaHPrime, thetaHPrime, phiSPrime, phiNPrime], [thetaP + FOV_CENTRAL_THETA_W, thetaP + FOV_CENTRAL_THETA_E,
                                                    phiP + FOV_CENTRAL_PHI_S, phiP + FOV_CENTRAL_PHI_N])


    viewPortPrimeAreaInsidePeripheral = getAreaInside([-thetaHPrime, thetaHPrime,
                                                       phiSPrime, phiNPrime],
                                                      [thetaP + FOV_PERIPHERAL_THETA_W, thetaP + FOV_PERIPHERAL_THETA_E,
                                                       phiP + FOV_PERIPHERAL_PHI_S, phiP + FOV_PERIPHERAL_PHI_N])

    viewPortPrimeAreaOutsidePeripheral = viewPortPrimeArea - viewPortPrimeAreaInsidePeripheral


    qualityInsideCentral = viewPortPrimeAreaInsideCentral*qualI/fovCentralArea + (fovCentralArea - viewPortPrimeAreaInsidePeripheral)*qualO/fovCentralArea
    qualityInsidePeripheral = (viewPortPrimeAreaInsidePeripheral - viewPortPrimeAreaInsideCentral) * qualI / (fovPeripheralArea - fovCentralArea) + (fovPeripheralArea - fovCentralArea - viewPortPrimeAreaInsidePeripheral + viewPortPrimeAreaInsideCentral) * qualO / (fovPeripheralArea - fovCentralArea)
    qualityOutsidePeripheral = (viewPortPrimeAreaOutsidePeripheral)*qualI/nonPeripheralArea + (nonPeripheralArea - viewPortPrimeAreaOutsidePeripheral)*qualO/nonPeripheralArea

    metric = qualityInsideCentral*CENTRAL_WEIGHT + qualityInsidePeripheral*PERIPHERAL_WEIGHT + qualityOutsidePeripheral*OUTSIDE_PERIPHERAL_WEIGHT

    return metric


def readCSV(fName, dataType=float):
    data = []
    with open(fName, "r") as f:
        csvReader = csv.reader(f, delimiter = ",")
        for row in csvReader:
            if len(row) > 1:
                lineList = []
                for element in row:
                    lineList.append(dataType(element))
                data.append(lineList)
            else:
                data.append(dataType(row[0]))
    return data


# def readPLs(fName):
#     pls = readCSV(fName)
#     return pls

def getMCS5G(snr):
    M = 2
    if snr < 4.2:
        M = 4
    elif snr < 10:
        M = 16
    elif snr < 20:
        M = 64
    else:
        M = 256
    return M
        
    

def generatePLs(uavPositions):
    pls = []
    assocBSs = []
    for uavPosition in uavPositions:
        uavHeight = uavPosition[2]
        minPl = math.inf
        bsIndex = 0
        assocBS = 0
        for bsLocation in BS_LOCATIONs:
            k1 = max(294.05*math.log10(uavHeight) - 432.94, 18)
            k2 = 233.98*math.log10(uavHeight) - 0.95
            l2d = get2DDist(uavPosition, bsLocation)
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
            d = get3DDist(uavPosition, bsLocation)
            pl = 32.4 + 20*math.log10(CENTER_FREQ/1e9) + 10*A*(uavHeight**B)*math.log10(d)
            xFading = np.random.uniform(0, SIGMA)
            pl += xFading
            if pl < minPl:
                minPl = pl
                assocBS = bsIndex
            bsIndex += 1
        minPl = 10.0**(0.1*minPl)
        pls.append(minPl)
        assocBSs.append(assocBS)
    return pls, assocBSs

def logParameters(folderName):
    logStr = "FPS = " + str(FPS)  \
            + "\n Center freq  = " + str(CENTER_FREQ) \
            + "\n Bandwidth  = " + str(B) \
            + "\n P_UAV = " + str(P_UAV)\
             + "\n Alpha = " + str(ALPHA)\
             + "\n THETA_H_PRIMES = " + str(THETA_H_PRIMES) \
            + "\n PHI_N_PRIMES = " + str(PHI_N_PRIMES) \
            + "\n PHI_S_PRIMES = " + str(PHI_S_PRIMES) \
            + "\n QPs = " + str(QPs) \
            + "\n Ms = " + str(Ms) \
            + "\n Center weight = " + str(CENTRAL_WEIGHT)\
            + "\n Peripheral weight = " + str(PERIPHERAL_WEIGHT) \
            + "\n Outside Peripheral Weight = " + str(OUTSIDE_PERIPHERAL_WEIGHT)

    with open(folderName + "parameters.txt", "w") as f:
        f.write(logStr)

def getUAVHeading():
    pass

def getBER(channelSNR, dataRate, M):
    ebNo = channelSNR*B/dataRate
    ber = (4.0/math.log2(M))*(1-1/math.sqrt(M))
    summation = 0
    for i in range( math.ceil(math.sqrt(M)/2)):
        k = i + 1
        summation += qFunc((2*k-1)*math.sqrt(3*ebNo*math.log2(M)/(M-1)))
    ber *= summation
    return ber

def getBER2(channelSNR, mod):
    n = math.log(mod, 2)
    qArg = math.sqrt(3*n*channelSNR/(mod-1))
    ber = 4 / n * (1 - math.sqrt(mod))*qFunc(qArg)
    return ber

def getBER5GNR(snr, M):
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

def getRateFromQP():
    pass

def getPSNRFromQP():
    pass

def getDataRateFromMCS(mod):
    dataRate = B*math.log2(mod)/2.0;
    return dataRate

def get3DDist(pt1, pt2):
    dist = math.sqrt(float(pt1[0] - pt2[0])**2.0 + float(pt1[1] - pt2[1])**2.0 + float(pt1[2] - pt2[2])**2.0)
    return dist

def get2DDist(pt1, pt2):
    dist = math.sqrt(float(pt1[0] - pt2[0])**2.0 + float(pt1[1] - pt2[1])**2.0)
    return dist

def calculateSNR(pathLoss, txPower):
    noise = B*(NOISE_SPECTRAL_DENSITY)
    signal = float(txPower/pathLoss)
    snr = signal / noise
    return snr


def getAreaInside(rectangle, boundary):
    xMinInside = max(rectangle[0], boundary[0])
    xMaxInside = min(rectangle[1], boundary[1])
    yMinInside = max(rectangle[2], boundary[2])
    yMaxInside = min(rectangle[3], boundary[3])
    areaInside = (xMaxInside - xMinInside)*(yMaxInside - yMinInside)
    return areaInside

def generatePositions(v):
    currPos = UAV_START
    positions = [currPos]
    endReached = False
    while endReached == False:
        distToEnd = get3DDist(currPos, UAV_END)
        hop = float(v)/FPS
        if distToEnd < hop:
            endReached = True
            positions.append(UAV_END)
            continue
        else:
            vecToEnd = [UAV_END[0] - currPos[0], UAV_END[1] - currPos[1], UAV_END[2]- currPos[2]]
            mag = math.sqrt(vecToEnd[0]**2.0 + vecToEnd[1]**2.0 + vecToEnd[2]**2.0)
            normVecToEnd = [vecToEnd[0]/mag, vecToEnd[1]/mag, vecToEnd[2]/mag]
            currPos = [currPos[0] + hop*normVecToEnd[0], currPos[1] + hop*normVecToEnd[1], currPos[2] + hop*normVecToEnd[2]]
        positions.append(currPos)
    return positions

def calculateMetric(thetaHPrime, thetaP, thetaPMean, thetaPStd, phiSPrime, phiNPrime, phiP, phiPMean, phiPStd, qualI, qualO):
    viewportPrimeArea = (2*thetaHPrime)*(phiNPrime - phiSPrime)
    fovCentralArea = (FOV_CENTRAL_PHI_N - FOV_CENTRAL_PHI_S)*(FOV_CENTRAL_THETA_E - FOV_CENTRAL_THETA_W)

    fovPeriperhalNStrechted = max(phiP + FOV_PERIPHERAL_PHI_N, phiPMean + 2*phiPStd)
    fovPeripheralSStretched = min(phiP + FOV_PERIPHERAL_PHI_S, phiPMean - 2*phiPStd)
    fovPeripheralWStretched = min(thetaP + FOV_PERIPHERAL_THETA_W, thetaPMean - 2*thetaPStd)
    fovPeripheralEStretched = max(thetaP + FOV_PERIPHERAL_THETA_E, thetaPMean +  2*thetaPStd)

    fovPeripheralArea = (fovPeriperhalNStrechted - fovPeripheralSStretched)*(fovPeripheralEStretched - fovPeripheralWStretched)
    nonPeripheralArea = 360.0*180.0 - fovPeripheralArea


    thetaPMean - 2*thetaPStd
    phiPMean + 2*phiPStd
    phiPMean - 2*phiPStd

    #nonFoVArea = 360.0*180.0 - fovArea

    viewPortPrimeAreaInsideCentral = getAreaInside([thetaP-thetaHPrime, thetaP+thetaHPrime,
                                                    phiP + phiSPrime,  phiP + phiNPrime],
                                                   [thetaP + FOV_CENTRAL_THETA_W, thetaP + FOV_CENTRAL_THETA_E,
                                                    phiP + FOV_CENTRAL_PHI_S, phiP + FOV_CENTRAL_PHI_N])

    viewPortPrimeAreaInsidePeripheral = getAreaInside([thetaP-thetaHPrime, thetaP+thetaHPrime,
                                                       phiP + phiSPrime, phiP + phiNPrime],
                                                      [thetaP + fovPeripheralWStretched, thetaP + fovPeripheralEStretched,
                                                       phiP + fovPeripheralSStretched, phiP + fovPeriperhalNStrechted])

    viewPortPrimeAreaOutsidePeripheral = max(viewportPrimeArea - viewPortPrimeAreaInsidePeripheral, 0)

    qualityInsideCentral = viewPortPrimeAreaInsideCentral*qualI/fovCentralArea + (fovCentralArea - viewPortPrimeAreaInsideCentral)*qualO/fovCentralArea
    qualityInsidePeripheral = (viewPortPrimeAreaInsidePeripheral - viewPortPrimeAreaInsideCentral)*qualI/(fovPeripheralArea - fovCentralArea) + (fovPeripheralArea - fovCentralArea - viewPortPrimeAreaInsidePeripheral + viewPortPrimeAreaInsideCentral)*qualO/(fovPeripheralArea - fovCentralArea)
    qualityOutsidePeripheral = (viewPortPrimeAreaOutsidePeripheral)*qualI/nonPeripheralArea + (nonPeripheralArea - viewPortPrimeAreaOutsidePeripheral)*qualO/nonPeripheralArea

    metric = qualityInsideCentral*CENTRAL_WEIGHT + qualityInsidePeripheral*PERIPHERAL_WEIGHT + qualityOutsidePeripheral*OUTSIDE_PERIPHERAL_WEIGHT

    return metric


def runSNRTestABR2():
    bestMetrics = []
    bestParameterCombinations = []
    snrs = np.arange(0, 40, 1.0)  # dB
    snrsStretched = []
    for snr in snrs:
        for i in range(30):
            snrsStretched.append(snr)

    pilotViewingDirections = generatePilotViewingAngles(len(snrsStretched))
    # pilotViewingDirections = [[33.98, 0], [-10.75, -39.1]]
    phiPHistory = []
    thetaPHistory = []
    tick = 0
    thetaPMean = 0
    phiPMean = 0
    thetaPStd = 0
    phiPStd = 0
    prevGoPBitsRx = 0
    qp = getQPABR(prevGoPBitsRx*FPS/(GOP))
    frameCount = 1
    for snr in snrsStretched:
        if frameCount % GOP == 0:
            qp = getQPABR(prevGoPBitsRx*FPS/(GOP))
            prevGoPBitsRx = 0
            print(qp)
        frameCount += 1
        snrNondB = 10.0 ** (0.1 * snr)
        pilotViewingAngle = pilotViewingDirections[tick]
        thetaP = pilotViewingAngle[0]
        phiP = pilotViewingAngle[1]
        thetaPHistory.append(thetaP)
        phiPHistory.append(phiP)

        m = getMCS5G(snr)

        if len(thetaPHistory) > GAUSSIAN_MINIMUM:
            thetaPMean = np.mean(thetaPHistory)
            thetaPStd = np.std(thetaPHistory)

        if len(phiPHistory) > GAUSSIAN_MINIMUM:
            phiPMean = np.mean(phiPHistory)
            phiPStd = np.std(phiPHistory)

        bestMetric = -1
        bestParameterCombination = []
        start = time.time()
        # thetaHPrime = 60
        # phiNPrime = 60
        # phiSPrime = -75
        bitsReceived = 0
        for thetaHPrime in THETA_H_PRIMES:
            print(thetaHPrime)
            for phiNPrime in PHI_N_PRIMES:
                for phiSPrime in PHI_S_PRIMES:
                    pixelsInside = (2.0 * thetaHPrime * FR_W / 360.0) * (math.fabs(phiNPrime - phiSPrime) *FR_H/ 180.0)
                    pixelsOutside = FR_H * FR_W - pixelsInside
                    percFrLenI = qpModels.getExpectedValue(qp, "FrameSizes") * (pixelsInside) / (
                                pixelsOutside + pixelsInside) * 8
                    percFrLenO = 0
                    percQualI = qpModels.getExpectedValue(qp, "FrameQualities")
                    percQualO = 0
                    r = getDataRateFromMCS(m) * CODE_RATE
                    #ro = getDataRateFromMCS(m) * CODE_RATE

                    FrLatency = percFrLenI /r

                    if FrLatency >= 1.0 / FPS:
                        continue

                    # Check if FrLatency meets the constraint
                    berI = getBER5GNR(snr, m)
                    berO = getBER5GNR(snr, m)

                    # Check if the probability of reception meets the constraint
                    prReceived = ((1 - berI) ** percFrLenI) * ((1 - berO) ** percFrLenO)

                    if prReceived <= ALPHA:
                        continue

                    metric = calculateMetric(thetaHPrime, thetaP, thetaPMean, thetaPStd, phiSPrime,
                                             phiNPrime, phiP, phiPMean, phiPStd, percQualI, percQualO)
                    if metric > bestMetric:
                        bestMetric = metric
                        bestParameterCombination = [thetaHPrime, phiNPrime, phiSPrime, qp, 0, m, 0]
                        bitsReceived = prReceived * percFrLenI

        prevGoPBitsRx += bitsReceived
        end = time.time()
        print("Elapsed time: " + str(end - start))
        bestMetrics.append(bestMetric)
        print(bestMetric)
        bestParameterCombinations.append(bestParameterCombination)
        print(bestParameterCombination)
        print("SNR: ")
        print(snr)
        print("---------")
        tick += 1

    return bestMetrics, bestParameterCombinations, pilotViewingDirections, snrs


def runSNRTestABR():
    bestMetrics = []
    bestParameterCombinations = []
    snrs = np.arange(0, 40, 1.0)  # dB
    snrsStretched = []
    for snr in snrs:
        for i in range(30):
            snrsStretched.append(snr)

    pilotViewingDirections = generatePilotViewingAngles(len(snrsStretched))
    # pilotViewingDirections = [[33.98, 0], [-10.75, -39.1]]
    phiPHistory = []
    thetaPHistory = []
    tick = 0
    thetaPMean = 0
    phiPMean = 0
    thetaPStd = 0
    phiPStd = 0
    prevGoPBitsRx = 0
    qp = getQPABR(prevGoPBitsRx*FPS/(GOP))
    frameCount = 1
    for snr in snrsStretched:
        if frameCount % GOP == 0:
            qp = getQPABR(prevGoPBitsRx*FPS/(GOP))
            prevGoPBitsRx = 0
            print(qp)
        frameCount += 1
        snrNondB = 10.0 ** (0.1 * snr)
        pilotViewingAngle = pilotViewingDirections[tick]
        thetaP = pilotViewingAngle[0]
        phiP = pilotViewingAngle[1]
        thetaPHistory.append(thetaP)
        phiPHistory.append(phiP)

        m = getMCS5G(snr)

        if len(thetaPHistory) > GAUSSIAN_MINIMUM:
            thetaPMean = np.mean(thetaPHistory)
            thetaPStd = np.std(thetaPHistory)

        if len(phiPHistory) > GAUSSIAN_MINIMUM:
            phiPMean = np.mean(phiPHistory)
            phiPStd = np.std(phiPHistory)

        bestMetric = -1
        bestParameterCombination = []
        start = time.time()
        thetaHPrime = 60
        phiNPrime = 60
        phiSPrime = -75
        # for thetaHPrime in THETA_H_PRIMES:
        #     print(thetaHPrime)
        #     for phiNPrime in PHI_N_PRIMES:
        #         for phiSPrime in PHI_S_PRIMES:
        pixelsInside = (2.0 * thetaHPrime * FR_W / 360.0) * (math.fabs(phiNPrime - phiSPrime) *FR_H/ 180.0)
        pixelsOutside = FR_H * FR_W - pixelsInside
        percFrLenI = qpModels.getExpectedValue(qp, "FrameSizes") * (pixelsInside) / (
                    pixelsOutside + pixelsInside) * 8
        percFrLenO = 0
        percQualI = qpModels.getExpectedValue(qp, "FrameQualities")
        percQualO = 0
        r = getDataRateFromMCS(m) * CODE_RATE
        #ro = getDataRateFromMCS(m) * CODE_RATE

        FrLatency = percFrLenI /r

        if FrLatency >= 1.0 / FPS:
            continue

        # Check if FrLatency meets the constraint
        berI = getBER5GNR(snr, m)
        berO = getBER5GNR(snr, m)

        # Check if the probability of reception meets the constraint
        prReceived = ((1 - berI) ** percFrLenI) * ((1 - berO) ** percFrLenO)
        bitsReceived = prReceived*percFrLenI
        prevGoPBitsRx += bitsReceived

        if prReceived <= ALPHA:
            continue

        metric = calculateMetric(thetaHPrime, thetaP, thetaPMean, thetaPStd, phiSPrime,
                                 phiNPrime, phiP, phiPMean, phiPStd, percQualI, percQualO)
        if metric > bestMetric:
            bestMetric = metric
            bestParameterCombination = [thetaHPrime, phiNPrime, phiSPrime, qp, 0, m, 0]

        end = time.time()
        print("Elapsed time: " + str(end - start))
        bestMetrics.append(bestMetric)
        print(bestMetric)
        bestParameterCombinations.append(bestParameterCombination)
        print(bestParameterCombination)
        print("SNR: ")
        print(snr)
        print("---------")
        tick += 1

    return bestMetrics, bestParameterCombinations, pilotViewingDirections, snrs


def runSNRTest():
    bestMetrics = []
    bestParameterCombinations = []
    snrs = np.arange(0, 40, 1.0) # dB
    snrsStretched = []
    prevGoPThroughput = 0
    for snr in snrs:
        for i in range(30):
            snrsStretched.append(snr)

    pilotViewingDirections = generatePilotViewingAngles(len(snrsStretched))
    #pilotViewingDirections = [[33.98, 0], [-10.75, -39.1]]
    phiPHistory = []
    thetaPHistory = []
    tick = 0
    thetaPMean = 0
    phiPMean = 0
    thetaPStd = 0
    phiPStd = 0
    prevGoPThroughput = 0
    frameCount = 1
    for snr in snrsStretched:
        snrNondB = 10.0 ** (0.1 * snr)
        pilotViewingAngle = pilotViewingDirections[tick]
        thetaP = pilotViewingAngle[0]
        phiP = pilotViewingAngle[1]
        thetaPHistory.append(thetaP)
        phiPHistory.append(phiP)

        if len(thetaPHistory) > GAUSSIAN_MINIMUM:
            thetaPMean = np.mean(thetaPHistory)
            thetaPStd = np.std(thetaPHistory)

        if len(phiPHistory) > GAUSSIAN_MINIMUM:
            phiPMean = np.mean(phiPHistory)
            phiPStd = np.std(phiPHistory)

        bestMetric = -1
        bestParameterCombination = []
        start = time.time()
        for thetaHPrime in THETA_H_PRIMES:
            print(thetaHPrime)
            for phiNPrime in PHI_N_PRIMES:
                for phiSPrime in PHI_S_PRIMES:
                    pixelsInside = (2.0*thetaHPrime*FR_W/360.0)*(math.fabs(phiNPrime - phiSPrime)*FR_H/180.0)
                    pixelsOutside = FR_H*FR_W - pixelsInside
                    for qpi in QPs:
                        for qpo in QPs:
                            percFrLenI = qpModels.getExpectedValue(qpi, "FrameSizes")*(pixelsInside)/(pixelsOutside + pixelsInside)*8
                            percFrLenO = qpModels.getExpectedValue(qpo, "FrameSizes")*(pixelsOutside)/(pixelsOutside + pixelsInside)*8
                            percQualI = qpModels.getExpectedValue(qpi, "FrameQualities")
                            percQualO = qpModels.getExpectedValue(qpo, "FrameQualities")
                            for mi in Ms:
                                for mo in Ms:

                                    ri = getDataRateFromMCS(mi)*CODE_RATE
                                    ro = getDataRateFromMCS(mo)*CODE_RATE
                                    
                                    FrLatency = percFrLenI/ri + percFrLenO/ro
                                    
                                    if FrLatency >= 1.0/FPS:
                                        continue
                                    
                                    # Check if FrLatency meets the constraint
                                    berI = getBER5GNR(snr, mi)
                                    berO = getBER5GNR(snr, mo)

                                    # Check if the probability of reception meets the constraint
                                    prReceived = ((1-berI)**percFrLenI)*((1-berO)**percFrLenO)
                                    if prReceived <= ALPHA:
                                        continue

                                    metric = calculateMetric(thetaHPrime, thetaP, thetaPMean, thetaPStd, phiSPrime, phiNPrime, phiP, phiPMean, phiPStd, percQualI, percQualO)
                                    if metric > bestMetric:
                                        bestMetric = metric
                                        bestParameterCombination = [thetaHPrime, phiNPrime, phiSPrime, qpi, qpo, mi, mo]

        end = time.time()
        print("Elapsed time: " + str(end - start))
        bestMetrics.append(bestMetric)
        print(bestMetric)
        bestParameterCombinations.append(bestParameterCombination)
        print(bestParameterCombination)
        print("SNR: ")
        print(snr)
        print("---------")
        tick += 1

    return bestMetrics, bestParameterCombinations, pilotViewingDirections, snrs

def writeCSV(fName, dataArr):
    with open(fName, 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile)
        for data in dataArr:
            writer.writerow([data])

def evaluateResults(parameters, pilotViewingAngles):
    numTicks = len(parameters)
    evaluationMetrics = []
    tickNum = 0
    for parameter in parameters:
        tickNum += 1
        if len(parameter) == 0:
            continue
        pilotViewingAngle = pilotViewingAngles[tickNum]
        qualI = parameter[2]
        qualO = parameter[3]
        thetaHPrime = parameter[0]
        phiSPrime = parameter[0]
        phiNPrime = parameter[1]
        thetaP = pilotViewingAngle[0]
        phiP = pilotViewingAngle[1]
        metric = evaluate(qualI, qualO, phiSPrime, phiNPrime, thetaHPrime, thetaP, phiP)
        evaluationMetrics.append(metric)
    return evaluationMetrics

def main():
    resultsDir = './Results/' + str(time.time()) + '/'
    os.mkdir(resultsDir)
    logParameters(resultsDir)
    bestMetrics, bestParameters, pilotViewingAngles, snrs = runSNRTest()
    #bestMetrics, bestParameters = run()
    writeCSV(resultsDir + 'bestMetrics_Alpha_SNR_Test_' + FNAME_SUFFIX  + '.csv', bestMetrics)
    writeCSV(resultsDir + 'bestParameters_Alpha_SNR_Test_' + FNAME_SUFFIX + '.csv', bestParameters)
    # writeCSV(resultsDir + 'snrs_Alpha' + str(ALPHA) + '.csv', snrs)
    # evaluationMetrics = evaluateResults(bestParameters, pilotViewingAngles)
    # writeCSV('evalMetrics_Alpha' + str(ALPHA) + '_' + str(time.time()) + '.csv', bestMetrics)

    
def run():
    uavPositions = generatePositions(VELOCITY)
    numTicks = len(uavPositions)
    #ls, associatedBSs = generatePLs(uavPositions)
    # pilotViewingAngles = readCSV("pilotViewingAngles.csv")
    #writeCSV("pls.csv", pls)
    #writeCSV("associatedBSs.csv", associatedBSs)
    pls = readCSV("pls.csv")
    associatedBSs = readCSV("associatedBSs.csv", int)
    #pilotViewingAngles = generatePilotViewingAngles(numTicks)
    #writeCSV("pilotViewingAngles.csv", pilotViewingAngles)
    pilotViewingAngles = readCSV("pilotViewingAngles.csv")
    metrics = []
    bestParams = []
    for tick in range(numTicks):
        start = time.time()
        print(tick)
        bestMetric = -1
        bestParameterCombination = None
        thetaP = pilotViewingAngles[tick][0]
        phiP = pilotViewingAngles[tick][1]
        for thetaHPrime in THETA_H_PRIMES:
            #print(thetaHPrime)
            for phiNPrime in PHI_N_PRIMES:
                #print(phiNPrime)
                for phiSPrime in PHI_S_PRIMES:
                    pixelsInside = (2.0*thetaHPrime*FR_W/360.0)*(math.fabs(phiNPrime - phiSPrime)/180.0)
                    pixelsOutside = FR_H*FR_W - pixelsInside
                    for qpi in QPs:
                        for qpo in QPs:
                            percFrLenI = qpModels.getPercentile(qpi, "FrameSizes", ALPHA)*(pixelsInside)/(pixelsOutside + pixelsInside)*10.0**3.0*8
                            percFrLenO = qpModels.getPercentile(qpo, "FrameSizes", ALPHA)*(pixelsOutside)/(pixelsOutside + pixelsInside)*10.0**3.0*8
                            percQualI = qpModels.getPercentile(qpi, "FrameQualities", ALPHA)
                            percQualO = qpModels.getPercentile(qpo, "FrameQualities", ALPHA)
                            for mi in Ms:
                                for mo in Ms:
                                    ri = getDataRateFromMCS(mi)
                                    ro = getDataRateFromMCS(mo)
                                    # ti = percFrLenI/ri
                                    # to = percFrLenO/ro
                                    tP = get3DDist(uavPositions[tick], BS_LOCATIONs[associatedBSs[tick]])/float(3*10.0**8.0)
                                    FrLatency = percFrLenI/ri + percFrLenO/ro + tP
                                    if FrLatency >= 1.0/FPS:
                                        continue

                                    # Check if FrLatency meets the constraint
                                    snr = calculateSNR(pls[tick], P_UAV)
                                    berI = getBER(snr, ri, mi)
                                    berO = getBER(snr, ro, mo)

                                    # Check if the probability of reception meets the constraint
                                    prReceived = ((1-berI)**percFrLenI)*((1-berO)**percFrLenO)
                                    if prReceived <= ALPHA:
                                        continue

                                    metric = calculateMetric(thetaHPrime, thetaP, 0, 0, phiSPrime, phiNPrime, phiP, 0, 0, percQualI, percQualO)
                                    if metric > bestMetric:
                                        bestMetric = metric
                                        bestParameterCombination = [thetaHPrime, phiNPrime, phiSPrime, qpi, qpo, mi, mo]


        end = time.time()
        print("Elapsed time: " + str(end - start))
        metrics.append(bestMetric)
        print(bestMetric)
        print(bestParameterCombination)
        print("SNR: ")
        print(snr)
        print("---------")
        bestParams.append(bestParameterCombination)
    return metrics, bestParameterCombination

main()

