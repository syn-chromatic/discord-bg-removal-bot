from PIL.Image import Image as ImageType
from fractions import Fraction
from dataclasses import dataclass
from abc import ABC


class AbstractFrame(ABC):
    image: ImageType
    width: int
    height: int
    duration: Fraction

    def __new__(cls, *args, **kwargs):
        if cls == AbstractFrame:
            raise TypeError("Cannot instantiate abstract class.")
        return super().__new__(cls)


@dataclass
class AbstractData(ABC):
    frames: list[AbstractFrame]
    framecount: int
    width: int
    height: int
    avg_fps: Fraction
    total_duration: Fraction

    def __new__(cls, *args, **kwargs):
        if cls == AbstractData:
            raise TypeError("Cannot instantiate abstract class.")
        return super().__new__(cls)


@dataclass
class VideoFrame(AbstractFrame):
    image: ImageType
    width: int
    height: int
    duration: Fraction


@dataclass
class AnimatedFrame(AbstractFrame):
    image: ImageType
    width: int
    height: int
    duration: Fraction


@dataclass
class ImageFrame(AbstractFrame):
    image: ImageType
    width: int
    height: int
    duration: Fraction


@dataclass
class VideoData(AbstractData):
    frames: list[VideoFrame]
    framecount: int
    width: int
    height: int
    avg_fps: Fraction
    total_duration: Fraction


@dataclass
class AnimatedData(AbstractData):
    frames: list[AnimatedFrame]
    framecount: int
    width: int
    height: int
    avg_fps: Fraction
    total_duration: Fraction


@dataclass
class ImageData(AbstractData):
    frames: list[ImageFrame]
    framecount: int
    width: int
    height: int
    avg_fps: Fraction
    total_duration: Fraction


@dataclass
class MimeTypeConfig:
    def __init__(self):
        self.image_mime_types: list[str] = ["png", "jpeg", "gif", "webp"]
        self.video_mime_types: list[str] = ["mp4"]
        self.mime_types = self.image_mime_types + self.video_mime_types
