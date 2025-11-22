"""Example showing various configuration options for the Codex SDK."""

import asyncio
import os
from codex_sdk import Codex
from codex_sdk.codex import CodexOptions
from codex_sdk.thread import ThreadOptions


async def basic_config():
    """Example of basic configuration."""
    print("=== Basic Configuration ===")
    
    # Configure the Codex client with API settings
    codex_options = CodexOptions(
        base_url=os.getenv("OPENAI_BASE_URL"),  # Optional: custom API endpoint
        api_key=os.getenv("CODEX_API_KEY"),     # Optional: API key
    )
    
    codex = Codex(options=codex_options)
    thread = codex.start_thread()
    
    print("✓ Codex client configured with API settings")


async def custom_binary_path():
    """Example of specifying a custom codex binary path."""
    print("\n=== Custom Binary Path ===")
    
    codex_options = CodexOptions(
        codex_path_override="/usr/local/bin/codex"  # Custom path to codex binary
    )
    
    codex = Codex(options=codex_options)
    print("✓ Using custom codex binary path")


async def environment_control():
    """Example of controlling the subprocess environment."""
    print("\n=== Environment Control ===")
    
    # Provide a custom environment for the codex subprocess
    custom_env = {
        "PATH": "/usr/local/bin:/usr/bin:/bin",
        "HOME": os.path.expanduser("~"),
        "CUSTOM_VAR": "value",
    }
    
    codex_options = CodexOptions(env=custom_env)
    codex = Codex(options=codex_options)
    
    print("✓ Codex subprocess configured with custom environment")


async def sandbox_configuration():
    """Example of different sandbox modes."""
    print("\n=== Sandbox Configuration ===")
    
    codex = Codex()
    
    # Read-only sandbox (default, safest)
    print("\n1. Read-only sandbox:")
    thread_ro = codex.start_thread(
        options=ThreadOptions(sandbox_mode="read-only")
    )
    print("   - Agent can read files but cannot modify them")
    print("   - No network access")
    
    # Workspace-write sandbox
    print("\n2. Workspace-write sandbox:")
    thread_ww = codex.start_thread(
        options=ThreadOptions(sandbox_mode="workspace-write")
    )
    print("   - Agent can write within the working directory")
    print("   - No network access by default")
    
    # Workspace-write with network access
    print("\n3. Workspace-write with network:")
    thread_ww_net = codex.start_thread(
        options=ThreadOptions(
            sandbox_mode="workspace-write",
            network_access_enabled=True,
        )
    )
    print("   - Agent can write within the working directory")
    print("   - Network access enabled")
    
    # Full access (dangerous, use only in containers)
    print("\n4. Full access (DANGER):")
    print("   options=ThreadOptions(sandbox_mode='danger-full-access')")
    print("   - Agent has full system access")
    print("   - Only use in isolated environments!")


async def working_directory_config():
    """Example of configuring working directory."""
    print("\n=== Working Directory Configuration ===")
    
    codex = Codex()
    
    # Specify a working directory
    thread = codex.start_thread(
        options=ThreadOptions(
            working_directory="/path/to/project",
            skip_git_repo_check=True,  # Skip Git repo requirement
        )
    )
    
    print("✓ Thread configured with custom working directory")


async def multi_directory_access():
    """Example of allowing access to multiple directories."""
    print("\n=== Multi-Directory Access ===")
    
    codex = Codex()
    
    # Allow access to multiple directories outside the workspace
    thread = codex.start_thread(
        options=ThreadOptions(
            working_directory="/path/to/project",
            additional_directories=[
                "/path/to/shared/lib",
                "/path/to/data",
            ],
            sandbox_mode="workspace-write",
        )
    )
    
    print("✓ Thread configured with access to multiple directories")


async def model_configuration():
    """Example of model configuration."""
    print("\n=== Model Configuration ===")
    
    codex = Codex()
    
    # Use a specific model
    thread = codex.start_thread(
        options=ThreadOptions(
            model="gpt-4",  # or "gpt-4-turbo", "gpt-3.5-turbo", etc.
        )
    )
    
    print("✓ Thread configured with specific model")


async def reasoning_effort():
    """Example of configuring reasoning effort."""
    print("\n=== Reasoning Effort Configuration ===")
    
    codex = Codex()
    
    # Configure reasoning effort level
    thread = codex.start_thread(
        options=ThreadOptions(
            model_reasoning_effort="high",  # "low", "medium", "high"
        )
    )
    
    print("✓ Thread configured with high reasoning effort")


async def approval_policy():
    """Example of approval policy configuration."""
    print("\n=== Approval Policy Configuration ===")
    
    codex = Codex()
    
    # Auto-approve all actions
    thread_auto = codex.start_thread(
        options=ThreadOptions(
            approval_policy="auto",
        )
    )
    print("✓ Thread configured with auto-approval")
    
    # Manual approval required
    thread_manual = codex.start_thread(
        options=ThreadOptions(
            approval_policy="manual",
        )
    )
    print("✓ Thread configured with manual approval")


async def web_search():
    """Example of enabling web search."""
    print("\n=== Web Search Configuration ===")
    
    codex = Codex()
    
    # Enable web search feature
    thread = codex.start_thread(
        options=ThreadOptions(
            web_search_enabled=True,
        )
    )
    
    print("✓ Thread configured with web search enabled")


async def complete_example():
    """Example combining multiple configuration options."""
    print("\n=== Complete Configuration Example ===")
    
    codex_options = CodexOptions(
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("CODEX_API_KEY"),
    )
    
    codex = Codex(options=codex_options)
    
    thread = codex.start_thread(
        options=ThreadOptions(
            model="gpt-4",
            sandbox_mode="workspace-write",
            working_directory=os.getcwd(),
            additional_directories=["/tmp/shared"],
            skip_git_repo_check=False,
            model_reasoning_effort="medium",
            network_access_enabled=False,
            web_search_enabled=True,
            approval_policy="auto",
        )
    )
    
    print("✓ Thread configured with comprehensive settings:")
    print("  - Model: gpt-4")
    print("  - Sandbox: workspace-write")
    print("  - Working dir: current directory")
    print("  - Additional dirs: /tmp/shared")
    print("  - Git check: enabled")
    print("  - Reasoning: medium")
    print("  - Network: disabled")
    print("  - Web search: enabled")
    print("  - Approval: auto")


async def main():
    """Run all configuration examples."""
    await basic_config()
    await custom_binary_path()
    await environment_control()
    await sandbox_configuration()
    await working_directory_config()
    await multi_directory_access()
    await model_configuration()
    await reasoning_effort()
    await approval_policy()
    await web_search()
    await complete_example()
    
    print("\n" + "="*50)
    print("All configuration examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
