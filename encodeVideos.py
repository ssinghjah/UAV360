import os
import ffmpeg

# List of all source videos
#SourceFiles = ['Armenia_8K_Trim', 'Hawaii_8K_Trim', 'HollandWidmill_4K_Trim', 'HuangshanChina_8K_Trim', 'Jerusalem_8K_Trim', 'Tokyo_8K_Trim', 'Zurich_4K_Trim']

SourceFiles = ['HollandWindmill_4K_Trim']

# List of QP values
QPs = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]

# List of metrics
Metrics = []

GOP = 50

SOURCE_FOLDER = '/home/Source'
ENCODED_FOLDER = '/home/Encoded'
METADATA_FOLDER = '/home/MetaData'
FORMATs = ['.mp4', '.webm', '.yuv']

def getResolutionFPS(probe):
    resolution = ''
    fps = ''
    for stream in probe['streams']:
        if stream['codec_type'] == 'video':
            resolution = str(stream['width']) + 'x' + str(stream['height'])
            fpsTerms = stream['r_frame_rate'].split('/')
            fps = float(fpsTerms[0])/float(fpsTerms[1])
            return resolution, str(fps)

def getSourceFilePath(locationName):
    candidatePath = ""
    for vidFormat in FORMATs:
        candidatePath = SOURCE_FOLDER + '/' + locationName + vidFormat
        if(os.path.isfile(candidatePath)):
            return candidatePath

# Iterate over all source videos
for locationName in SourceFiles:
    print("-------------")
    print(locationName)
    yuvFile = SOURCE_FOLDER + '/' + locationName + '.yuv'
    sourceFilePath = getSourceFilePath(locationName)

    probe = ffmpeg.probe(sourceFilePath)
    resolution, fps = getResolutionFPS(probe)
    print(resolution, fps)

    if (not os.path.isfile(yuvFile)):
        # convert to .yuv, if file does not exist
        os.system('ffmpeg -i ' + sourceFilePath + ' -c:v rawvideo -pixel_format 420p ' + yuvFile)
        
    #os.system('ffmpeg -f rawvideo -vcodec rawvideo -s ' + resolution + '-r ' + fps +  '-pix_fmt yuv420p -i ' + yuvFile + '-c:v libx265 --tune zerolatency -qp 0 ' + SOURCE_FOLDER + '/' + locationName + '.mp4' )
        
    for qp in QPs:
        # Re-encode at all QPs
        os.system('x265 --tune zerolatency  --input ' + SOURCE_FOLDER + '/' + locationName + '.yuv --output ' + ENCODED_FOLDER + '/' + locationName + '_' + str(qp) + '.mp4 --fps ' + str(fps) +  ' --input-res ' + resolution +  ' --qp ' + str(qp) + ' --keyint ' + str(GOP) + ' --min-keyint '+ str(GOP))

        # Calculate PSNR metric
        os.system('ffmpeg -i ' + ENCODED_FOLDER + '/' +  locationName + '_' + str(qp)  + '.mp4 -s ' + resolution + ' -i ' + SOURCE_FOLDER + '/' + locationName + '.yuv -s ' + resolution + ' -lavfi psnr=stats_file=' + METADATA_FOLDER + '/' + locationName + '_psnr_' + str(qp)  + '.txt -f null -')
    
        # display byte size of all frames
        fPath = ENCODED_FOLDER + '/' + locationName + '_' + str(qp) + '.mp4'
        os.system('ffprobe ' + fPath + ' -v error -select_streams V:0 -show_entries "frame=pict_type,pkt_size" -of csv=p=0 >' + METADATA_FOLDER  + '/frameInfo_' + locationName + '_' + str(qp) + '.csv')
    #os.system("rm -r " + yuvFile)
