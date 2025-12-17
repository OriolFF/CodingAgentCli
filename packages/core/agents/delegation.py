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
                # FALLBACK: Tool wasn't called, use code extractor agent
                logger.warning(f"⚠️ Code generator didn't use tools - triggering CODE EXTRACTOR for {file_path}")
                logger.info(f"🔍 CODE EXTRACTOR invoked to parse response")
                
                # Log the FULL OUTPUT from the model
                print(f"\n{'='*80}")
                print(f"📋 FULL MODEL RESPONSE (length: {len(output)} chars)")
                print(f"{'='*80}")
                print(output[:2000])  # First 2000 chars
                print(f"\n{'='*80}")
                print(f"📋 END OF MODEL RESPONSE")
                print(f"{'='*80}\n")
                
                # Use intelligent code extractor micro-agent
                from .code_extractor import extract_code_from_response
                from ..tools.file_operations import WriteFileTool
                
                try:
                    # Extract code using AI-powered agent
                    extraction_result = await extract_code_from_response(output, file_path)
                    
                    logger.info(f"📊 Code extractor found {extraction_result.num_files} file(s)")
                    
                    # Create each extracted file
                    write_tool = WriteFileTool()
                    created_files = []
                    
                    for extracted_file in extraction_result.files:
                        try:
                            await write_tool.execute(
                                extracted_file.file_path,
                                extracted_file.content
                            )
                            created_files.append(extracted_file.file_path)
                            logger.info(
                                f"✅ Created {extracted_file.file_path} "
                                f"({len(extracted_file.content)} bytes, {extracted_file.file_type})"
                            )
                        except Exception as e:
                            logger.error(f"❌ Failed to write {extracted_file.file_path}: {e}")
                    
                    if created_files:
                        files_summary = ", ".join(created_files)
                        return f"Created {len(created_files)} file(s): {files_summary}"
                    else:
                        return f"Failed to create any files from extraction"
                        
                except Exception as e:
                    logger.error(f"❌ Code extraction failed: {e}")
                    return f"Code extraction failed: {str(e)}"

                    
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


async def delegate_task(user_request: str) -> DelegationResult:
    """Main entry point for task delegation."""
    """Main entry point for task delegation.
    
    This is the main entry point for task delegation. The coordinator
    will analyze the request and route it to the right agents.
    
    Args:
        user_request: User's request
        
    Returns:
        DelegationResult with outcomes
        
    Example:
        >>> result = await delegate_task(
        ...     "Analyze the config system and update temperature to 0.5"
        ... )
        >>> print(result.task_summary)
        "Analyzed configuration, then updated default_temperature to 0.5"
    """
    print(f"🔵 ENTERED delegate_task")
    logger.info(f"🎯 COORDINATOR invoked with request: {user_request[:100]}...")
    
    print(f"🔵 Getting coordinator agent...")
    coordinator = get_coordinator_agent()
    print(f"✅ Got coordinator agent")
    
    logger.info(f"Delegating task: {user_request}")
    
    print(f"🔵 Running coordinator with request...")
    result = await coordinator.run(user_request)
    print(f"✅ Coordinator returned")
    
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
