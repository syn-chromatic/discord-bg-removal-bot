import nextcord
import asyncio

from nextcord.ext.commands import Context
from utils.bgr.bgr_download import DownloadMedia

from utils.bgr.bgr_mime import MimeTypeSniff

from io import BytesIO
from typing import Union
from uuid import uuid4

from utils.bgr.bgr_utils import BGProcess
from utils.bgr.bgr_media import ComposeGIF
from utils.bgr.bgr_dataclasses import (
    MimeTypeConfig,
    ResponseFile,
    ImageFrame,
    VideoData,
    AnimatedData,
)


class MediaHandlerBase:
    def __init__(self, ctx: Context, url: str):
        self._ctx = ctx
        self._url = url

    def _get_response_file(self) -> ResponseFile:
        try:
            response_file = MimeTypeSniff(self._url).get_mime_type()
        except Exception as error:
            raise error
        return response_file

    def _retrieve_data(self, rsp_file: ResponseFile):
        image_mime_types = MimeTypeConfig().image_mime_types
        video_mime_types = MimeTypeConfig().video_mime_types
        mime_type = rsp_file.mime_type

        if mime_type in image_mime_types:
            return self._get_image_data(rsp_file)

        if mime_type in video_mime_types:
            return self._get_video_data(rsp_file)

    def _create_file(self, output: BytesIO, ext: str):
        filename = self._filename() + f".{ext}"
        nextcord_file = nextcord.File(fp=output, filename=filename)
        return nextcord_file

    @staticmethod
    def _get_image_data(rsp_file: ResponseFile) -> Union[ImageFrame, AnimatedData]:
        try:
            data = DownloadMedia(rsp_file).download_image()
        except Exception as error:
            raise error
        return data

    @staticmethod
    def _get_video_data(rsp_file: ResponseFile) -> VideoData:
        try:
            data = DownloadMedia(rsp_file).download_video()
        except Exception as error:
            raise error
        return data

    @staticmethod
    def _filename() -> str:
        uuid_name = uuid4().hex[:10]
        return uuid_name


class MediaHandler(MediaHandlerBase):
    """MediaHandler class which handles different types of media files for rembg."""

    async def handler(self) -> Union[nextcord.File, None]:
        """Handle the type of media and removes the background."""
        rsp_file = await asyncio.to_thread(self._get_response_file)
        data = await asyncio.to_thread(self._retrieve_data, rsp_file)

        if data:
            data_out = await BGProcess(self._ctx, data).process()

            if isinstance(data_out, ImageFrame):
                out_io = BytesIO()
                data_out.image.save(out_io, "PNG")
                out_io.seek(0)
                nextcord_file = self._create_file(out_io, "png")
                return nextcord_file

            if isinstance(data_out, (VideoData, AnimatedData)):
                out_io = ComposeGIF(data_out).reconstruct()
                nextcord_file = self._create_file(out_io, "gif")
                return nextcord_file
