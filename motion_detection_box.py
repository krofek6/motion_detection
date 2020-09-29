import cv2
import imutils
import time
##import numpy as np

def motion_detection(video, markedImgPath):
    markCntList, markCntRange = video.get_Marked_contours(markedImgPath)

    # Read the first frame, edit it and set it as preFrame.
    ret, frame = video.readVideo()
    resizeFrame, newFrame = video.edit_frame(frame)
    preFrame = newFrame

    #Start a for loop that run according  to the number of frames in the video.
    #+ NOTE: frameCount usually doesn't get the correct number of frames! +
    for i in range(1,int(video.frameCount-2)):

        #Read the next frame and edit it
        ret, frame = video.readVideo()

        # Check if the frame exists, if not break the loop because video end
        if not ret:
            break
            
        resizeFrame, newFrame = video.edit_frame(frame)

        for index in markCntRange:
            x,y,w,h = cv2.boundingRect(markCntList[index][2])
            newFrameEntry = newFrame[y:y+h, x:x+w]
            preFrameEntry = preFrame[y:y+h, x:x+w]

            #Analyze the difference between the frames 
            frameDelta = cv2.absdiff(preFrameEntry, newFrameEntry)
            dilateThresh, contours = video.threshold_anlysis(frameDelta)

            #Start a loop for all the found differences
            for c in contours:

                #Check if the difference big enough

                if cv2.contourArea(c) > video.setting.MIN_DIFF:

                    #If it is, reste the no movment counter
                    markCntList[index][1] = 0

                    #Check if it a continuation of movment
                    if not markCntList[index][0]:

                        #If not, declare movment and calculate the movment time in seconds
                        markCntList[index][0] = True
                        # 0 = cv2.CAP_PROP_POS_MSEC
                        sec = video.video.get(0)/1000

                        #Convert the time from seconds to string and save it
                        timer = video.second_to_timer(sec)
                        startTime = timer

                    #Break the loop (one difference is enough to declare movment
                    break

            else:

                #If the loop end without breaking, check if movment
                if markCntList[index][0]:
                    
                    #Save the time when the movment first stop.
                    if markCntList[index][1]==0:
                        # 0 = cv2.CAP_PROP_POS_MSEC
                        msec = video.video.get(0)

                    #Add 1 to the no movment counter
                    markCntList[index][1] += 1

                    #Check if the movment counter big enough to declare stop moving
                    if markCntList[index][1] > video.setting.MIN_STIL_FRAME:
                        markCntList[index][0] = False

                        #Calculate the time when the movement stoped
                        sec = msec/1000
                        timer = video.second_to_timer(sec)
                        stopTime = timer

                        #Write the start and the stop time of the movment
                        video.setting.writeCSV(f'{video.fileName},{index},{startTime},{stopTime}\n')


        # for display video, delete the # in the next line
        #video.display_video(contours, [resizeFrame, dilateThresh, frameDelta])

        #Save the frame to compare to the next frame
        preFrame = newFrame

    #End the video capture
    video.end_video_capture()

