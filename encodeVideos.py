import os

# Define GoP
GoP = 30

# List of all source videos
SourceFiles = ['Ven', 'Miami']

# List of QP values
QPs = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
QPs = [0, 5]
# List of metrics
Metrics = []

GOP = 50

SOURCE_FOLDER = './Source'
ENCODED_FOLDER = './Encoded'
RESOLUTION = '1920x1080'

# Iterate over all source videos
for sourceFile in SourceFiles:

    yuvFile = SOURCE_FOLDER + '/' + sourceFile + '.yuv'
    if (not os.path.isfile(yuvFile)):
        # convert to .yuv, if file does not exist
        os.system('ffmpeg -i ' + SOURCE_FOLDER + '/' +  sourceFile + '.mp4 -c:v rawvideo -pixel_format 420p ' + yuvFile)
    for qp in QPs:
        # Re-encode at all QPs
        os.system('x265 --input ' + SOURCE_FOLDER + '/' + sourceFile + '.yuv --output ' + ENCODED_FOLDER + '/' + sourceFile + '_' + str(qp) + '.mp4 --fps 30 --input-res ' + RESOLUTION +  ' --qp ' + str(qp) + ' --keyint ' + str(GOP) + ' --min-keyint '+ str(GOP))
        # Calculate metric
        os.system('ffmpeg -i ' + ENCODED_FOLDER + '/' +  sourceFile + '_' + str(qp)  + '.mp4 -i ' + SOURCE_FOLDER + '/' + sourceFile + '.mp4 -lavfi psnr=stats_file=' + ENCODED_FOLDER + '/' + sourceFile + '_psnr_' + str(qp)  + '.txt -f null -')
    
        # display byte size of all frames
        fPath = './Encoded/' + sourceFile + '_' + str(qp) + '.mp4'
        os.system('ffprobe ' + fPath + ' -v error -select_streams V:0 -show_entries "frame=pict_type,pkt_size" -of csv=p=0 >frameInfo_' + sourceFile + '_' + str(qp) + '.csv')
