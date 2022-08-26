import requests
from io import BytesIO
from PIL import Image
from typing import Union
from nextcord import Embed

from utils import rembg_utils
from utils import general_utils as gen_utils
from variables.command_variables import rembg_variables as rm_vars


async def download_image(
    url,
) -> tuple[Union[Image.Image, None], Union[int, None], Union[Embed, None]]:
    """
    Download an image from a URL and return the image as an Image object,
    number of frames, and the error embed if there's an error.
    """
    PIL_Image: Union[Image.Image, None] = None
    num_frames: Union[int, None] = None
    error_embed: Union[Embed, None] = None

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 6.1; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/34.0.1847.137 Safari/537.36"
        )
    }

    response = requests.get(url, stream=True, headers=headers)

    image_data = BytesIO(response.raw.read())

    try:
        PIL_Image = Image.open(image_data)
        width, height = PIL_Image.size
        image_format = PIL_Image.format

        max_num_frames = rm_vars.max_frames_animated
        minimum_px = 32

        num_frames = await rembg_utils.get_num_frames(PIL_Image)
        max_px = await rembg_utils.get_max_pixels(num_frames)

        if num_frames > max_num_frames:
            error_embed = await gen_utils.construct_embed(
                f"{image_format} exceeds maximum of {max_num_frames} frames.\n"
                f"**Frame Count:** {num_frames}"
            )

        elif width > max_px or height > max_px:
            error_embed = await gen_utils.construct_embed(
                f"{image_format} needs to be <{max_px}px in width or height.\n"
                f"**Resolution:** {width}x{height}"
            )

        elif width < minimum_px or height < minimum_px:
            error_embed = await gen_utils.construct_embed(
                f"{image_format} needs to be >{minimum_px}px in width or height.\n"
                f"**Resolution:** {width}x{height}"
            )

    except Exception as error:
        print(error)
        error_embed = await gen_utils.construct_embed(
            "Error occurred while loading image!"
        )

    return PIL_Image, num_frames, error_embed


async def download_video(url):
    """
    Downloads a video from a given URL. Returns the video as a BytesIO object,
    and the error embed if there was an error.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 6.1; WOW64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/34.0.1847.137 Safari/537.36"
        )
    }

    response = requests.get(url, stream=True, headers=headers)
    video_data: BytesIO = BytesIO(response.raw.read())
    video_details = await rembg_utils.get_video_details(video_data)
    error_embed: Union[Embed, None] = None

    try:
        if video_details:
            width, height = video_details["width"], video_details["height"]
            fps = video_details["fps"]
            frame_count = video_details["frame_count"]
            duration = video_details["duration"]
            max_fps = rm_vars.max_video_fps
            max_num_frames = rm_vars.max_frames_animated
            max_px = rm_vars.max_px_animated
            minimum_px = 32

            if fps > max_fps:
                adjusted_framecount = await rembg_utils.get_adjusted_frame_count(
                    max_fps, fps, frame_count, duration
                )
            else:
                adjusted_framecount = frame_count

            if adjusted_framecount > max_num_frames:
                error_embed = await gen_utils.construct_embed(
                    f"Video exceeds maximum of {max_num_frames} frames.\n"
                    f"**Frame Count:** {frame_count}"
                )

            elif width > max_px or height > max_px:
                error_embed = await gen_utils.construct_embed(
                    f"Video needs to be <{max_px}px in width or height.\n"
                    f"**Resolution:** {width}x{height}"
                )

            elif width < minimum_px or height < minimum_px:
                error_embed = await gen_utils.construct_embed(
                    f"Video needs to be >{minimum_px}px in width or height.\n"
                    f"**Resolution:** {width}x{height}"
                )

    except Exception as error:
        print(error)
        error_embed = await gen_utils.construct_embed(
            "Error occured while loading video!"
        )

    return video_data, error_embed
