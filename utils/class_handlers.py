from nextcord.ext.commands import Context
from utils.download_utils import download_image, download_video
from utils.rembg_dataclass import ExtensionConfig
from utils.general_utils import mime_type_sniff

from utils.rembg_utils import (
    get_video_frames,
    process_frames,
    remove_background,
    send_result_embed,
    get_animated_frames,
)


class MediaHandler:
    """MediaHandler class which handles different types of media files for rembg."""

    def __init__(self, ctx: Context, url: str):
        self.ctx = ctx
        self.url = url

    async def handler(self):
        """Handle the type of media and removes the background."""
        image_mime_types = ExtensionConfig().image_mime_types
        video_mime_types = ExtensionConfig().video_mime_types

        mime_type, error_embed = await self.get_mime_type()

        if error_embed:
            await self.ctx.reply(embed=error_embed)
        elif mime_type in image_mime_types:
            await self.image_handler()
        elif mime_type in video_mime_types:
            await self.video_handler()

    async def get_mime_type(self):
        """Get MimeType."""
        _, mime_type, error_embed = await mime_type_sniff(self.url)
        return mime_type, error_embed

    async def image_handler(self):
        """Handle image uploads."""
        image, num_frames, error_embed = await download_image(self.url)

        if error_embed:
            await self.ctx.reply(embed=error_embed, mention_author=False)

        elif image and num_frames and num_frames == 1:
            rembg_image = await remove_background(image)
            if rembg_image:
                await send_result_embed(self.ctx, rembg_image)

        elif image and num_frames and num_frames > 1:
            animated_FramesDict = await get_animated_frames(image)
            await process_frames(self.ctx, animated_FramesDict)

    async def video_handler(self):
        """Handles video uploads."""
        video, error_embed = await download_video(self.url)

        if not video and error_embed:
            await self.ctx.reply(embed=error_embed, mention_author=False)

        elif video:
            video_FramesDict = await get_video_frames(video)
            await process_frames(self.ctx, video_FramesDict)
