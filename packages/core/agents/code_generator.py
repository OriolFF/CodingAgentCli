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
    """Create the code generator agent in TEXT-ONLY mode.
    
    This agent does NOT use tools to maximize compatibility with all models.
    Instead, it generates clean code as text, which is then extracted by the
    code_extractor agent.
    
    Returns:
        Configured agent
    """
    from ..config import get_config
    
    config = get_config()
    
    model_string = config.get_model_instance("code_generator")
    logger.info(f"Initializing code_generator agent (TEXT-ONLY mode) with model: {model_string}")
    
    # CRITICAL FIX: For Ollama models, use pydanticai-ollama package to pass options
    # This allows us to set num_predict=-1 for unlimited token generation
    if model_string.startswith("ollama:"):
        from pydanticai_ollama.models.ollama import OllamaModel, OllamaModelSettings
        from ..config.model_configuration import get_model_config
        
        model_name = model_string.split(":", 1)[1]
        
        # Get model-specific configuration from centralized config
        model_config = get_model_config(model_name)
        
        logger.info(f"📋 Model config for {model_name}:")
        logger.info(f"   - Context: {model_config.num_ctx:,} tokens")
        logger.info(f"   - Temperature: {model_config.temperature}")
        logger.info(f"   - Note: {model_config.description}")
        
        # Apply model-specific settings
        settings = OllamaModelSettings(
            num_predict=model_config.num_predict,
            num_ctx=model_config.num_ctx,
            temperature=model_config.temperature,
        )
        
        model_instance = OllamaModel(
            model_name=model_name,
            settings=settings,
        )
        logger.info(f"✅ Using OllamaModel with settings from model_configuration.py")
    else:
        # For non-Ollama models, use string identifier
        model_instance = model_string
        logger.info(f"Using model: {model_instance}")
    
    # CRITICAL: output_type=str ensures TEXT-ONLY mode
    # This prevents PydanticAI from trying to use structured output
    agent = Agent(
        model_instance,
        output_type=str,  # ← EXPLICIT TEXT-ONLY MODE
        system_prompt="""You are an expert code generator. Generate complete, production-ready code.

**CRITICAL RULES**:
- Output ONLY executable code, nothing else
- No markdown fences (```)
- No explanations, commentary, or prose
- No JSON metadata or wrapper syntax
- Start directly with code (imports, DOCTYPE, etc.)

**OUTPUT FORMAT**:
- For Python: Start with imports or code statements
- For HTML: Start with <!DOCTYPE html>
- For CSS: Start with selectors or @imports
- For JavaScript: Start with function declarations or code
- For any language: Output complete, valid, executable code

**QUALITY STANDARDS**:
- Generate COMPLETE implementations, not skeletons
- Include ALL necessary code, no placeholders
- No comments like "// rest of code..." or "// TODO"
- Fully functional, ready to run

Remember: Output ONLY code. Complete implementations. No explanations.""",
        retries=2,
    )
    
    # No tools! Text-only mode for universal compatibility
    
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
