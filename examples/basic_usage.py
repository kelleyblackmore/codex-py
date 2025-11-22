"""Basic usage example for the Codex SDK."""

import asyncio
from codex_sdk import Codex


async def main():
    """Run a basic example using the Codex SDK."""
    # Initialize the Codex client
    codex = Codex()
    
    # Start a new conversation thread
    thread = codex.start_thread()
    
    # Run a simple query
    print("Running query: 'List the files in the current directory'")
    turn = await thread.run("List the files in the current directory")
    
    # Print the response
    print("\n=== Final Response ===")
    print(turn["final_response"])
    
    # Print usage information
    if turn["usage"]:
        print("\n=== Token Usage ===")
        print(f"Input tokens: {turn['usage']['input_tokens']}")
        print(f"Cached input tokens: {turn['usage']['cached_input_tokens']}")
        print(f"Output tokens: {turn['usage']['output_tokens']}")
    
    # Print items (commands executed, file changes, etc.)
    print("\n=== Items ===")
    for item in turn["items"]:
        print(f"- {item['type']}: {item.get('text', item.get('command', 'N/A'))}")
    
    # Continue the conversation
    print("\n" + "="*50)
    print("Continuing conversation...")
    next_turn = await thread.run("What is the total size of all files?")
    print("\n=== Final Response ===")
    print(next_turn["final_response"])


if __name__ == "__main__":
    asyncio.run(main())
