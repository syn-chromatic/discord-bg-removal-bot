import ctypes
import math

import av
from av.container import InputContainer
from av.video import VideoStream

from wand.image import Image as ImageWand
from wand.sequence import Sequence
from wand.api import library as LibraryWand

from io import BytesIO
from PIL import Image, ImageSequence

from typing import Union
from fractions import Fraction

from utils.media_dataclasses import (
    VideoData,
    VideoFrame,
    AnimatedData,
    AnimatedFrame,
)


class VideoDecomposeBase:
    def __init__(self, video_io: BytesIO):
        self._video_io = video_io
        self._video_input = self._get_container()
        self._video_stream = self._get_stream(self._video_input)
        self._frames: list[VideoFrame] = []
        self._framecount = 0
        self._max_framecount = 50
        self._framecount_ratio = self._get_frame_ratio()
        self._total_duration: Fraction = Fraction(0)

    def _get_container(self) -> InputContainer:
        video_input = av.open(self._video_io, mode="r")
        return video_input

    def _get_stream(self, video_input: InputContainer) -> VideoStream:
        video_stream = video_input.streams.video[0]
        return video_stream

    def _get_frame_ratio(self):
        framecount = self._video_stream.frames
        framecount_ratio = math.ceil(framecount / self._max_framecount)
        return framecount_ratio

    def _get_resolution(self) -> tuple[int, int]:
        width = self._video_stream.width
        height = self._video_stream.height
        return width, height

    def _frame_duration(self, packet: av.Packet):
        time_base = packet.time_base
        duration = packet.duration
        frame_duration = time_base * duration * self._framecount_ratio
        frame_duration = Fraction(frame_duration)
        return frame_duration

    def _pil_to_bytesio(self, image: Image.Image, format: str) -> BytesIO:
        image_io = BytesIO()
        image.save(image_io, format=format)
        image_io.seek(0)
        return image_io

    def _create_frame(self, frame: av.VideoFrame, frame_duration: Fraction):
        width, height = self._get_resolution()
        frame_image = frame.to_image()
        video_frame = VideoFrame(
            image=frame_image, width=width, height=height, duration=frame_duration
        )
        return video_frame

    def _create_frame_data(self):
        ratio_stepper = 0
        idx_stepper = 0

        for packet_v in self._video_input.demux(self._video_stream):
            if packet_v.dts is None:
                continue

            frames_v = packet_v.decode()

            if ratio_stepper == 0:
                frame_duration = self._frame_duration(packet_v)
                self._total_duration += frame_duration

                for frame_v in frames_v:
                    video_frame = self._create_frame(frame_v, frame_duration)
                    self._frames.append(video_frame)
                    self._framecount += 1
                    idx_stepper += 1

            ratio_stepper += 1

            if ratio_stepper == self._framecount_ratio:
                ratio_stepper = 0

        return self._frames, self._framecount, self._total_duration


class VideoDecompose(VideoDecomposeBase):
    def __init__(self, video_io: BytesIO):
        super().__init__(video_io)

    def create_video_data(self) -> VideoData:
        width, height = self._get_resolution()
        frames, framecount, total_duration = self._create_frame_data()

        average_fps = Fraction(framecount, total_duration)

        video_data = VideoData(
            frames=frames,
            framecount=framecount,
            width=width,
            height=height,
            avg_fps=average_fps,
            total_duration=total_duration,
        )
        return video_data


class AnimatedDecomposeBase:
    def __init__(self, image: Image.Image):
        self._image = image
        self._sequence_frames = self._get_sequence_frames()
        self._frames: list[AnimatedFrame] = []
        self._framecount = 0
        self._max_framecount = 50
        self._framecount_ratio = self._get_frame_ratio()
        self._total_duration: Fraction = Fraction(0)

    def _get_sequence_frames(self):
        sequence_frames = ImageSequence.all_frames(self._image)
        return sequence_frames

    def _get_frame_ratio(self):
        framecount = len(self._sequence_frames)
        framecount_ratio = math.ceil(framecount / self._max_framecount)
        return framecount_ratio

    def _get_resolution(self, frame: Image.Image) -> tuple[int, int]:
        width = frame.width
        height = frame.height
        return width, height

    def _frame_duration(self, frame: Image.Image):
        duration = frame.info["duration"]
        duration = 1 if not duration else duration
        duration_s = Fraction(duration, 1000)
        frame_duration = duration_s * self._framecount_ratio
        frame_duration = Fraction(frame_duration)
        return frame_duration

    def _pil_to_bytesio(self, image: Image.Image, format: str) -> BytesIO:
        image_io = BytesIO()
        image.save(image_io, format=format)
        image_io.seek(0)
        return image_io

    def _create_frame(
        self, frame: Image.Image, frame_duration: Fraction
    ) -> AnimatedFrame:
        width, height = self._get_resolution(frame)

        animated_frame = AnimatedFrame(
            image=frame,
            width=width,
            height=height,
            duration=frame_duration,
        )
        return animated_frame

    def _create_frame_data(self):
        ratio_stepper = 0
        idx_stepper = 0

        for frame in self._sequence_frames:
            if ratio_stepper == 0:

                frame_duration = self._frame_duration(frame)
                self._total_duration += frame_duration

                animated_frame = self._create_frame(frame, frame_duration)
                self._frames.append(animated_frame)
                self._framecount += 1
                idx_stepper += 1

            ratio_stepper += 1

            if ratio_stepper == self._framecount_ratio:
                ratio_stepper = 0

        return self._frames, self._framecount, self._total_duration


class AnimatedDecompose(AnimatedDecomposeBase):
    def __init__(self, image: Image.Image):
        super().__init__(image)

    def create_animated_data(self) -> AnimatedData:
        frames, framecount, total_duration = self._create_frame_data()

        average_fps = Fraction(framecount, total_duration)

        animated_data = AnimatedData(
            frames=frames,
            framecount=framecount,
            avg_fps=average_fps,
            total_duration=total_duration,
        )
        return animated_data


class ComposeGIFBase:
    def __init__(self, data: Union[VideoData, AnimatedData]):
        self._data = data
        self._bg_dispose = ctypes.c_int(2)
        self._animated_io: BytesIO = BytesIO()
        self._frames = self._retrieve_frames()

    def _retrieve_frames(self):
        if isinstance(self._data, VideoData):
            return self._video_frames(self._data)
        return self._animated_frames(self._data)

    def _retrieve_frame_and_duration(self, frame: Union[VideoFrame, AnimatedFrame]):
        if isinstance(frame, VideoFrame):
            return self._video_frame_and_duration(frame)
        return self._animated_frame_and_duration(frame)

    def _retrieve_resolution(self, frame: Union[VideoFrame, AnimatedFrame]):
        if isinstance(frame, VideoFrame):
            return frame.width, frame.height
        return frame.width, frame.height

    def _video_frames(self, data: VideoData):
        return data.frames

    def _animated_frames(self, data: AnimatedData):
        return data.frames

    def _video_frame_and_duration(self, video_frame: VideoFrame):
        image = video_frame.image
        duration = video_frame.duration
        return image, duration

    def _animated_frame_and_duration(self, animated_frame: AnimatedFrame):
        image = animated_frame.image
        duration = animated_frame.duration
        return image, duration

    def _pil_to_bytesio(self, image: Image.Image, format: str) -> BytesIO:
        image_io = BytesIO()
        image.save(image_io, format=format)
        image_io.seek(0)
        return image_io


class ComposeGIF(ComposeGIFBase):
    def __init__(self, data: Union[VideoData, AnimatedData]):
        super().__init__(data)

    def reconstruct(self) -> BytesIO:
        with ImageWand() as wand:
            WandSequence: Sequence = wand.sequence
            for frame in self._frames:
                image, duration = self._retrieve_frame_and_duration(frame)
                width, height = self._retrieve_resolution(frame)
                image = self._pil_to_bytesio(image, "PNG")

                with (
                    ImageWand(blob=image) as wand_image,
                    ImageWand(
                        width=width, height=height, background=None
                    ) as bg_composite,
                ):
                    bg_composite.composite(wand_image, 0, 0)
                    LibraryWand.MagickSetImageDispose(
                        bg_composite.wand, self._bg_dispose
                    )
                    bg_composite.delay = int(duration * 100)
                    WandSequence.append(bg_composite)

            wand.type = "optimize"
            wand.format = "GIF"
            wand.save(file=self._animated_io)

        self._animated_io.seek(0)
        return self._animated_io
