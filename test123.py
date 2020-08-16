import motion_detection


videoPath = "C:\\Users\\krofe\\Documents\\Python staff\\research\\athos and porthos.mp4"

motion_detection.Video(videoPath).motion_detection()

##background_frame = motion_detection.Video(videoPath).get_background_test()
##
##motion_detection.Video(videoPath).motion_detection(background_frame, True)
