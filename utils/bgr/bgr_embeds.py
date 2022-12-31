from nextcord import Message
from nextcord.ext.commands import Context

from io import BytesIO
from typing import Union

from utils.general_utils import EmbedForm


class IteratorBase:
    def __init__(self, ctx: Context):
        self._ctx = ctx
        self._message: Union[Message, None] = None

    @staticmethod
    def _initial_embed_form() -> EmbedForm:
        embed_form = EmbedForm()
        embed_form.set_description("Initializing..")
        return embed_form

    @staticmethod
    def _iteration_embed_form(idx: int, total_idx: int, image_io: BytesIO) -> EmbedForm:
        description = f"Processed {idx} out of {total_idx} frames."
        embed_form = EmbedForm()
        embed_form.set_description(description)
        embed_form.set_image_file(image_io)
        return embed_form

    async def _remove_message(self):
        if self._message:
            await self._message.delete()

    async def _send_embed(self, embed_form: EmbedForm):
        if not self._message:
            self._message = await embed_form.ctx_reply(self._ctx, mention=False)
            return
        await embed_form.edit_message(self._message)


class EmbedImageIterator(IteratorBase):
    async def send(self):
        embed_form = self._initial_embed_form()
        await self._send_embed(embed_form)

    async def update(self, idx: int, total_idx: int, image_io: BytesIO):
        embed_form = self._iteration_embed_form(idx, total_idx, image_io)
        await self._send_embed(embed_form)

    async def clean(self):
        await self._remove_message()
