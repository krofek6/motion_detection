import cv2
import imutils
import time
import os



class Setting:
    def __init__ (self):
        """Class create the setting for the Video Class

        Recommended setting in comment for each paramter
        MIN_STIL_FRAME is mainly for motion detection without background frame.
        (for background it recommended to set it as 1 (see background_change() function .)
        
        """
##        self.MIN_STIL_FRAME = for background change 1
        self.MIN_STIL_FRAME = 30*3 #for motion: fps * 3
        self.RESIZE_WIDTH = 500 #500
        self.THRESHOLD = 25 #25
        self.MIN_DIFF = 100 #100
    

class Video:
    """Main class of motion_detection.

    Receive one or two array:
    videoPath --> a string cuntaining a video file path.
    setting   --> a Setting class array, if not given recive the defult Setting().
    """
    def __init__ (self, videoPath, setting=Setting()):
        """__init__ function of the Video class.
        Recive video path as a string and setting as a Setting class array.
        Start cv2 VideoCapture for the given video and get the video properties (fps and number of frame).
        """
        #Set the setting
        self.setting = setting

        #Start the video capture
        self.video = cv2.VideoCapture(videoPath)

        #Get the fps of the video
        self.fps = self.video.get(cv2.CAP_PROP_FPS)

        #Get the number of frame in the video
        self.frameCount = self.video.get(cv2.CAP_PROP_FRAME_COUNT)

    def end_video_capture(self):
        """End the video capture
        also, close imshow() windows if there some open.
        Should be used after calling the Video class.
        """

        #Realse the video (end the video capture)
        self.video.release()

        #Close all the open imshow() windows
        cv2.destroyAllWindows()

    def read_frame(self):
        """Read the next frame and return it."""
        ret, frame = self.video.read()
        return frame
    
    def edit_frame(self, frame):
        """Edit the frame and prepare it to be compare to another frame.
        Recive a frame array (as frame) and return a edited frame array.

        Return the edited frame and the resize frame (needed for display_video()).
        """

        #Resize the frame
        resizeFrame = imutils.resize(frame, width=self.setting.RESIZE_WIDTH)

        # change the frame to gray color
        grayFrame = cv2.cvtColor(resizeFrame, cv2.COLOR_BGR2GRAY)

        # Blur the frame
        newFrame = cv2.GaussianBlur(grayFrame, (21, 21), 0)

        return resizeFrame, newFrame

    def threshold_anlysis(self, frameDelta):
        """Analyze the frames comparison,
        Return the found contours and dilate threshold comparison needed for display_video()).
        """

        #Sift the diferrnt found between the frame (keep only the on above the minimum threshold)
        thresh = cv2.threshold(frameDelta,
                               self.setting.THRESHOLD,
                               255,
                               cv2.THRESH_BINARY)[1]

        #Dilate the result
        dilateThresh = cv2.dilate(thresh, None, iterations=2)

        #Find contours and grab them
        cntrsResult = cv2.findContours(dilateThresh.copy(),
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(cntrsResult)
        return dilateThresh, contours
    
    def get_background(self):
        """get the first frame of a given video and edit it.
        This function should be used for "change detection",
        (see background_change().)
        """

        #Read the first frame and edit it
        frame = self.read_frame()
        resizeFrame, backgroundFrame = self.edit_frame(frame)

        #End the capture
        self.end_video_capture()
        return backgroundFrame
        
        

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

    def motion_detection(self, backgroundFrame=None, flagB=False):
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

        #Start a for loop that run according  to the number of frames in the video.
        for i in range(int(self.frameCount)-1):

            #Read the next frame and edit it
            frame = self.read_frame()
            resizeFrame, newFrame = self.edit_frame(frame)

            #Check if it the first frame
            if i==0:

                #Check if need to set background frame (according to the given flag).
                if flagB:

                    #Set background frame
                    preFrame = backgroundFrame

                #If not, set the first frame and continue
                else:
                    preFrame = newFrame
                    continue

            #Analyze the difference between the frames 
            frameDelta = cv2.absdiff(preFrame, newFrame)
            dilateThresh, contours = self.threshold_anlysis(frameDelta)

            #Start a loop for all the found differences
            for c in contours:

                #Check if the difference big enough
                if cv2.contourArea(c) > self.setting.MIN_DIFF:

                    #If it is, reste the no movment counter
                    noMovmentCounter = 0

                    #Check if it a continuation of a movment
                    if not movment:

                        #If not, declare movment and calculate the movment time
                        movment = True
                        sec= index_to_second(i, self.fps)
                        print('start moving {}'.format(second_to_timer(sec)))

                    #Break the loop, (one big enough difference is enough to declare
                    #movment, there is no need to go over the other contours.
                    break
            else:

                #If the loop end without breaking, add 1 to the no movment counter
                noMovmentCounter += 1

            #Display the video for testing
            self.display_video(contours, [resizeFrame, dilateThresh, frameDelta])

            #Check if the movment counter big enough to declare stop moving
            if noMovmentCounter > self.setting.MIN_STIL_FRAME and movment:
                movment = False

                #Calculate the time when the movement stoped
                sec= index_to_second(i, self.fps, self.setting.MIN_STIL_FRAME)
                print('stop moving {}'.format(second_to_timer(sec)))

            #If there not background save the current frame to be compare to the next frame. 
            if not flagB:
                preFrame = newFrame

        #End the capture
        self.end_video_capture()

    def get_background_test(self):
        """only for athos and porthos.mp4"""
        backgroundNumber = int(43*self.fps)
        for i in range(int(self.frameCount)-1):
            frame = self.read_frame()
            if i == backgroundNumber:
                resizeFrame, backgroundFrame = self.edit_frame(frame)
                self.end_video_capture()
                return backgroundFrame


    if __name__ == "__main__":
        pass


def second_to_timer(sec):
    """Seconds to timer format.
    This function recive number of second that pass and convert it to timer in the format:
    Hours:Minutes:Seconds.

    Recive one array:
    sec --> int of the number of seconds

    Return one array- string format of the time.
    """
    return time.strftime("%H:%M:%S", time.gmtime(sec))

def index_to_second(i, fps, buffer=0):
    """Index to seconds
    Caculate the time of the frame by index and fps .
    Recive two to tree array:
    i      --> int of the index of the frame
    fps    --> int of the fps of the video
    buffer --> int of the no movment buffer (0 if not given)
    """
    return (i-buffer)/fps
    
def background_change(backgroundPath, videosPath):
    """Background Change
    Activete the motion_detection() on the Background Change method.
    
    The background video should start with clear frame (without animals)
    and later, by compare the first "clear" frame (the background) to other frames,
    the code will sense change like animal entering or living the frame.

    Recive two array
    backgroundPath --> a string of a full path of a video with a clear first frame.
    videoPath --> list of strings of video files paths
    (recomended to get from get_folder_videos())
    """

    #Get the background frame
    backgroundFrame = Video(backgroundPath).get_background()

    #set the setting 
    setting = Setting()
    setting.MIN_STIL_FRAME = 1

    #Search movment in all the given videos
    for videoPath in videosPath:
        Video(videoPath, setting).motion_detection(backgroundFrame, True)

def get_folder_videos(folderPath, fileTypeList):
    """Find all the video files in given folder.

    Recive two array:
    folderPath   --> string containing folder path.
    fileTypeList --> list of strings, each contain video file extension.

    Return one array:
    fileNameList --> list of all the video file name found in the folder. 
    """
    fileNameList = []
    for fileName in os.listdir(folderPath):
        for fileType in fileTypeList:
            if fileName[-len(fileType):] == fileType:
                fileNameList.append(folderPath + '\\' + fileName)
    return fileNameList
    
    
    
    
