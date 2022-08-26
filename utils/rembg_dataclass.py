from dataclasses import dataclass, field


@dataclass
class ExtensionConfig:
    """File Type Extension Configuration"""
    file_extensions: list[str] = field(
        default_factory=lambda: [
            "png", "jpg", "jpeg",
            "gif", "webp", "mp4"
            ]
    )

    image_mime_types: list[str] = field(
        default_factory=lambda: [
            'png', 'jpeg', 'gif', 'webp'
            ]
    )

    video_mime_types: list[str] = field(
        default_factory=lambda: [
            'mp4'
            ]
    )
