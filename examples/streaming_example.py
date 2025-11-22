"""Example showing how to stream events from the Codex agent."""

import asyncio
from codex_sdk import Codex


async def main():
    """Run a streaming example using the Codex SDK."""
    # Initialize the Codex client
    codex = Codex()
    
    # Start a new conversation thread
    thread = codex.start_thread()
    
    # Run a query with streaming
    print("Running query with streaming: 'Analyze this Python project structure'")
    print("\n=== Streaming Events ===\n")
    
    result = await thread.run_streamed("Analyze this Python project structure")
    
    async for event in result["events"]:
        event_type = event["type"]
        
        if event_type == "thread.started":
            print(f"✓ Thread started: {event['thread_id']}")
        
        elif event_type == "turn.started":
            print("✓ Turn started")
        
        elif event_type == "item.started":
            item = event["item"]
            item_type = item["type"]
            print(f"→ Item started: {item_type}")
            
            if item_type == "command_execution":
                print(f"  Command: {item['command']}")
        
        elif event_type == "item.updated":
            item = event["item"]
            if item["type"] == "command_execution":
                print(f"  Output: {item['aggregated_output'][:100]}...")
        
        elif event_type == "item.completed":
            item = event["item"]
            item_type = item["type"]
            print(f"✓ Item completed: {item_type}")
            
            if item_type == "agent_message":
                print(f"\n=== Agent Response ===")
                print(item["text"])
            elif item_type == "command_execution":
                print(f"  Exit code: {item.get('exit_code', 'N/A')}")
            elif item_type == "file_change":
                print(f"  Files changed: {len(item['changes'])}")
                for change in item["changes"]:
                    print(f"    - {change['kind']}: {change['path']}")
        
        elif event_type == "turn.completed":
            usage = event["usage"]
            print(f"\n✓ Turn completed")
            print(f"  Token usage: {usage['input_tokens']} in, {usage['output_tokens']} out")
        
        elif event_type == "turn.failed":
            error = event["error"]
            print(f"✗ Turn failed: {error['message']}")


if __name__ == "__main__":
    asyncio.run(main())
