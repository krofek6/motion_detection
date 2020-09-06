import motion_detection


##videoPath = r"C:\Users\krofe\Documents\Python staff\research\111\00000.MTS"

##motion_detection.Video(videoPath).motion_detection()

folderPath = r"C:\Users\krofe\Desktop\python\Aein_baseline1_7.6.20"
fileTypeList = ['MTS']
outputPath = r"C:\Users\krofe\Desktop\python\Aein_baseline1_7.6.20.csv"
videoList = motion_detection.get_folder_videos(folderPath, fileTypeList)
motion_detection.write_to_CSV(outputPath, videoList)


