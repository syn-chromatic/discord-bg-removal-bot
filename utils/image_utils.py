from io import BytesIO

from PIL import Image
from PIL.Image import Image as ImageType
from typing import Type

from utils.image_formats import PILFormat
from logger.exception_logging import ExceptionLogger
from exceptions.media_exceptions import (
    ExceedsMaxFrames,
    ExceedsMaxResolution,
    SubceedsMinResolution,
    UnsupportedFileType,
    ImageError,
)


class ImageIOBase:
    def __init__(self, bytes_io: BytesIO):
        self._bytes_io = bytes_io
        self._image = self._get_pil_image()

    def _eval_format(self, formats: list[Type[PILFormat]]) -> bool:
        format = self._image.format
        format_list = [pil_fmt.name for pil_fmt in formats]
        return format in format_list

    def _eval_max_px(self, max_dim: int) -> bool:
        width, height = self._image.size
        return width <= max_dim and height <= max_dim

    def _eval_min_px(self, min_dim: int) -> bool:
        width, height = self._image.size
        return width >= min_dim and height >= min_dim

    def _get_image_format(self) -> str:
        if self._image.format:
            return self._image.format
        return "Unknown"

    def _get_frame_count(self) -> int:
        if hasattr(self._image, "n_frames"):
            return self._image.n_frames
        return 1

    def _get_pil_image(self) -> ImageType:
        try:
            image = Image.open(self._bytes_io)
        except Exception as error:
            ExceptionLogger(error).log()
            raise ImageError()
        return image


class ImageIO(ImageIOBase):
    def __init__(self, bytes_io: BytesIO):
        super().__init__(bytes_io)

    def assert_format(self, formats: list[Type[PILFormat]]):
        image_format = self._get_image_format()
        if not self._eval_format(formats):
            raise UnsupportedFileType(image_format)

    def assert_resolution(self, min_dim: int, max_dim: int):
        image_format = self._get_image_format()
        width, height = self._image.size

        if not self._eval_max_px(max_dim):
            raise ExceedsMaxResolution(image_format, width, height, max_dim)

        if not self._eval_min_px(min_dim):
            raise SubceedsMinResolution(image_format, width, height, min_dim)

    def assert_frame_count(self, max_frames: int):
        image_format = self._get_image_format()
        frame_count = self._get_frame_count()
        if frame_count > max_frames:
            raise ExceedsMaxFrames(image_format, frame_count, max_frames)

    def get_image(self) -> ImageType:
        return self._image
