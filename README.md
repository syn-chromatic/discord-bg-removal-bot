# Discord bot for automatic background removals with support for PNGs, JPEGs, WEBPs and GIFs.




This library requires Python 3.9
`https://www.python.org/downloads/release/python-3910`

Select "Add Python 3.9 to PATH" otherwise pip won't be recognized from command prompt

### Installing requirements.txt
```pip install -r requirements.txt```

### ImageMagick Installation
The version I used was ImageMagick 7.1.0 Q16+HDRI, you can get the Windows version from:

`https://imagemagick.org/script/download.php#windows`

During installation of ImageMagick, make sure to have these options selected:

`Add application directory to your system path`

`Install development headers and libraries for C and C++`

`Install FFMPEG`


### Bot Configuration
Before running the bot you must configure the neccessary variables in `/variables/variables_bot.py`

`ACTIVITY_TEXT` is optional for displaying the bot's activity status, such as "Watching [Text]" 

Finally run `main_bot.py`
