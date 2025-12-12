"""Refactoring Agent for code improvement and optimization.

This specialized agent helps refactor code, improve structure,
and apply best practices.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from typing import List, Optional
from ..tools.file_operations import ReadFileTool
from ..tools.file_edit import EditFileTool
from ..tools.search import GrepSearchTool
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RefactoringResult(BaseModel):
    """Result from refactoring operations."""
    
    success: bool = Field(description="Whether refactoring succeeded")
    description: str = Field(description="Description of refactorings applied")
    files_modified: List[str] = Field(
        description="Files that were modified",
        default_factory=list
    )
    improvements: List[str] = Field(
        description="List of improvements made",
        default_factory=list
    )


# Lazy initialization
_refactoring_agent: Optional[Agent] = None


def get_refactoring_agent() -> Agent:
    """Get or create the refactoring agent.
    
    Returns:
        The refactoring agent
    """
    global _refactoring_agent
    if _refactoring_agent is None:
        _refactoring_agent = _create_refactoring_agent()
    return _refactoring_agent


def _create_refactoring_agent() -> Agent:
    """Create the refactoring agent with tools.
    
    Returns:
        Configured agent
    """
    from ..config import get_config
    config = get_config()
    
    agent = Agent(
        config.get_agent_model("refactoring"),
        system_prompt="""You are an expert software engineer specializing in code refactoring.

Your role is to:
1. Identify code smells and anti-patterns
2. Suggest and apply refactorings
3. Improve code structure and maintainability
4. Apply SOLID principles
5. Optimize performance where appropriate

When refactoring:
- Make small, incremental changes
- Preserve existing functionality
- Improve readability and maintainability
- Follow Python best practices (PEP 8, type hints)
- Add helpful comments where needed

Always explain what you're refactoring and why.""",
        retries=1,
    )
    
    @agent.tool
    async def analyze_code_quality(
        ctx: RunContext[None],
        file_path: str
    ) -> str:
        """Analyze code for quality issues.
        
        Args:
            ctx: Runtime context
            file_path: Path to code file
            
        Returns:
            Code analysis
        """
        tool = ReadFileTool()
        result = await tool.execute(file_path=file_path)
        
        if result.success:
            return f"Code to analyze:\n{result.output}"
        else:
            return f"Error reading file: {result.error}"
    
    @agent.tool
    async def refactor_code(
        ctx: RunContext[None],
        file_path: str,
        search_text: str,
        replacement: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> str:
        """Apply refactoring to code.
        
        Args:
            ctx: Runtime context
            file_path: File to refactor
            search_text: Code to replace
            replacement: Refactored code
            start_line: Optional start line
            end_line: Optional end line
            
        Returns:
            Refactoring result
        """
        tool = EditFileTool()
        result = await tool.execute(
            file_path=file_path,
            search_text=search_text,
            replace_text=replacement,
            start_line=start_line,
            end_line=end_line
        )
        
        if result.success:
            logger.info(f"Refactored {file_path}")
            return f"Refactoring applied:\n{result.output}"
        else:
            return f"Refactoring failed: {result.error}"
    
    @agent.tool
    async def find_code_pattern(
        ctx: RunContext[None],
        pattern: str,
        directory: str = "packages"
    ) -> str:
        """Find code patterns that need refactoring.
        
        Args:
            ctx: Runtime context
            pattern: Pattern to find
            directory: Directory to search
            
        Returns:
            Matching code locations
        """
        tool = GrepSearchTool()
        result = await tool.execute(
            pattern=pattern,
            directory=directory,
            file_pattern="*.py"
        )
        
        if result.success:
            return f"Found pattern occurrences:\n{result.output}"
        else:
            return f"Pattern search failed: {result.error}"
    
    return agent


async def refactor_file(
    file_path: str,
    focus: Optional[str] = None
) -> RefactoringResult:
    """Refactor a specific file.
    
    Args:
        file_path: File to refactor
        focus: Optional focus area (e.g., "Extract functions", "Simplify logic")
        
    Returns:
        RefactoringResult with changes made
    """
    agent = get_refactoring_agent()
    
    prompt = f"Refactor the code in: {file_path}"
    if focus:
        prompt += f"\nFocus on: {focus}"
    
    prompt += """
    
Please:
1. Analyze the code for quality issues
2. Identify specific refactoring opportunities
3. Apply refactorings to improve code quality
4. Explain what was changed and why

Make code more maintainable and follow best practices."""
    
    result = await agent.run(prompt)
    output = result.output if hasattr(result, 'output') else str(result.data)
    
    return RefactoringResult(
        success=True,
        description=output,
        files_modified=[file_path],
        improvements=[]
    )


async def extract_common_code(
    pattern: str,
    target_file: str = "packages/core/utils/helpers.py"
) -> RefactoringResult:
    """Find and extract common code patterns into a helper.
    
    Args:
        pattern: Code pattern to extract
        target_file: Where to put extracted code
        
    Returns:
        RefactoringResult with extraction details
    """
    agent = get_refactoring_agent()
    
    prompt = f"""Find duplicated code matching pattern: {pattern}

Then:
1. Find all occurrences of this pattern
2. Extract into a reusable function in {target_file}
3. Replace occurrences with calls to the new function

Reduce code duplication and improve maintainability."""
    
    result = await agent.run(prompt)
    output = result.output if hasattr(result, 'output') else str(result.data)
    
    return RefactoringResult(
        success=True,
        description=output,
        files_modified=[],
        improvements=["Extracted common code"]
    )
