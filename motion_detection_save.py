#Save video motion detection-
#Like regular motion detection, but also save all the frames with movment to a video file.
#Write the original time of the frames (the time of the original video),
#at the right corner of the frames.

#NOTE: this code will take longer to run an use a lot more memory (RAM) then the regular
#motion detection, it recomended to run while not working on the computer and without other
#memory consuming programs (like chrome, madia player, etc.) open at the same time.
import cv2

def motion_detection(video, writer, buffer, textCoord, font):

    #Create a list for saving the frames
    frameList = []
    
    #Set the the movment counter and movment flag
    noMovmentCounter = 0
    movment = False

    # Read the first frame, edit it and set it as preFrame.
    ret, frame = video.readVideo()
    resizeFrame, newFrame = video.edit_frame(frame)
    preFrame = newFrame

    #Start a for loop that run according  to the number of frames in the video.
    #+ NOTE: frameCount usually doesn't get the correct number of frames! +
    for i in range(1,int(video.frameCount-2)):

        #Read the next frame
        ret, frame = video.readVideo()

        # Check if the frame exists, if not break the loop because video end
        if not ret:
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

                # 0 = cv2.CAP_PROP_POS_MSEC
                sec = video.video.get(0)/1000

                #Convert the time from seconds to string and save it
                timer = video.second_to_timer(sec)

                #Check if it a continuation of movment
                if not movment:

                    #If not, declare movment and calculate the movment time in seconds
                    movment = True
                    startTime = timer

                    #Write previews frames
                    for f in frameList:

                        #Get the frame original time
                        timeText = video.second_to_timer(f[0]/1000)

                        #Write the original time on the frame. 
                        cv2.putText(f[1],
                                    f'{timeText} {video.fileName}',
                                    textCoord,
                                    font,
                                    1,(255, 255, 255), 2,4)

                        
                        writer.write(f[1])

                    #Reset the frames list
                    frameList = []

                #Write the corrent frame with it original time
                cv2.putText(frame,
                            f'{timer} {video.fileName}',
                            textCoord,
                            font, 1,(255, 255, 255), 2,4)
                writer.write(frame)

                #Break the loop (one difference is enough to declare movment
                break

        else:

            #If the loop end without breaking, check if movment
            if movment:

                #Caculate the frame time  
                # 0 = cv2.CAP_PROP_POS_MSEC
                sec = video.video.get(0)/1000

                #Convert the time from seconds to string and save it
                timer = video.second_to_timer(sec)

                #Write the corrent frame with it original time
                cv2.putText(frame, f'{timer} {video.fileName}',textCoord, font, 1,(255, 255, 255), 2,4)
                
                writer.write(frame)
                    
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
            else:
                #Save the frame in a list as a "buffer" to write to the file
                if len(frameList) > buffer:
                    frameList.pop(0)
                frameList.append([video.video.get(0), frame])
                    
        # for display video, delete the # in the next line
        #video.display_video(contours, [resizeFrame, dilateThresh, frameDelta])

        #Save the frame to compare to the next frame
        preFrame = newFrame

    #End the video capture
    video.end_video_capture()

