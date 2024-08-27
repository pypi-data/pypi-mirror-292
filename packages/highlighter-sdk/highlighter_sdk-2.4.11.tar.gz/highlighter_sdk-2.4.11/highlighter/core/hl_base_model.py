import re

from pydantic import BaseModel

__all__ = [
    "HLBaseModel",
    "camel_to_snake",
    "snake_to_camel",
]


def camel_to_snake(s):
    return re.sub("([A-Z])", r"_\g<1>", s).lower()


def snake_to_camel(s):
    first, *rest = s.split("_")
    return first + "".join(x.capitalize() for x in rest)


def map_keys_deeply(x, f):
    if isinstance(x, dict):
        result = {f(k): map_keys_deeply(v, f) for k, v in x.items()}
    elif isinstance(x, list):
        result = [map_keys_deeply(element, f) for element in x]
    else:
        result = x
    return result


class HLBaseModel(BaseModel, extra="forbid"):
    """To allow for seamless integration with the GraphQL CamelCaseWorld and
    th_python_snake_case_world. We have this customized Pydantic BaseModel.

    This expects all fields are defined in snake_case.
    When serialized the resulting dict will have CamelCase keys,
    this allows it to play nice with GraphQL.
    """

    def __init__(self, *args, **kwargs):
        kwargs = map_keys_deeply(kwargs, camel_to_snake)
        super().__init__(*args, **kwargs)

    def gql_dict(self):
        d = self.model_dump(exclude_none=True)
        d = map_keys_deeply(d, snake_to_camel)
        return d
