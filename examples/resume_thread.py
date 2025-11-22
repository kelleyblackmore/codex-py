"""Example showing how to resume a previous thread."""

import asyncio
import os
from codex_sdk import Codex


async def main():
    """Demonstrate resuming a thread."""
    codex = Codex()
    
    # Start a new thread and save its ID
    print("=== Starting a new thread ===")
    thread = codex.start_thread()
    
    turn1 = await thread.run("Create a file called hello.txt with 'Hello, World!'")
    print(f"Response: {turn1['final_response']}")
    
    # Get the thread ID
    thread_id = thread.id
    print(f"\nThread ID: {thread_id}")
    
    # Simulate losing the thread object (e.g., process restart)
    print("\n=== Simulating process restart ===")
    print("(In a real scenario, save the thread_id to environment or database)")
    
    # Resume the thread using the ID
    print("\n=== Resuming the thread ===")
    resumed_thread = codex.resume_thread(thread_id)
    
    turn2 = await resumed_thread.run("Now read the contents of hello.txt")
    print(f"Response: {turn2['final_response']}")
    
    # Verify it's the same thread
    print(f"\nResumed thread ID: {resumed_thread.id}")
    print(f"Same thread? {thread_id == resumed_thread.id}")


if __name__ == "__main__":
    asyncio.run(main())
