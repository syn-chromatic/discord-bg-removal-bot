
from nextcord.ext.commands import Context
from utils.download_utils import download_image, download_video

from utils.rembg_utils import (
    get_video_frames,
    process_frames,
    remove_background,
    send_result_embed,
    get_animated_frames,
)


class Video:
    async def handler(self, ctx: Context, url: str):
        video, error_embed = await download_video(url)

        if not video and error_embed:
            await ctx.reply(embed=error_embed, mention_author=False)

        elif video:
            video_FramesDict = await get_video_frames(video)
            await process_frames(ctx, video_FramesDict)


class Image:
    async def handler(self, ctx: Context, url: str):
        image, num_frames, error_embed = await download_image(url)

        if error_embed:
            await ctx.reply(embed=error_embed, mention_author=False)

        elif image and num_frames and num_frames == 1:
            rembg_image = await remove_background(image)
            await send_result_embed(ctx, rembg_image)

        elif image and num_frames and num_frames > 1:
            animated_FramesDict = await get_animated_frames(image)
            await process_frames(ctx, animated_FramesDict)
