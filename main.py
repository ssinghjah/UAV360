import math
from scipy import special
import random
import numpy as np
import sys
import qpModels
import time
import csv
import os

CENTER_FREQ = 28*10^9
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
#BS_LOCATIONs = [ [500, 250, 0],  [500, 250, 0], [500, 500, 0],  [500, 750, 0]]
BS_LOCATIONs = [[0, 250, 0], [0, 500, 0], [0, 750, 0], [0, 1000, 0],
                [250, 250, 0], [250, 500, 0], [250, 750, 0], [250, 1000, 0],
                [500, 250, 0], [500, 500, 0], [500, 750, 0], [500, 1000, 0],
                [750, 250, 0], [750, 500, 0], [750, 750, 0], [750, 1000, 0],
                [1000, 250, 0],  [1000, 250, 0], [1000, 500, 0], [1000, 750, 0]]
QPs = [10, 20, 40, 50]
Ms = [2, 4, 8, 16, 32]
ALPHA = 0.80
NOISE_SPECTRAL_DENSITY = 1.380649*10.0**(-23.0)*298;
B = float(400e6)
P_UAV = 1

FR_H = 1080
FR_W = 1920

# FOV_THETA = 190
# FOV_PHI = 120

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
        #pilotViewingDirections.append([theta, phi])
        pilotViewingDirections.append([0, 0])
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
                B = -0.07
                SIGMA = 3.60
            d = get3DDist(uavPosition, bsLocation)
            pl = 32.4 + 20*math.log10(CENTER_FREQ) + 10*A*(uavHeight**B)*math.log10(d)
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
    logStr = "FPS = " + str(FPS) \
             + "\n Bandwidth  = " + str(B) \
             + "\n P_UAV = " + str(P_UAV) \
             + "\n THETA_H_PRIMES = " + str(THETA_H_PRIMES) \
             + "\n PHI_N_PRIMES = " + str(PHI_N_PRIMES) \
             + "\n PHI_S_PRIMES = " + str(PHI_S_PRIMES) \
             + "\n QPs = " + str(QPs) \
             + "\n Ms = " + str(Ms) \
             + "\n ALPHA = " + str(ALPHA)

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
    return

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

    viewPortPrimeAreaInsideCentral = getAreaInside([-thetaHPrime, thetaHPrime,
                                                    phiSPrime, phiNPrime],
                                                   [thetaP + FOV_CENTRAL_THETA_W, thetaP + FOV_CENTRAL_THETA_E,
                                                    phiP + FOV_CENTRAL_PHI_S, phiP + FOV_CENTRAL_PHI_N])

    viewPortPrimeAreaInsidePeripheral = getAreaInside([-thetaHPrime, thetaHPrime,
                                                       phiSPrime, phiNPrime],
                                                      [thetaP + fovPeripheralWStretched, thetaP + fovPeripheralEStretched,
                                                       phiP + fovPeripheralSStretched, phiP + fovPeriperhalNStrechted])

    viewPortPrimeAreaOutsidePeripheral = viewportPrimeArea - viewPortPrimeAreaInsidePeripheral

    qualityInsideCentral = viewPortPrimeAreaInsideCentral*qualI/fovCentralArea + (fovCentralArea - viewPortPrimeAreaInsideCentral)*qualO/fovCentralArea
    qualityInsidePeripheral = (viewPortPrimeAreaInsidePeripheral - viewPortPrimeAreaInsideCentral)*qualI/(fovPeripheralArea - fovCentralArea) + (fovPeripheralArea - fovCentralArea - viewPortPrimeAreaInsidePeripheral + viewPortPrimeAreaInsideCentral)*qualO/(fovPeripheralArea - fovCentralArea)
    qualityOutsidePeripheral = (viewPortPrimeAreaOutsidePeripheral)*qualI/nonPeripheralArea + (nonPeripheralArea - viewPortPrimeAreaOutsidePeripheral)*qualO/nonPeripheralArea

    metric = qualityInsideCentral*CENTRAL_WEIGHT + qualityInsidePeripheral*PERIPHERAL_WEIGHT + qualityOutsidePeripheral*OUTSIDE_PERIPHERAL_WEIGHT

    return metric


def runSNRTest():
    bestMetrics = []
    bestParameterCombinations = []
    snrs = np.arange(0, 30, 1)
    pilotViewingDirections = generatePilotViewingAngles(len(snrs))
    #pilotViewingDirections = [[33.98, 0], [-10.75, -39.1]]
    phiPHistory = []
    thetaPHistory = []
    tick = 0
    thetaPMean = 0
    phiPMean = 0
    thetaPStd = 0
    phiPStd = 0
    for snr in snrs:
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
                    pixelsInside = (2.0*thetaHPrime*FR_W/360.0)*(math.fabs(phiNPrime - phiSPrime)/180.0)
                    pixelsOutside = FR_H*FR_W - pixelsInside
                    for qpi in QPs:
                        for qpo in QPs:
                            percFrLenI = qpModels.getPercentile("MiamiCity", qpi, "FrameSizes", ALPHA)*(pixelsInside)/(pixelsOutside + pixelsInside)*10.0**3.0*8
                            percFrLenO = qpModels.getPercentile("MiamiCity", qpo, "FrameSizes", ALPHA)*(pixelsOutside)/(pixelsOutside + pixelsInside)*10.0**3.0*8
                            percQualI = qpModels.getPercentile("MiamiCity", qpi, "FrameQualities", ALPHA)
                            percQualO = qpModels.getPercentile("MiamiCity", qpo, "FrameQualities", ALPHA)
                            for mi in Ms:
                                for mo in Ms:
                                    ri = getDataRateFromMCS(mi)
                                    ro = getDataRateFromMCS(mo)
                                    FrLatency = percFrLenI/ri + percFrLenO/ro
                                    if FrLatency >= 1.0/FPS:
                                        continue

                                    # Check if FrLatency meets the constraint
                                    berI = getBER(snr, ri, mi)
                                    berO = getBER(snr, ro, mo)

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
            writer.write(data)

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
    writeCSV(resultsDir + 'bestMetrics_Alpha' + str(ALPHA) + '.csv', bestMetrics)
    writeCSV(resultsDir + 'bestParameters_Alpha' + str(ALPHA) + '.csv', bestParameters)
    writeCSV(resultsDir + 'snrs_Alpha' + str(ALPHA) + '.csv', snrs)
    # evaluationMetrics = evaluateResults(bestParameters, pilotViewingAngles)
    # writeCSV('evalMetrics_Alpha' + str(ALPHA) + '_' + str(time.time()) + '.csv', bestMetrics)

    
def run():
    uavPositions = generatePositions(VELOCITY)
    numTicks = len(uavPositions)
    pls, associatedBSs = generatePLs(uavPositions)
    pilotViewingAngles = generatePilotViewingAngles(numTicks)
    metrics = []
    bestParams = []
    for tick in range(numTicks):
        start = time.time()
        print(tick)
        bestMetric = -1
        bestParameterCombination = None
        for thetaHPrime in THETA_H_PRIMES:
            thetaHPrime
            for phiNPrime in PHI_N_PRIMES:
                phiNPrime
                for phiSPrime in PHI_S_PRIMES:
                    pixelsInside = (2.0*thetaHPrime*FR_W/360.0)*(math.fabs(phiNPrime - phiSPrime)/180.0)
                    pixelsOutside = FR_H*FR_W - pixelsInside
                    for qpi in QPs:
                        for qpo in QPs + [math.inf]:
                            percFrLenI = qpModels.getPercentile("MiamiCity", qpi, "FrameSizes", ALPHA)*(pixelsInside)/(pixelsOutside + pixelsInside)*10.0**3.0*8
                            percFrLenO = qpModels.getPercentile("MiamiCity", qpo, "FrameSizes", ALPHA)*(pixelsOutside)/(pixelsOutside + pixelsInside)*10.0**3.0*8
                            percQualI = qpModels.getPercentile("MiamiCity", qpi, "FrameQualities", ALPHA)
                            percQualO = qpModels.getPercentile("MiamiCity", qpo, "FrameQualities", ALPHA)
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

                                    metric = calculateMetric(thetaHPrime, phiSPrime, phiNPrime, percQualI, percQualO)
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

