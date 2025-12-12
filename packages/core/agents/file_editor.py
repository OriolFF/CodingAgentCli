"""File Editor Agent for precise code modifications.

This specialized agent is designed to make targeted, precise edits to files
with a focus on maintaining code quality and consistency.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from typing import List, Optional
from ..tools.file_edit import EditFileTool
from ..tools.file_operations import ReadFileTool, WriteFileTool
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EditResult(BaseModel):
    """Structured output for file edit operations."""
    success: bool = Field(description="Whether the edit was successful")
    files_modified: List[str] = Field(description="List of files that were modified")
    changes_summary: str = Field(description="Summary of changes made")
    diff_preview: Optional[str] = Field(
        description="Preview of changes (diff format)",
        default=None
    )


# Lazy initialization
_file_editor_agent: Optional[Agent] = None


def get_file_editor_agent() -> Agent:
    """Get or create the file editor agent.
    
    Returns:
        The file editor agent
    """
    global _file_editor_agent
    if _file_editor_agent is None:
        _file_editor_agent = _create_file_editor_agent()
    return _file_editor_agent


def _create_file_editor_agent() -> Agent:
    """Create the file editor agent with tools.
    
    Returns:
        Configured agent
    """
    from ..config import get_config
    config = get_config()
    
    agent = Agent(
        config.get_agent_model("file_editor"),
        system_prompt="""You are an expert code editor specializing in precise, minimal changes.

Your role is to make targeted edits to code files while preserving:
- Existing functionality
- Code style and formatting  
- Comments and documentation

When editing:
- Make the smallest possible changes to achieve the goal
- Preserve all existing functionality
- Follow the project's code style
- Be precise and careful

Always explain what changes you're making and why.""",
        retries=1,
    )
    
    @agent.tool
    async def read_file_for_editing(
        ctx: RunContext[None],
        file_path: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> str:
        """Read a file to understand its contents before editing.
        
        Args:
            ctx: Runtime context
            file_path: Path to the file
            start_line: Optional start line
            end_line: Optional end line
            
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
            return f"Current contents of {file_path}:\n{result.output}"
        else:
            return f"Error reading file: {result.error}"
    
    @agent.tool
    async def edit_file_content(
        ctx: RunContext[None],
        file_path: str,
        search_text: str,
        replace_text: str,
        start_line: Optional[int] = None,
        end_line: Optional[int] = None
    ) -> str:
        """Edit a file by replacing search text with replacement text.
        
        Args:
            ctx: Runtime context
            file_path: Path to the file to edit
            search_text: Text to search for (exact match)
            replace_text: Text to replace with
            start_line: Optional line to start search from
            end_line: Optional line to end search at
            
        Returns:
            Description of the edit with diff
        """
        tool = EditFileTool()
        result = await tool.execute(
            file_path=file_path,
            search_text=search_text,
            replace_text=replace_text,
            start_line=start_line,
            end_line=end_line
        )
        
        if result.success:
            logger.info(f"Successfully edited {file_path}")
            return f"Edit successful. Changes:\n{result.output}"
        else:
            return f"Edit failed: {result.error}"
    
    @agent.tool
    async def create_new_file(
        ctx: RunContext[None],
        file_path: str,
        content: str
    ) -> str:
        """Create a new file with the given content.
        
        Args:
            ctx: Runtime context
            file_path: Path for the new file
            content: Content to write
            
        Returns:
            Confirmation message
        """
        tool = WriteFileTool()
        result = await tool.execute(
            file_path=file_path,
            content=content
        )
        
        if result.success:
            logger.info(f"Created new file: {file_path}")
            return f"Successfully created {file_path}"
        else:
            return f"Failed to create file: {result.error}"
    
    return agent


async def edit_files(
    instructions: str,
    context: Optional[str] = None
) -> EditResult:
    """Edit files based on natural language instructions.
    
    Args:
        instructions: What changes to make
        context: Optional additional context
        
    Returns:
        EditResult with summary of changes
    """
    agent = get_file_editor_agent()
    
    prompt = f"Make the following changes to the code: {instructions}"
    if context:
        prompt += f"\n\nContext: {context}"
    
    prompt += """
    
    Steps:
    1. Read the relevant files to understand current state
    2. Make precise, targeted edits
    3. Verify changes are correct
    4. Provide a clear summary
    
    Be careful and precise with your edits.
    """
    
    result = await agent.run(prompt)
    output = result.output if hasattr(result, 'output') else str(result.data)
    
    return EditResult(
        success=True,
        files_modified=[],
        changes_summary=output
    )

