from nextcord.ext.commands import Context

from rembg import remove
from io import BytesIO
from typing import Union

from PIL import Image
from PIL.Image import Image as ImageType
from numpy import ndarray

from utils.embed_utils import RelayIterator
from utils.media_dataclasses import (
    VideoFrame,
    AnimatedFrame,
    VideoData,
    AnimatedData,
    ImageFrame,
    RelayConfig,
)


FRAME_TYPES = Union[VideoFrame, AnimatedFrame, ImageFrame]
DATA_TYPES = Union[VideoData, AnimatedData, ImageFrame]


class BGRemoveBase:
    def __init__(self, frame: Union[ImageFrame, VideoFrame, AnimatedFrame]):
        self._frame = frame

    def _retrieve_image(self):
        if isinstance(self._frame, VideoFrame):
            return self._video_frame(self._frame)

        if isinstance(self._frame, AnimatedFrame):
            return self._animated_frame(self._frame)

        return self._image_frame(self._frame)

    def _insert_image(self, image: ImageType, frame: FRAME_TYPES):
        if isinstance(frame, VideoFrame):
            return self._ins_video_frame(image, frame)

        if isinstance(frame, AnimatedFrame):
            return self._ins_animated_frame(image, frame)

        return self._ins_image_frame(image, frame)

    @staticmethod
    def _video_frame(video_frame: VideoFrame):
        image = video_frame.image
        return image

    @staticmethod
    def _animated_frame(animated_frame: AnimatedFrame):
        image = animated_frame.image
        return image

    @staticmethod
    def _image_frame(image_frame: ImageFrame):
        image = image_frame.image
        return image

    @staticmethod
    def _ins_video_frame(image: ImageType, frame: VideoFrame) -> VideoFrame:
        frame.image = image
        return frame

    @staticmethod
    def _ins_animated_frame(image: ImageType, frame: AnimatedFrame) -> AnimatedFrame:
        frame.image = image
        return frame

    @staticmethod
    def _ins_image_frame(image: ImageType, frame: ImageFrame) -> ImageFrame:
        frame.image = image
        return frame

    @staticmethod
    def _image_conversion(image: Union[ImageType, bytes, ndarray]) -> ImageType:
        if isinstance(image, ImageType):
            return image

        if isinstance(image, bytes):
            return Image.open(image)

        return Image.fromarray(image)


class BGRemove(BGRemoveBase):
    def __init__(self, frame: FRAME_TYPES):
        super().__init__(frame)
        self.frame = frame

    def remove_background(self) -> FRAME_TYPES:
        image = self._retrieve_image()
        rembg_out = remove(data=image)
        rembg_image = self._image_conversion(rembg_out)
        frame = self._insert_image(rembg_image, self.frame)
        return frame


class BGProcessBase:
    def __init__(self, data: DATA_TYPES):
        self._data = data
        self._animated_io: BytesIO = BytesIO()
        self._frames = self._retrieve_frames()

    def _retrieve_frames(self):
        if isinstance(self._data, VideoData):
            return self._video_frames(self._data)

        if isinstance(self._data, AnimatedData):
            return self._animated_frames(self._data)

        return self._image_frames(self._data)

    def _retrieve_image(self, frame: FRAME_TYPES):
        if isinstance(frame, VideoFrame):
            return self._video_image(frame)

        if isinstance(frame, AnimatedFrame):
            return self._animated_image(frame)

        return self._image(frame)

    @staticmethod
    def _video_frames(data: VideoData):
        return data.frames

    @staticmethod
    def _animated_frames(data: AnimatedData):
        return data.frames

    @staticmethod
    def _image_frames(data: ImageFrame):
        return [data]

    @staticmethod
    def _video_image(video_frame: VideoFrame):
        return video_frame.image

    @staticmethod
    def _animated_image(animated_frame: AnimatedFrame):
        return animated_frame.image

    @staticmethod
    def _image(image_frame: ImageFrame):
        return image_frame.image

    @staticmethod
    def _pil_to_bytesio(image: ImageType):
        image_io = BytesIO()
        image.save(image_io, format="PNG")
        image_io.seek(0)
        return image_io

    @staticmethod
    def _process_image(frame: FRAME_TYPES):
        frame = BGRemove(frame).remove_background()
        return frame

    @staticmethod
    def _init_config():
        relay_config = RelayConfig(init=True, image=None, idx=0, total_idx=0)
        return relay_config

    @staticmethod
    def _relay_config(image: Union[BytesIO, None], idx: int, total_idx: int):
        relay_config = RelayConfig(
            init=False,
            image=image,
            idx=idx,
            total_idx=total_idx,
        )
        return relay_config


class BGProcess(BGProcessBase):
    def __init__(self, ctx: Context, data: DATA_TYPES):
        super().__init__(data)
        self.ctx = ctx

    async def process(self):
        iterator = RelayIterator(self.ctx)

        relay_config = self._init_config()
        await iterator.send(relay_config)
        total_idx = len(self._frames)

        for idx, frame in enumerate(self._frames):
            if idx == 0:
                relay_config = self._relay_config(None, 0, total_idx)
                await iterator.send(relay_config)

            bg_frame = self._process_image(frame)
            bg_image = self._retrieve_image(bg_frame)
            bg_image_io = self._pil_to_bytesio(bg_image)

            if idx + 1 != total_idx:
                relay_config = self._relay_config(bg_image_io, idx + 1, total_idx)
                await iterator.send(relay_config)

        await iterator.clean()
        return self._data
