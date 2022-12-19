import sniffpy

from aiohttp import ClientResponse, ClientSession
from sniffpy.mimetype import parse_mime_type
from nextcord.ext.commands import Context

from io import BytesIO
from typing import Union

from utils.bgr.bgr_dataclasses import ResponseFile, MimeTypeConfig
from utils.bgr.bgr_exceptions import (
    ResponseConnectionError,
    ResponseContentError,
    UnsupportedFileType,
    ContextAttachmentUnavailable,
)


class DownloadFileBase(MimeTypeConfig):
    def __init__(self):
        super().__init__()

    @staticmethod
    async def _headers() -> dict[str, str]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/34.0.1847.137 Safari/537.36"
        }
        return headers

    @staticmethod
    async def _get_mime_type(content_chunk: bytes) -> str:
        sniff_type = str(sniffpy.sniff(content_chunk))

        parse_mime = parse_mime_type(sniff_type)
        mime_type = parse_mime.subtype
        return mime_type

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
        await self._close_session()
        raise ContextAttachmentUnavailable()

    async def _get_content(self, response: ClientResponse) -> bytes:
        try:
            response_content = await response.content.read()
        except Exception:
            await self._close_session()
            raise ResponseContentError()
        return response_content

    async def _get_response(self, url: str) -> ClientResponse:
        try:
            self.session = ClientSession()
            self.response = await self.session.get(url=url, timeout=2)
        except Exception:
            await self._close_session()
            raise ResponseConnectionError()
        return self.response

    async def _close_session(self):
        await self.session.close()
        self.response.close()

    async def _from_url(self, url: str) -> ResponseFile:
        response = await self._get_response(url)
        content_iter = response.content.iter_chunked(2048)
        content_chunk = await content_iter.__anext__()
        mime_type = await self._get_mime_type(content_chunk)

        if mime_type in self.mime_types:
            remaining_chunks = await self._get_content(response)
            content = content_chunk + remaining_chunks

            response_file = ResponseFile(
                content=content,
                mime_type=mime_type,
            )
            return response_file
        await self._close_session()
        raise UnsupportedFileType(mime_type)


class DownloadFile(DownloadFileBase):
    def __init__(self):
        super().__init__()

    async def from_url(self, url: str) -> ResponseFile:
        response_file = await self._from_url(url)
        await self._close_session()
        return response_file

    async def from_ctx(self, ctx: Context) -> ResponseFile:
        attachment_url = await self._get_attachment_url(ctx)
        response_file = await self.from_url(attachment_url)
        await self._close_session()
        return response_file
