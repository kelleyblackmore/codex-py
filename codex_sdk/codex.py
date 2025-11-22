"""Main Codex client class."""

from typing import Dict, Optional

from .exec import CodexExec
from .thread import Thread, ThreadOptions


class CodexOptions:
    """Options for configuring the Codex client."""
    
    def __init__(
        self,
        codex_path_override: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Codex options.
        
        Args:
            codex_path_override: Path to the codex binary. If None, will attempt to find it.
            env: Environment variables to pass to the subprocess.
            base_url: Base URL for the API.
            api_key: API key for authentication.
        """
        self.codex_path_override = codex_path_override
        self.env = env
        self.base_url = base_url
        self.api_key = api_key


class Codex:
    """
    Codex is the main class for interacting with the Codex agent.
    
    Use the `start_thread()` method to start a new thread or `resume_thread()` to resume
    a previously started thread.
    """
    
    def __init__(self, options: Optional[CodexOptions] = None):
        """
        Initialize the Codex client.
        
        Args:
            options: Configuration options for the client.
        """
        opts = options or CodexOptions()
        self._exec = CodexExec(opts.codex_path_override, opts.env)
        self._base_url = opts.base_url
        self._api_key = opts.api_key
    
    def start_thread(self, options: Optional[ThreadOptions] = None) -> Thread:
        """
        Starts a new conversation with an agent.
        
        Args:
            options: Configuration options for the thread.
            
        Returns:
            A new thread instance.
        """
        return Thread(
            exec=self._exec,
            base_url=self._base_url,
            api_key=self._api_key,
            options=options,
        )
    
    def resume_thread(
        self,
        thread_id: str,
        options: Optional[ThreadOptions] = None,
    ) -> Thread:
        """
        Resumes a conversation with an agent based on the thread id.
        Threads are persisted in ~/.codex/sessions.
        
        Args:
            thread_id: The id of the thread to resume.
            options: Configuration options for the thread.
            
        Returns:
            A thread instance for the resumed conversation.
        """
        return Thread(
            exec=self._exec,
            base_url=self._base_url,
            api_key=self._api_key,
            options=options,
            thread_id=thread_id,
        )
