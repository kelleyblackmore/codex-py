"""Item types that represent actions and messages in a thread."""

from typing import Any, List, Literal, Optional, Union
from typing_extensions import TypedDict


CommandExecutionStatus = Literal["in_progress", "completed", "failed"]
"""The status of a command execution."""


class CommandExecutionItem(TypedDict):
    """A command executed by the agent."""
    id: str
    type: Literal["command_execution"]
    command: str
    aggregated_output: str
    exit_code: Optional[int]
    status: CommandExecutionStatus


PatchChangeKind = Literal["add", "delete", "update"]
"""Indicates the type of the file change."""


class FileUpdateChange(TypedDict):
    """A single file change."""
    path: str
    kind: PatchChangeKind


PatchApplyStatus = Literal["completed", "failed"]
"""The status of a file change."""


class FileChangeItem(TypedDict):
    """A set of file changes by the agent. Emitted once the patch succeeds or fails."""
    id: str
    type: Literal["file_change"]
    changes: List[FileUpdateChange]
    status: PatchApplyStatus


McpToolCallStatus = Literal["in_progress", "completed", "failed"]
"""The status of an MCP tool call."""


class McpContentBlock(TypedDict, total=False):
    """Content block from MCP."""
    type: str
    text: str


class McpToolCallResult(TypedDict):
    """Result from an MCP tool call."""
    content: List[McpContentBlock]
    structured_content: Any


class McpToolCallError(TypedDict):
    """Error from an MCP tool call."""
    message: str


class McpToolCallItem(TypedDict, total=False):
    """
    Represents a call to an MCP tool. The item starts when the invocation is dispatched
    and completes when the MCP server reports success or failure.
    """
    id: str
    type: Literal["mcp_tool_call"]
    server: str
    tool: str
    arguments: Any
    result: McpToolCallResult
    error: McpToolCallError
    status: McpToolCallStatus


class AgentMessageItem(TypedDict):
    """Response from the agent. Either natural-language text or JSON when structured output is requested."""
    id: str
    type: Literal["agent_message"]
    text: str


class ReasoningItem(TypedDict):
    """Agent's reasoning summary."""
    id: str
    type: Literal["reasoning"]
    text: str


class WebSearchItem(TypedDict):
    """Captures a web search request. Completes when results are returned to the agent."""
    id: str
    type: Literal["web_search"]
    query: str


class ErrorItem(TypedDict):
    """Describes a non-fatal error surfaced as an item."""
    id: str
    type: Literal["error"]
    message: str


class TodoItem(TypedDict):
    """An item in the agent's to-do list."""
    text: str
    completed: bool


class TodoListItem(TypedDict):
    """
    Tracks the agent's running to-do list. Starts when the plan is issued, updates as steps change,
    and completes when the turn ends.
    """
    id: str
    type: Literal["todo_list"]
    items: List[TodoItem]


ThreadItem = Union[
    AgentMessageItem,
    ReasoningItem,
    CommandExecutionItem,
    FileChangeItem,
    McpToolCallItem,
    WebSearchItem,
    TodoListItem,
    ErrorItem,
]
"""Canonical union of thread items and their type-specific payloads."""
