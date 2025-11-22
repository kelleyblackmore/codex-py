"""Example showing how to use structured output with JSON schema."""

import asyncio
import json
from codex_sdk import Codex, TurnOptions


async def main():
    """Run a structured output example using the Codex SDK."""
    # Initialize the Codex client
    codex = Codex()
    
    # Start a new conversation thread
    thread = codex.start_thread()
    
    # Define a JSON schema for the output
    schema = {
        "type": "object",
        "properties": {
            "summary": {
                "type": "string",
                "description": "A brief summary of the repository"
            },
            "file_count": {
                "type": "integer",
                "description": "Total number of files"
            },
            "primary_language": {
                "type": "string",
                "description": "The primary programming language"
            },
            "status": {
                "type": "string",
                "enum": ["healthy", "needs_attention", "critical"],
                "description": "Overall status of the repository"
            },
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of issues found"
            }
        },
        "required": ["summary", "file_count", "primary_language", "status"],
        "additionalProperties": False
    }
    
    # Run a query with structured output
    print("Running query with structured output schema...")
    print(f"Schema: {json.dumps(schema, indent=2)}\n")
    
    turn = await thread.run(
        "Analyze this repository and provide a structured summary",
        options=TurnOptions(output_schema=schema)
    )
    
    # Parse the JSON response
    print("=== Structured Response ===")
    try:
        response_data = json.loads(turn["final_response"])
        print(json.dumps(response_data, indent=2))
        
        # Access structured data
        print("\n=== Parsed Data ===")
        print(f"Summary: {response_data.get('summary')}")
        print(f"File Count: {response_data.get('file_count')}")
        print(f"Primary Language: {response_data.get('primary_language')}")
        print(f"Status: {response_data.get('status')}")
        if "issues" in response_data:
            print(f"Issues:")
            for issue in response_data["issues"]:
                print(f"  - {issue}")
    
    except json.JSONDecodeError:
        print("Response is not valid JSON:")
        print(turn["final_response"])


async def pydantic_example():
    """Example using Pydantic for schema definition (if installed)."""
    try:
        from pydantic import BaseModel, Field
        from typing import List, Literal
        
        class RepositoryAnalysis(BaseModel):
            summary: str = Field(description="A brief summary of the repository")
            file_count: int = Field(description="Total number of files")
            primary_language: str = Field(description="The primary programming language")
            status: Literal["healthy", "needs_attention", "critical"] = Field(
                description="Overall status of the repository"
            )
            issues: List[str] = Field(default=[], description="List of issues found")
        
        codex = Codex()
        thread = codex.start_thread()
        
        # Convert Pydantic model to JSON schema
        schema = RepositoryAnalysis.model_json_schema()
        
        print("\n" + "="*50)
        print("Running with Pydantic schema...")
        
        turn = await thread.run(
            "Analyze this repository and provide a structured summary",
            options=TurnOptions(output_schema=schema)
        )
        
        # Parse into Pydantic model
        response_data = RepositoryAnalysis.model_validate_json(turn["final_response"])
        
        print("\n=== Pydantic Model ===")
        print(response_data.model_dump_json(indent=2))
    
    except ImportError:
        print("\n(Pydantic not installed - skipping Pydantic example)")


if __name__ == "__main__":
    asyncio.run(main())
    asyncio.run(pydantic_example())
