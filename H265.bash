ffmpeg -i <input> -c:v rawvideo -pixel_format 420p <output>
x265 --input <input> --output <output> --fps 30 --input-res 1920x1080 --qp <QP> --min-keyint <GOP> --keyint <GOP>
ffmpeg -i <toTest> -i <reference> -lavfi psnr=stats_file=<log-file> -f null -
ffmpeg -f rawvideo -pix_fmt yuv420p -s:v 1920x1080  -i Source/sample-5s.yuv -c:v libx265 outputQP10_GOP10.mp4 -g 10 -x265-params "--qp 16"
