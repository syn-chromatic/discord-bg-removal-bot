import requests
import sniffpy

from sniffpy.mimetype import parse_mime_type
from utils.media_dataclasses import ExtensionConfig, ResponseFile


class ConnectionError(Exception):
    def __init__(self):
        super().__init__("Connection error occurred.")


class UnsupportedFileType(Exception):
    def __init__(self, mime_type: str):
        msg = "Detected file mime type as: " f"'{mime_type}', which is not supported."
        super().__init__(msg)


class MimeTypeSniff():
    def __init__(self, url):
        self.url = url
        self.valid_extensions = self.get_valid_extensions()
        self.response = self.get_response()

    def get_response(self) -> requests.Response:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 6.1; WOW64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/34.0.1847.137 Safari/537.36"
            )
        }

        try:
            response = requests.get(self.url, stream=True, headers=headers)
        except requests.exceptions.ConnectionError:
            raise ConnectionError()

        return response

    def get_valid_extensions(self):
        valid_extensions = [
            *ExtensionConfig().image_mime_types,
            *ExtensionConfig().video_mime_types,
        ]
        return valid_extensions

    def get_mime_type(self) -> ResponseFile:
        content = self.response.content
        sniff_type = str(sniffpy.sniff(content))
        parse_mime = parse_mime_type(sniff_type)
        mime_type = parse_mime.subtype

        if mime_type in self.valid_extensions:
            response_file = ResponseFile(
                content=content,
                mime_type=mime_type,
            )
            return response_file

        raise UnsupportedFileType(mime_type)
