# Discord bot for automatic background removals with support for PNGs, JPEGs, WEBPs, GIFs and MP4s.




This library requires Python 3.9
`https://www.python.org/downloads/release/python-3910`

Select `Add Python 3.9 to PATH` during installation otherwise pip and other Python executables won't be recognized from the command prompt




## Installing requirements.txt
```pip install -r requirements.txt```




## ImageMagick Installation
The version I used was ImageMagick 7.1.0 Q16+HDRI-dll, you can get the Windows version from:

`https://imagemagick.org/script/download.php#windows`

> The architecture must match your Python version (x64 or x86).




**During installation of ImageMagick, make sure to have these options selected:**

- Add application directory to your system path

- Install development headers and libraries for C and C++

- Install FFMPEG


## Bot Configuration
Before running the bot you must configure the neccessary variables in `/variables/variables_bot.py`
### Required Variables
- BOT_TOKEN — Retreived from Discord Developer Portal after creating a bot application
- COMMAND_PREFIX — The prefix is a single-character string used to invoke commands to the bot - i.e. "$"

### Optional Variables
- ACTIVITY_TEXT — For displaying the bot's activity status, such as *"Watching TEXT"*
- RELAY_CHANNEL_ID — For sending images to a different channel from where the command is used then retrieving the image url and inserting it into an embed for previewing of processed images

### Rembg Command Variables
- max_frames_animated — The bot will reject to process requested multi-frame inputs that have more than the assigned frames count
- max_px_image — The bot will reject to process requested single-frame inputs that are above the assigned pixel count in width or height
- max_px_animated — The bot will reject to process requested multi-frame inputs that are above the assigned pixel count in width or height
- max_video_fps — The bot will reduce fps by removing alternating frames from input until it matches the assigned maximum or below

Run `main_bot.py` to start the bot.
