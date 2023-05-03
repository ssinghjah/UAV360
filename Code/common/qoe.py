from settings import *

def getAreaInside(rectangle, boundary):
    xMinInside = max(rectangle[0], boundary[0])
    xMaxInside = min(rectangle[1], boundary[1])
    yMinInside = max(rectangle[2], boundary[2])
    yMaxInside = min(rectangle[3], boundary[3])
    areaInside = (xMaxInside - xMinInside)*(yMaxInside - yMinInside)
    return areaInside


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