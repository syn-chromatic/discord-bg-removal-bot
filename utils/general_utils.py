from uuid import uuid4
from io import BytesIO
from PIL.Image import Image as ImageType


from nextcord import Message, Attachment, Asset, File, Embed
from nextcord.ui import View
from nextcord.ext.commands import Context

from typing import Union, Any
from typing_extensions import Self

from exceptions.bot_exceptions import (
    EmbedFormContextUnavailable,
    EmbedFormMessageUnavailable,
    EmbedFormFileUnavailable,
)


class EmbedFormBase:
    def __init__(self):
        self._ctx: Union[Context, None] = None
        self._message: Union[Message, None] = None
        self._embed: Union[Embed, None] = None
        self._file_obj: Union[File, None] = None
        self._view: Union[View, None] = None

    def _get_embed(self) -> Embed:
        if not self._embed:
            self._embed = self._create_embed()
        return self._embed

    def _create_embed(self) -> Embed:
        embed = Embed()
        embed.color = self._get_green()
        return embed

    def _create_file(self, bytes_io: BytesIO, file_ext: str) -> File:
        embed = self._get_embed()
        filename = self._get_filename(file_ext)
        self._file_obj = File(fp=bytes_io, filename=filename)
        embed.set_image(url=f"attachment://{filename}")
        return self._file_obj

    def _get_send_kwargs(self) -> dict[str, Any]:
        kwargs = {}
        self._add_embed_kwarg(kwargs, strict_value=True)
        self._add_file_kwarg(kwargs, strict_value=True)
        self._add_view_kwarg(kwargs, strict_value=False)
        return kwargs

    def _get_reply_kwargs(self, mention: bool) -> dict[str, Any]:
        kwargs = {}
        self._add_embed_kwarg(kwargs, strict_value=True)
        self._add_file_kwarg(kwargs, strict_value=True)
        self._add_view_kwarg(kwargs, strict_value=False)
        self._add_mention_kwarg(kwargs, mention)
        return kwargs

    def _get_edit_kwargs(self) -> dict[str, Any]:
        kwargs = {}
        self._add_embed_kwarg(kwargs, strict_value=False)
        self._add_view_kwarg(kwargs, strict_value=False)
        self._add_file_kwarg(kwargs, strict_value=True)
        return kwargs

    def _add_embed_kwarg(self, kwargs: dict[str, Any], strict_value: bool):
        if strict_value and not self._embed:
            return
        kwargs.update({"embed": self._embed})

    def _add_file_kwarg(self, kwargs: dict[str, Any], strict_value: bool):
        if strict_value and not self._file_obj:
            return
        kwargs.update({"file": self._file_obj})

    def _add_view_kwarg(self, kwargs: dict[str, Any], strict_value: bool):
        if strict_value and not self._view:
            return
        kwargs.update({"view": self._view})

    @staticmethod
    def _add_mention_kwarg(kwargs: dict[str, Any], mention: bool) -> None:
        kwargs.update({"mention_author": mention})

    @staticmethod
    def _get_green() -> int:
        return 0x00FF00

    @staticmethod
    def _get_red() -> int:
        return 0xC82323

    @staticmethod
    def _get_white() -> int:
        return 0xC8C8C8

    @staticmethod
    def _get_filename(file_ext: str = "png") -> str:
        uuid_name = uuid4().hex[:10]
        filename = f"{uuid_name}.{file_ext}"
        return filename

    @staticmethod
    def _pil_to_io(image_pil: ImageType, image_format: str, optimize: bool) -> BytesIO:
        bytes_io = BytesIO()
        image_pil.save(bytes_io, format=image_format, optimize=optimize)
        bytes_io.seek(0)
        return bytes_io


class EmbedForm(EmbedFormBase):
    def __init__(self):
        super().__init__()

    def set_ctx(self, ctx: Context) -> Self:
        self._ctx = ctx
        return self

    def set_view(self, view: Union[View, None]) -> Self:
        self._view = view
        return self

    def set_title(self, text: str) -> Self:
        embed = self._get_embed()
        embed.title = text
        return self

    def set_description(self, text: str) -> Self:
        embed = self._get_embed()
        embed.description = text
        return self

    def set_footer(self, footer_text) -> Self:
        embed = self._get_embed()
        embed.set_footer(text=footer_text)
        return self

    def set_color(self, color_hex: int) -> Self:
        embed = self._get_embed()
        embed.color = color_hex
        return self

    def add_field(self, name: str, value: str, inline: bool = False) -> Self:
        embed = self._get_embed()
        embed.add_field(name=name, value=value, inline=inline)
        return self

    def set_image_file(self, bytes_io: BytesIO, file_ext: str = "png") -> Self:
        self._create_file(bytes_io, file_ext)
        return self

    def set_image_pillow(
        self, image_pil: ImageType, image_format: str, optimize: bool = True
    ) -> Self:
        bytes_io = self._pil_to_io(image_pil, image_format, optimize)
        file_ext = image_format.lower()
        self._create_file(bytes_io, file_ext)
        return self

    def set_image_url(self, url: str) -> Self:
        embed = self._get_embed()
        embed.set_image(url)
        return self

    def as_error(self) -> Self:
        embed = self._get_embed()
        embed.color = self._get_red()
        return self

    def set_white(self) -> Self:
        embed = self._get_embed()
        embed.color = self._get_white()
        return self

    def get_embed(self) -> Embed:
        embed = self._get_embed()
        return embed

    def get_file_object(self) -> File:
        if not self._file_obj:
            raise EmbedFormFileUnavailable()
        return self._file_obj

    async def send(self) -> Message:
        if not self._ctx:
            raise EmbedFormContextUnavailable()
        return await self.ctx_send(self._ctx)

    async def reply(self, mention: bool = True) -> Message:
        if not self._ctx:
            raise EmbedFormContextUnavailable()
        return await self.ctx_reply(self._ctx, mention)

    async def edit(self) -> Message:
        if not self._message:
            raise EmbedFormMessageUnavailable()
        return await self.edit_message(self._message)

    async def delete(self) -> None:
        if not self._message:
            raise EmbedFormMessageUnavailable()
        await self._message.delete()

    async def ctx_send(self, ctx: Context) -> Message:
        kwargs = self._get_send_kwargs()
        self._message = await ctx.send(**kwargs)
        return self._message

    async def ctx_reply(self, ctx: Context, mention: bool = True) -> Message:
        kwargs = self._get_reply_kwargs(mention)
        self._message = await ctx.reply(**kwargs)
        return self._message

    async def edit_message(self, message: Message) -> Message:
        kwargs = self._get_edit_kwargs()
        self._message = await message.edit(**kwargs)
        return self._message


class ContextAttachmentBase:
    def __init__(self, ctx: Context):
        self._ctx = ctx
        self._state = ctx._state

    def _get_reference_attachment(self) -> Union[Attachment, None]:
        message = self._get_reference_message()
        if not message:
            return
        attachments = message.attachments
        if not attachments:
            return
        return attachments[0]

    def _get_reference_embed_image(self) -> Union[Asset, None]:
        message = self._get_reference_message()
        if not message:
            return
        embeds = message.embeds
        for embed in embeds:
            image_url = embed.image.url
            if not image_url:
                break
            image_asset = Asset(
                state=self._state,
                url=image_url,
                key="",
            )
            return image_asset

    def _get_reference_message(self) -> Union[Message, None]:
        message_reference = self._ctx.message.reference
        if not message_reference:
            return
        message = message_reference.resolved
        if isinstance(message, Message):
            return message


class ContextAttachment(ContextAttachmentBase):
    def __init__(self, ctx: Context):
        super().__init__(ctx)

    def attachment_from_message(self) -> Union[Attachment, None]:
        message = self._ctx.message
        attachments = message.attachments
        if attachments:
            return attachments[0]

    def attachment_from_reference(self) -> Union[Attachment, None]:
        return self._get_reference_attachment()

    def any_attachment(self) -> Union[Attachment, None]:
        attachment = self.attachment_from_message()
        if not attachment:
            attachment = self.attachment_from_reference()
        return attachment

    async def file_from_message(self) -> Union[File, None]:
        attachment = self.attachment_from_message()
        if attachment:
            return await attachment.to_file()

    async def file_from_reference(self) -> Union[File, None]:
        attachment = self.attachment_from_reference()
        if attachment:
            return await attachment.to_file()

    async def file_from_reference_embed(self):
        image_asset = self._get_reference_embed_image()
        if image_asset:
            return await image_asset.to_file()

    async def any_file_attachment(self) -> Union[File, None]:
        file = await self.file_from_message()
        if not file:
            file = await self.file_from_reference()
        if not file:
            file = await self.file_from_reference_embed()
        return file
