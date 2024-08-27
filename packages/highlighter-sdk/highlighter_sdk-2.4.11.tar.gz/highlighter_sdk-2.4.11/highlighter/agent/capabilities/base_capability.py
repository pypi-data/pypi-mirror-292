from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import UUID, uuid4

import aiko_services as aiko
from aiko_services import (
    PROTOCOL_PIPELINE,
    PipelineImpl,
    compose_instance,
    pipeline_args,
    pipeline_element_args,
)
from pydantic import BaseModel
from shapely import geometry as geom

from highlighter.client import EAVT, Annotation, Entity

__all__ = [
    "Annotation",
    "Capability",
    "ContextPipelineElement",
    "Entities",
    "EntityUUID",
    "PROTOCOL_PIPELINE",
    "PipelineElement",
    "PipelineImpl",
    "StreamEvent",
    "compose_instance",
    "compose_instance",
    "pipeline_args",
    "pipeline_element_args",
]

EntityUUID = UUID


class Entities(dict):

    def add_entity(
        self,
        entity_id: Optional[UUID] = None,
        location: Optional[geom.Polygon] = None,
        observations: List[EAVT] = [],
        global_observations: List[EAVT] = [],
    ):
        if entity_id is None:
            entity_id = uuid4()

        annotations = []
        if observations:
            annotations = [
                Annotation(
                    id=uuid4(),
                    entity_id=entity_id,
                    location=location,
                    observations=observations,
                    datum_source=observations[0].datum_source,
                )
            ]

        entity = Entity(
            id=entity_id,
            annotations=annotations,
            global_observations=global_observations,
        )

        super().__setitem__(entity_id, entity)


"""Decouple the rest of the code from aiko.PipelineElement"""
ContextPipelineElement = aiko.ContextPipelineElement
StreamEvent = aiko.StreamEvent
PipelineElement = aiko.PipelineElement


class Capability(PipelineElement):

    class DefaultStreamParameters(BaseModel):
        """Populate with default stream param key fields"""

        pass

    def __init__(self, context: aiko.ContextPipelineElement):
        context.get_implementation("PipelineElement").__init__(self, context)

    @classmethod
    def default_stream_parameters(cls) -> BaseModel:
        return cls.DefaultStreamParameters()

    @classmethod
    def get_capability_input_output_deploy(cls) -> Dict:
        return {}

    def _get_parameter(self, name, default=None, use_pipeline=True) -> Tuple[Any, bool]:
        """Adds the correct output type to get_parameter type checking
        does not complain
        """
        return self.get_parameter(name, default, use_pipeline)

    @classmethod
    def get_capability_definition(cls) -> Dict:
        input_output_deploy = cls.get_capability_input_output_deploy()
        capability_definition = dict(
            name=cls.__name__,
            **input_output_deploy,
        )

        default_parameters = cls.default_stream_parameters().model_dump()
        capability_definition["parameters"] = default_parameters
        return capability_definition

    def start_stream(self, stream, stream_id) -> Tuple[StreamEvent, Optional[str]]:
        """Called when a stream is created"""
        # If there are name clashes between capabiliteis then
        # the parameter that is in the capability later in the pipeline will take
        # precedence. To get around this you can prepend the stream parameter
        # name with the Capability name in the cli
        # "-sp CapabilityA.foo=42 -sp CapabilityB.foo=3.14
        return StreamEvent.OKAY, None

    def stop_stream(self, stream, stream_id) -> Tuple[StreamEvent, Optional[str]]:
        """Called when a stream is terminated"""
        return StreamEvent.OKAY, None

    def process_frame(self, stream, image: Union[str, Path, bytes]) -> Tuple[StreamEvent, Union[Dict, str]]:
        """Called once per frame"""
        raise NotImplementedError()
