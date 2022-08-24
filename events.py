from bot_instance import BOT


@BOT.event
async def on_ready():
    print('Bot is ready.')
