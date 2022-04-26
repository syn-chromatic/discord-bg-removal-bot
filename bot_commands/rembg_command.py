import nextcord as discord
from urllib.parse import urlparse

from variables import variables_instance as instance
from helpers import rembg_utils

bot = instance.BOT_INSTANCE

supported_exts = ["png", "jpg", "jpeg", "gif", "webp", "mp4"]
image_mime_types = ['png', 'jpeg', 'gif', 'webp']
video_mime_types = ['mp4']


@bot.command(description='')
async def rembg(ctx):
    if ctx.message.attachments:
        mediaURL = ctx.message.attachments[0].url
        parsedURLExt = urlparse(mediaURL).path.split('.')
        
        if len(parsedURLExt)>1: 
            URLExtension = parsedURLExt[1]
        else:
            URLExtension = None
            
            
        if URLExtension and URLExtension in supported_exts:
            type_check, mime_type, errorEmbed = await rembg_utils.mime_type_sniff(mediaURL)
            
            if type_check is True and mime_type in image_mime_types:
                await rembg_utils.handle_image(ctx, mediaURL)
            elif type_check is True and mime_type in video_mime_types:
                await rembg_utils.handle_video(ctx, mediaURL)
            else:
                await ctx.reply(embed=errorEmbed, mention_author=False)
            
        elif URLExtension and URLExtension not in supported_exts:
            await ctx.reply(embed=rembg_utils.constructEmbedNotice(f"Detected extension as: '.{URLExtension}', which is not supported."), 
                                                        mention_author=False)
        
        else:
            await ctx.reply(embed=rembg_utils.constructEmbedNotice("Could not parse file extension."), 
                                                        mention_author=False)

    else:
        await ctx.reply(embed=rembg_utils.constructEmbedNotice("Upload an image with the command."), 
                                                    mention_author=False)
    
