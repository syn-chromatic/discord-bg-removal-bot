import nextcord


from uuid import uuid4
from io import BytesIO
from PIL.Image import Image as ImageType
from nextcord.ext.commands import Context

from typing_extensions import Self


class EmbedFormBase:
    def __init__(self):
        self._embed = nextcord.Embed()
        self._embed.color = self._get_green()
        self._file_obj = None

    @staticmethod
    def _get_green() -> int:
        return 0x00FF00

    @staticmethod
    def _get_red() -> int:
        return 0xC82323

    @staticmethod
    def _get_filename(file_ext: str = "png") -> str:
        uuid_name = uuid4().hex[:10]
        filename = f"{uuid_name}.{file_ext}"
        return filename

    @staticmethod
    def _pil_to_bytes_io(image_pil: ImageType, image_format: str) -> BytesIO:
        bytes_io = BytesIO()
        image_pil.save(bytes_io, format=image_format)
        bytes_io.seek(0)
        return bytes_io


class EmbedForm(EmbedFormBase):
    def __init__(self):
        super().__init__()

    def set_title(self, text: str) -> Self:
        self._embed.title = text
        return self

    def set_description(self, text: str) -> Self:
        self._embed.description = text
        return self

    def set_footer(self, footer_text) -> Self:
        self._embed.set_footer(text=footer_text)
        return self

    def set_color(self, color_hex: int) -> Self:
        self._embed.color = color_hex
        return self

    def add_field(self, name: str, value: str, inline: bool) -> Self:
        self._embed.add_field(name=name, value=value, inline=inline)
        return self

    def set_image_file(self, bytes_io: BytesIO, file_ext: str = "png") -> Self:
        filename = self._get_filename(file_ext)
        self._file_obj = nextcord.File(fp=bytes_io, filename=filename)
        self._embed.set_image(url=f"attachment://{filename}")
        return self

    def set_image_pillow(self, image_pil: ImageType, image_format: str) -> Self:
        bytes_io = self._pil_to_bytes_io(image_pil, image_format)
        self.set_image_file(bytes_io)
        return self

    def set_image_url(self, url: str) -> Self:
        self._embed.set_image(url)
        return self

    def as_error(self) -> Self:
        self._embed.color = self._get_red()
        return self

    def get_embed(self) -> nextcord.Embed:
        return self._embed

    async def ctx_send(self, ctx: Context):
        return await ctx.send(embed=self._embed, file=self._file_obj)

    async def ctx_reply(self, ctx: Context, mention: bool):
        return await ctx.send(
            embed=self._embed,
            file=self._file_obj,
            mention_author=mention,
        )

    async def edit_message(self, message: nextcord.Message):
        return await message.edit(embed=self._embed, file=self._file_obj)
