"""Agent delegation system for intelligent task routing.

This module provides a coordinator agent that can analyze user requests
and delegate tasks to the most appropriate specialized agent.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from typing import Optional, List
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DelegationResult(BaseModel):
    """Result from delegating a task to specialized agents."""
    
    success: bool = Field(description="Whether the task succeeded")
    result: str = Field(description="Result from the delegated task")
    agents_used: List[str] = Field(
        description="List of agents that were invoked",
        default_factory=list
    )
    task_summary: str = Field(description="Summary of what was done")


# Lazy initialization for coordinator
_coordinator_agent: Optional[Agent] = None


def get_coordinator_agent() -> Agent:
    """Get or create the coordinator agent.
    
    Returns:
        The coordinator agent with delegation capabilities
    """
    global _coordinator_agent
    if _coordinator_agent is None:
        _coordinator_agent = _create_coordinator_agent()
    return _coordinator_agent


def _create_coordinator_agent() -> Agent:
    """Create the coordinator agent with specialized agent tools.
    
    Returns:
        Configured coordinator agent
    """
    # Note: Using text-only mode since structured output needs careful setup
    agent = Agent(
        "ollama:mistral",
        system_prompt="""You are an intelligent task coordinator for a multi-agent system.

Your role is to:
1. Analyze user requests and understand their intent
2. Route tasks to the most appropriate specialized agent
3. Use the available agent tools to delegate work
4. Provide clear, helpful responses

Available specialized agents (as tools):
- analyze_codebase: For code analysis, architecture review, finding patterns
- edit_files: For making code changes, refactoring, modifications  
- search_code: For finding specific code, searching patterns

**Response Guidelines**:
- Always respond in natural, conversational language
- Be helpful and clear in your explanations
- Format responses with headers, bullets, or sections for readability
- Never output raw JSON unless explicitly requested
- Provide context about what the delegated agents found

Example: Instead of JSON, say:
"I analyzed the delegation system using the codebase investigator:

**Purpose**: Routes user requests to specialized agents
**Key Components**: Coordinator agent, tool wrappers, result parsing
**Strengths**: Clean separation, extensible design"

Delegate effectively and communicate results clearly!

When handling requests:
- Use analyze_codebase for "what", "how", "explain" questions
- Use edit_files for "change", "update", "modify" requests
- Use search_code for "find", "search", "locate" requests
- You can chain multiple agents for complex tasks

RESULT: <detailed result>
AGENTS_USED: <comma-separated list of agents>
SUMMARY: <brief summary>""",
        retries=2,
    )
    
    # Import here to avoid circular imports
    from .codebase_investigator import get_codebase_agent
    from .file_editor import get_file_editor_agent
    
    @agent.tool
    async def analyze_codebase(
        ctx: RunContext[None],
        request: str,
        focus: Optional[str] = None
    ) -> str:
        """Analyze code structure, patterns, and quality.
        
        Use this tool when the user wants to:
        - Understand how code works
        - Get explanations of code structure
        - Identify patterns or issues
        - Assess code quality
        
        Args:
            ctx: Runtime context
            request: What to analyze
            focus: Optional focus area (e.g., "security", "performance")
            
        Returns:
            Analysis results
        """
        logger.info(f"Delegating to codebase investigator: {request}")
        
        codebase_agent = get_codebase_agent()
        
        prompt = f"Analyze: {request}"
        if focus:
            prompt += f"\nFocus on: {focus}"
        
        try:
            result = await codebase_agent.run(prompt)
            return f"Code Analysis:\n{result.data.summary}"
        except Exception as e:
            logger.error(f"Codebase analysis failed: {e}")
            return f"Analysis failed: {str(e)}"
    
    @agent.tool
    async def edit_files(
        ctx: RunContext[None],
        instructions: str,
        file_context: Optional[str] = None
    ) -> str:
        """Make precise changes to files.
        
        Use this tool when the user wants to:
        - Modify existing code
        - Update configuration
        - Refactor code
        - Fix issues
        
        Args:
            ctx: Runtime context
            instructions: What changes to make
            file_context: Optional context about which files
            
        Returns:
            Edit results
        """
        logger.info(f"Delegating to file editor: {instructions}")
        
        file_editor_agent = get_file_editor_agent()
        
        prompt = f"Make these changes: {instructions}"
        if file_context:
            prompt += f"\nContext: {file_context}"
        
        try:
            result = await file_editor_agent.run(prompt)
            files_modified = ", ".join(result.data.files_modified)
            return f"Files edited: {files_modified}\n{result.data.changes_summary}"
        except Exception as e:
            logger.error(f"File editing failed: {e}")
            return f"Edit failed: {str(e)}"
    
    @agent.tool
    async def search_code(
        ctx: RunContext[None],
        query: str,
        file_pattern: str = "*.py"
    ) -> str:
        """Search for code patterns or files.
        
        Use this tool when the user wants to:
        - Find specific code
        - Locate files
        - Search for patterns
        - Discover where something is used
        
        Args:
            ctx: Runtime context
            query: What to search for
            file_pattern: File pattern to search (e.g., "*.py")
            
        Returns:
            Search results
        """
        logger.info(f"Searching code for: {query}")
        
        # Use codebase agent's search capabilities
        codebase_agent = get_codebase_agent()
        
        prompt = f"Search for: {query} in files matching {file_pattern}"
        
        try:
            result = await codebase_agent.run(prompt)
            return f"Search results:\n{result.data.summary}"
        except Exception as e:
            logger.error(f"Code search failed: {e}")
            return f"Search failed: {str(e)}"
    
    return agent


async def delegate_task(
    request: str,
    context: Optional[str] = None
) -> DelegationResult:
    """Delegate a task to appropriate specialized agents.
    
    This is the main entry point for task delegation. The coordinator
    will analyze the request and route it to the right agents.
    
    Args:
        request: User's request
        context: Optional additional context
        
    Returns:
        DelegationResult with outcomes
        
    Example:
        >>> result = await delegate_task(
        ...     "Analyze the config system and update temperature to 0.5"
        ... )
        >>> print(result.task_summary)
        "Analyzed configuration, then updated default_temperature to 0.5"
    """
    coordinator = get_coordinator_agent()
    
    prompt = request
    if context:
        prompt += f"\n\nContext: {context}"
    
    logger.info(f"Delegating task: {request}")
    
    result = await coordinator.run(prompt)
    
    # Parse text output into DelegationResult
    output = result.output if hasattr(result, 'output') else str(result.data)
    
    # Simple parsing - look for SUCCESS, RESULT, AGENTS_USED, SUMMARY
    success = "SUCCESS: true" in output.lower() or "success" in output.lower()
    
    # Extract agents used (simple heuristic)
    agents_used = []
    if "analyze_codebase" in output or "codebase" in output.lower():
        agents_used.append("codebase_investigator")
    if "edit_files" in output or "editor" in output.lower():
        agents_used.append("file_editor")
    
    return DelegationResult(
        success=success,
        result=output,
        agents_used=agents_used,
        task_summary=output[:200] + "..." if len(output) > 200 else output
    )
