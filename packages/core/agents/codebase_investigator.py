"""Codebase Investigator Agent for code analysis and exploration.

This specialized agent is designed to analyze codebases, identify patterns,
and provide insights about code structure and quality.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from typing import List, Optional
from ..tools.search import GrepSearchTool, GlobSearchTool, ListDirectoryTool
from ..tools.file_operations import ReadFileTool
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CodeAnalysis(BaseModel):
    """Structured output for code analysis."""
    summary: str = Field(description="Overall summary of the code/codebase")
    key_files: List[str] = Field(description="Important files identified")
    patterns: List[str] = Field(description="Patterns or conventions found")
    suggestions: List[str] = Field(description="Improvement suggestions")
    complexity_score: int = Field(
        description="Complexity rating from 1-10",
        ge=1,
        le=10
    )


# Create the codebase investigator agent
codebase_agent = Agent(
    "ollama:mistral",
    result_type=CodeAnalysis,
    system_prompt="""You are an expert code analyst and software architect.
    
Your role is to analyze codebases, identify patterns, assess code quality,
and provide actionable insights for improvement.

When analyzing code:
1. Look for architectural patterns and design principles
2. Identify code smells and potential issues
3. Assess code complexity and maintainability
4. Suggest improvements based on best practices
5. Be specific and provide examples

Be concise but thorough in your analysis.""",
    retries=2,
)


# Register tools with the agent
@codebase_agent.tool
async def analyze_directory_structure(ctx: RunContext[None], directory: str = ".") -> str:
    """Analyze the structure of a directory.
    
    Args:
        ctx: Runtime context
        directory: Directory to analyze
        
    Returns:
        Description of directory structure
    """
    tool = ListDirectoryTool()
    result = await tool.execute(directory=directory, show_hidden=False, max_depth=2)
    
    if result.success:
        logger.info(f"Analyzed directory structure: {directory}")
        return f"Directory structure:\n{result.output}"
    else:
        return f"Error analyzing directory: {result.error}"


@codebase_agent.tool
async def find_files_by_pattern(
    ctx: RunContext[None],
    pattern: str,
    directory: str = "."
) -> str:
    """Find files matching a glob pattern.
    
    Args:
        ctx: Runtime context
        pattern: Glob pattern (e.g., "*.py", "**/*.ts")
        directory: Directory to search in
        
    Returns:
        List of matching files
    """
    tool = GlobSearchTool()
    result = await tool.execute(
        pattern=pattern,
        directory=directory,
        recursive=True,
        max_results=100
    )
    
    if result.success:
        logger.info(f"Found {result.metadata['match_count']} files matching '{pattern}'")
        return f"Files matching '{pattern}':\n{result.output}"
    else:
        return f"Error finding files: {result.error}"


@codebase_agent.tool
async def search_code_content(
    ctx: RunContext[None],
    pattern: str,
    file_pattern: str = "*.py",
    directory: str = "."
) -> str:
    """Search for patterns in code files.
    
    Args:
        ctx: Runtime context
        pattern: Regex pattern to search for
        file_pattern: File pattern to search (e.g., "*.py")
        directory: Directory to search in
        
    Returns:
        Matching lines with file locations
    """
    tool = GrepSearchTool()
    result = await tool.execute(
        pattern=pattern,
        directory=directory,
        file_pattern=file_pattern,
        case_sensitive=True,
        max_results=50
    )
    
    if result.success:
        logger.info(f"Found {result.metadata['match_count']} matches for '{pattern}'")
        return f"Search results for '{pattern}':\n{result.output}"
    else:
        return f"Error searching code: {result.error}"


@codebase_agent.tool
async def read_file_content(
    ctx: RunContext[None],
    file_path: str,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None
) -> str:
    """Read the contents of a file.
    
    Args:
        ctx: Runtime context
        file_path: Path to the file
        start_line: Optional start line (1-indexed)
        end_line: Optional end line (1-indexed, inclusive)
        
    Returns:
        File contents
    """
    tool = ReadFileTool()
    result = await tool.execute(
        file_path=file_path,
        start_line=start_line,
        end_line=end_line
    )
    
    if result.success:
        logger.info(f"Read file: {file_path}")
        return f"Contents of {file_path}:\n{result.output}"
    else:
        return f"Error reading file: {result.error}"


async def analyze_codebase(directory: str = ".", focus: Optional[str] = None) -> CodeAnalysis:
    """Analyze a codebase and provide insights.
    
    Args:
        directory: Directory to analyze
        focus: Optional focus area (e.g., "security", "performance", "architecture")
        
    Returns:
        CodeAnalysis with findings and recommendations
    """
    prompt = f"Analyze the codebase in directory '{directory}'."
    if focus:
        prompt += f" Focus on: {focus}."
    
    prompt += """
    
    Use the available tools to:
    1. Explore the directory structure
    2. Find relevant code files
    3. Search for patterns and conventions
    4. Read key files
    
    Provide a comprehensive analysis with specific examples and actionable recommendations.
    """
    
    result = await codebase_agent.run(prompt)
    return result.data
