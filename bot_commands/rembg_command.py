from bot_instance import BOT
from nextcord.ext.commands import Context
from utils.general_utils import construct_embed
from utils.class_handlers import MediaHandler


@BOT.command(description="")
async def rembg(ctx: Context):
    """Command to remove the background of images or videos."""
    if ctx.message.attachments:
        media_url = ctx.message.attachments[0].url
        await MediaHandler(ctx, media_url).handler()

    else:
        await ctx.reply(
            embed=construct_embed("Upload an image with the command."),
            mention_author=False,
        )
