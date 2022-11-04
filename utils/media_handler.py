import nextcord
from nextcord.ext.commands import Context
from utils.download_utils import DownloadMedia

from utils.mime_utils import MimeTypeSniff
from utils.embed_utils import ConstructEmbed
from io import BytesIO
from typing import Union
from utils.rembg_utils import BGProcess
from utils.media_utils import ComposeGIF
from utils.media_dataclasses import (
    ExtensionConfig,
    ResponseFile,
    ImageFrame,
    VideoData,
    AnimatedData,
)


class MediaHandlerBase:
    def __init__(self, ctx: Context, url: str):
        self._ctx = ctx
        self._url = url
        self._response_file = self._get_response_file()

    def _get_response_file(self) -> ResponseFile:
        try:
            response_file = MimeTypeSniff(self._url).get_mime_type()
        except Exception as error:
            raise error
        return response_file

    def _get_image_data(self) -> Union[ImageFrame, AnimatedData]:
        try:
            data = DownloadMedia(self._response_file).download_image()
        except Exception as error:
            raise error
        return data

    def _get_video_data(self) -> VideoData:
        try:
            data = DownloadMedia(self._response_file).download_video()
        except Exception as error:
            raise error
        return data

    async def _reply_error(self, message: str):
        error_embed = ConstructEmbed().message(message)
        error_embed = error_embed.is_error().get_embed()
        await self._ctx.reply(embed=error_embed)


class MediaHandler(MediaHandlerBase):
    """MediaHandler class which handles different types of media files for rembg."""

    def __init__(self, ctx: Context, url: str):
        super().__init__(ctx, url)

    async def handler(self) -> Union[nextcord.File, None]:
        """Handle the type of media and removes the background."""

        image_mime_types = ExtensionConfig().image_mime_types
        video_mime_types = ExtensionConfig().video_mime_types

        mime_type = self._response_file.mime_type

        if mime_type in image_mime_types:
            data = self._get_image_data()
            data_out = await BGProcess(self._ctx, data).process()
            if isinstance(data_out, AnimatedData):
                out_io = ComposeGIF(data_out).reconstruct()
                nextcord_file = nextcord.File(out_io, filename="output.gif")
                return nextcord_file

            elif isinstance(data_out, ImageFrame):
                out_io = BytesIO()
                data_out.image.save(out_io, "PNG")
                out_io.seek(0)
                nextcord_file = nextcord.File(out_io, filename="output.png")
                return nextcord_file

        elif mime_type in video_mime_types:
            data = self._get_video_data()
            data_out = await BGProcess(self._ctx, data).process()
            if isinstance(data_out, VideoData):
                out_io = ComposeGIF(data_out).reconstruct()
                nextcord_file = nextcord.File(out_io, filename="output.gif")
                return nextcord_file
