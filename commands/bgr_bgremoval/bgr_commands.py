from nextcord.ext.commands import Context

from utils.general_utils import EmbedForm
from utils.bgr.bgr_handler import MediaHandler
from exceptions.bgr_exceptions import BaseBGRException

from bot_instance import BotClient

client = BotClient()
bot = client.get_bot()


@bot.command(description="")
async def rembg(ctx: Context):
    """Command to remove the background of images or videos."""
    if not ctx.message.attachments:
        embed_form = EmbedForm().as_error()
        embed_form.set_description("Upload an image with the command.")
        await embed_form.ctx_reply(ctx, mention=False)
        return

    media_url = ctx.message.attachments[0].url

    try:
        file = await MediaHandler(ctx, media_url).handler()
        if file:
            await ctx.reply(file=file, mention_author=False)

    except BaseBGRException as error:
        embed_form = EmbedForm().as_error()
        embed_form.set_description(str(error))
        await embed_form.ctx_reply(ctx, mention=False)

    except Exception:
        embed_form = EmbedForm().as_error()
        embed_form.set_description("Unexpected error occurred.")
        await embed_form.ctx_reply(ctx, mention=False)
