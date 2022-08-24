from bot_instance import BOT
from nextcord.ext.commands import Context
from utils.general_utils import get_extension_class, construct_embed


@BOT.command(description="")
async def rembg(ctx: Context):
    if ctx.message.attachments:
        media_url = ctx.message.attachments[0].url
        extension_class, error_embed = await get_extension_class(media_url)

        if error_embed:
            await ctx.reply(embed=error_embed)
        elif extension_class:
            await extension_class.handler(ctx, media_url)
    else:
        await ctx.reply(
            embed=construct_embed("Upload an image with the command."),
            mention_author=False,
        )
