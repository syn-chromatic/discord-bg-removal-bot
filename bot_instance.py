import nextcord
from nextcord.ext.commands import Bot
from variables import bot_config

intents: nextcord.Intents = nextcord.Intents.all()

BOT: Bot = Bot(
    command_prefix=bot_config.COMMAND_PREFIX,
    intents=intents,
    activity=nextcord.Activity(
                type=nextcord.ActivityType.watching,
                name=bot_config.ACTIVITY_TEXT),
    help_command=None
    )
