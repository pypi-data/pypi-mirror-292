import os

import aiko_services as aiko

__all__ = [
    "init_agent",
    "run_agent",
]


def init_agent(definition_pathname, name):

    if not os.path.exists(definition_pathname):
        raise SystemExit(f"Error: PipelineDefinition not found: {definition_pathname}")

    pipeline_definition = aiko.PipelineImpl.parse_pipeline_definition(definition_pathname)
    name = name if name else pipeline_definition.name

    init_args = aiko.pipeline_args(
        name,
        protocol=aiko.PROTOCOL_PIPELINE,
        definition=pipeline_definition,
        definition_pathname=definition_pathname,
    )
    pipeline = aiko.compose_instance(aiko.PipelineImpl, init_args)
    return pipeline, pipeline_definition


def run_agent(pipeline, stream_id, stream_parameters):

    pipeline.create_stream(stream_id, dict(stream_parameters))
