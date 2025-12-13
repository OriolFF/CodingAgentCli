"""Code Generator Agent for generating code content.

This specialized agent is designed to generate high-quality code
in any programming language without writing files.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from typing import Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CodeGenerationResult(BaseModel):
    """Result from code generation operations."""
    
    success: bool = Field(description="Whether generation succeeded")
    code: str = Field(description="Generated code content")
    language: str = Field(description="Programming language used")
    description: str = Field(description="What was generated")


# Lazy initialization
_code_generator_agent: Optional[Agent] = None


def get_code_generator_agent() -> Agent:
    """Get or create the code generator agent.
    
    Returns:
        The code generator agent
    """
    global _code_generator_agent
    if _code_generator_agent is None:
        _code_generator_agent = _create_code_generator_agent()
    return _code_generator_agent


def _create_code_generator_agent() -> Agent:
    """Create the code generator agent.
    
    Returns:
        Configured agent
    """
    from ..config import get_config
    config = get_config()
    
    model_instance = config.get_model_instance("code_generator")
    logger.info(f"Initializing code_generator agent with model: {model_instance}")
    
    agent = Agent(
        model_instance,
        system_prompt="""You are a code generator. Respond ONLY with clean, executable code.

**CRITICAL RULES**:
- No markdown fences (```)
- No explanations or commentary
- No JSON metadata or tool call syntax
- No prose, headers, or wrappers
- Output raw code that can be executed/compiled directly

**OUTPUT FORMAT**:
- For Python: Start with imports or code statements
- For HTML: Start with <!DOCTYPE html>
- For CSS: Start with selectors or @imports
- For JavaScript: Start with function declarations or imports
- For Kotlin/Java: Start with package/imports
- For any language: Output complete, valid, compilable/executable code

**EXAMPLES**:

Request: "Python function to reverse string"
Response:
def reverse_string(s: str) -> str:
    return s[::-1]

Request: "HTML landing page"
Response:
<!DOCTYPE html>
<html>
<head><title>Page</title></head>
<body><h1>Hello</h1></body>
</html>

Request: "CSS with Material 3 colors"
Response:
:root {
  --md-primary: #6750A4;
  --md-surface: #FFFBFE;
}

Remember: ONLY code. No other text.""",
        retries=2,
    )
    
    # Import file writing tool
    from ..tools.file_operations import WriteFileTool
    
    write_tool = WriteFileTool()
    
    @agent.tool
    async def create_new_file(
        ctx: RunContext[None],
        file_path: str,
        content: str,
        description: str = "Generated file"
    ) -> str:
        """Create a new file with generated code.
        
        Args:
            file_path: Path where to create the file
            content: Complete file content
            description: Brief description of what the file contains
            
        Returns:
            Confirmation message
        """
        try:
            result = write_tool.execute(file_path, content)
            logger.info(f"Code generator created file: {file_path} ({len(content)} bytes)")
            return f"Successfully created {file_path} with {len(content)} characters"
        except Exception as e:
            logger.error(f"Failed to create file {file_path}: {e}")
            return f"Failed to create {file_path}: {str(e)}"
    
    return agent


async def generate_code(
    description: str,
    language: str = "python",
    style_guide: Optional[str] = None
) -> CodeGenerationResult:
    """Generate code based on description.
    
    Args:
        description: What code to generate
        language: Programming language (python, html, javascript, etc.)
        style_guide: Optional style guide to follow (e.g., "Material 3", "PEP 8")
        
    Returns:
        CodeGenerationResult with generated code
    """
    agent = get_code_generator_agent()
    
    prompt = f"Generate {language} code: {description}"
    if style_guide:
        prompt += f"\n\nFollow {style_guide} guidelines and design patterns."
    
    logger.info(f"Generating {language} code: {description[:100]}...")
    
    result = await agent.run(prompt)
    code = result.output if hasattr(result, 'output') else str(result.data)
    
    logger.info(f"Code generated: {len(code)} characters")
    
    return CodeGenerationResult(
        success=True,
        code=code,
        language=language,
        description=description
    )
