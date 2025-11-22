"""Test that all package imports work correctly."""

import pytest


def test_package_imports():
    """Test that the package can be imported."""
    import codex_sdk
    assert codex_sdk.__version__ == "0.1.0"


def test_main_class_imports():
    """Test that main classes can be imported."""
    from codex_sdk import Codex, Thread
    assert Codex is not None
    assert Thread is not None


def test_type_imports():
    """Test that type definitions can be imported."""
    from codex_sdk import (
        ThreadEvent,
        ThreadItem,
        Usage,
        Turn,
        StreamedTurn,
    )
    assert ThreadEvent is not None
    assert ThreadItem is not None
    assert Usage is not None
    assert Turn is not None
    assert StreamedTurn is not None


def test_event_type_imports():
    """Test that event types can be imported."""
    from codex_sdk import (
        ThreadStartedEvent,
        TurnStartedEvent,
        TurnCompletedEvent,
        TurnFailedEvent,
        ItemStartedEvent,
        ItemUpdatedEvent,
        ItemCompletedEvent,
        ThreadErrorEvent,
    )
    assert ThreadStartedEvent is not None
    assert TurnStartedEvent is not None
    assert TurnCompletedEvent is not None
    assert TurnFailedEvent is not None
    assert ItemStartedEvent is not None
    assert ItemUpdatedEvent is not None
    assert ItemCompletedEvent is not None
    assert ThreadErrorEvent is not None


def test_item_type_imports():
    """Test that item types can be imported."""
    from codex_sdk import (
        CommandExecutionItem,
        FileChangeItem,
        McpToolCallItem,
        AgentMessageItem,
        ReasoningItem,
        WebSearchItem,
        ErrorItem,
        TodoListItem,
    )
    assert CommandExecutionItem is not None
    assert FileChangeItem is not None
    assert McpToolCallItem is not None
    assert AgentMessageItem is not None
    assert ReasoningItem is not None
    assert WebSearchItem is not None
    assert ErrorItem is not None
    assert TodoListItem is not None


def test_codex_instantiation():
    """Test that Codex can be instantiated with a mock path."""
    from codex_sdk import Codex
    from codex_sdk.codex import CodexOptions
    
    # Use a mock path to avoid requiring the actual binary
    options = CodexOptions(codex_path_override="/mock/path/to/codex")
    codex = Codex(options=options)
    assert codex is not None


def test_codex_options():
    """Test that CodexOptions can be used."""
    from codex_sdk import Codex
    from codex_sdk.codex import CodexOptions
    
    options = CodexOptions(
        codex_path_override="/mock/path/to/codex",
        base_url="https://api.example.com",
        api_key="test-key",
    )
    codex = Codex(options=options)
    assert codex is not None


def test_thread_options():
    """Test that ThreadOptions can be used."""
    from codex_sdk import Codex
    from codex_sdk.codex import CodexOptions
    from codex_sdk.thread import ThreadOptions
    
    codex_options = CodexOptions(codex_path_override="/mock/path/to/codex")
    codex = Codex(options=codex_options)
    
    thread_options = ThreadOptions(
        model="gpt-4",
        sandbox_mode="read-only",
    )
    thread = codex.start_thread(options=thread_options)
    assert thread is not None
    assert thread.id is None  # ID is populated after first turn


def test_turn_options():
    """Test that TurnOptions can be used."""
    from codex_sdk.thread import TurnOptions
    
    schema = {
        "type": "object",
        "properties": {
            "result": {"type": "string"}
        }
    }
    options = TurnOptions(output_schema=schema)
    assert options.output_schema == schema
