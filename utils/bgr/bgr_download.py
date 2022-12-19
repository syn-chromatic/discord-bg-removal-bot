from io import BytesIO
from PIL import Image

from typing import Union
from configuration.command_variables.bgr_variables import (
    MAX_FRAMES,
    MAX_PX_IMAGE,
    MAX_PX_ANIMATED,
)

from utils.bgr.bgr_dataclasses import (
    ResponseFile,
    ImageFrame,
    VideoData,
    AnimatedData,
)

from utils.bgr.bgr_media import (
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


class DownloadMedia:
    def __init__(self, response_file: ResponseFile):
        self.response_file = response_file
        self.content = self.response_file.content
        self.mime_type = self.response_file.mime_type

    @staticmethod
    def get_num_frames(image_pil: Image.Image) -> int:
        """Get the number of frames in the image."""
        try:
            num_frames = image_pil.n_frames
        except Exception:
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

    def download_image(self) -> Union[ImageFrame, AnimatedData]:
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

    def download_video(self) -> VideoData:
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
