import json
import sys
from enum import Enum
from pathlib import Path
from tempfile import mkdtemp
from typing import List
from uuid import UUID

import click

from ..agent.capabilities import sources as source_capabilities
from ..agent.capabilities import targets as target_capabilities
from ..agent.capabilities.base_capability import Capability


def _is_uuid(s):
    try:
        _ = UUID(s)
        return True
    except Exception as _:
        return False


@click.group("agent")
@click.pass_context
def agent_group(ctx):
    pass


DATASOURCE_TAGS = ("--data-source", "-ds")
DATATARGET_TAGS = ("--data-target", "-dt")
STREAM_PARAMS_TAGS = ("--stream-parameters", "-sp")


class AgentRunHelpFormatter(click.HelpFormatter):
    def __init__(self, *args, **kwargs):
        (self._capability_help, self._capability_cli_args) = self._get_capability_help()
        super().__init__(*args, **kwargs)

    def _get_capability_help(self):
        argv = sys.argv
        capability_name = argv[-2]
        capability_cls: Capability
        if (capability_cls := getattr(source_capabilities, capability_name, None)) is not None:
            capability_def = capability_cls.get_capability_definition()
            capability_tag = " ".join(DATASOURCE_TAGS)
        elif (capability_cls := getattr(target_capabilities, capability_name, None)) is not None:
            capability_def = capability_cls.get_capability_definition()
            capability_tag = " ".join(DATATARGET_TAGS)
        else:
            capability_def = None
            capability_tag = ""

        if capability_def is None:
            return None, None

        help_str = """\b
__CAPABILITY_NAME__

\b
Params:
__PARAMS__
    
\b
Inputs:
__INPUTS__
    
\b
Outputs:
__OUTPUTS__
            """
        params_items = ["\b"]
        params_args_str = [capability_tag, capability_name]
        help_str = help_str.replace("__CAPABILITY_NAME__", capability_def["name"])

        for field_name, default_value in capability_cls.default_stream_parameters().model_dump().items():
            field_type = type(default_value)

            if issubclass(field_type, Enum):
                choices = "|".join([member.name for member in default_value.__class__])
                params_items.append(f"  {field_name}: {choices}")
                params_args_str.append(f"{STREAM_PARAMS_TAGS[1]} {field_name}={default_value.value}")
            else:
                params_items.append(f"  {field_name}: {field_type.__name__}")
                params_args_str.append(f"{STREAM_PARAMS_TAGS[1]} {field_name}={default_value}")

        help_str = help_str.replace("__PARAMS__", "\n".join(params_items))
        params_args_str.append("...")

        input_items = ["\b"]
        for i in capability_def["input"]:
            input_items.append(f"  {i['name']}: {i['type']}")
        help_str = help_str.replace("__INPUTS__", "\n".join(input_items))

        output_items = ["\b"]
        for i in capability_def["output"]:
            output_items.append(f"  {i['name']}: {i['type']}")
        help_str = help_str.replace("__OUTPUTS__", "\n".join(output_items))

        return click.wrap_text(help_str, width=200), " ".join(params_args_str)

    def write_text(self, text):
        if self._capability_help is None:
            super().write_text(text)
        else:
            super().write_text(self._capability_help)

    def write_heading(self, heading):
        if self._capability_help is None:
            super().write_heading(heading)
        else:
            super().write_heading("")

    def write_usage(self, prog, args="", prefix="Usage: "):
        if self._capability_help is None:
            super().write_usage(prog, args, prefix=prefix)
        else:
            super().write_usage(prog, self._capability_cli_args, prefix="Capability Usage: ")

    def write_dl(
        self,
        rows,
        col_max: int = 30,
        col_spacing: int = 2,
    ) -> None:
        if self._capability_help is None:
            super().write_dl(rows, col_max=col_max, col_spacing=col_spacing)
        else:
            return None


class AgentRunCommand(click.Command):
    def get_help(self, ctx):
        formatter = AgentRunHelpFormatter()
        self.format_help(ctx, formatter)
        return formatter.getvalue()


def parse_stream_params(agent, agent_definition, str_params: List[str]) -> dict:
    # If different Capabilities have clashing parameter names then
    # the parameter in the Capability later in the pipeline will take
    # precedence. To get around this you can prepend the stream parameter
    # name with the Capability name in the cli
    # "-sp CapabilityA.foo=42 -sp CapabilityB.foo=3.14
    stream_params = {}
    for node in agent.pipeline_graph.nodes():
        node_name = node.element.__class__.__name__

        # Start with in code params
        default_stream_parameters = node.element.default_stream_parameters().model_dump()

        # Overwite with global pipeline definition params
        global_pipeline_definition_params = {
            k: v for k, v in agent_definition.parameters if k in default_stream_parameters
        }
        default_stream_parameters.update(global_pipeline_definition_params)

        # Overwite with per element pipeline definition paras
        element_definition = [e for e in agent_definition.elements if e.name == node_name][0]
        pipeline_element_definition_params = {
            k: v for k, v in element_definition.parameters.items() if k in default_stream_parameters
        }
        default_stream_parameters.update(pipeline_element_definition_params)

        # Overwite with cli params
        cli_params = {}
        for param_str in str_params:
            k, v = param_str.split("=")
            cli_params[k] = v

        for param_name in default_stream_parameters:

            # preference fully qualified param names
            node_param_name = f"{node_name}.{param_name}"
            if node_param_name in cli_params:
                override_value = cli_params[node_param_name]
                default_stream_parameters[param_name] = override_value

            # fall back to unqualified param names
            elif param_name in cli_params:
                override_value = cli_params[param_name]
                default_stream_parameters[param_name] = override_value

        ele_stream_params = node.element.DefaultStreamParameters(**default_stream_parameters).model_dump()
        stream_params.update({f"{node_name}.{k}": v for k, v in ele_stream_params.items()})

    return stream_params


@agent_group.command("run", cls=AgentRunCommand)
@click.option(*DATASOURCE_TAGS, type=click.Choice(source_capabilities.__all__), default=None)
@click.option(*DATATARGET_TAGS, type=click.Choice(target_capabilities.__all__), default=None)
@click.option("--stream-id", "-s", type=int, default=1)
@click.option(*STREAM_PARAMS_TAGS, type=str, multiple=True, default=[])
@click.option("--dump-definition", type=str, default=None)
@click.argument("agent_definition", type=click.Path(dir_okay=False, exists=False))
@click.argument("input_data", type=click.Path(exists=False), default="-", required=False)
@click.pass_context
def _run(
    ctx,
    data_source,
    data_target,
    stream_id,
    stream_parameters,
    dump_definition,
    agent_definition,
    input_data,
):
    """Run a local Highlighter Agent to process data.

    To feed data into the agent you have 3 options:

    \b 
    1. Add a DataSource Capability to the Agent definition:
        # agent_definition.json has an ImageDataSource Capability
        hl agent run agent_definition.json image.jpg

    \b
    2. Use the cli --data-source flag:
        # Add an ImageDataSource to the front of your Agent
        hl agent run --data-source ImageDataSource agent_definition.json image.jpg

    \b
    3. Pass frame params directly
        # Your Capabilities process_frame functions have named 
        # arguments "foo" and "bar"
        cat frame_data.json | hl agent run agent_definition.json 
        or
        hl agent run agent_definition.json '[{"foo": 123, "bar": 456}]'

    \b
    If --data-source or --data-target are not specified then it is assumed one
    or both of them are defined in the agent_definition.

    \b
    To get specific help for a --data-source or --data-target use --help 
    after specifying it, eg:
        hl agent run --data-source ImageDataSource --help

    \b 
    Examples:
        # Process a single image from path
        hl agent run --data-source ImageDataSource PIPELINE.json image.jpg 

    \b 
        # Process a single image from bytes
        cat image.jpg | hl agent run --data-source ImageDataSource -sp read_image_bytes=True PIPELINE.json

    \b 
        # Process many images from paths
        find ./image/dir -name "*.jpg" | hl agent run --data-source ImageDataSource PIPELINE.json

    \b 
       # Process a video from frame 10 to frame 20
        hl agent run -ds VideoDataSource \\
                -sp start_frame=10 \\
                -sp stop_frame=20 \\
                PIPELINE.json \\
                video.mp4

    """
    from highlighter.agent import init_agent

    if Path(agent_definition).exists():
        with Path(agent_definition).open("r") as f:
            definition_dict = json.load(f)

        elements = definition_dict["elements"]
        graph_def = definition_dict["graph"][0]
        if data_source is not None:
            source_cls: Capability = getattr(source_capabilities, data_source)
            source_definition = source_cls.get_capability_definition()
            elements = [source_definition] + elements
            graph_def = f"({source_definition['name']} " + graph_def[1:]

        if data_target is not None:
            target_cls: Capability = getattr(target_capabilities, data_target)
            target_definition = target_cls.get_capability_definition()
            elements = elements + [target_definition]
            graph_def = graph_def[:-1] + f" {target_definition['name']})"

        definition_dict["elements"] = elements
        definition_dict["graph"] = [graph_def]

        agent_def_json = json.dumps(definition_dict, sort_keys=True, indent=2)

        if dump_definition is not None:
            agent_path = Path(dump_definition)
        else:
            agent_path = Path(mkdtemp()) / "agent_def.json"

        with agent_path.open("w") as f:
            f.write(agent_def_json)

        name = Path(agent_definition).name

    elif _is_uuid(agent_definition):
        raise NotImplementedError("Need to implement pulling the agent_definition from Highlighter")
    else:
        if not Path(agent_definition).suffix == ".json":
            raise SystemExit(f"agent_definition '{agent_definition}' path does not exist")
        else:
            raise SystemExit(f"agent_definition '{agent_definition}' id does not exist")

    agent, agent_definition = init_agent(agent_path, name)

    _stream_parameters: dict = parse_stream_params(agent, agent_definition, stream_parameters)

    def agent_driven_by_datasource(agent):
        head_capability_name = [x for x in agent.pipeline_graph][0].name
        if getattr(source_capabilities, head_capability_name, None) is not None:
            return True, head_capability_name
        return False, None

    (driven_by_datasource, data_source_capability_name) = agent_driven_by_datasource(agent)

    if driven_by_datasource:
        if input_data == "-":
            # if "-" is passed as input_data read bytes from stdin
            if not sys.stdin.isatty():
                _stream_parameters[f"{data_source_capability_name}.source_inputs"] = sys.stdin.buffer.read()
            else:
                # Assume source_inputs are in the agent definition
                pass

        else:
            # The agent source_inputs is the path to the file.
            # It is expected the data-source capability knows how to handel that.
            _stream_parameters[f"{data_source_capability_name}.source_inputs"] = [input_data]

        agent.create_stream(stream_id, _stream_parameters)
        agent.run(mqtt_connection_required=False)

    else:
        if input_data == "-":
            # if "-" is passed as input_data read bytes from stdin
            if not sys.stdin.isatty():
                frame_data = json.load(sys.stdin)
            else:
                frame_data = [{}]

        else:
            # The agent source_inputs is the path to the file.
            # It is expected the data-source capability knows how to handel that.
            frame_data = json.loads(input_data)

        if isinstance(frame_data, dict):
            frame_data = [frame_data]

        agent.create_stream(stream_id, _stream_parameters)
        stream = {"stream_id": 1}
        for frame_id, frame in enumerate(frame_data):
            stream["frame_id"] = frame_id
            agent.process_frame(stream, frame)
