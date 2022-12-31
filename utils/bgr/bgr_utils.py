import asyncio
from nextcord.ext.commands import Context

from rembg import remove
from io import BytesIO
from typing import Union

from PIL import Image
from PIL.Image import Image as ImageType
from numpy import ndarray

from utils.bgr.bgr_embeds import EmbedImageIterator
from utils.bgr.bgr_dataclasses import (
    AbstractData,
    AbstractFrame,
)


class BGRemoveBase:
    def __init__(self, frame: AbstractFrame):
        self._frame = frame

    def _retrieve_image(self) -> ImageType:
        return self._frame.image

    @staticmethod
    def _insert_image(image: ImageType, frame: AbstractFrame) -> AbstractFrame:
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
    def __init__(self, frame: AbstractFrame):
        super().__init__(frame)
        self.frame = frame

    def remove_background(self) -> AbstractFrame:
        image = self._retrieve_image()
        rembg_out = remove(data=image)
        rembg_image = self._image_conversion(rembg_out)
        frame = self._insert_image(rembg_image, self.frame)
        return frame


class BGProcessBase:
    def __init__(self, data: AbstractData):
        self._data = data
        self._animated_io: BytesIO = BytesIO()
        self._frames = self._retrieve_frames()

    def _retrieve_frames(self) -> list[AbstractFrame]:
        return self._data.frames

    @staticmethod
    def _retrieve_image(frame: AbstractFrame) -> ImageType:
        return frame.image

    @staticmethod
    def _pil_to_bytesio(image: ImageType) -> BytesIO:
        image_io = BytesIO()
        image = image.convert("P", colors=256)
        image.save(image_io, format="PNG", optimize=True)
        image_io.seek(0)
        return image_io

    @staticmethod
    def _process_image(frame: AbstractFrame) -> AbstractFrame:
        frame = BGRemove(frame).remove_background()
        return frame


class BGProcess(BGProcessBase):
    def __init__(self, ctx: Context, data: AbstractData):
        super().__init__(data)
        self.ctx = ctx

    async def process(self) -> AbstractData:
        embed_iterator = EmbedImageIterator(self.ctx)
        await embed_iterator.send()
        total_idx = len(self._frames)

        for idx, frame in enumerate(self._frames, start=1):
            bg_frame = await asyncio.to_thread(self._process_image, frame)
            bg_image = self._retrieve_image(bg_frame)
            bg_image_io = await asyncio.to_thread(self._pil_to_bytesio, bg_image)

            if idx != total_idx:
                await embed_iterator.update(idx, total_idx, bg_image_io)

        await embed_iterator.clean()
        return self._data
