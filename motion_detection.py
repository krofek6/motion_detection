import cv2
import imutils
import time
##import numpy as np


class Setting:
    def __init__ (self):
        """Class create the setting for the Video Class

        Recommended setting in comment for each paramter
        MIN_STIL_FRAME is mainly for motion detection without background frame.
        (for background it recommended to set it as 1 (see background_change() function .)
        
        """
        self.MIN_STIL_FRAME = 25*3 #for motion: fps * 3
        self.RESIZE_WIDTH = 500 #500
        self.THRESHOLD = 25 #25
        self.MIN_DIFF = 80 #100
        self.writeOutput = None
        self.writeToCSV = False
##        self.outputFile = None
##        self.displayVideo = True
        


class Video:
    """Main class of motion_detection.

    Receive one or two array:
    videoPath --> a string cuntaining a video file path.
    setting   --> a Setting class array, if not given recive the defult Setting().
    """
    def __init__ (self, fileName, videoPath ,setting=Setting()):
        """__init__ function of the Video class.
        Recive video path as a string and setting as a Setting class array.
        Start cv2 VideoCapture for the given video and get the video properties (fps and number of frame).
        """
        self.fileName = fileName

        self.videoPath = videoPath
        
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
    

    def getFrame(self, flag, frameId):

        # Check if frameId is frame number or frame time in sec
        if flag:
            self.video.set(cv2.CAP_PROP_POS_FRAMES, frameId-1)
        else:
            self.video.set(cv2.CAP_PROP_POS_MSEC, frameId*1000)
        ret, frame = self.readVideo()
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


    def motion_detection(self):
        """Main function of the Video class.

        This function can work in two different way:
        
        Motion detection- analyze the diffrence between each frame and the previous frame.
        With this way the function detect movment and not change.
        For example, if an animal will relatively stay still in the frame,
        the function will not detect it.
        In addition, the function look for at least one significant diffrence between the
        frames, and try to decide if there's a movment, so if there one movment or several
        movments (simultaneously) the function will return the same value.

        Background change detection- analyze the diffrence between the given  backgound
        frame and all the othere frames.
        With this way the function detect change from the "clear" frame (the background frame)
        and not movment.
        For example, if an animal will relatively stay still or move in the frame, the
        function will sense it as "movment".
        In addition, the function look for at least one significant diffrence between the
        frames, and try to decide if there's a change, so if there one diffrence or several
        diffrence (simultaneously) from the background frame, the function will return the
        same value.
        """
        
        #Set the the movment counter and movment flag
        noMovmentCounter = 0
        movment = False

        # Read the first frame, edit it and set it as preFrame.
        ret, frame = self.readVideo()
        resizeFrame, newFrame = self.edit_frame(frame)
        preFrame = newFrame

        #Start a for loop that run according  to the number of frames in the video.
        #+ NOTE: frameCount usually doesn't get the correct number of frames! +
        for i in range(1,int(self.frameCount-2)):

            #Read the next frame and edit it
            ret, frame = self.readVideo()

            # Check if the frame exists, if not break the loop because video end
            if not ret:
                break
            
            resizeFrame, newFrame = self.edit_frame(frame)
            
            #Analyze the difference between the frames 
            frameDelta = cv2.absdiff(preFrame, newFrame)
            dilateThresh, contours = self.threshold_anlysis(frameDelta)


            #Start a loop for all the found differences
            for c in contours:

                #Check if the difference big enough

                if cv2.contourArea(c) > self.setting.MIN_DIFF:

                    #If it is, reste the no movment counter
                    noMovmentCounter = 0

                    #Check if it a continuation of movment
                    if not movment:

                        #If not, declare movment and calculate the movment time in seconds
                        movment = True
                        # 0 = cv2.CAP_PROP_POS_MSEC
                        sec = self.video.get(0)/1000

                        #Convert the time from seconds to string and save it
                        timer = self.second_to_timer(sec)
                        startTime = timer

                    #Break the loop (one difference is enough to declare movment
                    break

            else:

                #If the loop end without breaking, check if movment
                if movment:
                    
                    #Save the time when the movment first stop.
                    if noMovmentCounter==0:
                        # 0 = cv2.CAP_PROP_POS_MSEC
                        msec = self.video.get(0)

                    #Add 1 to the no movment counter
                    noMovmentCounter += 1

                    #Check if the movment counter big enough to declare stop moving
                    if noMovmentCounter > self.setting.MIN_STIL_FRAME:
                        movment = False

                        #Calculate the time when the movement stoped
                        sec = msec/1000
                        timer = self.second_to_timer(sec)
                        stopTime = timer

                        #Write the start and the stop time of the movment
                        self.setting.writeOutput(f'{self.fileName},{startTime},{stopTime}\n')
                    
            # for display video, delete the # in the next line
            #self.display_video(contours, [resizeFrame, dilateThresh, frameDelta])

            #Save the frame to compare to the next frame
            preFrame = newFrame

        #End the video capture
        self.end_video_capture()

        
    def second_to_timer(self, sec):
        """Seconds to timer format.
        This function recive number of second that pass and convert it to timer in the format:
        Hours:Minutes:Seconds.

        Recive one array:
        sec --> int of the number of seconds

        Return one array- string format of the time.
        """
        return time.strftime("%H:%M:%S", time.gmtime(round(sec)))

    if __name__ == "__main__":
        pass






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



def write_to_CSV(outputPath, videoList):
    output = open(outputPath, 'a')
    setting = Setting()
    setting.writeOutput = output.write
    setting.writeOutput('File Name,Start,Stop\n')
    for fileName, video in videoList:
        Video(fileName, video, setting).motion_detection()
    output.close()
        
