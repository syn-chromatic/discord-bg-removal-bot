import nextcord
import asyncio

from PIL import Image
from PIL.Image import Image as ImageType
from io import BytesIO
from typing import Union
from uuid import uuid4


from fractions import Fraction
from nextcord.ext.commands import Context

from utils.http_utils import ContextHTTPFile
from utils.bgr.bgr_utils import BGProcess
from exceptions.exception_logging import ExceptionLogger

from configuration.command_variables.bgr_variables import (
    MAX_FRAMES,
    MAX_PX_IMAGE,
    MAX_PX_ANIMATED,
)


from utils.bgr.bgr_dataclasses import (
    MimeTypeConfig,
    ImageFrame,
    AbstractData,
    ImageData,
)


from utils.bgr.bgr_media import (
    ComposeGIF,
    VideoDecompose,
    AnimatedDecompose,
    DisposeDuplicateFrames,
)


from exceptions.media_exceptions import (
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
        self._mime_config = MimeTypeConfig()

    async def _validate_mime_type(self) -> str:
        async with ContextHTTPFile() as cf:
            mime_type = await cf.ensure_mime_type(self._url, self._mime_config)
        return mime_type

    async def _get_response_file(self) -> BytesIO:
        async with ContextHTTPFile() as cf:
            bytes_io = await cf.from_url(self._url)
        return bytes_io

    def _retrieve_data(
        self, bytes_io: BytesIO, mime_type: str
    ) -> Union[AbstractData, None]:
        image_mime_types = self._mime_config.image_mime_types
        video_mime_types = self._mime_config.video_mime_types

        if mime_type in image_mime_types:
            return self._get_image_data(bytes_io, mime_type)

        if mime_type in video_mime_types:
            return self._get_video_data(bytes_io, mime_type)

    def _create_file(self, output: BytesIO, ext: str) -> nextcord.File:
        filename = self._filename() + f".{ext}"
        nextcord_file = nextcord.File(fp=output, filename=filename)
        return nextcord_file

    @staticmethod
    def _get_image_data(bytes_io: BytesIO, mime_type: str) -> AbstractData:
        data = MediaData(bytes_io, mime_type).get_image_data()
        return data

    @staticmethod
    def _get_video_data(bytes_io: BytesIO, mime_type: str) -> AbstractData:
        data = MediaData(bytes_io, mime_type).get_video_data()
        return data

    @staticmethod
    def _filename() -> str:
        uuid_name = uuid4().hex[:10]
        return uuid_name


class MediaHandler(MediaHandlerBase):
    """MediaHandler class which handles different types of media files for rembg."""

    async def handler(self) -> Union[nextcord.File, None]:
        """Handle the type of media and removes the background."""
        mime_type = await self._validate_mime_type()
        bytes_io = await self._get_response_file()

        data = await asyncio.to_thread(self._retrieve_data, bytes_io, mime_type)

        if not data:
            return
        data_out = await BGProcess(self._ctx, data).process()

        if isinstance(data_out, ImageData):
            out_io = BytesIO()
            image_frame = data_out.frames[0]
            image_frame.image.save(out_io, "PNG")
            out_io.seek(0)
            nextcord_file = self._create_file(out_io, "png")
            return nextcord_file

        out_io = ComposeGIF(data_out).reconstruct()
        nextcord_file = self._create_file(out_io, "gif")
        return nextcord_file


class MediaData:
    def __init__(self, bytes_io: BytesIO, mime_type: str):
        self.bytes_io = bytes_io
        self.mime_type = mime_type

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
        try:
            image_pil = Image.open(self.bytes_io)
        except Exception as error:
            ExceptionLogger(error).log()
            raise ImageError()
        return image_pil

    @staticmethod
    def decompose_animated(image_pil: Image.Image) -> AbstractData:
        try:
            animated_data = AnimatedDecompose(image_pil).create_animated_data()
            frame_disposal = DisposeDuplicateFrames(animated_data)
            animated_data = frame_disposal.dispose_frames()
        except Exception as error:
            ExceptionLogger(error).log()
            raise ImageDecompositionError()
        return animated_data

    @staticmethod
    def create_image_data(image_pil: ImageType, width: int, height: int) -> ImageData:
        image_frame = ImageFrame(
            image=image_pil, width=width, height=height, duration=Fraction(0)
        )
        image_data = ImageData(
            frames=[image_frame],
            framecount=1,
            width=width,
            height=height,
            avg_fps=Fraction(1),
            total_duration=Fraction(0),
        )
        return image_data

    def get_image_data(self) -> AbstractData:
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
            image_data = self.create_image_data(image_pil, width, height)
            return image_data

        return self.decompose_animated(image_pil)

    @staticmethod
    def decompose_video(video_io: BytesIO) -> AbstractData:
        try:
            video_data = VideoDecompose(video_io).create_video_data()
            frame_disposal = DisposeDuplicateFrames(video_data)
            video_data = frame_disposal.dispose_frames()
        except Exception as error:
            ExceptionLogger(error).log()
            raise VideoDecompositionError()
        return video_data

    def get_video_data(self) -> AbstractData:
        video_data = self.decompose_video(self.bytes_io)

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
