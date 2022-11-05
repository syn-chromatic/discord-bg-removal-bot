import bot_instance
from nextcord.ext.commands import Context

from utils.bgr.bgr_embeds import ConstructEmbed
from utils.bgr.bgr_handler import MediaHandler
from utils.bgr.bgr_exceptions import BGR_EXCEPTIONS

bot = bot_instance.BOT


@bot.command(description="")
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

    except BGR_EXCEPTIONS as error:
        embed = ConstructEmbed().message(str(error))
        embed = embed.is_error().get_embed()
        await ctx.reply(embed=embed, mention_author=False)

    except Exception:
        reply_str = "Unexpected error occurred."
        embed = ConstructEmbed().message(reply_str)
        embed = embed.is_error().get_embed()
        await ctx.reply(embed=embed, mention_author=False)
