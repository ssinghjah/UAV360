import csv
import math

import numpy as np

Data = {}

QPs = np.arange(10, 55, 5)
Locations = ["Chicago"]
RootPath = "./Results/Models/"
LOCATION = "Chicago"

def readCSV(fileName):
    csvData = []
    f = open(fileName, "r")
    lines = f.readlines()
    f.close()
    for line in lines:
        if ',' in line:
            dataArr = line.split(',')
            for data in dataArr:
                if not math.isinf(float(data)):
                    csvData.append(float(data))
        else:
            csvData.append(float(line))
    return csvData

def writeCSV(fName, dataArr):
    with open(fName, 'w', newline='\n') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(dataArr)

def fillDataStructure():
    for location in Locations:
        Data[location] = {}
        for qp in QPs:
            Data[location][qp] = {}
            # open file
            fName = RootPath + location + "_frameSizes_QP_" + str(qp) + ".csv"
            frameSizes = readCSV(fName)
            fName = RootPath + location + "_frameSNRs_QP_" + str(qp) + ".csv"
            frameQuals = readCSV(fName)
            qpInfoObject = {"FrameSizes": frameSizes, "FrameQualities": frameQuals}
            Data[location][qp] = qpInfoObject

def getPercentile(qp, measurement, percentile):
    if math.isinf(qp):
        return 0
    qpInfo = Data[LOCATION][qp]
    measurements = qpInfo[measurement]
    measurements.sort()
    index = math.ceil(len(measurements)*percentile)
    value = measurements[index]
    return value

def getExpectedValue(qp, measurement, percentile):
    if math.isinf(qp):
        return 0
    qpInfo = Data[LOCATION][qp]
    measurements = qpInfo[measurement]
    value = np.mean(measurements)
    return value

fillDataStructure()
