import logging
import traceback

from aiohttp import ClientResponse, ClientSession
from sniffpy.mimetype import parse_mime_type
from nextcord.ext.commands import Context

from io import BytesIO
from typing import Union

from utils.bgr.bgr_dataclasses import MimeTypeConfig
from exceptions.exception_logging import ExceptionLogger
from exceptions.bot_exceptions import ContextAttachmentUnavailable
from exceptions.http_exceptions import (
    ResponseConnectionError,
    ResponseContentError,
    UnsupportedMimeType,
)

logger = logging.getLogger("nextcord")


class ContextHTTPBase:
    def __init__(self):
        super().__init__()
        self._session: ClientSession = ClientSession()
        self._response: Union[ClientResponse, None] = None
        self._content: bytes = bytes()

    @staticmethod
    async def _headers() -> dict[str, str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/34.0.1847.137 Safari/537.36"
        }
        return headers

    @staticmethod
    async def _get_content_size(response: ClientResponse) -> Union[float, None]:
        content_bytes = response.content_length
        if content_bytes:
            content_bytes = int(content_bytes)
            content_mb = content_bytes / 1024 / 1024
            return content_mb

    @staticmethod
    async def _get_file_size(bytes_io: BytesIO) -> float:
        content_nbytes = bytes_io.getbuffer().nbytes
        content_mb = content_nbytes / 1024 / 1024
        return content_mb

    async def _get_attachment_url(self, ctx: Context) -> str:
        attachments = ctx.message.attachments
        if attachments:
            return attachments[0].url
        raise ContextAttachmentUnavailable()

    async def _get_content(self, response: ClientResponse) -> bytes:
        try:
            response_content = await response.content.read()
        except Exception:
            raise ResponseContentError()
        return response_content

    async def _get_content_io(self, response: ClientResponse) -> BytesIO:
        bytes_content = await self._get_content(response)
        bytes_io = BytesIO(bytes_content)
        return bytes_io

    async def _setup_response(self, url: str) -> ClientResponse:
        try:
            self._response = await self._session.get(url=url, timeout=2)
        except Exception:
            raise ResponseConnectionError()
        return self._response

    async def _get_response(self, url: str) -> ClientResponse:
        if self._response:
            return self._response
        return await self._setup_response(url)

    async def _get_mime_type(self, url: str) -> str:
        response = await self._get_response(url)
        content_type = response.content_type
        parse_mime = parse_mime_type(content_type)
        mime_type = parse_mime.subtype
        return mime_type

    async def _close_client(self):
        await self._session.close()
        if self._response:
            self._response.close()

    async def _from_url(self, url: str) -> BytesIO:
        response = await self._get_response(url)
        bytes_io = await self._get_content_io(response)
        return bytes_io

    def _format_traceback(self, tb) -> str:
        frmt_tb = "".join(traceback.format_tb(tb))
        return frmt_tb


class ContextHTTPFile(ContextHTTPBase):
    def __init__(self):
        super().__init__()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exception_type, exception, tb):
        if exception:
            ExceptionLogger(exception).log()
        await self._close_client()

    async def get_mime_type(self, url: str) -> str:
        mime_type = await self._get_mime_type(url)
        return mime_type

    async def ensure_mime_type(self, url: str, mime_config: MimeTypeConfig) -> str:
        mime_type = await self._get_mime_type(url)
        if mime_type in mime_config.mime_types:
            return mime_type
        raise UnsupportedMimeType(mime_type)

    async def get_ctx_attachment_url(self, ctx: Context) -> str:
        attachment_url = await self._get_attachment_url(ctx)
        return attachment_url

    async def from_url(self, url: str) -> BytesIO:
        bytes_io = await self._from_url(url)
        return bytes_io
