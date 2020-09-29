import cv2
import imutils
import time




class Setting:
    """Class create the setting for the Video Class

    Recommended setting in comment for each paramter
    MIN_STIL_FRAME is mainly for motion detection without background frame.
    (for background it recommended to set it as 1 (see background_change() function .)
    
    """

    #The minimum number of frames that need to be count before declare "stop moving"
    #(recomended to be 3 seconds ~ fps* 3)
    MIN_STIL_FRAME = 25*3 #for motion: fps * 3

    #The width size (in pixel) to resize the frame to before analysis.
    RESIZE_WIDTH = 500 #500

    #The minimum threshold (in pixel) for cv2.threshold
    THRESHOLD = 25 #25

    #The minimum size(in pixel) of the detected differences between the frames.
    MIN_DIFF = 80 #100

    #----------------------------
    #For the file.write function 
    writeCSV = None

        


class Video:
    """Main class of motion_detection.

    Receive two or tree array:
    videoPath --> a string containing a video file path.
    fileName  --> a string containing the video name.
    setting   --> a Setting class array, if not given recive the defult Setting().
    """
    def __init__ (self, videoPath, fileName ,setting=Setting()):
        """__init__ function of the Video class.
        Recive video path as a string and setting as a Setting class array.
        Start cv2 VideoCapture for the given video and get the video properties (fps and number of frame).
        """

        #Set the file name
        self.fileName = fileName

##        self.videoPath = videoPath
        
        #Set the setting
        self.setting = setting

        #Start the video capture
        self.video = cv2.VideoCapture(videoPath)

        #Get the fps of the video
        self.fps = self.video.get(cv2.CAP_PROP_FPS)

        #Get the number of frame in the video
        self.frameCount = self.video.get(cv2.CAP_PROP_FRAME_COUNT)

        # cv2 function for fast run
        self.readVideo = self.video.read


    def end_video_capture(self):
        """End the video capture
        also, close imshow() windows if there some open.
        Should be used after calling the Video class.
        """

        #Realse the video (end the video capture)
        self.video.release()

        #Close all the open imshow() windows
        cv2.destroyAllWindows()

    def edit_frame(self, frame):
        """Edit the frame and prepare it to be compare to another frame.
        Recive a frame array (as frame) and return a edited frame array.

        Return the edited frame and the resize frame (needed for display_video()).
        """

        #Resize the frame
        resizeFrame = imutils.resize(frame, width=self.setting.RESIZE_WIDTH)

        # change the frame to gray color
        # 6 = cv2.COLOR_BGR2GRAY
        grayFrame = cv2.cvtColor(resizeFrame, 6)

        # Blur the frame
        newFrame = cv2.GaussianBlur(grayFrame, (21, 21), 0)

        return resizeFrame, newFrame

    def threshold_anlysis(self, frameDelta):
        """Analyze the frames comparison,
        Return the found contours and dilate threshold comparison needed for display_video()).
        """

        #Sift the diferrnt found between the frame (keep only the on above the minimum threshold)
        # 0 = cv2.THRESH_BINARY
        thresh = cv2.threshold(frameDelta,
                               self.setting.THRESHOLD,
                               255,
                               0)[1]

        #Dilate the result
        dilateThresh = cv2.dilate(thresh, None, iterations=2)

        #Find contours and grab them
        # 0 = cv2.RETR_EXTERNAL, 2 = cv2.CHAIN_APPROX_SIMPLE
        cntrsResult = cv2.findContours(dilateThresh.copy(), 0, 2)
        return dilateThresh, cntrsResult[0]
    

    def get_frame(self, flag, frameId, output=None):

        # Check if frameId is frame number or frame time in sec
        if flag:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, frameId-1)
        else:
            self.video.set(cv2.CAP_PROP_POS_MSEC, frameId*1000)
        ret, frame = self.readVideo()
        self.end_video_capture()
        if output!=None:
            cv2.imwrite(output, frame)
        else:
            return frame

    def display_video(self, contours, frames):
        """Display the video and mark all the detected movment in it.

        Recive 2 array:
        contours --> a list with all the found difference
        frames   --> a list of frame (resize dilte and thresh) for display to the user.

        *This function is mainly for testing the code and the function motion_detection()*
        """

        #Start a for loop and go over all the given contour
        for c in contours:

            #Check if the contour biger than the define minimum size (continue if not)
            if cv2.contourArea(c) < self.setting.MIN_DIFF:
                continue

            #Draw quadrangle around the motion area 
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frames[0], (x, y), (x + w, y + h), (255, 0, 0), 3)

        #Use cv2 imshow() to display the frames 
        cv2.imshow("Security Feed", frames[0])
        cv2.imshow("Thresh", frames[1])
        cv2.imshow("Frame Delta", frames[2])
        key = cv2.waitKey(2)

    def getFrame(self, flag, frameId):
        """Get specific frame from the video

        This function get the frame by it's index or by it's time.

        Recive two array:
        flag    --> a boolean array that determine if the ID is index or time.
        frameId --> an intiger of the frame index or time in seconds.

        Return one array-> the frame.
        """

        # Check if frameId is frame number or frame time in sec
        if flag:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, frameId-1)
        else:
            self.video.set(cv2.CAP_PROP_POS_MSEC, frameId*1000)
        ret, frame = self.readVideo()
        return frame
    
    def get_Marked_contours(self, markedImgPath):
        
        markedImg = cv2.imread(markedImgPath)
        
        # Resize the image
        resizeImg = imutils.resize(markedImg, width=self.setting.RESIZE_WIDTH)

        # Change the image to gray color
        grayImg = cv2.cvtColor(resizeImg, cv2.COLOR_BGR2GRAY)

        cntrsResult = cv2.findContours(grayImg, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        cnts = imutils.grab_contours(cntrsResult)

        markCntList = [[False, 0, c] for c in cnts]

        markCntRange = range(len(markCntList))

        return markCntList, markCntRange
        



    def second_to_timer(self, sec):
        """Seconds to timer format.
        This function recive number of second that pass and convert it to timer in the format:
        Hours:Minutes:Seconds.

        Recive one array:
        sec --> int of the number of seconds

        Return one array- string format of the time.
        """
        return time.strftime("%H:%M:%S", time.gmtime(round(sec)))

##    if __name__ == "__main__":
##        pass




def get_folder_videos(folderPath, fileTypeList):
    """Find all the video files in given folder.

    Recive two array:
    folderPath   --> string containing folder path.
    fileTypeList --> list of strings, each contain video file extension.

    Return one array:
    fileNameList --> list of all the video file name found in the folder. 
    """
    import os
    fileList = []
    appendList = fileList.append
    for root, dirs, files in os.walk(folderPath):
        for fileName in files:
            for fileType in fileTypeList:
                if fileName[-len(fileType):] == fileType:
                    appendList([fileName, f'{root}//{fileName}'])
    return fileList


class ScanVideo:
    
    def __init__ (self, outputPath, videoList, setting=Setting()):
        self.csvFile = open(outputPath, 'a')
        self.setting = setting
        self.setting.writeCSV = self.csvFile.write
        self.videoList = videoList
        
    def run_box(self, markedImgPath):
        import motion_detection_box
        self.setting.writeCSV('File Name,Box number,Start,Stop\n')
        for fileName, video in self.videoList:
            motion_detection_box.motion_detection(Video(video, fileName, self.setting), markedImgPath)
        self.csvFile.close()
            
    def run_save(self, videoOutPath, buffer, textCoord=(50,50)):
        import motion_detection_save
        self.setting.writeCSV('File Name,Start,Stop\n')
        firstVideo = self.videoList.pop(0)
        video = Video(firstVideo[1], firstVideo[0], self.setting)
        width = video.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = video.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fourcc = int(video.video.get(cv2.CAP_PROP_FOURCC))
        font = cv2.FONT_HERSHEY_SIMPLEX
        writer = cv2.VideoWriter(videoOutPath, fourcc, video.fps, (int(width), int(height)), True)
        motion_detection_save.motion_detection(video, writer, buffer, textCoord, font)
        for fileName, video in self.videoList:
            motion_detection_save.motion_detection(Video(video, fileName, self.setting),
                                                   writer, buffer, textCoord, font)
        writer.release()
        self.csvFile.close()

    def run_motion(self):
        import motion_detection
        self.setting.writeCSV('File Name,Start,Stop\n')
        for fileName, video in self.videoList:
            motion_detection.motion_detection(Video(video, fileName, self.setting))
        self.csvFile.close()
        
        
        
