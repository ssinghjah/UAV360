from settings import *
import json
import qpModels

def getAreaInside(rectangle, boundary):
    xMinInside = max(rectangle[0], boundary[0])
    xMaxInside = min(rectangle[1], boundary[1])
    yMinInside = max(rectangle[2], boundary[2])
    yMaxInside = min(rectangle[3], boundary[3])
    areaInside = (xMaxInside - xMinInside)*(yMaxInside - yMinInside)
    return areaInside


def calculateMetric(thetaHPrime, thetaP, phiSPrime, phiNPrime, phiP, qualI, qualO):
    viewportPrimeArea = (2*thetaHPrime)*abs(phiNPrime - phiSPrime)
    fovCentralArea = (FOV_CENTRAL_PHI_N - FOV_CENTRAL_PHI_S)*(FOV_CENTRAL_THETA_E - FOV_CENTRAL_THETA_W)

    fovPeripheralArea = (FOV_PERIPHERAL_PHI_N - FOV_PERIPHERAL_PHI_S)*(FOV_PERIPHERAL_THETA_E - FOV_PERIPHERAL_THETA_W)

    nonPeripheralArea = 360.0*180.0 - fovPeripheralArea
    viewPortPrimeAreaInsideCentral = getAreaInside([-thetaHPrime, thetaHPrime,
                                                    phiSPrime, phiNPrime],
                                                   [thetaP + FOV_CENTRAL_THETA_W, thetaP + FOV_CENTRAL_THETA_E,
                                                    phiP + FOV_CENTRAL_PHI_S, phiP + FOV_CENTRAL_PHI_N])

    viewPortPrimeAreaInsidePeripheral = getAreaInside([-thetaHPrime, thetaHPrime,
                                                       phiSPrime, phiNPrime],
                                                      [thetaP + FOV_PERIPHERAL_THETA_W, thetaP + FOV_PERIPHERAL_THETA_E,
                                                       phiP + FOV_PERIPHERAL_PHI_S, phiP + FOV_PERIPHERAL_PHI_N])

    viewPortPrimeAreaOutsidePeripheral = viewportPrimeArea - viewPortPrimeAreaInsidePeripheral
    qualityInsideCentral = viewPortPrimeAreaInsideCentral*qualI/fovCentralArea + (fovCentralArea - viewPortPrimeAreaInsideCentral)*qualO/fovCentralArea
    qualityInsidePeripheral = (viewPortPrimeAreaInsidePeripheral - viewPortPrimeAreaInsideCentral)*qualI/(fovPeripheralArea - fovCentralArea) + (fovPeripheralArea - fovCentralArea - viewPortPrimeAreaInsidePeripheral + viewPortPrimeAreaInsideCentral)*qualO/(fovPeripheralArea - fovCentralArea)
    qualityOutsidePeripheral = (viewPortPrimeAreaOutsidePeripheral)*qualI/nonPeripheralArea + (nonPeripheralArea - viewPortPrimeAreaOutsidePeripheral)*qualO/nonPeripheralArea

    metric = qualityInsideCentral*CENTRAL_WEIGHT + qualityInsidePeripheral*PERIPHERAL_WEIGHT + qualityOutsidePeripheral*OUTSIDE_PERIPHERAL_WEIGHT

    return metric

def check_constraints(ber_i, ber_o):
    pass

import matplotlib.pyplot as plt

def post_process_frames(frame_path):
    # read frame log line by line
    qoes = []
    bers = []
    prob_received = []
    prob_received_ts = []
    rx_ts = []
    sinrs = []

    capture_ts = []
    with open(frame_path) as f:
        lines = f.readlines()
        for line in lines:
            line_object = json.loads(line)
            print("-----")
            print("Frame:", line_object)
            parameters = line_object["parameters"]
            qualI = qpModels.getExpectedValue("MiamiCity", parameters["qp_i"], "FrameQualities")
            qualO = qpModels.getExpectedValue("MiamiCity", parameters["qp_o"], "FrameQualities")
            qoe_metric = calculateMetric(parameters["theta_h"], 0, parameters["phi_s"], parameters["phi_n"], 0, qualI, qualO)
            print("Capture timestamp:", line_object["capture_timestamp"])
            print("QoE Metric:", qoe_metric)
            print("BER-Inside:", line_object["ber_i"])
            print("BER-Outside:", line_object["ber_o"])
            print("SINR:", line_object["sinr"])

            print("Frame-Latency:", (line_object["display_timestamp"] - line_object["capture_timestamp"]))
            qoes.append(qoe_metric)
            bers.append(line_object["ber_i"])
            sinrs.append(line_object["sinr"])
            capture_ts.append(line_object["capture_timestamp"])
            bits_i = line_object["pixels_i"] * 8.0
            bits_o = line_object["pixels_o"] * 8.0
            prReceived = ((1 - line_object["ber_i"]) ** bits_i) * ((1 - line_object["ber_o"]) ** bits_o)
            prob_received.append(prReceived)
            prob_received_ts.append(line_object["capture_timestamp"])

    plt.plot(capture_ts, qoes)
    plt.yticks(np.arange(30, 35, 0.25))
    plt.grid()
    plt.ylabel("Pilot QoE (dB)")
    plt.xlabel("Capture time (seconds)")
    plt.show()

    plt.plot(prob_received_ts, prob_received)
    plt.grid()
    plt.ylabel("Probability of frame reception")
    plt.xlabel("Capture time (seconds)")
    plt.show()

    plt.plot(prob_received_ts, bers)
    plt.grid()
    plt.ylabel("Bit error rate")
    plt.xlabel("Capture time (seconds)")
    plt.show()

    plt.plot(prob_received_ts, sinrs)
    plt.grid()
    plt.ylabel("SINR")
    plt.xlabel("Capture time (seconds)")
    plt.show()

post_process_frames("/home/simran/Work/UAV360/Code/uav/rx_frames.jsonl")