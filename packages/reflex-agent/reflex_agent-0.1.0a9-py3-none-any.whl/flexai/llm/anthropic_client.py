from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import AsyncGenerator, TYPE_CHECKING, Type

# Try to import the anthropic library.
try:
    from anthropic import AsyncAnthropic
    from anthropic.types import ToolUseBlock
    from pydantic import BaseModel
except ImportError:
    raise ImportError(
        "The anthropic library is required for the AnthropicClient. "
        "Please install it using `pip install anthropic`."
    )
from flexai.llm.client import Client
from flexai.message import (
    AIMessage,
    Message,
    ToolUseMessage,
    UserMessage,
)

if TYPE_CHECKING:
    from flexai.tool import Tool


@dataclass(frozen=True)
class AnthropicClient(Client):
    """Client for interacting with the Anthropic language model."""

    # The client to use for interacting with the model.
    client: AsyncAnthropic = AsyncAnthropic()

    # The model to use for generating responses.
    model: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20240620")

    # The maximum number of tokens to generate in a response.
    max_tokens: int = 8192

    # Extra headers to include in the request.
    extra_headers: dict = field(default_factory=lambda: {"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"})

    async def get_chat_response(
        self,
        messages: list[Message],
        system: str = "",
        tools: list[Tool] | None = None,
    ) -> list[AIMessage]:
        # Get the response from the chat model.
        response = await self.client.messages.create(
            **self._get_params(messages, system, tools)
        )

        # Separate the tool use blocks from the regular messages.
        return [
            (
                self.to_tool_use_message(
                    message,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                )
                if isinstance(message, ToolUseBlock)
                else AIMessage(
                    content=message.text,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                )
            )
            for message in response.content
        ]

    async def stream_chat_response(
        self,
        messages: list[Message],
        system: str = "",
        tools: list[Tool] | None = None,
    ) -> AsyncGenerator[AIMessage, None]:
        async with self.client.messages.stream(
            **self._get_params(messages, system, tools)
        ) as stream:
            async for text in stream.text_stream:
                yield AIMessage(content=text)

    def _get_params(self, messages, system, tools) -> dict:
        """Get the common params to send to the model.

        Args:
            messages: The messages to send to the model.
            system: The system message to send to the model.
            tools: The tools to send to the model.

        Returns:
            The common params to send to the model.
        """
        kwargs = {
            "max_tokens": self.max_tokens,
            "messages": self.to_llm_messages(messages),
            "model": self.model,
            "system": system,
            "extra_headers": self.extra_headers,
        }

        # If tools are provided, force the model to use them (for now).
        if tools:
            kwargs["tools"] = self.to_tool_descriptions(tools)
            kwargs["tool_choice"] = {"type": "any"}
        else:
            kwargs["tools"] = []
        return kwargs

    @staticmethod
    def to_tool_use_message(tool_use_block: ToolUseBlock, **kwargs) -> ToolUseMessage:
        """Convert a tool use block to a ToolUseMessage.

        Args:
            tool_use_block: The tool use block to convert.
            kwargs: Additional keyword arguments to pass to the message.

        Returns:
            The tool use message.
        """
        return ToolUseMessage(
            content=tool_use_block.json(),
            id=tool_use_block.id,
            tool_name=tool_use_block.name,
            input=tool_use_block.input,
            **kwargs,
        )

    @staticmethod
    def to_llm_messages(messages: list[Message]) -> list[dict]:
        """Convert messages to the Anthropic format.

        Args:
            messages: The messages to convert.

        Returns:
            The messages in the anthropic format.
        """
        return [{"role": m.role, "content": m.content} for m in messages]

    @staticmethod
    def to_tool_descriptions(tools: list[Tool]) -> list[dict]:
        """Convert tools to the Anthropic format.

        Args:
            tools: The tools to convert.

        Returns:
            The tools in the anthropic format.
        """
        return [tool.to_description() for tool in tools]
    

    async def get_structured_response(
        self,
        messages: list[Message],
        model: Type[BaseModel],
        system: str | None = None,
    ) -> list[Type[BaseModel]]:
        """Get the structured response from the chat model.
        Args:
            messages: The messages to send to the model.
            model: The model to use for the response.
        Returns:
            The structured response from the model.
        """
        system = f"""{system or ""}
Return your answer according to the 'properties' of the following schema:
{model.schema()}
Return only the JSON object with the properties filled in.
Do not include anything in your response other than the JSON object.
Do not begin your response with ```json or end it with ```.
"""
        responses = await self.get_chat_response(messages, system=system)
        results = []
        for response in responses:
            try:
                obj = model.parse_raw(response.content)
                results.append(obj)
            except Exception as e:
                # Try again, printing the exception.
                messages = messages + [
                    response,
                    UserMessage(
                        content=f"There was an error while parsing. Make sure to only include the JSON. Error: {e}"
                    ),
                ]
                return await self.get_structured_response(
                    messages, model=model, system=system
                )
        return results
