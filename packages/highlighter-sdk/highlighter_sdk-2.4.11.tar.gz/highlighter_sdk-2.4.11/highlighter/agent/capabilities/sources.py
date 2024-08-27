from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from PIL import Image
from pydantic import BaseModel

from highlighter.client import HLClient, download_bytes, get_presigned_url
from highlighter.client.io import _pil_open_image_bytes, _pil_open_image_path

from .base_capability import Capability, StreamEvent

__all__ = [
    "ImageDataSource",
    "TextDataSource",
]


class TextDataSource(Capability):
    """

    Example:
        # process a single string
        hl agent run --data-source TextDataSource PIPELINE.json "tell me a joke."

        # process many text files
        ToDo

        # Read from stdin
        cat file | hl agent run --data-source TextDataSource -sp read_stdin=true PIPELINE.json
    """

    class DefaultStreamParameters(Capability.DefaultStreamParameters):
        source_inputs: List = []
        read_stdin: bool = False

    @property
    def read_stdin(self) -> bool:
        value, _ = self._get_parameter("read_stdin")
        return value

    @property
    def source_inputs(self) -> bool:
        value, _ = self._get_parameter("source_inputs")
        return value

    @classmethod
    def get_capability_input_output_deploy(cls) -> Dict:
        return {
            "input": [{"name": "text", "type": "str"}],
            "output": [{"name": "text", "type": "str"}],
            "deploy": {"local": {"module": "highlighter.agent.capabilities"}},
        }

    def _decode_byte_string_to_locations(self, byte_data) -> List[str]:
        separator = b"\x1c"  # ASCII 28 (File Separator)
        byte_lines = byte_data.split(separator)
        text_lines = []
        for byte_string in byte_lines:
            try:
                text_string = byte_string.decode("utf-8")
                text_lines.append(text_string)
            except UnicodeDecodeError:
                raise ValueError("The byte string could not be decoded using UTF-8 encoding.")

        return text_lines

    def get_frame_generator(self, stream, text_lines):
        class FrameGenerator:
            def __init__(self, text_lines, logger):
                self.text_lines = text_lines
                self._logger = logger
                self._logger.info(f"Init FrameGenerator with {len(self.text_lines)}")

            def __call__(self, stream):
                if len(self.text_lines):
                    text = self.text_lines.pop(0)
                    frame_id = stream["frame_id"]
                    self._logger.info(f"generating frame: {frame_id} - {text}")
                    return StreamEvent.OKAY, {"text": text}
                return StreamEvent.STOP, None

        return FrameGenerator(text_lines, self.logger)

    def start_stream(self, stream, stream_id) -> Tuple[StreamEvent, Optional[str]]:

        if stream["stream_id"] == 0:  # TODO: "stream_required"
            raise SystemExit("Must create a stream")

        if self.read_stdin:
            if not isinstance(self.source_inputs, bytes):
                raise ValueError(
                    f"If {self.__class__.__name__}.read_stdin is"
                    " True source_inputs must be bytes, got:"
                    f" {self.source_inputs}. Try setting read_stdin=False."
                )
            text_lines = [self.source_inputs]
        elif isinstance(self.source_inputs, list):
            text_lines = self.source_inputs
        elif isinstance(self.source_inputs, bytes):
            text_lines = self._decode_byte_string_to_locations(self.source_inputs)
        else:
            return (
                StreamEvent.ERROR,
                f"Invalid value for source_inputs, got: {self.source_inputs}",
            )
        frame_generator = self.get_frame_generator(stream, text_lines)

        self.create_frames(stream, frame_generator, rate=1)
        return StreamEvent.OKAY, None

    def process_frame(self, stream, text: str) -> Tuple[StreamEvent, Dict]:
        return StreamEvent.OKAY, {"text": text}

    def stop_stream(self, stream, stream_id) -> Tuple[StreamEvent, Optional[str]]:
        stream["terminate"] = True
        self.stop()
        return StreamEvent.OKAY, None


class OutputType(str, Enum):
    numpy = "numpy"
    pillow = "pillow"


class ImageDataSource(Capability):
    """

    Example:
        # process a single image
        hl agent run PIPELINE.json --data-source ImageDataSource image.jpg

        # process many images
        find image/dir/ -n "*.jpg" | hl agent run PIPELINE.json --data-source ImageDataSource
    """

    class DefaultStreamParameters(BaseModel):
        source_inputs: List = []
        read_image_bytes: bool = False
        output_type: OutputType = OutputType.numpy

    @property
    def read_image_bytes(self) -> bool:
        value, _ = self._get_parameter("read_image_bytes")
        return value

    @property
    def output_type(self) -> OutputType:
        value, _ = self._get_parameter("output_type")
        return value

    @property
    def source_inputs(self) -> bool:
        value, _ = self._get_parameter("source_inputs")
        return value

    @classmethod
    def get_capability_input_output_deploy(cls) -> Dict:
        return {
            "input": [{"name": "image", "type": "Union[str, Path, bytes]"}],
            "output": [{"name": "image", "type": "Union[PIL.Image.Image, np.ndarray]"}],
            "deploy": {"local": {"module": "highlighter.agent.capabilities"}},
        }

    def _decode_byte_string(self, byte_string) -> List[str]:
        try:
            text_string = byte_string.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError("The byte string could not be decoded using UTF-8 encoding.")

        path_strings = text_string.strip().split("\n")

        return path_strings

    def get_frame_generator(self, stream, images):
        class FrameGenerator:
            def __init__(self, images, logger):
                self.images = images
                self._logger = logger
                self._logger.info(f"Init FrameGenerator with {len(self.images)}")

            def __call__(self, stream):
                if len(self.images):
                    image = self.images.pop(0)
                    frame_id = stream["frame_id"]
                    self._logger.info(f"generating frame: {frame_id}")
                    return StreamEvent.OKAY, {"image": image}
                return StreamEvent.STOP, None

        return FrameGenerator(images, self.logger)

    def start_stream(self, stream, stream_id) -> Tuple[StreamEvent, Optional[str]]:
        super().start_stream(stream, stream_id)

        if stream["stream_id"] == 0:  # TODO: "stream_required"
            raise SystemExit("Must create a stream")

        if self.read_image_bytes:
            if not isinstance(self.source_inputs, bytes):
                raise ValueError(
                    f"If {self.__class__.__name__}.read_image_bytes is"
                    " True source_inputs must be bytes, got:"
                    f" {self.source_inputs}. Try setting read_image_bytes=False."
                )
            images = [self.source_inputs]
        elif isinstance(self.source_inputs, list):
            images = self.source_inputs
        elif isinstance(self.source_inputs, bytes):
            images = self._decode_byte_string(self.source_inputs)
        else:
            return (
                StreamEvent.ERROR,
                f"Invalid value for source_inputs, got: {self.source_inputs}",
            )
        frame_generator = self.get_frame_generator(stream, images)
        self.create_frames(stream, frame_generator, rate=1)
        return StreamEvent.OKAY, None

    def process_frame(self, stream, image: Union[str, Path, bytes]) -> Tuple[StreamEvent, Dict]:
        # ToDo: Find a better palce to put/get this from
        #       see also, EntityWrite.process_frame.
        #       I found it useful when reviewing outputs
        #       to be able to identify the source image

        stream["source_info"] = {}
        if isinstance(image, (str, Path)):
            stream["source_info"] = {"source_file_location": str(image)}

        image_pil: Image.Image = self._read_image(image)
        if self.output_type == OutputType.numpy:
            output = np.array(image_pil)
            self.logger.info(f"image shape: {output.shape}")
        else:
            output = image_pil
            self.logger.info(f"image shape: {output.size}")
        return StreamEvent.OKAY, {"image": output}

    def stop_stream(self, stream, stream_id) -> Tuple[StreamEvent, Optional[str]]:
        stream["terminate"] = True
        self.stop()
        return StreamEvent.OKAY, None

    def _try_cast_int(self, i) -> Optional[int]:
        try:
            _int = int(i)
        except ValueError as _:
            return None
        return _int

    def _read_image_from_location(self, image_location: str) -> Image.Image:
        if image_location.startswith("http:"):
            # ToDo: Add caching
            image_bytes = download_bytes(image_location)
            assert image_bytes is not None
            image = _pil_open_image_bytes(image_bytes)
        elif Path(image_location).exists():
            image = _pil_open_image_path(image_location)
        elif (image_id := self._try_cast_int(image_location)) is not None:
            presigned_url = get_presigned_url(HLClient.get_client(), image_id)
            image_bytes = download_bytes(presigned_url)
            assert image_bytes is not None
            image = _pil_open_image_bytes(image_bytes)
        else:
            raise ValueError(f"Unable to read image from location: {image_location}")

        return image

    def _read_image(self, image: Union[str, Path, bytes]) -> Image.Image:
        if isinstance(image, (str, Path)):
            return self._read_image_from_location(str(image))
        elif isinstance(image, bytes):
            return _pil_open_image_bytes(image)
        else:
            raise ValueError("Invalid image value, expected str|Path|bytes," f"got: {image}")
