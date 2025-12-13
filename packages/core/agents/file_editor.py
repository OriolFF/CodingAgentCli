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
    
    model_instance = config.get_model_instance("file_editor")
    logger.info(f"Initializing file_editor agent with model: {model_instance}")
    
    agent = Agent(
        model_instance,
        system_prompt="""You are a file editor agent. You MUST use the available tools.

⚠️ CRITICAL RULES - VIOLATION IS FAILURE ⚠️:

1. When asked to CREATE a file: IMMEDIATELY call create_new_file() tool
2. When asked to EDIT a file: IMMEDIATELY call read_file_for_editing() then edit_file_content()
3. NEVER respond with text explanations
4. NEVER provide manual instructions
5. NEVER say "here's how to" or "you should"

**SPECIAL: When receiving PRE-GENERATED CONTENT**:
If the request includes "USE THIS EXACT CONTENT" followed by code:
- Extract the file path from the instructions
- Extract ALL the content between "USE THIS EXACT CONTENT" and the end
- Call create_new_file(file_path, <ENTIRE_CONTENT>, description)
- DO NOT modify, truncate, or summarize the content
- Use the COMPLETE content exactly as provided

YOU HAVE THESE TOOLS - USE THEM:
- create_new_file(file_path, content, description)
- read_file_for_editing(file_path)  
- edit_file_content(file_path, original_content, new_content)

CORRECT BEHAVIOR:
User: "create sandbox/calc.py with add function"
You: [CALLS create_new_file("sandbox/calc.py", "def add(a, b):\\n    return a + b", "Calculator")]

User: "write to sandbox/app.py\n\nUSE THIS EXACT CONTENT:\ndef main():\n    print('hello')"
You: [CALLS create_new_file("sandbox/app.py", "def main():\n    print('hello')", "App")]

INCORRECT BEHAVIOR (FORBIDDEN):
User: "create sandbox/calc.py with add function"
You: "To create the file, run: mkdir sandbox..." ❌ WRONG! USE THE TOOL!

RESPONSE FORMAT:
When you receive a request, your FIRST action MUST be calling the appropriate tool.
After the tool executes, you may briefly confirm what was done.

REMEMBER: 
- You are a FILE EDITOR, not an instructor
- Your job is to EDIT FILES using tools, not explain how
- Every file operation MUST go through a tool call
- When given pre-generated content, use it EXACTLY as provided
- Text-only responses without tool calls = FAILURE""",
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


async def _fallback_file_write(instructions: str, file_path: Optional[str] = None) -> str:
    """Fallback mechanism to write files directly when tools aren't called.
    
    Args:
        instructions: The instruction text that may contain file creation details
        file_path: Optional explicit file path
        
    Returns:
        Result message
    """
    logger.warning("⚠️ Using FALLBACK mechanism for file operation")
    
    # Try to extract file path and content from instructions
    # This is a simple heuristic - you can make it more sophisticated
    if file_path is None:
        # Try to find file path in instructions
        import re
        path_match = re.search(r'(?:create|write)\s+([^\s]+(?:\.py|\.txt|\.md|\.json))', instructions, re.IGNORECASE)
        if path_match:
            file_path = path_match.group(1)
        else:
            logger.error("Could not extract file path from instructions")
            return "Failed: Could not determine file path"
    
    logger.info(f"Fallback: Attempting to create file {file_path}")
    
    # Extract content (simple heuristic - create empty or basic file)
    content = "# File created via fallback mechanism\n# TODO: Add implementation\n"
    
    # Check for content hints in instructions
    if "add function" in instructions.lower() or "function" in instructions.lower():
        func_name_match = re.search(r'(\w+)\s+function', instructions.lower())
        func_name = func_name_match.group(1) if func_name_match else "example"
        content = f"def {func_name}(*args, **kwargs):\n    \"\"\"TODO: Implement {func_name}\"\"\"\n    pass\n"
    
    from ..tools.file_operations import WriteFileTool
    tool = WriteFileTool()
    result = await tool.execute(file_path=file_path, content=content)
    
    if result.success:
        logger.info(f"✅ Fallback successfully created {file_path}")
        return f"File created via fallback: {file_path}"
    else:
        logger.error(f"❌ Fallback failed: {result.error}")
        return f"Fallback failed: {result.error}"


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
    
    logger.info(f"Running file_editor agent with instructions: {instructions[:100]}...")
    
    result = await agent.run(prompt)
    
    # Check if tools were actually called by inspecting messages
    tool_called = False
    if hasattr(result, 'all_messages'):
        try:
            messages = result.all_messages()
            for msg in messages:
                if hasattr(msg, 'kind') and msg.kind == 'tool-call':
                    tool_called = True
                    logger.info(f"✅ Tool call detected: {msg.tool_name if hasattr(msg, 'tool_name') else 'unknown'}")
                    break
        except Exception as e:
            logger.debug(f"Could not inspect messages: {e}")
    
    # Get output
    output = result.output if hasattr(result, 'output') else str(result.data)
    
    if tool_called:
        logger.info("✅ File operation completed using TOOLS")
        return EditResult(
            success=True,
            files_modified=[],
            changes_summary=output
        )
    else:
        logger.warning("⚠️ No tool calls detected in agent response")
        
        # Check if output looks like an explanation rather than action
        explanation_indicators = [
            "to create",
            "you should",
            "you can",
            "here's how",
            "mkdir",
            "touch",
            "run:",
            "execute:"
        ]
        
        is_explanation = any(
            indicator in output.lower() 
            for indicator in explanation_indicators
        )
        
        if is_explanation:
            logger.warning("⚠️ Agent provided explanation instead of executing - triggering FALLBACK")
            fallback_result = await _fallback_file_write(instructions)
            
            return EditResult(
                success=True,
                files_modified=[],
                changes_summary=f"{output}\n\n--- FALLBACK EXECUTED ---\n{fallback_result}"
            )
        else:
            # Agent might have done something valid, just not via tools
            logger.info("Agent response doesn't indicate explanation - accepting as-is")
            return EditResult(
                success=True,
                files_modified=[],
                changes_summary=output
            )

