import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import nextcord as discord
from nextcord.ext import commands

from variables import variables_instance as instance
from variables import variables_bot as varbot

if not varbot.BOT_TOKEN:
    print('Configure your Bot Token variable in /variables/variables_bot.py')
    input(); sys.exit()
if not varbot.COMMAND_PREFIX:
    print('Configure your Command Prefix, used to invoke a command, such as "-" in /variables/variables_bot.py') 
    input(); sys.exit()

intents = discord.Intents.default()

activity = discord.Activity(type=discord.ActivityType.watching, name=varbot.ACTIVITY_TEXT)
instance.BOT_INSTANCE = commands.Bot(command_prefix=varbot.COMMAND_PREFIX, help_command=None, intents=intents, activity=activity)

from bot_commands import rembg_command

@instance.BOT_INSTANCE.event
async def on_ready():
    print('Bot is ready.')
    
try:    
    instance.BOT_INSTANCE.run(varbot.BOT_TOKEN)
except Exception as error:
    print(error); input(); sys.exit()
