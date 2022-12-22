import nextcord
import asyncio

from PIL import Image
from io import BytesIO
from typing import Union
from uuid import uuid4
from nextcord.ext.commands import Context

from utils.http_utils import DownloadFile
from utils.bgr.bgr_utils import BGProcess

from configuration.command_variables.bgr_variables import (
    MAX_FRAMES,
    MAX_PX_IMAGE,
    MAX_PX_ANIMATED,
)


from utils.bgr.bgr_dataclasses import (
    MimeTypeConfig,
    ResponseFile,
    ImageFrame,
    VideoData,
    AnimatedData,
)


from utils.bgr.bgr_media import (
    ComposeGIF,
    VideoDecompose,
    AnimatedDecompose,
    DisposeDuplicateFrames,
)

from utils.bgr.bgr_exceptions import (
    ImageError,
    ImageDecompositionError,
    VideoDecompositionError,
    ExceedsMaxFrames,
    ExceedsMaxResolution,
    SubceedsMinResolution,
)


class MediaHandlerBase:
    def __init__(self, ctx: Context, url: str):
        self._ctx = ctx
        self._url = url

    async def _get_response_file(self) -> ResponseFile:
        response_file = await DownloadFile().from_url(self._url)
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
        data = MediaData(rsp_file).get_image_data()
        return data

    @staticmethod
    def _get_video_data(rsp_file: ResponseFile) -> VideoData:
        data = MediaData(rsp_file).get_video_data()
        return data

    @staticmethod
    def _filename() -> str:
        uuid_name = uuid4().hex[:10]
        return uuid_name


class MediaHandler(MediaHandlerBase):
    """MediaHandler class which handles different types of media files for rembg."""

    async def handler(self) -> Union[nextcord.File, None]:
        """Handle the type of media and removes the background."""
        rsp_file = await self._get_response_file()
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


class MediaData:
    def __init__(self, response_file: ResponseFile):
        self.response_file = response_file
        self.content = self.response_file.content
        self.mime_type = self.response_file.mime_type

    @staticmethod
    def get_num_frames(image_pil: Image.Image) -> int:
        """Get the number of frames in the image."""
        try:
            num_frames = image_pil.n_frames
        except AttributeError:
            num_frames = 1
        return num_frames

    @staticmethod
    def get_max_pixels(num_frames: int) -> int:
        """Determines the maximum number of pixels."""
        if num_frames > 1:
            max_px = MAX_PX_ANIMATED
        else:
            max_px = MAX_PX_IMAGE
        return max_px

    def open_image(self):
        image_io = BytesIO(self.content)

        try:
            image_pil = Image.open(image_io)
        except Exception:
            raise ImageError()

        return image_pil

    @staticmethod
    def decompose_animated(image_pil: Image.Image):
        try:
            animated_data = AnimatedDecompose(image_pil).create_animated_data()
            animated_data = DisposeDuplicateFrames().dispose_animated(animated_data)
        except Exception:
            raise ImageDecompositionError()
        return animated_data

    def get_image_data(self) -> Union[ImageFrame, AnimatedData]:
        image_pil = self.open_image()

        width, height = image_pil.size
        image_format = str(image_pil.format)

        max_frames = MAX_FRAMES
        num_frames = self.get_num_frames(image_pil)

        min_px = 32
        max_px = self.get_max_pixels(num_frames)

        # Divided by 2 due to automatic frame disposal
        if (num_frames / 2) > max_frames:
            raise ExceedsMaxFrames(image_format, num_frames, max_frames)

        if width > max_px or height > max_px:
            raise ExceedsMaxResolution(image_format, width, height, max_px)

        if width < min_px or height < min_px:
            raise SubceedsMinResolution(image_format, width, height, min_px)

        if num_frames == 1:
            image_data = ImageFrame(
                image=image_pil,
                width=width,
                height=height,
            )
            return image_data

        return self.decompose_animated(image_pil)

    @staticmethod
    def decompose_video(video_io: BytesIO) -> VideoData:
        try:
            video_data = VideoDecompose(video_io).create_video_data()
            video_data = DisposeDuplicateFrames().dispose_video(video_data)
        except Exception:
            raise VideoDecompositionError()
        return video_data

    def get_video_data(self) -> VideoData:
        video_io = BytesIO(self.content)
        video_data = self.decompose_video(video_io)

        width, height = video_data.width, video_data.height

        max_frames = MAX_FRAMES
        num_frames = video_data.framecount

        min_px = 32
        max_px = self.get_max_pixels(num_frames)

        if num_frames > max_frames:
            raise ExceedsMaxFrames(self.mime_type, num_frames, max_frames)

        if width > max_px or height > max_px:
            raise ExceedsMaxResolution(self.mime_type, width, height, max_px)

        if width < min_px or height < min_px:
            raise SubceedsMinResolution(self.mime_type, width, height, min_px)

        return video_data
