# Discord Background Removal Bot
Automatic background removals with support for PNGs, JPEGs, WEBPs, GIFs and MP4s.

___
## `➢` Table of Contents
1. [Installation](#-installation)
2. [Configuration](#-configuration)
4. [Commands](#-commands)
5. [Preview](#-preview)

___
## `➢` Installation
`Requires Python >= 3.9`

### `⤷` Installing Python Dependencies
&emsp; `pip install -r requirements.txt`

### `⤷` Installing ImageMagick
&emsp; **Version Required:** `ImageMagick 7.1.x Q16+HDRI-dll` 

&emsp; **Download:** https://imagemagick.org/script/download.php

&emsp; Make sure the architecture matches your Python version (x64 or x86). 

- During installation, select the following options:

   - Add application directory to your system path
   - Install development headers and libraries for C and C++
   - Install FFMPEG

___
## `➢` Configuration
### `⤷` Required Variables
- File Location: `/configuration/bot_config.py`

   - `BOT_TOKEN` — Acquired from Discord Developer Portal after creating a bot application
   - `COMMAND_PREFIX` — A single-character string to invoke bot commands (e.g. "$")


### `⤷` Optional Variables
- File Location: `/configuration/command_variables/bgr_variables.py`

   - `MAX_FRAMES` — Maximum number of frames allowed for multi-frame inputs
   - `MAX_PX_IMAGE` — Maximum pixel count (width or height) allowed for single-frame inputs
   - `MAX_PX_ANIMATED` — Maximum pixel count (width or height) allowed for multi-frame inputs

___
## `➢` Commands
| Command  | Description                           |
| :------: | :-----------------------------------: |
| help     | Standard Help Command                 |
| helpbgr  | Help Command For Background Removal   |
| rembg    | Background Removal [^1]               |

___
## `➢` Preview
### `⤷` Background Removal - \[MP4 482x640 \* 37f\]
![](https://github.com/Syn-dromatic/discord-bg-removal-bot/blob/main/preview/preview.gif)


[^1]: Accepts an attachment or a reference attachment, meaning it could either be an uploaded image, or a reply to a message containing an uploaded image.
