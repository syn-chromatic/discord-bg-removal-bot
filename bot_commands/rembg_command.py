from bot_instance import BOT
from nextcord.ext.commands import Context

from utils.embed_utils import ConstructEmbed
from utils.media_handler import MediaHandler


@BOT.command(description="")
async def rembg(ctx: Context):
    """Command to remove the background of images or videos."""
    if not ctx.message.attachments:
        embed = ConstructEmbed().message("Upload an image with the command.")
        embed = embed.is_error().get_embed()
        await ctx.reply(embed=embed, mention_author=False)
        return

    media_url = ctx.message.attachments[0].url

    try:
        file = await MediaHandler(ctx, media_url).handler()
        if file:
            await ctx.reply(file=file, mention_author=False)

    except Exception as error:
        embed = ConstructEmbed().message(str(error))
        embed = embed.is_error().get_embed()
        await ctx.reply(embed=embed, mention_author=False)
