"""Execution layer that spawns the Codex CLI binary."""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import AsyncGenerator, Dict, List, Optional


INTERNAL_ORIGINATOR_ENV = "CODEX_INTERNAL_ORIGINATOR_OVERRIDE"
PYTHON_SDK_ORIGINATOR = "codex_sdk_py"


class CodexExecArgs:
    """Arguments for executing the Codex CLI."""
    
    def __init__(
        self,
        input: str,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        thread_id: Optional[str] = None,
        images: Optional[List[str]] = None,
        model: Optional[str] = None,
        sandbox_mode: Optional[str] = None,
        working_directory: Optional[str] = None,
        additional_directories: Optional[List[str]] = None,
        skip_git_repo_check: bool = False,
        output_schema_file: Optional[str] = None,
        model_reasoning_effort: Optional[str] = None,
        network_access_enabled: Optional[bool] = None,
        web_search_enabled: Optional[bool] = None,
        approval_policy: Optional[str] = None,
    ):
        self.input = input
        self.base_url = base_url
        self.api_key = api_key
        self.thread_id = thread_id
        self.images = images or []
        self.model = model
        self.sandbox_mode = sandbox_mode
        self.working_directory = working_directory
        self.additional_directories = additional_directories or []
        self.skip_git_repo_check = skip_git_repo_check
        self.output_schema_file = output_schema_file
        self.model_reasoning_effort = model_reasoning_effort
        self.network_access_enabled = network_access_enabled
        self.web_search_enabled = web_search_enabled
        self.approval_policy = approval_policy


class CodexExec:
    """Handles execution of the Codex CLI binary."""
    
    def __init__(
        self,
        executable_path: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize the Codex executor.
        
        Args:
            executable_path: Path to the codex binary. If None, will attempt to find it.
            env: Environment variables to pass to the subprocess. If None, inherits from current process.
        """
        self.executable_path = executable_path or self._find_codex_path()
        self.env_override = env
    
    async def run(self, args: CodexExecArgs) -> AsyncGenerator[str, None]:
        """
        Execute the Codex CLI and yield JSONL events.
        
        Args:
            args: Arguments for the Codex execution.
            
        Yields:
            JSONL event strings.
            
        Raises:
            RuntimeError: If the Codex CLI exits with a non-zero status.
        """
        command_args = ["exec", "--experimental-json"]
        
        if args.model:
            command_args.extend(["--model", args.model])
        
        if args.sandbox_mode:
            command_args.extend(["--sandbox", args.sandbox_mode])
        
        if args.working_directory:
            command_args.extend(["--cd", args.working_directory])
        
        if args.additional_directories:
            for dir_path in args.additional_directories:
                command_args.extend(["--add-dir", dir_path])
        
        if args.skip_git_repo_check:
            command_args.append("--skip-git-repo-check")
        
        if args.output_schema_file:
            command_args.extend(["--output-schema", args.output_schema_file])
        
        if args.model_reasoning_effort:
            command_args.extend([
                "--config",
                f'model_reasoning_effort="{args.model_reasoning_effort}"'
            ])
        
        if args.network_access_enabled is not None:
            command_args.extend([
                "--config",
                f"sandbox_workspace_write.network_access={str(args.network_access_enabled).lower()}"
            ])
        
        if args.web_search_enabled is not None:
            command_args.extend([
                "--config",
                f"features.web_search_request={str(args.web_search_enabled).lower()}"
            ])
        
        if args.approval_policy:
            command_args.extend([
                "--config",
                f'approval_policy="{args.approval_policy}"'
            ])
        
        if args.images:
            for image in args.images:
                command_args.extend(["--image", image])
        
        if args.thread_id:
            command_args.extend(["resume", args.thread_id])
        
        # Prepare environment
        env = {}
        if self.env_override:
            env.update(self.env_override)
        else:
            env.update(os.environ)
        
        if INTERNAL_ORIGINATOR_ENV not in env:
            env[INTERNAL_ORIGINATOR_ENV] = PYTHON_SDK_ORIGINATOR
        
        if args.base_url:
            env["OPENAI_BASE_URL"] = args.base_url
        
        if args.api_key:
            env["CODEX_API_KEY"] = args.api_key
        
        # Spawn the process
        process = subprocess.Popen(
            [self.executable_path] + command_args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=1,  # Line buffered
        )
        
        try:
            # Write input to stdin
            if process.stdin:
                process.stdin.write(args.input)
                process.stdin.close()
            
            # Read lines from stdout
            if process.stdout:
                for line in process.stdout:
                    line = line.rstrip('\n\r')
                    if line:
                        yield line
            
            # Wait for process to complete
            return_code = process.wait()
            
            if return_code != 0:
                stderr_output = ""
                if process.stderr:
                    stderr_output = process.stderr.read()
                raise RuntimeError(
                    f"Codex Exec exited with code {return_code}: {stderr_output}"
                )
        
        finally:
            # Cleanup
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
    
    def _find_codex_path(self) -> str:
        """
        Find the path to the Codex CLI binary.
        
        Returns:
            Path to the codex binary.
            
        Raises:
            RuntimeError: If the binary cannot be found or platform is unsupported.
        """
        # First, check if 'codex' is in PATH
        codex_in_path = self._which_codex()
        if codex_in_path:
            return codex_in_path
        
        # Otherwise, look for a bundled binary
        system = platform.system().lower()
        machine = platform.machine().lower()
        
        # Map platform and architecture to target triple
        target_triple = None
        if system == "linux":
            if machine in ("x86_64", "amd64"):
                target_triple = "x86_64-unknown-linux-musl"
            elif machine in ("aarch64", "arm64"):
                target_triple = "aarch64-unknown-linux-musl"
        elif system == "darwin":
            if machine == "x86_64":
                target_triple = "x86_64-apple-darwin"
            elif machine in ("aarch64", "arm64"):
                target_triple = "aarch64-apple-darwin"
        elif system == "windows":
            if machine in ("x86_64", "amd64"):
                target_triple = "x86_64-pc-windows-msvc"
            elif machine in ("aarch64", "arm64"):
                target_triple = "aarch64-pc-windows-msvc"
        
        if not target_triple:
            raise RuntimeError(f"Unsupported platform: {system} ({machine})")
        
        # Look for bundled binary relative to this file
        script_dir = Path(__file__).parent
        vendor_root = script_dir.parent / "vendor"
        arch_root = vendor_root / target_triple
        codex_binary_name = "codex.exe" if system == "windows" else "codex"
        binary_path = arch_root / "codex" / codex_binary_name
        
        if binary_path.exists():
            return str(binary_path)
        
        raise RuntimeError(
            f"Could not find codex binary. Please install codex or provide executable_path. "
            f"Looked for: {binary_path}"
        )
    
    def _which_codex(self) -> Optional[str]:
        """Check if codex is available in PATH."""
        try:
            result = subprocess.run(
                ["which", "codex"] if sys.platform != "win32" else ["where", "codex"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception:
            pass
        return None
