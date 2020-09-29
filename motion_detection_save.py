import cv2

def motion_detection(video, writer, buffer, textCoord, font):
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
##    font = cv2.FONT_HERSHEY_SIMPLEX
    
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

        #Read the next frame and edit it
        ret, frame = video.readVideo()

        # Check if the frame exists, if not break the loop because video end
        if not ret:
            break
            
        resizeFrame, newFrame = video.edit_frame(frame)
            
        #Analyze the difference between the frames 
        frameDelta = cv2.absdiff(preFrame, newFrame)
        dilateThresh, contours = video.threshold_anlysis(frameDelta)


        #Start a loop for all the found differences
        for c in contours:

            #Check if the difference big enough

            if cv2.contourArea(c) > video.setting.MIN_DIFF:

                #If it is, reste the no movment counter
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


                    #Write previews frame
                    for f in frameList:
                        timeText = video.second_to_timer(f[0]/1000)
                        cv2.putText(f[1],
                                    f'{timeText} {video.fileName}',
                                    textCoord,
                                    font,
                                    1,(255, 255, 255), 2,4)
                        
                        writer.write(f[1])
                    frameList = []

                cv2.putText(frame,
                            f'{timer} {video.fileName}',
                            textCoord,
                            font, 1,(255, 255, 255), 2,4)
##                cv2.putText(frame, timer,(50, 50), font, 1,(255, 0, 0),  2,4)
                writer.write(frame)

                #Break the loop (one difference is enough to declare movment
                break

        else:

            #If the loop end without breaking, check if movment
            if movment:
                
                # 0 = cv2.CAP_PROP_POS_MSEC
                sec = video.video.get(0)/1000

                #Convert the time from seconds to string and save it
                timer = video.second_to_timer(sec)

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
                if len(frameList) > buffer:
                    frameList.pop(0)
                frameList.append([video.video.get(0), frame])
                    
        # for display video, delete the # in the next line
        #video.display_video(contours, [resizeFrame, dilateThresh, frameDelta])

        #Save the frame to compare to the next frame
        preFrame = newFrame

    #End the video capture
    video.end_video_capture()

##    writer.release()

