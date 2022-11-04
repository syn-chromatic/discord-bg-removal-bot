from io import BytesIO
from PIL import Image

from typing import Union

from variables.command_variables import rembg_variables as rm_vars

from utils.media_dataclasses import ResponseFile, ImageFrame, VideoData, AnimatedData
from utils.media_utils import VideoDecompose, AnimatedDecompose


class ImageError(Exception):
    def __init__(self):
        msg = "An error occurred while loading the image."
        super().__init__(msg)


class ImageDecompositionError(Exception):
    def __init__(self):
        msg = "An error occurred while decomposing the image."
        super().__init__(msg)


class VideoDecompositionError(Exception):
    def __init__(self):
        msg = "An error occurred while decomposing the video."
        super().__init__(msg)


class ExceedsMaxFrames(Exception):
    def __init__(self, format, num_frames, max_frames):
        msg = (
            f"{format} exceeds maximum of {max_frames} frames.\n"
            f"**Frame Count:** {num_frames}"
        )
        super().__init__(msg)


class ExceedsMaxResolution(Exception):
    def __init__(self, format, width, height, max_px):
        msg = (
            f"{format} needs to be <{max_px}px in width or height.\n"
            f"**Resolution:** {width}x{height}"
        )
        super().__init__(msg)


class SubceedsMinResolution(Exception):
    def __init__(self, format, width, height, min_px):
        msg = (
            f"{format} needs to be >{min_px}px in width or height.\n"
            f"**Resolution:** {width}x{height}"
        )
        super().__init__(msg)


class DownloadMedia:
    def __init__(self, response_file: ResponseFile):
        self.response_file = response_file
        self.content = self.response_file.content
        self.mime_type = self.response_file.mime_type

    def get_num_frames(self, image_pil: Image.Image) -> int:
        """Get the number of frames in the image."""
        try:
            num_frames = image_pil.n_frames
        except Exception:
            num_frames = 1
        return num_frames

    def get_max_pixels(self, num_frames: int) -> int:
        """Determines the maximum number of pixels."""
        if num_frames > 1:
            max_px = rm_vars.max_px_animated
        else:
            max_px = rm_vars.max_px_image
        return max_px

    def open_image(self):
        image_io = BytesIO(self.content)

        try:
            image_pil = Image.open(image_io)
        except Exception:
            raise ImageError()

        return image_pil

    def decompose_animated(self, image_pil: Image.Image):
        try:
            animated_data = AnimatedDecompose(image_pil).create_animated_data()
        except Exception:
            raise ImageDecompositionError()
        return animated_data

    def download_image(self) -> Union[ImageFrame, AnimatedData]:
        image_pil = self.open_image()

        width, height = image_pil.size
        image_format = image_pil.format

        max_frames = rm_vars.max_frames_animated
        num_frames = self.get_num_frames(image_pil)

        min_px = 32
        max_px = self.get_max_pixels(num_frames)

        if num_frames > max_frames:
            raise ExceedsMaxFrames(image_format, num_frames, max_frames)

        elif width > max_px or height > max_px:
            raise ExceedsMaxResolution(image_format, width, height, max_px)

        elif width < min_px or height < min_px:
            raise SubceedsMinResolution(image_format, width, height, min_px)

        if num_frames == 1:
            image_data = ImageFrame(
                image=image_pil,
                width=width,
                height=height,
            )
            return image_data

        return self.decompose_animated(image_pil)

    def decompose_video(self, video_io: BytesIO) -> VideoData:
        try:
            video_data = VideoDecompose(video_io).create_video_data()
        except Exception:
            raise VideoDecompositionError()
        return video_data

    def download_video(self) -> VideoData:
        video_io = BytesIO(self.content)
        video_data = self.decompose_video(video_io)

        width, height = video_data.width, video_data.height

        max_frames = rm_vars.max_frames_animated
        num_frames = video_data.framecount

        min_px = 32
        max_px = self.get_max_pixels(num_frames)

        if num_frames > max_frames:
            raise ExceedsMaxFrames(self.mime_type, num_frames, max_frames)

        elif width > max_px or height > max_px:
            raise ExceedsMaxResolution(self.mime_type, width, height, max_px)

        elif width < min_px or height < min_px:
            raise SubceedsMinResolution(self.mime_type, width, height, min_px)

        return video_data