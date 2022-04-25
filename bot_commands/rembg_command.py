import nextcord as discord
from variables import variables_instance as instance
from helpers import rembg_utils

bot = instance.BOT_INSTANCE
supported_exts = ("png", "jpg", "jpeg", "gif", "webp", "mp4")
image_mime_types = ['png', 'jpeg', 'gif', 'webp']
video_mime_types = ['mp4']

@bot.command(description='')
async def rembg(ctx):
    if ctx.message.attachments and ctx.message.attachments[0].url.lower().endswith(supported_exts):
        mediaURL = ctx.message.attachments[0].url
    else:
        mediaURL = None

    if mediaURL:
        type_check, mime_type, errorEmbed = await rembg_utils.mime_type_sniff(mediaURL)
        
        if type_check is True and mime_type in image_mime_types:
            await rembg_utils.handle_image(ctx, mediaURL)
        elif type_check is True and mime_type in video_mime_types:
            await rembg_utils.handle_video(ctx, mediaURL)
        else:
            await ctx.reply(embed=errorEmbed, mention_author=False)
        
    else:
        await ctx.reply(embed=rembg_utils.constructEmbedNotice("Upload an image with the command."), mention_author=False)
    
