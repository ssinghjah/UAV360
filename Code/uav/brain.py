import numpy as np
import math
import qp_models
import time

# from settings import *
# from qoe import *


THETA_H_PRIMES = np.arange(15, 180, 15)
PHI_N_PRIMES = np.arange(15, 90, 15)
PHI_S_PRIMES = np.arange(-90, -15, 15)

def get_parameters():
    qp_i = 10
    qp_o = 10
    m_i = 16
    m_o = 16
    theta_h = 60
    theta_n = 20
    theta_s = -60
    return {"theta_h": theta_h,"phi_n": theta_n, "phi_s": theta_s,"qp_i": qp_i, "qp_o": qp_o, "m_i": m_i, "m_o": m_o, "optimization_timestamp": time.time()}

def getDataRateFromMCS(mod):
    dataRate = B*math.log2(mod)/2.0;
    return dataRate

def predictBER(channelSNR, dataRate, M):
    ebNo = channelSNR*B/dataRate
    ber = (4.0/math.log2(M))*(1-1/math.sqrt(M))
    summation = 0
    for i in range( math.ceil(math.sqrt(M)/2)):
        k = i + 1
        summation += qFunc((2*k-1)*math.sqrt(3*ebNo*math.log2(M)/(M-1)))
    ber *= summation
    return ber

def _exhaustiveSearch(snr):
    for thetaHPrime in THETA_H_PRIMES:
        print(thetaHPrime)
        for phiNPrime in PHI_N_PRIMES:
            for phiSPrime in PHI_S_PRIMES:
                pixelsInside = (2.0 * thetaHPrime * FR_W / 360.0) * (math.fabs(phiNPrime - phiSPrime) / 180.0)
                pixelsOutside = FR_H * FR_W - pixelsInside
                for qpi in QPs:
                    for qpo in QPs:
                        percFrLenI = qp_models.getPercentile("MiamiCity", qpi, "FrameSizes", ALPHA) * (pixelsInside) / (
                                    pixelsOutside + pixelsInside) * 10.0 ** 3.0 * 8
                        percFrLenO = qp_models.getPercentile("MiamiCity", qpo, "FrameSizes", ALPHA) * (pixelsOutside) / (
                                    pixelsOutside + pixelsInside) * 10.0 ** 3.0 * 8
                        percQualI = qp_models.getPercentile("MiamiCity", qpi, "FrameQualities", ALPHA)
                        percQualO = qp_models.getPercentile("MiamiCity", qpo, "FrameQualities", ALPHA)
                        for mi in Ms:
                            for mo in Ms:
                                ri = getDataRateFromMCS(mi)
                                ro = getDataRateFromMCS(mo)
                                FrLatency = percFrLenI / ri + percFrLenO / ro
                                if FrLatency >= 1.0 / FPS:
                                    continue

                                # Check if FrLatency meets the constraint
                                berI = predictBER(snr, ri, mi)
                                berO = predictBER(snr, ro, mo)

                                # Check if the probability of reception meets the constraint
                                prReceived = ((1 - berI) ** percFrLenI) * ((1 - berO) ** percFrLenO)
                                if prReceived <= ALPHA:
                                    continue

                                metric = calculateMetric(thetaHPrime, thetaP, thetaPMean, thetaPStd, phiSPrime,
                                                         phiNPrime, phiP, phiPMean, phiPStd, percQualI, percQualO)
                                if metric > bestMetric:
                                    bestMetric = metric
                                    bestParameterCombination = [thetaHPrime, phiNPrime, phiSPrime, qpi, qpo, mi, mo]