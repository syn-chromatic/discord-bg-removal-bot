import requests
import sniffpy

from sniffpy.mimetype import parse_mime_type
from utils.bgr.bgr_dataclasses import MimeTypeConfig, ResponseFile


class ConnectionError(Exception):
    def __init__(self):
        super().__init__("Connection error occurred.")


class UnsupportedFileType(Exception):
    def __init__(self, mime_type: str):
        msg = "Detected file mime type as: " f"'{mime_type}', which is not supported."
        super().__init__(msg)


class MimeTypeSniff(MimeTypeConfig):
    def __init__(self, url) -> None:
        super().__init__()
        self.url = url
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
                self.url,
                stream=True,
                headers=self._headers(),
                timeout=10
            )
        except Exception:
            raise ConnectionError()

        return response

    def get_mime_type(self) -> ResponseFile:
        content_iter = self.response.iter_content(2048)
        content_chunk = content_iter.__next__()

        sniff_type = str(sniffpy.sniff(content_chunk))

        parse_mime = parse_mime_type(sniff_type)
        mime_type = parse_mime.subtype

        if mime_type in self.mime_types:
            content = content_chunk + self.response.content
            response_file = ResponseFile(
                content=content,
                mime_type=mime_type,
            )
            return response_file

        raise UnsupportedFileType(mime_type)
