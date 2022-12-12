import re
import csv
import numpy as np
import math

def writeCSVFile(csvFileName, data):
    with open(csvFileName, 'w', encoding='UTF8') as f:
        # create the csv writer
        writer = csv.writer(f)
        # write a row to the csv file
        writer.writerow(data)

PSNR_INF = 250
folder = './Encoded/'
videoFNames = ['Miami', 'Ven']
QPs = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
for videoFName in videoFNames:
    qpMeans = []
    for QP in QPs:
        fPath = folder + videoFName + '_psnr_' + str(QP) + '.txt'
        qpPSNRs = []
        # read file
        with open(fPath) as f:
            lines = [line.rstrip() for line in f]
            for line in lines:
                psnrReg = str(re.escape('psnr_avg:'))
                emptySpaceReg = str(re.escape('psnr_y'))
                psnr = float(re.findall(psnrReg+"(.*)" + emptySpaceReg, line)[0])
                qpPSNRs.append(psnr)
                #if not math.isinf(psnr):
                #    qpPSNRs.append(psnr)

            writeCSVFile(folder + videoFName + '_' + str(QP) + '.csv', qpPSNRs)
        '''
        qpMeans.append(np.mean(qpPSNRs))
        csvFileName = folder + videoFName + '_PSNRs.csv'
        with open(csvFileName, 'w', encoding='UTF8') as f:
            # create the csv writer
            writer = csv.writer(f)
            # write a row to the csv file
            writer.writerow(qpMeans)
        '''
        

