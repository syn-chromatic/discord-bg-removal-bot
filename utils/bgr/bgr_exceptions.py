class MimeConnectionError(Exception):
    def __init__(self):
        super().__init__("Connection error occurred.")


class UnsupportedFileType(Exception):
    def __init__(self, mime_type: str):
        msg = "Detected file mime type as: " f"'{mime_type}', which is not supported."
        super().__init__(msg)


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
    def __init__(self, fp_format: str, num_frames: int, max_frames: int):
        msg = (
            f"{fp_format} exceeds maximum of {max_frames} frames.\n"
            f"Frame Count: {num_frames}"
        )
        super().__init__(msg)


class ExceedsMaxResolution(Exception):
    def __init__(self, fp_format: str, width: int, height: int, max_px: int):
        msg = (
            f"{fp_format.upper()} needs to be <{max_px}px in width or height.\n"
            f"Resolution: {width}x{height}"
        )
        super().__init__(msg)


class SubceedsMinResolution(Exception):
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
