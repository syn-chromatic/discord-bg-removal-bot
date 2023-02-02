from nextcord.ext.commands import Context

from utils.help.help_utils import HelpMenu
from utils.help.help_dcs import (
    MediaWRefInput,
)

from bot_instance import BotClient

client = BotClient()
bot = client.get_bot()


@bot.command()
async def help(ctx: Context):
    help_menu = HelpMenu()
    client_user = client.get_client_user()
    client_name = client_user.name
    help_menu.set_title(client_name)
    help_menu.add_command("helpbgr", "Background Removal", inline=True)
    help_menu.add_support_link()
    await help_menu.reply(ctx)


@bot.command()
async def helpbgr(ctx: Context):
    help_menu = HelpMenu()
    help_menu.set_title("Background Removal")
    help_menu.add_command("rembg", "Removes background from media.", MediaWRefInput())
    await help_menu.reply(ctx)
