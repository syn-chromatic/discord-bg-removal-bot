
from nextcord.ext.commands import Context
from utils.download_utils import download_image, download_video
from utils.rembg_dataclass import ExtensionConfig

from utils.rembg_utils import (
    get_video_frames,
    process_frames,
    remove_background,
    send_result_embed,
    get_animated_frames,
)


class MediaHandler():
    def __init__(self, mime_type):
        self.mime_type = mime_type
        image_mime_types = ExtensionConfig().image_mime_types
        video_mime_types = ExtensionConfig().video_mime_types

        if mime_type in image_mime_types:
            self.handler = self.image_handler
        elif mime_type in video_mime_types:
            self.handler = self.video_handler

    async def handler(self, ctx: Context, url: str):
        pass

    async def image_handler(self, ctx: Context, url: str):
        image, num_frames, error_embed = await download_image(url)

        if error_embed:
            await ctx.reply(embed=error_embed, mention_author=False)

        elif image and num_frames and num_frames == 1:
            rembg_image = await remove_background(image)
            if rembg_image:
                await send_result_embed(ctx, rembg_image)

        elif image and num_frames and num_frames > 1:
            animated_FramesDict = await get_animated_frames(image)
            await process_frames(ctx, animated_FramesDict)

    async def video_handler(self, ctx: Context, url: str):
        video, error_embed = await download_video(url)

        if not video and error_embed:
            await ctx.reply(embed=error_embed, mention_author=False)

        elif video:
            video_FramesDict = await get_video_frames(video)
            await process_frames(ctx, video_FramesDict)
