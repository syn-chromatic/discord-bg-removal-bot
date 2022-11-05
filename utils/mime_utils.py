import requests
import sniffpy

from sniffpy.mimetype import parse_mime_type
from utils.media_dataclasses import MimeTypeConfig, ResponseFile


class ConnectionError(Exception):
    def __init__(self):
        super().__init__("Connection error occurred.")


class UnsupportedFileType(Exception):
    def __init__(self, mime_type: str):
        msg = "Detected file mime type as: " f"'{mime_type}', which is not supported."
        super().__init__(msg)


class MimeTypeSniff:
    def __init__(self, url):
        self.url = url
        self.valid_mime_types = self.get_valid_mime_types()
        self.response = self.get_response()

    @staticmethod
    def _headers():
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/34.0.1847.137 Safari/537.36"
        }
        return headers

    def get_response(self) -> requests.Response:
        try:
            response = requests.get(
                self.url, stream=True, headers=self._headers(), timeout=10
            )
        except requests.exceptions.ConnectionError:
            raise ConnectionError()

        return response

    @staticmethod
    def get_valid_mime_types():
        valid_types = [
            *MimeTypeConfig().image_mime_types,
            *MimeTypeConfig().video_mime_types,
        ]
        return valid_types

    def get_mime_type(self) -> ResponseFile:
        content_iter = self.response.iter_content(2048)
        content_chunk = content_iter.__next__()

        sniff_type = str(sniffpy.sniff(content_chunk))

        parse_mime = parse_mime_type(sniff_type)
        mime_type = parse_mime.subtype

        if mime_type in self.valid_mime_types:
            content = self.response.content
            response_file = ResponseFile(
                content=content,
                mime_type=mime_type,
            )
            return response_file

        raise UnsupportedFileType(mime_type)
