"""Thread management for conversations with the Codex agent."""

import json
import tempfile
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from typing_extensions import TypedDict

from .events import ThreadEvent, Usage
from .exec import CodexExec, CodexExecArgs
from .items import ThreadItem


class TextInput(TypedDict):
    """Text input to send to the agent."""
    type: str  # "text"
    text: str


class LocalImageInput(TypedDict):
    """Local image input to send to the agent."""
    type: str  # "local_image"
    path: str


UserInput = Union[TextInput, LocalImageInput]
"""An input to send to the agent."""

Input = Union[str, List[UserInput]]
"""Input can be a simple string or a list of structured inputs (text and images)."""


class Turn(TypedDict):
    """Completed turn."""
    items: List[ThreadItem]
    final_response: str
    usage: Optional[Usage]


class StreamedTurn(TypedDict):
    """The result of a streamed turn."""
    events: AsyncGenerator[ThreadEvent, None]


class ThreadOptions:
    """Options for configuring a thread."""
    
    def __init__(
        self,
        model: Optional[str] = None,
        sandbox_mode: Optional[str] = None,
        working_directory: Optional[str] = None,
        additional_directories: Optional[List[str]] = None,
        skip_git_repo_check: bool = False,
        model_reasoning_effort: Optional[str] = None,
        network_access_enabled: Optional[bool] = None,
        web_search_enabled: Optional[bool] = None,
        approval_policy: Optional[str] = None,
    ):
        """
        Initialize thread options.
        
        Args:
            model: Model to use for the conversation.
            sandbox_mode: Sandbox mode (e.g., "read-only", "workspace-write", "danger-full-access").
            working_directory: Working directory for the thread.
            additional_directories: Additional directories to allow access to.
            skip_git_repo_check: Skip Git repository check.
            model_reasoning_effort: Reasoning effort level (e.g., "low", "medium", "high").
            network_access_enabled: Enable network access in the sandbox.
            web_search_enabled: Enable web search feature.
            approval_policy: Approval policy (e.g., "auto", "manual").
        """
        self.model = model
        self.sandbox_mode = sandbox_mode
        self.working_directory = working_directory
        self.additional_directories = additional_directories
        self.skip_git_repo_check = skip_git_repo_check
        self.model_reasoning_effort = model_reasoning_effort
        self.network_access_enabled = network_access_enabled
        self.web_search_enabled = web_search_enabled
        self.approval_policy = approval_policy


class TurnOptions:
    """Options for a single turn in a thread."""
    
    def __init__(self, output_schema: Optional[Dict[str, Any]] = None):
        """
        Initialize turn options.
        
        Args:
            output_schema: JSON schema for structured output.
        """
        self.output_schema = output_schema


class Thread:
    """Represents a thread of conversation with the agent. One thread can have multiple consecutive turns."""
    
    def __init__(
        self,
        exec: CodexExec,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        options: Optional[ThreadOptions] = None,
        thread_id: Optional[str] = None,
    ):
        """
        Initialize a thread.
        
        Args:
            exec: CodexExec instance for running the CLI.
            base_url: Base URL for the API.
            api_key: API key for authentication.
            options: Thread configuration options.
            thread_id: ID of an existing thread to resume.
        """
        self._exec = exec
        self._base_url = base_url
        self._api_key = api_key
        self._id = thread_id
        self._options = options or ThreadOptions()
    
    @property
    def id(self) -> Optional[str]:
        """Returns the ID of the thread. Populated after the first turn starts."""
        return self._id
    
    async def run_streamed(
        self,
        input: Input,
        options: Optional[TurnOptions] = None,
    ) -> StreamedTurn:
        """
        Provides the input to the agent and streams events as they are produced during the turn.
        
        Args:
            input: Input to send to the agent (string or list of structured inputs).
            options: Options for this turn.
            
        Returns:
            StreamedTurn containing an async generator of events.
        """
        return {"events": self._run_streamed_internal(input, options)}
    
    async def _run_streamed_internal(
        self,
        input: Input,
        options: Optional[TurnOptions] = None,
    ) -> AsyncGenerator[ThreadEvent, None]:
        """Internal implementation of run_streamed."""
        turn_options = options or TurnOptions()
        
        # Handle output schema
        schema_file_path = None
        temp_file = None
        try:
            if turn_options.output_schema:
                temp_file = tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.json',
                    delete=False,
                )
                json.dump(turn_options.output_schema, temp_file)
                temp_file.close()
                schema_file_path = temp_file.name
            
            # Normalize input
            prompt, images = self._normalize_input(input)
            
            # Build exec arguments
            exec_args = CodexExecArgs(
                input=prompt,
                base_url=self._base_url,
                api_key=self._api_key,
                thread_id=self._id,
                images=images,
                model=self._options.model,
                sandbox_mode=self._options.sandbox_mode,
                working_directory=self._options.working_directory,
                additional_directories=self._options.additional_directories,
                skip_git_repo_check=self._options.skip_git_repo_check,
                output_schema_file=schema_file_path,
                model_reasoning_effort=self._options.model_reasoning_effort,
                network_access_enabled=self._options.network_access_enabled,
                web_search_enabled=self._options.web_search_enabled,
                approval_policy=self._options.approval_policy,
            )
            
            # Execute and yield events
            async for line in self._exec.run(exec_args):
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as e:
                    raise RuntimeError(f"Failed to parse event: {line}") from e
                
                # Update thread ID from the first event
                if event.get("type") == "thread.started":
                    self._id = event.get("thread_id")
                
                yield event
        
        finally:
            # Cleanup temp file
            if temp_file and schema_file_path:
                try:
                    Path(schema_file_path).unlink()
                except Exception:
                    pass
    
    async def run(
        self,
        input: Input,
        options: Optional[TurnOptions] = None,
    ) -> Turn:
        """
        Provides the input to the agent and returns the completed turn.
        
        Args:
            input: Input to send to the agent (string or list of structured inputs).
            options: Options for this turn.
            
        Returns:
            Completed turn with items, final response, and usage.
            
        Raises:
            RuntimeError: If the turn fails.
        """
        items: List[ThreadItem] = []
        final_response = ""
        usage: Optional[Usage] = None
        turn_failure = None
        
        async for event in self._run_streamed_internal(input, options):
            event_type = event.get("type")
            
            if event_type == "item.completed":
                item = event.get("item")
                if item and item.get("type") == "agent_message":
                    final_response = item.get("text", "")
                if item:
                    items.append(item)
            elif event_type == "turn.completed":
                usage = event.get("usage")
            elif event_type == "turn.failed":
                turn_failure = event.get("error")
                break
        
        if turn_failure:
            raise RuntimeError(turn_failure.get("message", "Turn failed"))
        
        return {
            "items": items,
            "final_response": final_response,
            "usage": usage,
        }
    
    def _normalize_input(self, input: Input) -> tuple[str, List[str]]:
        """
        Normalize input into prompt text and image paths.
        
        Args:
            input: Input to normalize.
            
        Returns:
            Tuple of (prompt, images).
        """
        if isinstance(input, str):
            return input, []
        
        prompt_parts: List[str] = []
        images: List[str] = []
        
        for item in input:
            if item.get("type") == "text":
                prompt_parts.append(item.get("text", ""))
            elif item.get("type") == "local_image":
                images.append(item.get("path", ""))
        
        return "\n\n".join(prompt_parts), images
