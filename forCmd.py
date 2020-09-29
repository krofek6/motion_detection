import argparse
import motion_detection_main as md


DESCRIPTION = 'Motion Detection: Scan video files and try to detect all the motion in them.'


parser = argparse.ArgumentParser(description=DESCRIPTION, argument_default=argparse.SUPPRESS)


op = parser.add_argument_group('What to generate')

op.add_argument('-c', '--csv',
                metavar = 'PATH',
                default='Result.csv',
                help = 'Create a CSV file with all the movment time.')


##op.add_argument('-l', '--log',
##                metavar = 'PATH',
##                help = 'Create a log file.')

##op.add_argument('-D', '--dir',
##                metavar = 'PATH',
####                default = 'Result',
##                help = 'Create a folder containing result.csv, log.txt, video.'\
##                       '(default if note -c or -w or -g)')

op.add_argument('-g', '--get_frame',
                metavar = ('ID_TYPE', 'ID', 'FILE', 'PATH'),
                nargs=4,
                help = 'Get frame by ID, ane extract it to an image file.\n'\
                       'FILE - path of a video file, PATH - path for the result image,\n'\
                       'ID_Type can be T for time in seconds, or I for frame index number.\n'\
                       "*NOTE: This may print error like:'[NULL @ 00000000] sps_id 0 out of range'\n")

ip = parser.add_argument_group('Input (use only one of them!)')

ip.add_argument('-r', '--root',
                metavar = ('DIR', 'TYPE'),
                nargs='+',
                help='Search video files in the given folder and scan them.\n'\
                     'Search files that has one of the given types.')

ip.add_argument('-v', '--video',
                metavar = ('FILE_NAME','FILE'),
                nargs=2,
                help='Scan the given video file.')

mod = parser.add_argument_group('Mode (use only one of them!)')

mod.add_argument('-n', '--normal',
                 action = 'store_true',
                 help = 'Detect motion in the given videos.\n'\
                        '(default)')

mod.add_argument('-m', '--marked',
                 metavar = 'FILE',
                 help = 'Detect motion in the given videos in spesific area.\n'\
                        'scan only the marked area in the given image file')
mod.add_argument('-w', '--write',
                 metavar = 'PATH',
                 help = 'Create a video containing all the frame with movment.')


st = parser.add_argument_group('Settings')

st.add_argument('-W', '--width',
                metavar = 'INT',
                type = int,
                help ='The width (in pixel) the frame risize to when analysis.')

st.add_argument('-T', '--threshold',
                metavar = 'THRESHOLD',
                type = int,
                help = 'Minimum threshold.')

st.add_argument('-M', '--minimum_difference',
                metavar = 'MIN_DIFF',
                type = int,
                help = 'Minimum difference (in pixel).')

st.add_argument('-S', '--still_frame',
                metavar = 'MIN_FRAME',
                type = int,
                help = 'Minimum still frame. the code will count frame with no movment and '\
                       'declare that the movment stop after it counter  pass the minimum frames.')

args = parser.parse_args()








def main(args):
    if 'get_frame' in args:
        argList = args.get_frame
        if argList[0].upper() == 'I':
            print('Run get frame by Index,')
            print(f'Get frame number {argList[1]}, from {argList[2]}...')
            md.Video(argList[2]).get_frame(True, int(argList[1]), output=argList[3])
            print(f'Save the frame Successfully as {argList[3]}')
        
        elif argList[0].upper() == 'T':
            print('Run get frame by Time,')
            print(f'Get frame of seconds {argList[1]}, from {argList[2]}...')
            md.Video(argList[2]).get_frame(False, int(argList[1]), output=argList[3])
            print(f'Save the frame Successfully as {argList[3]}')
        else:
            print('Invalid input for get_frame')
        return
    elif 'root' in args:
        root = args.root.pop(0)
        typeList = args.root
        print(f'Scan for video file in {root}...')
        videoList = md.get_folder_videos(root, typeList)
        print(f'Found {len(videoList)} video')
    elif 'video' in args:
        videoList = [args.video]
    else:
        print('Invalid input - need video path')


    setting=md.Setting()
    if 'width' in args:
        print(f'Change width setting to {args.width}')
        setting.RESIZE_WIDTH = args.width
    if 'threshold' in args:
        print(f'Change threshold setting to {args.threshold}')
        setting.THRESHOLD = args.threshold
    if 'minimum_difference' in args:
        print(f'Change minimum difference setting to {args.minimum_difference}')
        setting.MIN_DIFF = args.minimum_difference
    if 'still_frame' in args:
        print(f'Change still frame setting to {args.still_frame}')
        setting.MIN_STIL_FRAME = args.still_frame

    if 'marked' in args:
        print('Run marked motion detection')
        md.ScanVideo(args.csv, videoList, setting=setting).run_box(args.marked)
    elif 'write' in args:
        print('Run write motion detection')
        print(setting.MIN_STIL_FRAME)
        md.ScanVideo(args.csv, videoList, setting=setting).run_save(args.write, setting.MIN_STIL_FRAME)
    else:
        print('Run normal motion detection')
        md.ScanVideo(args.csv, videoList, setting=setting).run_motion()
        print(f'Finished runing Successfully')
        
if __name__ == "__main__":
    main(args)


