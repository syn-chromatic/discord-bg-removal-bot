from bot_instance import BotClient

client = BotClient()
bot = client.get_bot()

@bot.event
async def on_ready():
    print('Bot is ready.')
