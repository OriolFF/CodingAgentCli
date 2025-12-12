"""Base agent implementation using PydanticAI.

This module demonstrates the basic usage of PydanticAI with Ollama.
"""

import os
from pydantic_ai import Agent


# Set Ollama base URL via environment variable (if not already set)
if "OLLAMA_BASE_URL" not in os.environ:
    os.environ["OLLAMA_BASE_URL"] = "http://localhost:11434/v1"

# Create first PydanticAI agent with Ollama
# Using mistral with text output (Ollama has issues with structured JSON via OpenAI API)
# NOTE: Structured outputs (Pydantic models) don't work reliably with Ollama
# through the OpenAI-compatible API. See docs/model_compatibility.md for details.
# Future implementation will add proper structured output support.
simple_agent = Agent(
    "ollama:mistral",
    # No output_type for now - just text responses
    system_prompt="You are a helpful assistant. Provide concise, accurate answers.",
    retries=2,
)


async def test_agent_async(question: str) -> str:
    """Test agent with async call.

    Args:
        question: Question to ask the agent

    Returns:
        String answer from the agent

    Raises:
        RuntimeError: If Ollama is not running or model not available
    """
    try:
        result = await simple_agent.run(question)
        return result.output
    except Exception as e:
        raise RuntimeError(
            f"Failed to run agent. Is Ollama running? Error: {e}"
        ) from e


def test_agent_sync(question: str) -> str:
    """Test agent with synchronous call.

    Args:
        question: Question to ask the agent

    Returns:
        String answer from the agent

    Raises:
        RuntimeError: If Ollama is not running or model not available
    """
    try:
        result = simple_agent.run_sync(question)
        return result.output
    except Exception as e:
        raise RuntimeError(
            f"Failed to run agent. Is Ollama running? Error: {e}"
        ) from e

