"""Documentation Agent for generating documentation.

This specialized agent helps create and maintain project documentation
including README files, API docs, and docstrings.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from typing import List, Optional
from ..tools.file_operations import ReadFileTool, WriteFileTool
from ..tools.search import GlobSearchTool, ListDirectoryTool
from ..utils.logger import get_logger

logger = get_logger(__name__)


class DocumentationResult(BaseModel):
    """Result from documentation generation."""
    
    success: bool = Field(description="Whether operation succeeded")
    content: str = Field(description="Generated documentation")
    files_updated: List[str] = Field(
        description="Files that were updated",
        default_factory=list
    )


# Lazy initialization
_documentation_agent: Optional[Agent] = None


def get_documentation_agent() -> Agent:
    """Get or create the documentation agent.
    
    Returns:
        The documentation agent
    """
    global _documentation_agent
    if _documentation_agent is None:
        _documentation_agent = _create_documentation_agent()
    return _documentation_agent


def _create_documentation_agent() -> Agent:
    """Create the documentation agent with tools.
    
    Returns:
        Configured agent
    """
    agent = Agent(
        "ollama:mistral",
        system_prompt="""You are an expert technical writer specializing in software documentation.

Your role is to:
1. Generate clear, comprehensive documentation
2. Write well-structured README files
3. Create API documentation
4. Add helpful docstrings to code
5. Maintain documentation consistency

When writing documentation:
- Use clear, simple language
- Include code examples where helpful
- Follow documentation best practices
- Use proper markdown formatting
- Be comprehensive but concise

Focus on helping users understand and use the code effectively.""",
        retries=1,
    )
    
    @agent.tool
    async def analyze_project_structure(
        ctx: RunContext[None],
        directory: str = "."
    ) -> str:
        """Analyze project structure for documentation.
        
        Args:
            ctx: Runtime context
            directory: Project directory
            
        Returns:
            Project structure overview
        """
        tool = ListDirectoryTool()
        result = await tool.execute(
            directory=directory,
            show_hidden=False,
            max_depth=3
        )
        
        if result.success:
            return f"Project structure:\n{result.output}"
        else:
            return f"Error analyzing structure: {result.error}"
    
    @agent.tool
    async def read_code_for_docs(
        ctx: RunContext[None],
        file_path: str
    ) -> str:
        """Read code to document.
        
        Args:
            ctx: Runtime context
            file_path: Path to code file
            
        Returns:
            Code contents
        """
        tool = ReadFileTool()
        result = await tool.execute(file_path=file_path)
        
        if result.success:
            return f"Code to document:\n{result.output}"
        else:
            return f"Error reading code: {result.error}"
    
    @agent.tool
    async def write_documentation(
        ctx: RunContext[None],
        doc_path: str,
        content: str
    ) -> str:
        """Write documentation to file.
        
        Args:
            ctx: Runtime context
            doc_path: Path for documentation file
            content: Documentation content
            
        Returns:
            Confirmation message
        """
        tool = WriteFileTool()
        result = await tool.execute(
            file_path=doc_path,
            content=content
        )
        
        if result.success:
            logger.info(f"Created documentation: {doc_path}")
            return f"Documentation written to: {doc_path}"
        else:
            return f"Error writing documentation: {result.error}"
    
    @agent.tool
    async def find_python_modules(
        ctx: RunContext[None],
        directory: str = "packages"
    ) -> str:
        """Find Python modules to document.
        
        Args:
            ctx: Runtime context
            directory: Directory to search
            
        Returns:
            List of Python files
        """
        tool = GlobSearchTool()
        result = await tool.execute(
            pattern="*.py",
            directory=directory,
            recursive=True
        )
        
        if result.success:
            return f"Python modules:\n{result.output}"
        else:
            return f"Error finding modules: {result.error}"
    
    return agent


async def generate_readme(
    project_dir: str = ".",
    output_file: str = "README.md"
) -> DocumentationResult:
    """Generate a README file for the project.
    
    Args:
        project_dir: Project directory
        output_file: Path for README file
        
    Returns:
        DocumentationResult with generated README
    """
    agent = get_documentation_agent()
    
    prompt = f"""Generate a comprehensive README.md for this project.

Please:
1. Analyze the project structure in '{project_dir}'
2. Identify key components and their purposes
3. Create a well-structured README with:
   - Project title and description
   - Features
   - Installation instructions
   - Usage examples
   - Project structure
   - Contributing guidelines

Write the README to: {output_file}

Make it clear, professional, and helpful for new users."""
    
    result = await agent.run(prompt)
    output = result.output if hasattr(result, 'output') else str(result.data)
    
    return DocumentationResult(
        success=True,
        content=output,
        files_updated=[output_file]
    )


async def generate_api_docs(
    module_path: str,
    output_dir: str = "docs/api"
) -> DocumentationResult:
    """Generate API documentation for a module.
    
    Args:
        module_path: Path to module
        output_dir: Directory for API docs
        
    Returns:
        DocumentationResult with generated docs
    """
    agent = get_documentation_agent()
    
    prompt = f"""Generate API documentation for the module: {module_path}

Please:
1. Read and analyze the code
2. Document all public classes and functions
3. Include parameter descriptions
4. Add usage examples
5. Write to {output_dir}

Create clear, comprehensive API documentation."""
    
    result = await agent.run(prompt)
    output = result.output if hasattr(result, 'output') else str(result.data)
    
    return DocumentationResult(
        success=True,
        content=output,
        files_updated=[]
    )
