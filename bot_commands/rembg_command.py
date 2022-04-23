import nextcord as discord
from variables import variables_instance as instance
from helpers import rembg_utils

bot = instance.BOT_INSTANCE

@bot.command(description='')
async def rembg(ctx):
    image_exts = ("png", "jpg", "jpeg", "gif", "webp")

    if ctx.message.attachments and ctx.message.attachments[0].url.lower().endswith(image_exts):
        image_url = ctx.message.attachments[0].url
        await rembg_utils.handle_image(ctx, image_url)
        
    elif not ctx.message.attachments:
        await ctx.reply("`Upload an image with the command!`", mention_author=False)
        
    else:
        await ctx.reply("`Currently only PNGs, JPEGs, WEBPs and GIFs are supported.`", mention_author=False)
    
