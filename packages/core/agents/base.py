"""Base agent implementation using PydanticAI.

This module demonstrates the basic usage of PydanticAI with structured outputs.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent


class SimpleResponse(BaseModel):
    """Structured response from agent.

    This Pydantic model ensures the agent's output is validated and type-safe.
    """

    answer: str = Field(description="The answer to the question")
    confidence: float = Field(
        description="Confidence score from 0 to 1", ge=0.0, le=1.0, default=0.8
    )


# Create first PydanticAI agent with Ollama
simple_agent = Agent(
    "ollama:mistral",
    output_type=SimpleResponse,
    system_prompt="You are a helpful assistant. Provide concise, accurate answers.",
)


async def test_agent_async(question: str) -> SimpleResponse:
    """Test agent with async call.

    Args:
        question: Question to ask the agent

    Returns:
        SimpleResponse with answer and confidence

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


def test_agent_sync(question: str) -> SimpleResponse:
    """Test agent with synchronous call.

    Args:
        question: Question to ask the agent

    Returns:
        SimpleResponse with answer and confidence

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

