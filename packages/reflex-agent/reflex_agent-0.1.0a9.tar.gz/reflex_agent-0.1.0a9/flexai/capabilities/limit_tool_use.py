from dataclasses import dataclass

from flexai.capability import Capability
from flexai.message import Message, AIMessage, ToolUseMessage


@dataclass(frozen=True)
class LimitToolUse(Capability):
    """Force an agent to stop if there are too many tool use."""

    # The maximum number of tool uses allowed.
    max_tool_uses: int

    async def modify_response(
        self, messages: list[Message], response: AIMessage
    ) -> AIMessage:
        # There's nothing to modify
        if not isinstance(response, ToolUseMessage):
            return response

        total_tool_uses = 0
        for message in messages:
            if isinstance(message, ToolUseMessage):
                total_tool_uses += 1
        # Can't use one more
        if total_tool_uses == self.max_tool_uses:
            return ToolUseMessage(
                id="",
                tool_name="send_message",
                input={"message": f"Exceeded tool usage limit: {self.max_tool_uses}"},
                content=response.content,
            )
        return response
