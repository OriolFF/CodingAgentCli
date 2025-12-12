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


# Create the file editor agent
file_editor_agent = Agent(
    "ollama:mistral",
    result_type=EditResult,
    system_prompt="""You are a precise code editor specializing in making targeted,
minimal changes to code files.

Your role is to:
1. Make only the necessary changes requested
2. Preserve existing code style and formatting
3. Maintain code quality and correctness
4. Provide clear summaries of what was changed

When editing files:
- Be surgical and precise
- Don't make unnecessary changes
- Verify that changes are correct
- Use proper search-and-replace to ensure accuracy

Always prioritize code quality and correctness.""",
    retries=1,  # Low retries for edit operations
)


@file_editor_agent.tool
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


@file_editor_agent.tool
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


@file_editor_agent.tool
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
    
    result = await file_editor_agent.run(prompt)
    return result.data
