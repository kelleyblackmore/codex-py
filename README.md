# Codex SDK for Python

Embed the Codex agent in your workflows and apps.

The Python SDK wraps the bundled `codex` binary. It spawns the CLI and exchanges JSONL events over stdin/stdout.

This is a Python port of the [TypeScript SDK](https://github.com/openai/codex/tree/main/sdk/typescript) from the official [OpenAI Codex repository](https://github.com/openai/codex).

## Installation

```bash
pip install codex-py
```

Requires Python 3.8+.

**Note:** This SDK requires the Codex CLI to be installed. Install it via:
- `npm install -g @openai/codex`, or
- `brew install --cask codex`, or
- Download from [GitHub Releases](https://github.com/openai/codex/releases)

## Quickstart

```python
import asyncio
from codex_sdk import Codex

async def main():
    codex = Codex()
    thread = codex.start_thread()
    turn = await thread.run("Diagnose the test failure and propose a fix")
    
    print(turn["final_response"])
    print(turn["items"])

asyncio.run(main())
```

Call `run()` repeatedly on the same `Thread` instance to continue that conversation.

```python
next_turn = await thread.run("Implement the fix")
```

### Streaming responses

`run()` buffers events until the turn finishes. To react to intermediate progress—tool calls, streaming responses, and file change notifications—use `run_streamed()` instead, which returns an async generator of structured events.

```python
import asyncio
from codex_sdk import Codex

async def main():
    codex = Codex()
    thread = codex.start_thread()
    result = await thread.run_streamed("Diagnose the test failure and propose a fix")
    
    async for event in result["events"]:
        if event["type"] == "item.completed":
            print("item", event["item"])
        elif event["type"] == "turn.completed":
            print("usage", event["usage"])

asyncio.run(main())
```

### Structured output

The Codex agent can produce a JSON response that conforms to a specified schema. The schema can be provided for each turn as a plain JSON object (dictionary).

```python
import asyncio
from codex_sdk import Codex, TurnOptions

async def main():
    schema = {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "status": {"type": "string", "enum": ["ok", "action_required"]},
        },
        "required": ["summary", "status"],
        "additionalProperties": False,
    }
    
    codex = Codex()
    thread = codex.start_thread()
    turn = await thread.run(
        "Summarize repository status",
        options=TurnOptions(output_schema=schema)
    )
    print(turn["final_response"])

asyncio.run(main())
```

You can also use [Pydantic](https://docs.pydantic.dev/) to define schemas:

```python
from pydantic import BaseModel
from codex_sdk import Codex, TurnOptions

class RepositoryStatus(BaseModel):
    summary: str
    status: str  # "ok" or "action_required"

async def main():
    codex = Codex()
    thread = codex.start_thread()
    
    # Convert Pydantic model to JSON schema
    schema = RepositoryStatus.model_json_schema()
    
    turn = await thread.run(
        "Summarize repository status",
        options=TurnOptions(output_schema=schema)
    )
    print(turn["final_response"])
```

### Attaching images

Provide structured input entries when you need to include images alongside text. Text entries are concatenated into the final prompt while image entries are passed to the Codex CLI via `--image`.

```python
import asyncio
from codex_sdk import Codex

async def main():
    codex = Codex()
    thread = codex.start_thread()
    turn = await thread.run([
        {"type": "text", "text": "Describe these screenshots"},
        {"type": "local_image", "path": "./ui.png"},
        {"type": "local_image", "path": "./diagram.jpg"},
    ])
    print(turn["final_response"])

asyncio.run(main())
```

### Resuming an existing thread

Threads are persisted in `~/.codex/sessions`. If you lose the in-memory `Thread` object, reconstruct it with `resume_thread()` and keep going.

```python
import asyncio
import os
from codex_sdk import Codex

async def main():
    saved_thread_id = os.environ["CODEX_THREAD_ID"]
    
    codex = Codex()
    thread = codex.resume_thread(saved_thread_id)
    await thread.run("Implement the fix")

asyncio.run(main())
```

### Working directory controls

Codex runs in the current working directory by default. To avoid unrecoverable errors, Codex requires the working directory to be a Git repository. You can skip the Git repository check by passing the `skip_git_repo_check` option when creating a thread.

```python
import asyncio
from codex_sdk import Codex, ThreadOptions

async def main():
    codex = Codex()
    thread = codex.start_thread(
        options=ThreadOptions(
            working_directory="/path/to/project",
            skip_git_repo_check=True,
        )
    )
    turn = await thread.run("List files in this directory")
    print(turn["final_response"])

asyncio.run(main())
```

### Controlling the Codex CLI environment

By default, the Codex CLI inherits the Python process environment. Provide the optional `env` parameter when instantiating the `Codex` client to fully control which variables the CLI receives—useful for sandboxed hosts.

```python
from codex_sdk import Codex, CodexOptions

codex = Codex(
    options=CodexOptions(
        env={
            "PATH": "/usr/local/bin",
        }
    )
)
```

The SDK still injects its required variables (such as `OPENAI_BASE_URL` and `CODEX_API_KEY`) on top of the environment you provide.

## API Reference

### Classes

- **`Codex`**: Main client class for interacting with the Codex agent
  - `start_thread(options=None)`: Start a new conversation thread
  - `resume_thread(thread_id, options=None)`: Resume an existing thread

- **`Thread`**: Represents a conversation thread
  - `run(input, options=None)`: Execute a turn and wait for completion
  - `run_streamed(input, options=None)`: Execute a turn and stream events
  - `id`: Property that returns the thread ID

- **`CodexOptions`**: Configuration for the Codex client
  - `codex_path_override`: Custom path to codex binary
  - `env`: Custom environment variables
  - `base_url`: API base URL
  - `api_key`: API key for authentication

- **`ThreadOptions`**: Configuration for a thread
  - `model`: Model to use
  - `sandbox_mode`: Sandbox mode ("read-only", "workspace-write", "danger-full-access")
  - `working_directory`: Working directory path
  - `additional_directories`: List of additional directories to allow access
  - `skip_git_repo_check`: Skip Git repository check
  - `model_reasoning_effort`: Reasoning effort level
  - `network_access_enabled`: Enable network access
  - `web_search_enabled`: Enable web search
  - `approval_policy`: Approval policy mode

- **`TurnOptions`**: Configuration for a single turn
  - `output_schema`: JSON schema for structured output

### Type Definitions

See the source code for complete type definitions of events and items:
- `ThreadEvent`: Union of all event types
- `ThreadItem`: Union of all item types (commands, file changes, messages, etc.)
- `Usage`: Token usage information

## Development

To set up for development:

```bash
# Clone the repository
git clone https://github.com/kelleyblackmore/codex-py.git
cd codex-py

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black codex_sdk/

# Type check
mypy codex_sdk/

# Lint
ruff check codex_sdk/
```

## License

This project is licensed under the Apache-2.0 License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [OpenAI Codex](https://github.com/openai/codex) - Official Codex CLI and TypeScript SDK
- [Codex TypeScript SDK](https://github.com/openai/codex/tree/main/sdk/typescript) - Official TypeScript SDK

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.