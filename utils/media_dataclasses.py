from io import BytesIO
from typing import Union
from PIL.Image import Image as ImageType
from fractions import Fraction
from dataclasses import dataclass, field
from nextcord import Message


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
class RelayMessage:
    message: Message
    url: str


@dataclass
class RelayConfig:
    init: bool
    image: Union[BytesIO, None]
    idx: int
    total_idx: int


@dataclass
class ExtensionConfig:
    """File Type Extension Configuration"""

    file_extensions: list[str] = field(
        default_factory=lambda: ["png", "jpg", "jpeg", "gif", "webp", "mp4"]
    )

    image_mime_types: list[str] = field(
        default_factory=lambda: ["png", "jpeg", "gif", "webp"]
    )

    video_mime_types: list[str] = field(default_factory=lambda: ["mp4"])
