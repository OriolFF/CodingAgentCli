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
        print(f"\n{'='*80}")
        print(f"🎯 COORDINATOR → CODE_GENERATOR")
        print(f"{'='*80}")
        print(f"Task: Generate {language} code")
        print(f"Description: {description}")
        print(f"Target file: {file_path}")
        print(f"{'='*80}\n")
        logger.info(f"🎯 COORDINATOR delegating to CODE_GENERATOR: {description} ({language}) -> {file_path}")
        
        code_gen_agent = get_code_generator_agent()
        
        # Construct prompt
        prompt = f"Create {file_path} with {language} code: {description}"
        
        try:
            print(f"🔄 CODE_GENERATOR agent started...")
            result = await code_gen_agent.run(prompt)
            output = result.output if hasattr(result, 'output') else str(result.data)
            print(f"✅ CODE_GENERATOR agent finished (response length: {len(output)} chars)")
            
            # Code generator is TEXT-ONLY now (no tools), always use code extractor
            logger.info(f"🔍 CODE EXTRACTOR invoked to parse response")
            
            # Log the FULL OUTPUT from the model
            print(f"\n{'='*80}")
            print(f"📋 CODE GENERATOR RESPONSE (length: {len(output)} chars)")
            print(f"{'='*80}")
            print(output[:2000])  # First 2000 chars
            print(f"\n{'='*80}")
            print(f"📋 END OF RESPONSE")
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
                    # NEW: Quality validation and auto-refactoring
                    logger.info(f"📊 Validating quality of {len(created_files)} generated file(s)...")
                    
                    print(f"\n{'='*80}")
                    print(f"🔍 QUALITY VALIDATION")
                    print(f"{'='*80}")
                    
                    from ..utils.code_quality import validate_file_quality
                    from .refactoring_agent import refactor_file
                    
                    files_needing_refactor = []
                    validation_results = {}
                    
                    for file_path in created_files:
                        print(f"\n📋 Validating: {file_path}")
                        quality_report = await validate_file_quality(file_path)
                        validation_results[file_path] = quality_report
                        
                        if quality_report.has_critical_issues:
                            critical_issues = [i for i in quality_report.issues if i.severity == "critical"]
                            print(f"⚠️  Found {len(critical_issues)} critical issue(s):")
                            for issue in critical_issues:
                                print(f"   - {issue.description}")
                            files_needing_refactor.append(file_path)
                        elif quality_report.has_issues:
                            print(f"ℹ️  Has {len(quality_report.issues)} minor issue(s), skipping refactor")
                        else:
                            print(f"✅ No issues found")
                    
                    # Apply refactoring to fix critical issues
                    refactored_files = []
                    if files_needing_refactor:
                        print(f"\n{'='*80}")
                        print(f"🔧 AUTO-REFACTORING {len(files_needing_refactor)} FILE(S)")
                        print(f"{'='*80}\n")
                        
                        for file_path in files_needing_refactor:
                            print(f"🔧 Refactoring: {file_path}")
                            try:
                                refactor_result = await refactor_file(
                                    file_path,
                                    focus="Fix syntax errors, complete incomplete code, resolve undefined variables, and fix structural issues"
                                )
                                
                                if refactor_result.success:
                                    refactored_files.append(file_path)
                                    print(f"✅ Successfully refactored {file_path}")
                                    logger.info(f"✅ Refactored {file_path}")
                                else:
                                    print(f"❌ Refactoring failed for {file_path}")
                                    logger.error(f"❌ Refactoring failed for {file_path}")
                                    
                            except Exception as e:
                                print(f"❌ Refactoring error: {e}")
                                logger.error(f"❌ Refactoring error for {file_path}: {e}")
                        
                        print(f"\n{'='*80}")
                        print(f"📊 REFACTORING COMPLETE")
                        print(f"{'='*80}\n")
                    
                    # Return summary
                    files_summary = ", ".join(created_files)
                    if refactored_files:
                        return (
                            f"Created {len(created_files)} file(s): {files_summary}. "
                            f"Auto-refactored {len(refactored_files)} file(s) to fix quality issues."
                        )
                    else:
                        result_msg = f"Created {len(created_files)} file(s): {files_summary}"
                    
                    print(f"\n{'='*80}")
                    print(f"↩️  CODE_GENERATOR → COORDINATOR")
                    print(f"{'='*80}")
                    print(f"Result: {result_msg}")
                    print(f"{'='*80}\n")
                    logger.info(f"↩️  CODE_GENERATOR returning to COORDINATOR: {result_msg}")
                    return result_msg
                else:
                    error_msg = f"Failed to create any files from extraction"
                    print(f"\n{'='*80}")
                    print(f"❌ CODE_GENERATOR → COORDINATOR (ERROR)")
                    print(f"{'='*80}")
                    print(f"Error: {error_msg}")
                    print(f"{'='*80}\n")
                    logger.error(f"❌ CODE_GENERATOR error: {error_msg}")
                    return error_msg
                    
            except Exception as e:
                logger.error(f"❌ Code extraction failed: {e}")
                print(f"\n{'='*80}")
                print(f"❌ CODE_GENERATOR → COORDINATOR (EXCEPTION)")
                print(f"{'='*80}")
                print(f"Exception: {str(e)}")
                print(f"{'='*80}\n")
                return f"Code extraction failed: {str(e)}"

                    
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            print(f"\n{'='*80}")
            print(f"❌ CODE_GENERATOR → COORDINATOR (FAILED)")
            print(f"{'='*80}")
            print(f"Error: {str(e)}")
            print(f"{'='*80}\n")
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
        print(f"\n{'='*80}")
        print(f"🎯 COORDINATOR → CODEBASE_INVESTIGATOR")
        print(f"{'='*80}")
        print(f"Task: Analyze codebase")
        print(f"Request: {request}")
        if focus:
            print(f"Focus: {focus}")
        print(f"{'='*80}\n")
        logger.info(f"🎯 COORDINATOR delegating to CODEBASE_INVESTIGATOR: {request}")
        
        codebase_agent = get_codebase_agent()
        
        prompt = f"Analyze: {request}"
        if focus:
            prompt += f"\nFocus on: {focus}"
        
        try:
            print(f"🔄 CODEBASE_INVESTIGATOR agent started...")
            result = await codebase_agent.run(prompt)
            # Handle text-only response
            output = result.output if hasattr(result, 'output') else str(result.data)
            print(f"✅ CODEBASE_INVESTIGATOR agent finished")
            
            result_msg = f"Code Analysis:\n{output}"
            print(f"\n{'='*80}")
            print(f"↩️  CODEBASE_INVESTIGATOR → COORDINATOR")
            print(f"{'='*80}")
            print(f"Analysis complete (length: {len(output)} chars)")
            print(f"{'='*80}\n")
            logger.info(f"↩️  CODEBASE_INVESTIGATOR returning to COORDINATOR")
            return result_msg
        except Exception as e:
            logger.error(f"Codebase analysis failed: {e}")
            print(f"\n{'='*80}")
            print(f"❌ CODEBASE_INVESTIGATOR → COORDINATOR (FAILED)")
            print(f"{'='*80}")
            print(f"Error: {str(e)}")
            print(f"{'='*80}\n")
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
        print(f"\n{'='*80}")
        print(f"🎯 COORDINATOR → FILE_EDITOR")
        print(f"{'='*80}")
        print(f"Task: Edit files")
        print(f"Instructions: {instructions}")
        if file_context:
            print(f"Context: {file_context}")
        if content:
            print(f"Pre-generated content: {len(content)} chars")
        print(f"{'='*80}\n")
        
        if content:
            logger.info(f"🎯 COORDINATOR delegating to FILE_EDITOR with pre-generated content ({len(content)} chars): {instructions}")
        else:
            logger.info(f"🎯 COORDINATOR delegating to FILE_EDITOR: {instructions}")
        
        file_editor_agent = get_file_editor_agent()
        
        prompt = f"Make these changes: {instructions}"
        if file_context:
            prompt += f"\nContext: {file_context}"
        if content:
            prompt += f"\n\nUSE THIS EXACT CONTENT (do not modify):\n{content}"
        
        try:
            # Force tool usage with tool_choice=required
            from pydantic_ai import ModelSettings
            print(f"🔄 FILE_EDITOR agent started...")
            result = await file_editor_agent.run(
                prompt,
                model_settings=ModelSettings(tool_choice='required')
            )
            # Handle text-only response
            output = result.output if hasattr(result, 'output') else str(result.data)
            print(f"✅ FILE_EDITOR agent finished")
            
            result_msg = f"File editor result:\n{output}"
            print(f"\n{'='*80}")
            print(f"↩️  FILE_EDITOR → COORDINATOR")
            print(f"{'='*80}")
            print(f"Edit complete")
            print(f"{'='*80}\n")
            logger.info(f"↩️  FILE_EDITOR returning to COORDINATOR")
            return result_msg
        except Exception as e:
            logger.error(f"File editing failed: {e}")
            print(f"\n{'='*80}")
            print(f"❌ FILE_EDITOR → COORDINATOR (FAILED)")
            print(f"{'='*80}")
            print(f"Error: {str(e)}")
            print(f"{'='*80}\n")
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
        print(f"\n{'='*80}")
        print(f"🎯 COORDINATOR → CODEBASE_INVESTIGATOR (search)")
        print(f"{'='*80}")
        print(f"Task: Search code")
        print(f"Query: {query}")
        print(f"Pattern: {file_pattern}")
        print(f"{'='*80}\n")
        logger.info(f"🎯 COORDINATOR delegating search to CODEBASE_INVESTIGATOR: {query}")
        
        # Use codebase agent's search capabilities
        codebase_agent = get_codebase_agent()
        
        prompt = f"Search for: {query} in files matching {file_pattern}"
        
        try:
            print(f"🔄 CODEBASE_INVESTIGATOR (search) agent started...")
            result = await codebase_agent.run(prompt)
            # Handle text-only response
            output = result.output if hasattr(result, 'output') else str(result.data)
            print(f"✅ CODEBASE_INVESTIGATOR (search) agent finished")
            
            result_msg = f"Search results:\n{output}"
            print(f"\n{'='*80}")
            print(f"↩️  CODEBASE_INVESTIGATOR (search) → COORDINATOR")
            print(f"{'='*80}")
            print(f"Search complete")
            print(f"{'='*80}\n")
            logger.info(f"↩️  CODEBASE_INVESTIGATOR (search) returning to COORDINATOR")
            return result_msg
        except Exception as e:
            logger.error(f"Code search failed: {e}")
            print(f"\n{'='*80}")
            print(f"❌ CODEBASE_INVESTIGATOR (search) → COORDINATOR (FAILED)")
            print(f"{'='*80}")
            print(f"Error: {str(e)}")
            print(f"{'='*80}\n")
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
    print(f"\n{'#'*80}")
    print(f"🚀 USER → COORDINATOR")
    print(f"{'#'*80}")
    print(f"Request: {user_request}")
    print(f"{'#'*80}\n")
    logger.info(f"🚀 USER request received by COORDINATOR: {user_request[:100]}...")
    
    coordinator = get_coordinator_agent()
    logger.info(f"COORDINATOR agent initialized")
    
    print(f"🔄 COORDINATOR agent analyzing request and routing to sub-agents...\n")
    result = await coordinator.run(user_request)
    print(f"\n✅ COORDINATOR agent finished processing\n")
    
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
    
    delegation_result = DelegationResult(
        success=success,
        result=output,
        agents_used=agents_used,
        task_summary=output[:200] + "..." if len(output) > 200 else output
    )
    
    print(f"\n{'#'*80}")
    print(f"✅ COORDINATOR → USER (FINAL RESULT)")
    print(f"{'#'*80}")
    print(f"Success: {success}")
    print(f"Agents used: {', '.join(agents_used) if agents_used else 'None detected'}")
    print(f"Result preview: {output[:200]}..." if len(output) > 200 else f"Result: {output}")
    print(f"{'#'*80}\n")
    logger.info(f"✅ COORDINATOR returning final result to USER (success={success})")
    
    return delegation_result
