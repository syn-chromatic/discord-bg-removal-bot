####################################
###      COMMAND VARIABLES       ###
####################################

# The bot will reject to process requested multi-frame
# inputs that have more than the assigned frames count
max_frames_animated: int = 50

# The bot will reject to process requested single-frame
# inputs that are above the assigned pixel count in width or height
max_px_image: int = 6000

# The bot will reject to process requested multi-frame
# inputs that are above the assigned pixel count in width or height
max_px_animated: int = 640

# The bot will reduce fps by removing alternating frames
# from input until it matches the assigned maximum or below
max_video_fps: int = 15
