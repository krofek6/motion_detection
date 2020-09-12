import motion_detection_box
import time

start_time = time.time()

videoPath = r"C:\Users\krofe\Documents\Python staff\research\athos and porthos.mp4"

imgPath = r"C:\Users\krofe\Documents\Python staff\research\test.png"


output = open('testBox.csv', 'a')
setting = motion_detection_box.Setting()
setting.writeOutput = output.write
setting.writeOutput('File Name,Box Number,Start,Stop\n')
##start_time = time.time()

motion_detection_box.Video('a', videoPath, setting).motion_detection(imgPath)
output.close()
##        
##print("--- %s seconds ---" % (time.time() - start_time))


