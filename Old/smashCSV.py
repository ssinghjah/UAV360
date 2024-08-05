import csv

fPath  = './Results/ToPlot/bestParameters_Alpha0.99.csv'
fOutput = './Results/ToPlot/bestParameters_Alpha0.99_clean.csv'

rowsFloat = []
with open(fPath, 'r') as f:
    lines = f.readlines()
    for line in lines:
        line = line.strip()
        line = line.replace(' ', '')
        line = line.replace('[', '')
        line = line.replace(']', '')
        line = line.replace('"', '')
        cols = line.split(',')
        fRow = []
        for col in cols:
            fCol = -1 
            try:
                fCol = float(col)
            except Exception as e:
                print(str(e))
                pass
            fRow.append(fCol)
        rowsFloat.append(fRow)

print(rowsFloat)
with open(fOutput, 'w') as f:
    csvWriter = csv.writer(f, delimiter = ',')
    csvWriter.writerows(rowsFloat)
