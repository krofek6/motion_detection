# Regular motion detection-
# Create CSV file with the times of the deected motion. 
import cv2

def motion_detection(video):
    """The main function of motion_detection.
    Detect motion in the given video,
    Compairing the diffrence between each frame and the previous frame.

    Recive one array:
    video --> a Video class array.

    Write the result to csv.
    """
        
    #Set the the movment counter and movment flag
    #noMovmentCounter: count the number of frame with no movment in row. 
    noMovmentCounter = 0
    #movment: if true -> movment was detected in the previous frames.
    movment = False

    #Read the first frame, edit it and set it as preFrame.
    ret, frame = video.readVideo()
    resizeFrame, newFrame = video.edit_frame(frame)
    preFrame = newFrame

    #Start a for loop that run according  to the number of frames in the video.
    #+ NOTE: frameCount usually doesn't get the correct number of frames! +
    for i in range(1,int(video.frameCount+10)):

        #Read the next frame
        ret, frame = video.readVideo()

        # Check if the frame exists, if not break the loop because video end
        if not ret:

            #Check if the video end during a movement 
            if movment:

                #Write the movmet
                stopTime = 'Video End'
                video.setting.writeCSV(f'{video.fileName},{startTime},{stopTime}\n')
            break

        #Edit the next frame and set it as newFrame.
        resizeFrame, newFrame = video.edit_frame(frame)
            
        #Analyze the difference between the frames 
        frameDelta = cv2.absdiff(preFrame, newFrame)
        dilateThresh, contours = video.threshold_anlysis(frameDelta)


        #Start a loop for all the found differences
        for c in contours:

            #Check if the difference big enough

            if cv2.contourArea(c) > video.setting.MIN_DIFF:

                #If it is, reset the no movment counter
                noMovmentCounter = 0

                #Check if it a continuation of movment
                if not movment:

                    #If not, declare movment and calculate the movment time in seconds
                    movment = True
                    # 0 = cv2.CAP_PROP_POS_MSEC
                    sec = video.video.get(0)/1000

                    #Convert the time from seconds to string and save it
                    timer = video.second_to_timer(sec)
                    startTime = timer

                #Break the loop (one difference is enough to declare movment
                break

        else:

            #If the loop end without breaking, check if movment
            if movment:
                    
                #Save the time when the movment first stop.
                if noMovmentCounter==0:
                    # 0 = cv2.CAP_PROP_POS_MSEC
                    msec = video.video.get(0)

                #Add 1 to the no movment counter
                noMovmentCounter += 1

                #Check if the movment counter big enough to declare stop moving
                if noMovmentCounter > video.setting.MIN_STIL_FRAME:
                    movment = False

                    #Calculate the time when the movement stoped
                    sec = msec/1000
                    timer = video.second_to_timer(sec)
                    stopTime = timer

                    #Write the start and the stop time of the movment
                    video.setting.writeCSV(f'{video.fileName},{startTime},{stopTime}\n')
                    
        # for display video, delete the # in the next line
        #video.display_video(contours, [resizeFrame, dilateThresh, frameDelta])

        #Save the frame to compare to the next frame
        preFrame = newFrame

    #End the video capture
    video.end_video_capture()

