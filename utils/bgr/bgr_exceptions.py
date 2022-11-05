class MimeConnectionError(Exception):
    """An exception raised when a connection error occurs during Mime Sniffing."""

    def __init__(self):
        super().__init__("Connection error occurred.")


class UnsupportedFileType(Exception):
    """An exception raised when an unsupported file type is detected."""

    def __init__(self, mime_type: str):
        msg = "Detected file mime type as: " f"'{mime_type}', which is not supported."
        super().__init__(msg)


class ImageError(Exception):
    """An exception raised when an error occurs upon loading an image."""

    def __init__(self):
        msg = "An error occurred while loading the image."
        super().__init__(msg)


class ImageDecompositionError(Exception):
    """An exception raised when an error occurs in AnimatedDecompose."""

    def __init__(self):
        msg = "An error occurred while decomposing the image."
        super().__init__(msg)


class VideoDecompositionError(Exception):
    """An exception raised when an error occurs in VideoDecompose."""

    def __init__(self):
        msg = "An error occurred while decomposing the video."
        super().__init__(msg)


class ExceedsMaxFrames(Exception):
    """
    An exception raised when a video or animated file
    exceeds a specified frames limit.
    """

    def __init__(self, fp_format: str, num_frames: int, max_frames: int):
        msg = (
            f"{fp_format} exceeds maximum of {max_frames} frames.\n"
            f"Frame Count: {num_frames}"
        )
        super().__init__(msg)


class ExceedsMaxResolution(Exception):
    """An exception raised when a media file exceeds a specified maximum resolution."""

    def __init__(self, fp_format: str, width: int, height: int, max_px: int):
        msg = (
            f"{fp_format.upper()} needs to be <{max_px}px in width or height.\n"
            f"Resolution: {width}x{height}"
        )
        super().__init__(msg)


class SubceedsMinResolution(Exception):
    """An exception raised when a media file subceeds a specified minimum resolution."""

    def __init__(self, fp_format: str, width: int, height: int, min_px: int):
        msg = (
            f"{fp_format.upper()} needs to be >{min_px}px in width or height.\n"
            f"Resolution: {width}x{height}"
        )
        super().__init__(msg)


BGR_EXCEPTIONS = (
    MimeConnectionError,
    UnsupportedFileType,
    ImageError,
    ImageDecompositionError,
    VideoDecompositionError,
    ExceedsMaxFrames,
    ExceedsMaxResolution,
    SubceedsMinResolution,
)
