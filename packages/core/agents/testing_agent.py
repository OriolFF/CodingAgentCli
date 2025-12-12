"""Testing Agent for test generation and execution.

This specialized agent helps generate test cases, run tests,
and analyze test results.
"""

from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from typing import List, Optional
from ..tools.shell import ShellExecutionTool
from ..tools.file_operations import ReadFileTool, WriteFileTool
from ..tools.search import GrepSearchTool
from ..utils.logger import get_logger

logger = get_logger(__name__)


class TestResult(BaseModel):
    """Result from testing operations."""
    
    success: bool = Field(description="Whether operation succeeded")
    output: str = Field(description="Test output or generated tests")
    tests_passed: int = Field(description="Number of tests passed", default=0)
    tests_failed: int = Field(description="Number of tests failed", default=0)
    coverage: Optional[float] = Field(description="Test coverage percentage", default=None)


# Lazy initialization
_testing_agent: Optional[Agent] = None


def get_testing_agent() -> Agent:
    """Get or create the testing agent.
    
    Returns:
        The testing agent
    """
    global _testing_agent
    if _testing_agent is None:
        _testing_agent = _create_testing_agent()
    return _testing_agent


def _create_testing_agent() -> Agent:
    """Create the testing agent with tools.
    
    Returns:
        Configured agent
    """
    from ..config import get_config
    config = get_config()
    
    model_instance = config.get_model_instance("testing")
    logger.info(f"Initializing testing agent with model: {model_instance}")
    
    agent = Agent(
        model_instance,
        system_prompt="""You are an expert testing engineer specializing in Python testing.

Your role is to:
1. Generate comprehensive test cases using pytest
2. Run tests and analyze results
3. Calculate test coverage
4. Suggest improvements to test suites
5. Write clear, maintainable test code

When generating tests:
- Use pytest conventions
- Include docstrings
- Test edge cases
- Use appropriate fixtures
- Follow AAA pattern (Arrange, Act, Assert)

Be thorough but keep tests simple and readable.""",
        retries=1,
    )
    
    @agent.tool
    async def read_code_to_test(
        ctx: RunContext[None],
        file_path: str
    ) -> str:
        """Read code that needs testing.
        
        Args:
            ctx: Runtime context
            file_path: Path to code file
            
        Returns:
            File contents
        """
        tool = ReadFileTool()
        result = await tool.execute(file_path=file_path)
        
        if result.success:
            return f"Code to test:\n{result.output}"
        else:
            return f"Error reading file: {result.error}"
    
    @agent.tool
    async def write_test_file(
        ctx: RunContext[None],
        test_path: str,
        test_content: str
    ) -> str:
        """Write generated tests to file.
        
        Args:
            ctx: Runtime context
            test_path: Path for test file
            test_content: Test code content
            
        Returns:
            Confirmation message
        """
        tool = WriteFileTool()
        result = await tool.execute(
            file_path=test_path,
            content=test_content
        )
        
        if result.success:
            logger.info(f"Created test file: {test_path}")
            return f"Test file created: {test_path}"
        else:
            return f"Error creating test file: {result.error}"
    
    @agent.tool
    async def run_tests(
        ctx: RunContext[None],
        test_path: Optional[str] = None,
        coverage: bool = False
    ) -> str:
        """Run pytest tests.
        
        Args:
            ctx: Runtime context
            test_path: Optional specific test file/directory
            coverage: Whether to calculate coverage
            
        Returns:
            Test results
        """
        tool = ShellExecutionTool(allow_dangerous=True)
        
        # Build pytest command
        cmd = "uv run pytest"
        if test_path:
            cmd += f" {test_path}"
        if coverage:
            cmd += " --cov=packages --cov-report=term"
        cmd += " -v"
        
        result = await tool.execute(command=cmd)
        
        if result.success:
            return f"Test results:\n{result.output}"
        else:
            return f"Tests failed or had errors:\n{result.output}"
    
    @agent.tool
    async def find_existing_tests(
        ctx: RunContext[None],
        pattern: str = "test_"
    ) -> str:
        """Find existing test files.
        
        Args:
            ctx: Runtime context
            pattern: Pattern to search for
            
        Returns:
            List of test files
        """
        tool = GrepSearchTool()
        result = await tool.execute(
            pattern=pattern,
            directory="tests",
            file_pattern="*.py"
        )
        
        if result.success:
            return f"Existing tests:\n{result.output}"
        else:
            return f"No tests found or error: {result.error}"
    
    return agent


async def generate_tests(
    file_path: str,
    test_file: Optional[str] = None
) -> TestResult:
    """Generate tests for a given file.
    
    Args:
        file_path: Path to file to test
        test_file: Optional path for generated test file
        
    Returns:
        TestResult with generated tests
    """
    agent = get_testing_agent()
    
    prompt = f"""Generate comprehensive pytest tests for the code in: {file_path}

Please:
1. Read the code to understand what needs testing
2. Generate appropriate test cases covering main functionality
3. Include edge cases and error conditions
4. Write tests to: {test_file or f'tests/test_{file_path.split("/")[-1]}'}

Make tests clear, well-documented, and following pytest best practices."""
    
    result = await agent.run(prompt)
    output = result.output if hasattr(result, 'output') else str(result.data)
    
    return TestResult(
        success=True,
        output=output,
        tests_passed=0,
        tests_failed=0
    )


async def run_test_suite(
    test_path: Optional[str] = None,
    with_coverage: bool = False
) -> TestResult:
    """Run the test suite.
    
    Args:
        test_path: Optional specific test to run
        with_coverage: Whether to calculate coverage
        
    Returns:
        TestResult with test execution results
    """
    agent = get_testing_agent()
    
    prompt = f"Run tests"
    if test_path:
        prompt += f" for {test_path}"
    if with_coverage:
        prompt += " with coverage analysis"
    
    result = await agent.run(prompt)
    output = result.output if hasattr(result, 'output') else str(result.data)
    
    # Parse test results (simple heuristic)
    passed = output.count(" PASSED")
    failed = output.count(" FAILED")
    
    return TestResult(
        success=failed == 0,
        output=output,
        tests_passed=passed,
        tests_failed=failed
    )
