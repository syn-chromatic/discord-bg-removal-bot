from dataclasses import dataclass


@dataclass(frozen=True)
class InputDescription:
    text: str
    pos: int


@dataclass(frozen=True)
class StrDescription(InputDescription):
    text: str = "`[INPUT]` ― *Input String*"
    pos: int = 0


@dataclass(frozen=True)
class ImageDescription(InputDescription):
    text: str = "`[IMAGE]` ― *Image Attachment*"
    pos: int = 1


@dataclass(frozen=True)
class ImageRefDescription(InputDescription):
    text: str = "`[R\\IMAGE]` ― *Reference Image Attachment*"
    pos: int = 2


@dataclass(frozen=True)
class MediaDescription(InputDescription):
    text: str = "`[MEDIA]` ― *Media Attachment*"
    pos: int = 3


@dataclass(frozen=True)
class MediaRefDescription(InputDescription):
    text: str = "`[R\\MEDIA]` ― *Reference Media Attachment*"
    pos: int = 4


@dataclass(frozen=True)
class AddImageDescription(InputDescription):
    text: str = "`[+IMAGE]` ― *Additional Image Attachment*"
    pos: int = 5


@dataclass(frozen=True)
class AddRefImageDescription(InputDescription):
    text: str = "`[+R\\IMAGE]` ― *Additional Reference Image Attachment*"
    pos: int = 6


@dataclass(frozen=True)
class AddMediaDescription(InputDescription):
    text: str = "`[+MEDIA]` ― *Media Attachment*"
    pos: int = 7


@dataclass(frozen=True)
class AddMediaRefDescription(InputDescription):
    text: str = "`[+R\\MEDIA]` ― *Reference Media Attachment*"
    pos: int = 8


@dataclass(frozen=True)
class CommandInputType:
    header: str
    input_descriptions: frozenset[InputDescription]


@dataclass(frozen=True)
class StrWithImageInput(CommandInputType):
    header: str = "`[INPUT]` `[+IMAGE]` `[+R\\IMAGE]`"
    input_descriptions: frozenset[InputDescription] = frozenset(
        {
            StrDescription(),
            AddImageDescription(),
            AddRefImageDescription(),
        }
    )


@dataclass(frozen=True)
class StrInput(CommandInputType):
    header: str = "`[INPUT]`"
    input_descriptions: frozenset[InputDescription] = frozenset({StrDescription()})


@dataclass(frozen=True)
class ImageWRefInput(CommandInputType):
    header: str = "`[IMAGE]` ⚬ `[R\\IMAGE]`"
    input_descriptions: frozenset[InputDescription] = frozenset(
        {
            ImageDescription(),
            ImageRefDescription(),
        }
    )


@dataclass(frozen=True)
class MediaWRefInput(CommandInputType):
    header: str = "`[MEDIA]` ⚬ `[R\\MEDIA]`"
    input_descriptions: frozenset[InputDescription] = frozenset(
        {
            MediaDescription(),
            MediaRefDescription(),
        }
    )
