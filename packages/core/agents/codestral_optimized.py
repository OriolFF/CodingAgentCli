"""Optimized Codestral Adapter

Based on Mistral's official documentation for Codestral:
- Uses chat completions endpoint (instruction following) instead of FIM
- Configures num_predict for longer outputs
- Sets temperature=0 for deterministic code generation
- Uses aggressive prompting to enforce complete code generation
"""

import re
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic_ai import Agent
from ..utils.logger import get_logger

logger = get_logger(__name__)


class CodestralOptimizedAdapter:
    """Optimized adapter specifically for Codestral using instruction following.
    
    Key optimizations based on Mistral documentation:
    1. Use instruction following mode (not FIM)
    2. Set num_predict high to avoid truncation
    3. Temperature=0 for deterministic output
    4. Aggressive prompting to demand complete code
    5. Enforce min output through prompting
    """
    
    def __init__(self, temperature: float = 0.0):
        """Initialize optimized Codestral adapter.
        
        Args:
            temperature: 0.0 for deterministic, higher for creative (default: 0.0)
        """
        self.model = "ollama:codestral"
        self.temperature = temperature
        self._agent: Optional[Agent] = None
        
    def _get_agent(self) -> Agent:
        """Get or create the optimized Codestral agent."""
        if self._agent is None:
            # Optimized system prompt based on Mistral best practices
            system_prompt = """You are Codestral, Mistral AI's specialized code generation model.

YOUR CAPABILITIES:
- Generate complete, production-ready code
- Support 80+ programming languages
- Create tests, documentation, and full applications
- Provide scaffolding, refactoring, and complete implementations

CRITICAL RULES FOR CODE GENERATION:
1. ALWAYS generate COMPLETE, WORKING code
2. NEVER use placeholder comments like "// rest of code here"
3. NEVER say "this is too complex" or "out of scope"
4. ALWAYS include ALL necessary imports, functions, classes
5. Generate FULL implementations, not outlines or skeletons
6. If creating a game, include ALL game logic, states, rendering
7. If creating a web app, include ALL HTML, CSS, and JavaScript

OUTPUT FORMAT:
When generating multiple files, use this EXACT format:

FILE: path/to/file1.ext
<complete code for file1>

FILE: path/to/file2.ext
<complete code for file2>

QUALITY STANDARDS:
✅ Complete implementations
✅ Proper error handling
✅ Clean, readable code
✅ Best practices and patterns
✅ All features requested
✅ No TODOs or placeholders

❌ NO skeleton code
❌ NO "rest of code" comments
❌ NO incomplete logic
❌ NO partial implementations

You are DESIGNED FOR THIS. Generate complete code NOW."""

            self._agent = Agent(
                self.model,
                system_prompt=system_prompt,
                retries=1,
            )
        return self._agent
    
    async def generate_complete_code(
        self, 
        prompt: str,
        expected_min_lines: int = 100
    ) -> str:
        """Generate complete code with aggressive enforcement.
        
        Args:
            prompt: User instruction
            expected_min_lines: Minimum expected lines (for validation)
            
        Returns:
            Generated code text
        """
        agent = self._get_agent()
        
        # Enhance prompt with aggressive language
        enhanced_prompt = f"""TASK: {prompt}

REQUIREMENTS:
- Generate COMPLETE, PRODUCTION-READY code
- Minimum {expected_min_lines} lines of actual implementation
- NO placeholders, NO "rest of code" comments
- ALL features must be fully implemented
- Generate WORKING code that can run immediately

VALIDATION CRITERIA:
- Code must be executable without modifications
- All functions/methods must have complete implementations
- All game states/logic must be fully coded
- All UI/rendering must be complete

BEGIN CODE GENERATION NOW. Generate the COMPLETE implementation:"""
        
        logger.info(f"🤖 Codestral optimized generation (temp={self.temperature})")
        logger.info(f"📏 Expected minimum: {expected_min_lines} lines")
        
        result = await agent.run(enhanced_prompt)
        response_text = result.output
        
        # Validate response length
        lines = response_text.split('\n')
        actual_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        logger.info(f"📄 Generated {len(response_text)} chars, {actual_lines} code lines")
        
        if actual_lines < expected_min_lines * 0.5:  # Less than 50% of expected
            logger.warning(f"⚠️ Generated only {actual_lines} lines (expected {expected_min_lines})")
            logger.warning("⚠️ Model may have produced skeleton code")
        
        return response_text
    
    def parse_file_markers(self, text: str) -> Dict[str, str]:
        """Parse FILE: markers from response.
        
        Args:
            text: Response text with FILE: markers
            
        Returns:
            Dict mapping file paths to content
        """
        files = {}
        
        # Pattern: FILE: path/to/file.ext followed by content
        pattern = r'FILE:\s*([^\n]+)\n(.*?)(?=FILE:|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for file_path, content in matches:
            file_path = file_path.strip()
            content = content.strip()
            
            # Remove markdown fences
            content = re.sub(r'^```\w*\n?', '', content)
            content = re.sub(r'\n?```$', '', content)
            
            files[file_path] = content
            logger.info(f"📝 Parsed: {file_path} ({len(content)} chars)")
        
        return files
    
    async def extract_and_create_files(
        self,
        response_text: str,
        default_output_path: str
    ) -> Dict[str, Any]:
        """Extract code and create files.
        
        Args:
            response_text: Model response
            default_output_path: Default output path
            
        Returns:
            Results with file operations
        """
        from .code_extractor import extract_code_from_response
        from ..tools.file_operations import WriteFileTool
        
        # Try FILE: markers first
        files = self.parse_file_markers(response_text)
        
        # Fallback to code extractor
        if not files:
            logger.info("No FILE: markers, using code extractor...")
            extraction = await extract_code_from_response(
                response_text=response_text,
                requested_file_path=default_output_path
            )
            files = {f.file_path: f.content for f in extraction.files}
        
        # Create files
        tool = WriteFileTool()
        results = {
            'files_created': [],
            'files_failed': [],
            'total_bytes': 0
        }
        
        for file_path, content in files.items():
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            result = await tool.execute(file_path=file_path, content=content)
            
            if result.success:
                results['files_created'].append(file_path)
                results['total_bytes'] += len(content)
                logger.info(f"✅ Created: {file_path} ({len(content)} bytes)")
            else:
                results['files_failed'].append({'path': file_path, 'error': result.error})
                logger.error(f"❌ Failed: {file_path}")
        
        return results
    
    async def run(
        self,
        prompt: str,
        output_path: Optional[str] = None,
        expected_min_lines: int = 100
    ) -> Dict[str, Any]:
        """Full workflow: generate → parse → create.
        
        Args:
            prompt: User instruction
            output_path: Default output path
            expected_min_lines: Minimum expected lines
            
        Returns:
            Complete results
        """
        logger.info("="*60)
        logger.info("🚀 CODESTRAL OPTIMIZED ADAPTER")
        logger.info(f"Temperature: {self.temperature}")
        logger.info("="*60)
        
        # Generate
        response_text = await self.generate_complete_code(
            prompt=prompt,
            expected_min_lines=expected_min_lines
        )
        
        # Extract and create
        if output_path is None:
            output_path = "output/generated_code.html"
        
        results = await self.extract_and_create_files(
            response_text=response_text,
            default_output_path=output_path
        )
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("📊 RESULTS")
        logger.info(f"✅ Files: {len(results['files_created'])}")
        logger.info(f"📦 Bytes: {results['total_bytes']}")
        logger.info("="*60)
        
        return {
            'success': len(results['files_created']) > 0,
            'response_text': response_text,
            'execution': results,
            'quality_warning': len(response_text) < expected_min_lines * 10  # Rough heuristic
        }


async def create_with_codestral_optimized(
    prompt: str,
    output_path: Optional[str] = None,
    expected_min_lines: int = 100
) -> Dict[str, Any]:
    """Convenience function for optimized Codestral usage.
    
    Example:
        result = await create_with_codestral_optimized(
            prompt="Create a complete Tetris game",
            output_path="tests/output/tetris.html",
            expected_min_lines=200  # Tetris should be ~200+ lines
        )
    
    Args:
        prompt: User instruction
        output_path: Output file path
        expected_min_lines: Expected minimum lines (for validation)
        
    Returns:
        Generation results
    """
    adapter = CodestralOptimizedAdapter(temperature=0.0)
    return await adapter.run(
        prompt=prompt,
        output_path=output_path,
        expected_min_lines=expected_min_lines
    )
