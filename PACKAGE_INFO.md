# Codex Python SDK - Package Information

## Overview
This package provides a Python SDK for the OpenAI Codex agent, mirroring the functionality of the TypeScript SDK. It wraps the Codex CLI binary and provides a clean, async/await API for programmatic access.

## Installation

```bash
pip install codex-sdk
```

**Prerequisites**: The Codex CLI must be installed separately:
- `npm install -g @openai/codex`, or
- `brew install --cask codex`, or
- Download from [GitHub Releases](https://github.com/openai/codex/releases)

## Quick Start

```python
import asyncio
from codex_sdk import Codex

async def main():
    codex = Codex()
    thread = codex.start_thread()
    turn = await thread.run("List files in the current directory")
    print(turn["final_response"])

asyncio.run(main())
```

## Features

### Core Functionality
- ✅ **Async/Await API** - Full async support using AsyncGenerator
- ✅ **Type Safety** - Complete type hints with TypedDict
- ✅ **Streaming** - Real-time event streaming with `run_streamed()`
- ✅ **Buffered** - Simple buffered execution with `run()`
- ✅ **Thread Management** - Start, resume, and persist conversations
- ✅ **Structured Output** - JSON schema support with Pydantic integration
- ✅ **Image Support** - Attach local images to prompts
- ✅ **Configuration** - Extensive options for sandbox, model, etc.

### Security & Reliability
- ✅ **Non-blocking I/O** - Async subprocess execution
- ✅ **Secure Temp Files** - Owner-only permissions (0o600)
- ✅ **Proper Error Handling** - Specific exception types
- ✅ **Graceful Cancellation** - Clean cleanup on interruption
- ✅ **Resource Management** - Proper process and file cleanup

## Architecture

### Package Structure
```
codex_sdk/
├── __init__.py       # Package exports
├── codex.py          # Main Codex client
├── thread.py         # Thread management
├── exec.py           # CLI execution layer (async)
├── events.py         # Event type definitions
└── items.py          # Item type definitions
```

### Execution Flow
1. User creates `Codex` client with options
2. Client creates `Thread` for conversation
3. Thread uses `CodexExec` to spawn CLI process
4. Exec manages async subprocess with stdin/stdout/stderr
5. Events stream back through AsyncGenerator
6. Thread buffers or streams events to user

## API Overview

### Main Classes

#### `Codex`
Main client for interacting with the Codex agent.

```python
codex = Codex(options=CodexOptions(
    base_url="https://api.example.com",
    api_key="sk-...",
    codex_path_override="/custom/path/to/codex",
    env={"PATH": "/usr/local/bin"},
))

thread = codex.start_thread(options)
thread = codex.resume_thread(thread_id, options)
```

#### `Thread`
Represents a conversation with the agent.

```python
# Buffered execution
turn = await thread.run("Do something")
print(turn["final_response"])
print(turn["items"])
print(turn["usage"])

# Streaming execution
result = await thread.run_streamed("Do something")
async for event in result["events"]:
    print(event["type"])
```

#### Configuration Options

**CodexOptions**: Client configuration
- `codex_path_override`: Custom path to binary
- `env`: Custom environment variables
- `base_url`: API endpoint
- `api_key`: Authentication key

**ThreadOptions**: Thread configuration
- `model`: Model to use (e.g., "gpt-4")
- `sandbox_mode`: "read-only", "workspace-write", "danger-full-access"
- `working_directory`: Working directory path
- `additional_directories`: Extra accessible paths
- `skip_git_repo_check`: Skip Git requirement
- `model_reasoning_effort`: "low", "medium", "high"
- `network_access_enabled`: Allow network in sandbox
- `web_search_enabled`: Enable web search
- `approval_policy`: "auto" or "manual"

**TurnOptions**: Turn configuration
- `output_schema`: JSON schema for structured output

### Type Definitions

#### Events
- `ThreadStartedEvent` - New thread created
- `TurnStartedEvent` - Turn begins
- `TurnCompletedEvent` - Turn ends with usage
- `TurnFailedEvent` - Turn failed with error
- `ItemStartedEvent` - New item added
- `ItemUpdatedEvent` - Item updated
- `ItemCompletedEvent` - Item completed
- `ThreadErrorEvent` - Fatal error

#### Items
- `AgentMessageItem` - Agent's text response
- `ReasoningItem` - Agent's reasoning
- `CommandExecutionItem` - Command run by agent
- `FileChangeItem` - Files modified by agent
- `McpToolCallItem` - MCP tool invocation
- `WebSearchItem` - Web search performed
- `TodoListItem` - Agent's task list
- `ErrorItem` - Non-fatal error

## Examples

The `examples/` directory contains:
1. **basic_usage.py** - Simple queries and continuations
2. **streaming_example.py** - Real-time event streaming
3. **structured_output.py** - JSON schema with Pydantic
4. **resume_thread.py** - Thread persistence
5. **configuration_example.py** - All configuration options

## Development

### Setup
```bash
git clone https://github.com/kelleyblackmore/codex-py.git
cd codex-py
pip install -e ".[dev]"
```

### Testing
```bash
pytest                    # Run all tests
pytest -v                 # Verbose output
pytest --cov=codex_sdk    # With coverage
```

### Code Quality
```bash
black codex_sdk/          # Format code
ruff check codex_sdk/     # Lint code
mypy codex_sdk/           # Type check
```

## Version History

### 0.1.0 (Initial Release)
- Complete async/await API
- Full TypeScript SDK parity
- Type-safe event and item definitions
- Streaming and buffered execution
- Structured output support
- Image attachment support
- Thread persistence
- Comprehensive examples
- Security improvements (async subprocess, secure temp files)
- All code review issues addressed
- Zero CodeQL security alerts

## License
Apache-2.0 - See LICENSE file for details

## Credits
- Original Codex CLI and TypeScript SDK by OpenAI
- Python SDK implementation by the community

## Links
- **Repository**: https://github.com/kelleyblackmore/codex-py
- **Issues**: https://github.com/kelleyblackmore/codex-py/issues
- **Original Codex**: https://github.com/openai/codex
- **Documentation**: See README.md

## Support
For issues, questions, or contributions, please visit the GitHub repository.
