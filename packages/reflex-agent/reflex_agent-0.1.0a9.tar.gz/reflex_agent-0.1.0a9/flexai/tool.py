"""Base class to define agent tools."""

import inspect
from dataclasses import dataclass
from typing import Callable, Type


@dataclass(frozen=True)
class Tool:
    """A tool is a function that can be called by an agent."""

    # The name of the tool.
    name: str

    # A description of how the tool works - this should be detailed
    description: str

    # The function parameters and their types.
    params: tuple[tuple[str, str], ...]

    # The return type of the function.
    return_type: str

    # The function to call.
    fn: Callable

    @classmethod
    def from_function(cls, func: Callable):
        """Create a tool from a function."""
        signature = inspect.signature(func)
        params = tuple(
            (
                (
                    name,
                    (
                        param.annotation.__name__
                        if hasattr(param.annotation, "__name__")
                        else "No annotation"
                    ),
                )
            )
            for name, param in signature.parameters.items()
        )
        return_type = (
            signature.return_annotation.__name__
            if hasattr(signature.return_annotation, "__name__")
            else "No annotation"
        )
        description = inspect.getdoc(func) or "No description"
        return cls(
            name=func.__name__,
            description=description,
            params=params,
            return_type=return_type,
            fn=func,
        )

    def to_description(self) -> dict:
        """Convert the tool to a description."""
        type_map = {
            "str": "string",
            "int": "number",
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object",
        }

        input_schema = {
            "type": "object",
            "properties": {},
        }
        for param_name, param_type in self.params:
            param_type = type_map.get(str(param_type), param_type)
            input_schema["properties"][param_name] = {
                "type": param_type,
            }

        description = {
            "name": self.name,
            "description": self.description,
            "input_schema": input_schema,
        }
        return description


def send_message(message: str) -> None:
    """Send a final message to the user. This should be done after all internal processing is completed."""
    pass
