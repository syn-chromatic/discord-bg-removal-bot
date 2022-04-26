####################################
### BOT REQUIRED VARIABLES ###
####################################

BOT_TOKEN = ""
COMMAND_PREFIX = ""



####################################
### BOT OPTIONAL VARIABLES ###
####################################

# For displaying the bot's activity status, such as "Watching TEXT"
# Leave empty if you don't want that feature
ACTIVITY_TEXT = ""

# For sending images to a different channel from where the command is used 
# Then retrieving the image url and inserting it into an embed for previewing of processed images
# Leave at None if you do not want that feature
RELAY_CHANNEL_ID = None 



####################################
### REMBG COMMAND VARIABLES ###
####################################

# The bot will reject to process requested multi-frame inputs that have more than the assigned frames count
max_frames_animated = 50

# The bot will reject to process requested single-frame inputs that are above the assigned pixel count in width or height
max_px_image = 6000 

# The bot will reject to process requested multi-frame inputs that are above the assigned pixel count in width or height
max_px_animated = 640 

# The bot will reduce fps by removing alternating frames from input until it matches the assigned maximum or below
max_video_fps = 15 
