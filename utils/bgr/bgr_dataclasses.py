from PIL.Image import Image as ImageType
from fractions import Fraction
from dataclasses import dataclass


@dataclass
class VideoFrame:
    image: ImageType
    width: int
    height: int
    duration: Fraction


@dataclass
class VideoData:
    frames: list[VideoFrame]
    framecount: int
    width: int
    height: int
    avg_fps: Fraction
    total_duration: Fraction


@dataclass
class AnimatedFrame:
    image: ImageType
    width: int
    height: int
    duration: Fraction


@dataclass
class AnimatedData:
    frames: list[AnimatedFrame]
    framecount: int
    avg_fps: Fraction
    total_duration: Fraction


@dataclass
class ImageFrame:
    image: ImageType
    width: int
    height: int


@dataclass
class ResponseFile:
    content: bytes
    mime_type: str


@dataclass
class MimeTypeConfig:
    def __init__(self):
        self.image_mime_types: list[str] = ["png", "jpeg", "gif", "webp"]
        self.video_mime_types: list[str] = ["mp4"]
        self.mime_types = self.image_mime_types + self.video_mime_types
