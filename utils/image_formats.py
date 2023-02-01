from dataclasses import dataclass
from typing_extensions import Type, Self


@dataclass(frozen=True)
class PILFormat:
    name: str

    def __new__(cls) -> Type[Self]:
        return cls


@dataclass(frozen=True)
class ImagePNG(PILFormat):
    name: str = "PNG"


@dataclass(frozen=True)
class ImageJPEG(PILFormat):
    name: str = "JPEG"


@dataclass(frozen=True)
class ImageWEBP(PILFormat):
    name: str = "WEBP"
