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
    from ..config import get_config
    config = get_config()
    
    # Note: Using text-only mode since structured output needs careful setup
    agent = Agent(
        config.get_agent_model("coordinator"),
        system_prompt="""You are an intelligent task coordinator for a multi-agent system.

**YOUR JOB**: Actually USE the tools to complete user requests. Don't explain, DO.

Available tools (YOU MUST USE THESE):
- analyze_codebase(request, focus): For code analysis, understanding structure
- edit_files(instructions, file_context): For making code changes
- search_code(query, file_pattern): For finding code/files

**RULES**:
1. ALWAYS call the appropriate tool(s) to answer the question
2. DO NOT explain what tools you would use - ACTUALLY USE THEM
3. After using tools, present results in natural language
4. Be direct and action-oriented

**Examples of what to do**:

User: "How many Python files are there?"
✅ DO: Call search_code("*.py") then say "I found 42 Python files in the repository"
❌ DON'T: "I would use search_code to find Python files..."

User: "Analyze config.py"
✅ DO: Call analyze_codebase("analyze config.py") then present the analysis
❌ DON'T: "Let me explain how I would analyze this..."

User: "Find the longest file"
✅ DO: Call search_code to find files, then report the result
❌ DON'T: "Here's how to search for files..."

**Response Format** (natural language):
Present tool results conversationally without metadata. Example:

"I found 42 Python files in the repository, including:
- packages/core/agents/ (7 files)
- packages/core/tools/ (12 files)  
- tests/ (23 files)"

NOT: "RESULT: {...} AGENTS_USED: search_code"

**Remember**: ACT, don't explain. Use the tools, get results, present them naturally.""",
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
            # Handle text-only response
            output = result.output if hasattr(result, 'output') else str(result.data)
            return f"Code Analysis:\n{output}"
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
            # Force tool usage with tool_choice=required
            from pydantic_ai import ModelSettings
            result = await file_editor_agent.run(
                prompt,
                model_settings=ModelSettings(tool_choice='required')
            )
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
            # Handle text-only response
            output = result.output if hasattr(result, 'output') else str(result.data)
            return f"Search results:\n{output}"
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
    
    # Detect success/failure - default to success unless clear error
    error_indicators = [
        "error:", "failed:", "exception:", "could not", "unable to",
        "not found", "does not exist", "cannot"
    ]
    success = not any(indicator in output.lower() for indicator in error_indicators)
    
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
