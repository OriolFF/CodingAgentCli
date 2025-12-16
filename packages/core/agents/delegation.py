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
    
    model_instance = config.get_model_instance("coordinator")
    logger.info(f"Initializing coordinator agent with model: {model_instance}")
    
    # Note: Using text-only mode since structured output needs careful setup
    agent = Agent(
        model_instance,
        system_prompt="""You are an intelligent task coordinator for a multi-agent system.

**YOUR JOB**: Actually USE the tools to complete user requests. Don't explain, DO.

Available tools (YOU MUST USE THESE):
- generate_code(description, language, file_path): For creating NEW code files (handles generation AND writing)
- analyze_codebase(request, focus): For code analysis, understanding structure
- edit_files(instructions, file_context): For modifying EXISTING files
- search_code(query, file_pattern): For finding code/files

**ROUTING LOGIC**:

1. **Create NEW file with code** (HTML, Python, JS, etc.):
   - Call generate_code(description, language, file_path) - THAT'S IT!
   - The code_generator will generate AND write the file automatically
   - Example: "create landing.html with Material 3"
     → generate_code("landing page with Material 3", "html", "sandbox/landing.html")
   - DO NOT call edit_files after generate_code (file is already written!)

2. **Analyze or understand** existing code:
   - Call analyze_codebase(request, focus)
   - Example: "analyze config.py" → analyze_codebase("analyze config.py")

3. **Modify or refactor** existing files:
   - Call edit_files(instructions, file_context)
   - Example: "add type hints to calc.py" → edit_files("add type hints to calc.py")

4. **Search or find** code:
   - Call search_code(query, file_pattern)
   - Example: "find async functions" → search_code("async def")

**RULES**:
1. ALWAYS call the appropriate tool(s) to answer the question
2. DO NOT explain what tools you would use - ACTUALLY USE THEM
3. For code generation, ONLY call generate_code() once - it writes the file automatically
4. After using tools, present results in natural language
5. Be direct and action-oriented

**Examples of what to do**:

User: "create app.py with FastAPI hello endpoint"
✅ DO: generate_code("FastAPI app with hello endpoint", "python", "sandbox/app.py")

User: "create landing.html with Material 3 design"
✅ DO: generate_code("landing page with Material 3", "html", "sandbox/landing.html")

User: "How many Python files are there?"
✅ DO: search_code("*.py") then say "I found 42 Python files in the repository"

User: "Analyze config.py"
✅ DO: analyze_codebase("analyze config.py") then present the analysis

User: "Modify calculator.py to add type hints"
✅ DO: edit_files("add type hints to calculator.py")

❌ DON'T: generate_code() THEN edit_files() - generate_code already writes the file!

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
    from .code_generator import get_code_generator_agent
    
    @agent.tool
    async def generate_code(
        ctx: RunContext[None],
        description: str,
        language: str = "python",
        file_path: str = ""
    ) -> str:
        """Generate code and write it to a file.
        
        The code_generator will try to generate the code AND write it to the file using tools.
        If tools aren't called (model explains instead), we fall back to manual file writing.
        
        Args:
            ctx: Runtime context
            description: What code to generate
            language: Programming language (python, html, javascript, css, etc.)
            file_path: Where to save the file (e.g., "sandbox/app.py")
            
        Returns:
            Confirmation message
        """
        logger.info(f"Delegating to code generator: {description} ({language}) -> {file_path}")
        
        code_gen_agent = get_code_generator_agent()
        
        # Construct prompt that includes file creation
        prompt = f"Create {file_path} with {language} code: {description}"
        
        try:
            result = await code_gen_agent.run(prompt)
            
            # Check if tools were called
            tool_called = False
            if hasattr(result, 'all_messages'):
                try:
                    messages = result.all_messages()
                    for msg in messages:
                        if hasattr(msg, 'kind') and msg.kind == 'tool-call':
                            tool_called = True
                            logger.info(f"✅ Code generator used tools to create {file_path}")
                            break
                except Exception as e:
                    logger.debug(f"Could not inspect messages: {e}")
            
            output = result.output if hasattr(result, 'output') else str(result.data)
            
            if tool_called:
                # File was created by the tool
                logger.info(f"Code generation completed for {file_path} via TOOLS")
                return output
            else:
                # FALLBACK: Tool wasn't called, extract code and write manually
                logger.warning(f"⚠️ Code generator didn't use tools - triggering FALLBACK for {file_path}")
                
                # Simple code extraction
                code_content = output.strip()
                
                # Pattern 1: Extract from function-call-like format
                # Example: create_new_file({ "file_path": "...", "content": "...", ... })
                import re
                import json
                
                func_call_pattern = r'create_new_file\s*\(\s*(\{.*?\})\s*\)'
                func_match = re.search(func_call_pattern, code_content, re.DOTALL)
                
                if func_match:
                    try:
                        json_obj = json.loads(func_match.group(1))
                        if 'content' in json_obj:
                            code_content = json_obj['content']
                            logger.info(f"Extracted code from function-call format")
                        elif 'arguments' in json_obj and 'content' in json_obj['arguments']:
                            code_content = json_obj['arguments']['content']
                            logger.info(f"Extracted code from nested arguments")
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.debug(f"Failed to parse function call JSON: {e}")
                
                # Pattern 2: Direct JSON object (fallback from previous implementation)
                elif code_content.startswith('{'):
                    try:
                        json_obj = json.loads(code_content)
                        if 'arguments' in json_obj and 'content' in json_obj['arguments']:
                            code_content = json_obj['arguments']['content']
                            logger.info(f"Extracted code from JSON arguments field")
                        elif 'content' in json_obj:
                            code_content = json_obj['content']
                            logger.info(f"Extracted code from JSON content field")
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.debug(f"Failed to parse JSON: {e}")
                
                # Pattern 3: Markdown code blocks
                code_block_pattern = r'```(?:[a-z]+)?\s*\n?(.*?)```'
                match = re.search(code_block_pattern, code_content, re.DOTALL)
                
                if match:
                    code_content = match.group(1).strip()
                    logger.info(f"Extracted code from markdown block")
                
                if not code_content or len(code_content) < 10:
                    logger.error(f"❌ No valid code extracted (got {len(code_content)} chars)")
                    return f"Failed to extract code from response"
                
                # Write the code
                from ..tools.file_operations import WriteFileTool
                write_tool = WriteFileTool()
                
                try:
                    await write_tool.execute(file_path, code_content)
                    logger.info(f"✅ FALLBACK: Successfully wrote {file_path} ({len(code_content)} bytes)")
                    return f"Created {file_path} using fallback ({len(code_content)} characters)"
                except Exception as e:
                    logger.error(f"❌ FALLBACK failed to write {file_path}: {e}")
                    return f"Failed to create {file_path}: {str(e)}"
                    
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return f"Generation failed: {str(e)}"
    
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
        file_context: Optional[str] = None,
        content: Optional[str] = None
    ) -> str:
        """Make precise changes to files or write pre-generated content.
        
        Use this tool when the user wants to:
        - Write pre-generated code to a file (when content is provided)
        - Modify existing code (when content is NOT provided)
        - Update configuration
        - Refactor code
        - Fix issues
        
        Args:
            ctx: Runtime context
            instructions: What changes to make or file path to write to
            file_context: Optional context about which files
            content: Optional pre-generated content to write (from generate_code)
            
        Returns:
            Edit results
        """
        if content:
            logger.info(f"Delegating to file editor with pre-generated content ({len(content)} chars): {instructions}")
        else:
            logger.info(f"Delegating to file editor: {instructions}")
        
        file_editor_agent = get_file_editor_agent()
        
        prompt = f"Make these changes: {instructions}"
        if file_context:
            prompt += f"\nContext: {file_context}"
        if content:
            prompt += f"\n\nUSE THIS EXACT CONTENT (do not modify):\n{content}"
        
        try:
            # Force tool usage with tool_choice=required
            from pydantic_ai import ModelSettings
            result = await file_editor_agent.run(
                prompt,
                model_settings=ModelSettings(tool_choice='required')
            )
            # Handle text-only response
            output = result.output if hasattr(result, 'output') else str(result.data)
            return f"File editor result:\n{output}"
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
