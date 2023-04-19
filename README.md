# 🤖 Discord Background Removal Bot
Automatic background removals with support for PNGs, JPEGs, WEBPs, GIFs and MP4s.


## 📽️ Preview
*Video - 482x640 / 37 frames, CPU processing takes approximately 1 minute*

![](https://github.com/Syn-dromatic/discord-bg-removal-bot/blob/main/preview/preview.gif)

___
## 📋 Prerequisites 
This library requires [Python 3.9](https://www.python.org/downloads/release/python-3910)

Make sure to select 'Add Python 3.9 to PATH' during installation.

___


## 🛠️ Installation
1. Install dependencies: `pip install -r requirements.txt`.
2. Install ImageMagick 7.1.x Q16+HDRI-dll (Windows version available [here](https://imagemagick.org/script/download.php#windows)). 

Make sure the architecture matches your Python version (x64 or x86). 

During installation, select the following options:
   - Add application directory to your system path
   - Install development headers and libraries for C and C++
   - Install FFMPEG

___

## ⚙️ Configuration
Required variables can be found in `/configuration/bot_config.py`
#### Required Variables
- BOT_TOKEN — Acquired from Discord Developer Portal after creating a bot application
- COMMAND_PREFIX — A single-character string to invoke bot commands (e.g. "$")

___
## ⚙️ Optional Configuration
Optional variables can be found in `/configuration/command_variables/bgr_variables.py`
#### Rembg Command Variables
- MAX_FRAMES — Maximum number of frames allowed for multi-frame inputs
- MAX_PX_IMAGE — Maximum pixel count (width or height) allowed for single-frame inputs
- MAX_PX_ANIMATED — Maximum pixel count (width or height) allowed for multi-frame inputs

___
## 📚 Commands
- help: Standard help command
- helpbgr: Help command for background removal
- rembg: Command for background removal; *accepts an attachment or a reference attachment (either upload an image or reply to a message containing an image)*

Run `main_bot.py` to start the bot.
