import requests
import sniffpy

from nextcord import Embed
from typing import Union

from sniffpy.mimetype import MIMEType, parse_mime_type
from utils.rembg_dataclass import ExtensionConfig


async def construct_embed(message: str) -> Embed:
    """Constructs an embed with the message provided."""
    if isinstance(message, str):
        embed = Embed(description=message, type="rich", color=0xC82323)
    else:
        error_message = "Unexpected error occurred while creating embed message."
        embed = Embed(description=error_message, type="rich", color=0xC82323)
    return embed


async def mime_type_sniff(url) -> tuple[bool, Union[str, None], Union[Embed, None]]:
    """Mime type sniffing"""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 6.1; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/34.0.1847.137 Safari/537.36"
        )
    }
    type_check: bool = False
    mime_type: Union[str, None] = None
    error_embed: Union[Embed, None] = None

    try:
        response = requests.get(url, stream=True, headers=headers)
    except requests.exceptions.ConnectionError:
        error_embed = await construct_embed("Connection Error.")
        return type_check, mime_type, error_embed

    sniffpy_response: str = str(sniffpy.sniff(response.content))
    mime_type_parse: MIMEType = parse_mime_type(sniffpy_response)
    mime_type = mime_type_parse.subtype

    valid_extensions = [
        *ExtensionConfig().image_mime_types,
        *ExtensionConfig().video_mime_types,
    ]

    if mime_type in valid_extensions:
        type_check = True

    else:
        type_check = False
        error_embed = await construct_embed(
            "Detected file mime type as: " f"'{mime_type}', which is not supported."
        )
    return type_check, mime_type, error_embed
