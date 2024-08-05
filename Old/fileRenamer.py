import os
from os import walk

FOLDER = "./Results/Models/"
for (dirpath, dirnames, filenames) in walk(FOLDER):
    for fileName in filenames:
        if '_4K_Trim_' in fileName:
            newFileName = fileName.replace("_4K_Trim_", "_")
            print(newFileName)
            os.rename(FOLDER + fileName, FOLDER + newFileName)
        elif '_8K_Trim_' in fileName:
            newFileName = fileName.replace("_8K_Trim_", "_")
            print(newFileName)
            os.rename(FOLDER + fileName, FOLDER + newFileName)
        elif '_Trim_' in fileName:
            newFileName = fileName.replace("_Trim_", "_")
            print(newFileName)
            os.rename(FOLDER + fileName, FOLDER + newFileName)
        elif 'LakeShibara' in fileName:
            newFileName = fileName.replace("LakeShibara", "LakeHibara")
            print(newFileName)
            os.rename(FOLDER + fileName, FOLDER + newFileName)



