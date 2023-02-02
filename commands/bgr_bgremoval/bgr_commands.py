from nextcord.ext.commands import Context

from utils.general_utils import EmbedForm, ContextAttachment
from utils.bgr.bgr_handler import MediaHandler
from exceptions.bot_exceptions import BaseBotException
from logger.exception_logging import ExceptionLogger

from bot_instance import BotClient

client = BotClient()
bot = client.get_bot()


@bot.command(description="")
async def rembg(ctx: Context):
    """Command to remove the background of images or videos."""
    file_attachment = await ContextAttachment(ctx).any_file_attachment()
    if not file_attachment:
        embed_form = EmbedForm().as_error()
        embed_form.set_description(
            "Upload an image with the command, "
            "or reply to a message that has an attachment."
        )
        await embed_form.ctx_reply(ctx, mention=False)
        return

    try:
        file = await MediaHandler(ctx, file_attachment).handler()
        if file:
            await ctx.reply(file=file, mention_author=False)

    except BaseBotException as error:
        ExceptionLogger(error).log()
        embed_form = EmbedForm().as_error()
        embed_form.set_description(str(error))
        await embed_form.ctx_reply(ctx, mention=False)

    except Exception as error:
        ExceptionLogger(error).log()
        embed_form = EmbedForm().as_error()
        embed_form.set_description("Unexpected error occurred.")
        await embed_form.ctx_reply(ctx, mention=False)
