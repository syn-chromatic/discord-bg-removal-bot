import ctypes
import math
import nextcord
import av
from rembg import remove
from wand.image import Image as ImageWand
from wand.sequence import SingleImage
from wand.sequence import Sequence
from wand.api import library as LibraryWand

from copy import copy
from io import BytesIO
from PIL import Image, ImageSequence

from variables.command_variables import rembg_variables as rm_vars
from variables import bot_config
from typing import Union
from nextcord import Message, Embed
from nextcord.errors import Forbidden
from nextcord.ext.commands import Context
from nextcord import TextChannel, Guild


async def send_result_embed(ctx: Context, image_io: BytesIO, image_format="PNG"):
    """Sends an image embed to the channel the command was invoked in."""
    image_filename = f"removed_background.{image_format}"
    file = nextcord.File(fp=image_io, filename=image_filename)

    descriptionText = "Background removed!"

    embed = nextcord.Embed(title="", description=descriptionText)
    embed.set_image(url=f"attachment://{image_filename}")
    await ctx.reply(file=file, embed=embed, mention_author=False)


def embed_iterator(
    idx, total_idx, relay=False, relay_url=None, relay_error=None, initialization=False
) -> Embed:
    """Iterator for the relay channel."""
    if initialization:
        embed = nextcord.Embed(description="Initializing..")

    else:
        descriptionIterator = f"Processed {idx+1} out of {total_idx} frames."
        descriptionRelayError = (
            f"{descriptionIterator}\n\n" f"**Relay Channel Error:** {relay_error}"
        )

        if relay and relay_error:
            embed = nextcord.Embed(description=descriptionRelayError)

        else:
            embed = nextcord.Embed(description=descriptionIterator)
            if relay:
                embed.set_image(url=relay_url)

    return embed


async def get_channel(
    ctx: Context, channel_id: Union[int, None]
) -> Union[TextChannel, None]:
    """Get a channel by ID."""
    guild: Union[Guild, None] = ctx.guild
    channel = None
    if channel_id:
        channel = guild.get_channel(channel_id) if guild else None
        channel = channel if isinstance(channel, TextChannel) else None
    return channel


async def relay_transmitter(
    ctx: Context, Image_IO: BytesIO
) -> tuple[Union[Message, None], Union[str, None], Union[str, None]]:
    """Transmitter for the relay channel."""
    relay_channel_id: Union[int, None] = bot_config.RELAY_CHANNEL_ID
    relay_channel = await get_channel(ctx, relay_channel_id)

    relay_message: Union[Message, None] = None
    relay_url: Union[str, None] = None
    error: Union[str, None] = None
    relay_file: nextcord.File = nextcord.File(
        copy(Image_IO), filename="relay_image.png"
    )

    if relay_channel:
        try:
            relay_message = await relay_channel.send(file=relay_file)
            relay_url = str(relay_message.attachments[0]) if relay_message else None

        except Forbidden:
            error = "Missing Permissions to send messages to channel"

    else:
        error = "Invalid Channel ID or Missing Permissions to view it"

    return relay_message, relay_url, error


async def process_frames(ctx: Context, FramesDict):
    """Process animated image or video frames."""
    num_frames = len(FramesDict)
    iterator_messsage = await ctx.channel.send(
        embed=embed_iterator(0, 0, initialization=True)
    )

    previous_relay = None

    for idx, data in FramesDict.items():
        image_data = await remove_background(Image.open(data["image"]))
        if isinstance(image_data, Image.Image):
            data["image"] = image_data
            if bot_config.RELAY_CHANNEL_ID:
                relay_message, relay_url, error = await relay_transmitter(
                    ctx, data["image"]
                )

                if relay_message and relay_url:
                    if previous_relay:
                        await previous_relay.delete()
                    await iterator_messsage.edit(
                        embed=embed_iterator(
                            idx, num_frames, relay=True, relay_url=relay_url
                        )
                    )
                    previous_relay = relay_message

                else:
                    await iterator_messsage.edit(
                        embed=embed_iterator(
                            idx, num_frames, relay=True, relay_error=error
                        )
                    )
            else:
                await iterator_messsage.edit(embed=embed_iterator(idx, num_frames))

    rembg_GIF_IO = await reconstruct_gif(FramesDict)
    await send_result_embed(ctx, rembg_GIF_IO, image_format="gif")

    if previous_relay:
        await previous_relay.delete()
    await iterator_messsage.delete()


async def reconstruct_gif(FramesDict) -> BytesIO:
    """Reconstructs a gif from the frames in the dictionary."""
    BackgroundDispose = ctypes.c_int(2)
    Image_IO = BytesIO()

    with ImageWand() as wand:
        WandSequence: Sequence = wand.sequence
        for idx, data in FramesDict.items():
            with (
                ImageWand(blob=data["image"]) as wand_image,
                ImageWand(
                    width=wand_image.width, height=wand_image.height, background=None
                ) as wand_bg_composite,
            ):

                wand_bg_composite: ImageWand = wand_bg_composite.composite(
                    wand_image, 0, 0
                )
                LibraryWand.MagickSetImageDispose(
                    wand_bg_composite.wand, BackgroundDispose
                )

                WandSequence.append(wand_bg_composite)

        for idx, data in FramesDict.items():
            frame = WandSequence[idx]
            if isinstance(frame, SingleImage):
                frame.delay = int(data["duration"] / 10)

        wand.type = "optimize"
        wand.format = "GIF"
        wand.save(file=Image_IO)

    Image_IO.seek(0)
    return Image_IO


def pil_to_bytesio(image_pil: Image.Image, image_format: str) -> BytesIO:
    """ Converts a PIL image to a BytesIO buffer."""
    image_io = BytesIO()
    image_pil.save(image_io, format=image_format)
    image_io.seek(0)
    return image_io


async def get_animated_frames(Image_IO) -> dict[int, dict[str, BytesIO]]:
    """Creates a dictionary of frames from an animated image."""
    image_frames = {
        idx: {"image": pil_to_bytesio(frame, "PNG"), "duration": frame.info["duration"]}
        for idx, frame in enumerate(ImageSequence.Iterator(Image_IO))
    }
    return image_frames


async def remove_background(Image_PIL: Image.Image) -> Union[BytesIO, None]:
    """Remove the background of an image."""
    rembg_IO: Union[BytesIO, None] = None

    rembg_PIL = remove(data=Image_PIL)
    if isinstance(rembg_PIL, Image.Image):
        rembg_IO = pil_to_bytesio(rembg_PIL, "PNG")
    return rembg_IO


async def get_num_frames(pil_image: Image.Image) -> int:
    """Get the number of frames in the image."""
    try:
        num_frames = pil_image.n_frames
    except Exception:
        num_frames = 1

    return num_frames


async def get_max_pixels(num_frames: int) -> int:
    """Determines the maximum number of pixels."""
    if num_frames > 1:
        max_px = rm_vars.max_px_animated
    else:
        max_px = rm_vars.max_px_image

    return max_px


async def get_video_details(bytes_file) -> Union[dict[str, int], None]:
    """Creates a dict with the video details."""
    video_details: Union[dict[str, int], None] = None

    try:
        av_container = av.open(copy(bytes_file), mode="r")
        frame_count = len(
            [packet for packet in av_container.demux(video=0) if packet.size > 0]
        )
        duration = av_container.duration / 1000000
        fps = math.ceil(frame_count / duration)

        av_container = av.open(copy(bytes_file), mode="r")
        width, height = next(
            (frame.width, frame.height)
            for frame in av_container.decode(video=0)
            if frame.width and frame.height
        )
        video_details = {
            "frame_count": frame_count,
            "fps": fps,
            "width": width,
            "height": height,
            "duration": duration,
        }

    except Exception as e:
        print(e)

    return video_details


async def get_video_frames(bytes_file) -> Union[dict[str, Union[BytesIO, int]], None]:
    """Create a dictionary of frames from a video file."""
    video_ImageFrames: Union[dict, None] = None
    video_details = await get_video_details(bytes_file)

    if video_details:
        av_container = av.open(copy(bytes_file), mode="r")
        max_fps = rm_vars.max_video_fps
        fps_ratio = math.ceil(video_details["fps"] / max_fps)

        adjusted_frame_count = math.ceil(video_details["frame_count"] / fps_ratio)
        adjusted_fps = round(adjusted_frame_count / video_details["duration"], 2)
        adjusted_frame_duration = (1 / adjusted_fps) * 1000

        ratio_stepper = 0
        idx_stepper = 0
        video_ImageFrames = {}

        for frame in av_container.decode(video=0):
            if ratio_stepper == 0:
                video_ImageFrames[idx_stepper] = {
                    "image": pil_to_bytesio(frame.to_image(), "PNG"),
                    "duration": adjusted_frame_duration,
                }
                idx_stepper += 1
            ratio_stepper += 1
            if ratio_stepper == fps_ratio:
                ratio_stepper = 0
    return video_ImageFrames


async def get_adjusted_frame_data(
    max_fps, video_fps, video_framecount, video_duration
) -> tuple[int, int, int, float]:
    """Adjusts the frame data to match the max_fps."""
    fps_ratio = math.ceil(video_fps / max_fps)

    adjusted_frame_count = math.ceil(video_framecount / fps_ratio)
    adjusted_fps = int(round(adjusted_frame_count / video_duration, 2))
    adjusted_frame_duration = (1 / adjusted_fps) * 1000

    return fps_ratio, adjusted_fps, adjusted_frame_count, adjusted_frame_duration


async def get_adjusted_frame_count(
    max_fps, video_fps, video_framecount, video_duration
) -> int:
    """Returns the adjusted frame count for the video."""
    _, _, adjusted_frame_count, _ = await get_adjusted_frame_data(
        max_fps, video_fps, video_framecount, video_duration
    )
    return adjusted_frame_count
