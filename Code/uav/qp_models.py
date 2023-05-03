import numpy as np
import csv
import math

QPs = np.arange(10, 55, 5)
Locations = ["MiamiCity", "AngelFalls"]
RootPath = "./Release/"
Data = {}

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
            fName = RootPath + location + "/frameSizes_QP_" + str(qp) + ".csv"
            frameSizes = readCSV(fName)
            fName = RootPath + location + "/frameSNRs_QP_" + str(qp) + ".csv"
            frameQuals = readCSV(fName)
            qpInfoObject = {"FrameSizes": frameSizes, "FrameQualities": frameQuals}
            Data[location][qp] = qpInfoObject


def getPercentile(location, qp, measurement, percentile):
    if math.isinf(qp):
        return 0
    qpInfo = Data[location][qp]
    measurements = qpInfo[measurement]
    measurements.sort()
    index = math.ceil(len(measurements)*percentile)
    value = measurements[index]
    value = np.mean(measurements)
    return value

fillDataStructure()