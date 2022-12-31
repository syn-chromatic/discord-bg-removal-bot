import ctypes
import math
import numpy as np

import av
from av.container import InputContainer
from av.video import VideoStream

from wand.image import Image as ImageWand
from wand.sequence import Sequence
from wand.api import library as LibraryWand

from io import BytesIO
from PIL import Image, ImageSequence
from PIL.Image import Image as ImageType

from typing import Union
from fractions import Fraction

from configuration.command_variables.bgr_variables import MAX_FRAMES
from utils.bgr.bgr_dataclasses import (
    VideoData,
    VideoFrame,
    AbstractData,
    AbstractFrame,
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
        self._max_framecount = MAX_FRAMES
        self._framecount_ratio = self._get_frame_ratio()
        self._total_duration: Fraction = Fraction(0)

    def _get_container(self) -> InputContainer:
        video_input = av.open(self._video_io, mode="r")
        return video_input

    @staticmethod
    def _get_stream(video_input: InputContainer) -> VideoStream:
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

    def _frame_duration(self, packet: av.Packet) -> Fraction:
        time_base = packet.time_base
        duration = packet.duration
        frame_duration = time_base * duration * self._framecount_ratio
        frame_duration = Fraction(frame_duration)
        return frame_duration

    @staticmethod
    def _pil_to_bytesio(image: Image.Image, fp_format: str) -> BytesIO:
        image_io = BytesIO()
        image.save(image_io, format=fp_format)
        image_io.seek(0)
        return image_io

    def _create_frame(
        self, frame: av.VideoFrame, frame_duration: Fraction
    ) -> VideoFrame:
        width, height = self._get_resolution()
        frame_image = frame.to_image()
        frame_image.convert("RGBA")
        video_frame = VideoFrame(
            image=frame_image, width=width, height=height, duration=frame_duration
        )
        return video_frame

    def _create_frame_data(self) -> tuple[list[VideoFrame], int, Fraction]:
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
        self._max_framecount = MAX_FRAMES
        self._framecount_ratio = self._get_frame_ratio()
        self._total_duration: Fraction = Fraction(0)

    def _get_sequence_frames(self):
        sequence_frames = ImageSequence.all_frames(self._image)
        return sequence_frames

    def _get_frame_ratio(self) -> int:
        framecount = len(self._sequence_frames)
        framecount_ratio = math.ceil(framecount / self._max_framecount)
        return framecount_ratio

    @staticmethod
    def _get_resolution(frame: Image.Image) -> tuple[int, int]:
        width = frame.width
        height = frame.height
        return width, height

    @staticmethod
    def _correct_duration(duration: Union[int, None]) -> int:
        if not duration or (duration and duration < 20):
            duration = 20
        return duration

    def _frame_duration(self, frame: Image.Image) -> Fraction:
        duration = frame.info["duration"]
        duration = self._correct_duration(duration)
        duration_s = Fraction(duration, 1000)
        frame_duration = duration_s * self._framecount_ratio
        frame_duration = Fraction(frame_duration)
        return frame_duration

    @staticmethod
    def _pil_to_bytesio(image: Image.Image, fp_format: str) -> BytesIO:
        image_io = BytesIO()
        image.save(image_io, format=fp_format)
        image_io.seek(0)
        return image_io

    def _create_frame(
        self, frame: Image.Image, frame_duration: Fraction
    ) -> AnimatedFrame:
        width, height = self._get_resolution(frame)
        frame = frame.convert("RGBA")

        animated_frame = AnimatedFrame(
            image=frame,
            width=width,
            height=height,
            duration=frame_duration,
        )
        return animated_frame

    def _create_frame_data(self) -> tuple[list[AnimatedFrame], int, Fraction]:
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
    def create_animated_data(self) -> AnimatedData:
        frames, framecount, total_duration = self._create_frame_data()

        average_fps = Fraction(framecount, total_duration)

        animated_data = AnimatedData(
            frames=frames,
            framecount=framecount,
            width=0,
            height=0,
            avg_fps=average_fps,
            total_duration=total_duration,
        )
        return animated_data


class ComposeGIFBase:
    def __init__(self, data: AbstractData):
        self._data = data
        self._bg_dispose = ctypes.c_int(2)
        self._animated_io: BytesIO = BytesIO()
        self._frames = self._retrieve_frames()

    def _retrieve_frames(self) -> list[AbstractFrame]:
        return self._data.frames

    @staticmethod
    def _retrieve_frame_and_duration(
        frame: AbstractFrame,
    ) -> tuple[ImageType, Fraction]:
        image = frame.image
        duration = frame.duration
        return image, duration

    @staticmethod
    def _retrieve_resolution(frame: AbstractFrame) -> tuple[int, int]:
        return frame.width, frame.height

    @staticmethod
    def _pil_to_bytesio(image: Image.Image, fp_format: str) -> BytesIO:
        image_io = BytesIO()
        image.save(image_io, format=fp_format)
        image_io.seek(0)
        return image_io


class ComposeGIF(ComposeGIFBase):
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


class DisposeDuplicateBase:
    def __init__(self, data: AbstractData):
        self._data = data
        self._frames = self._retrieve_frames()

    def _retrieve_frames(self) -> list[AbstractFrame]:
        return self._data.frames

    @staticmethod
    def _retrieve_frame_and_duration(
        frame: AbstractFrame,
    ) -> tuple[ImageType, Fraction]:
        image = frame.image
        duration = frame.duration
        return image, duration

    @staticmethod
    def _insert_new_duration(frame: AbstractFrame, duration: Fraction) -> AbstractFrame:
        frame.duration = duration
        return frame

    def _remove_frame(self, idx: int):
        self._data.frames.pop(idx)
        self._data.framecount -= 1

    @staticmethod
    def _retrieve_resolution(frame: AbstractFrame) -> tuple[int, int]:
        return frame.width, frame.height

    @staticmethod
    def mse(a: ImageType, b: ImageType):
        nd_a = np.asarray(a, dtype="float")
        nd_b = np.asarray(b, dtype="float")

        nd_a = np.divide(nd_a, 100)
        nd_b = np.divide(nd_b, 100)

        image_diff = np.subtract(nd_a, nd_b)
        image_diff = image_diff**2
        image_sum = np.sum(image_diff)

        mse_error = np.divide(image_sum, (nd_a.shape[0] * nd_b.shape[1]))
        return mse_error

    def _dispose_duplicates(self, duplicate_idx: list[int]):
        shift = 0
        for idx in duplicate_idx:
            idx -= shift
            self._remove_frame(idx)
            shift += 1

    def _dispose(self, mse_strength):
        previous_frame = None
        duplicate_idx = []
        duplicate_duration = Fraction(0)

        for idx, frame in enumerate(self._frames):
            image, duration = self._retrieve_frame_and_duration(frame)
            width, height = self._retrieve_resolution(frame)

            if not previous_frame:
                previous_frame = frame
                duplicate_duration += duration
                continue

            prev_image, _ = self._retrieve_frame_and_duration(previous_frame)
            prev_width, prev_height = self._retrieve_resolution(previous_frame)

            if width == prev_width and height == prev_height:
                mse_error = self.mse(image, prev_image)

                if mse_error < mse_strength:
                    duplicate_duration += duration
                    duplicate_idx.append(idx)
                    self._insert_new_duration(previous_frame, duplicate_duration)
                    continue

            self._dispose_duplicates(duplicate_idx)

            previous_frame = None
            duplicate_idx = []
            duplicate_duration = Fraction(0)
            duplicate_duration += duration

        self._dispose_duplicates(duplicate_idx)


class DisposeDuplicateFrames(DisposeDuplicateBase):
    def __init__(self, data: AbstractData):
        super().__init__(data)

    def dispose_frames(self, mse_strength: float = 0.03) -> AbstractData:
        self._dispose(mse_strength)
        return self._data
