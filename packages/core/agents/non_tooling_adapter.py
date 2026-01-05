"""Non-Tooling Model Adapter

Wrapper for models that don't support tool calling (like Codestral, CodeLlama).
Converts text-only responses into executable file operations.
"""

import re
from typing import Optional, Dict, Any
from pathlib import Path
from pydantic_ai import Agent
from ..utils.logger import get_logger

logger = get_logger(__name__)


class NonToolingAdapter:
    """Adapter for models without tool support.
    
    Strategy:
    1. Send prompt to non-tooling model (text-only completion)
    2. Parse response text to extract code and file intentions
    3. Use code extractor to clean and structure the code
    4. Execute file operations manually via tools
    """
    
    def __init__(self, model: str, temperature: float = 0.1):
        """Initialize adapter.
        
        Args:
            model: Model identifier (e.g., 'ollama:codestral')
            temperature: Temperature for generation
        """
        self.model = model
        self.temperature = temperature
        self._agent: Optional[Agent] = None
        
    def _get_agent(self) -> Agent:
        """Get or create the text-only agent."""
        if self._agent is None:
            self._agent = Agent(
                self.model,
                system_prompt="""You are a code generation specialist.

IMPORTANT: You CANNOT use tools or functions. Generate ONLY text responses.

When asked to create files:
1. Generate the complete, working code
2. Use clear markers to indicate file boundaries
3. Include file paths in your response

FORMAT for single file:
```
FILE: path/to/file.ext
<complete code here>
```

FORMAT for multiple files:
```
FILE: path/to/index.html
<html code>

FILE: path/to/styles.css
<css code>

FILE: path/to/app.js
<javascript code>
```

RULES:
- Generate COMPLETE code (no placeholders like "// rest of code...")
- Include all necessary imports, functions, classes
- Use proper syntax and formatting
- Be explicit about file paths
- No explanations - ONLY code

Remember: Just generate text. No tools. No functions. Pure code generation.""",
                retries=1,
            )
        return self._agent
    
    async def generate_code(self, prompt: str) -> str:
        """Generate code using text-only model.
        
        Args:
            prompt: User prompt/instruction
            
        Returns:
            Raw text response from model
        """
        agent = self._get_agent()
        logger.info(f"🤖 Using non-tooling adapter with {self.model}")
        
        result = await agent.run(prompt)
        response_text = result.output  # Text-only response
        
        logger.info(f"📄 Generated {len(response_text)} chars of text")
        return response_text
    
    def parse_file_markers(self, text: str) -> Dict[str, str]:
        """Parse FILE: markers from text response.
        
        Args:
            text: Raw text with FILE: markers
            
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
            
            # Remove markdown code fences if present
            content = re.sub(r'^```\w*\n?', '', content)
            content = re.sub(r'\n?```$', '', content)
            
            files[file_path] = content
            logger.info(f"📝 Parsed file marker: {file_path} ({len(content)} chars)")
        
        return files
    
    async def extract_and_parse_code(
        self, 
        response_text: str, 
        default_output_path: str
    ) -> Dict[str, str]:
        """Extract code from response using code extractor.
        
        Args:
            response_text: Raw model response
            default_output_path: Default output path if not specified
            
        Returns:
            Dict mapping file paths to clean code content
        """
        from .code_extractor import extract_code_from_response
        
        logger.info("🔍 Extracting code using code extractor agent...")
        
        # Try to parse FILE: markers first
        marked_files = self.parse_file_markers(response_text)
        
        if marked_files:
            logger.info(f"✅ Found {len(marked_files)} files with markers")
            return marked_files
        
        # Fallback to code extractor
        logger.info("No markers found, using intelligent code extractor...")
        extraction_result = await extract_code_from_response(
            response_text=response_text,
            requested_file_path=default_output_path
        )
        
        files = {}
        for extracted_file in extraction_result.files:
            files[extracted_file.file_path] = extracted_file.content
            logger.info(f"📝 Extracted: {extracted_file.file_path} ({len(extracted_file.content)} chars)")
        
        return files
    
    async def execute_file_operations(self, files: Dict[str, str]) -> Dict[str, Any]:
        """Execute file creation for parsed files.
        
        Args:
            files: Dict mapping file paths to content
            
        Returns:
            Dict with execution results
        """
        from ..tools.file_operations import WriteFileTool
        
        tool = WriteFileTool()
        results = {
            'files_created': [],
            'files_failed': [],
            'total_bytes': 0
        }
        
        for file_path, content in files.items():
            logger.info(f"💾 Creating file: {file_path}")
            
            # Ensure parent directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Execute write
            result = await tool.execute(file_path=file_path, content=content)
            
            if result.success:
                results['files_created'].append(file_path)
                results['total_bytes'] += len(content)
                logger.info(f"✅ Created: {file_path} ({len(content)} bytes)")
            else:
                results['files_failed'].append({
                    'path': file_path,
                    'error': result.error
                })
                logger.error(f"❌ Failed: {file_path} - {result.error}")
        
        return results
    
    async def run(self, prompt: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """Complete workflow: generate → parse → execute.
        
        Args:
            prompt: User instruction
            output_path: Default output path
            
        Returns:
            Dict with generation results and file operations
        """
        logger.info("="*60)
        logger.info("🔧 NON-TOOLING ADAPTER WORKFLOW")
        logger.info(f"Model: {self.model}")
        logger.info("="*60)
        
        # Step 1: Generate code (text-only)
        logger.info("\n📝 Step 1: Generating code...")
        response_text = await self.generate_code(prompt)
        
        # Step 2: Parse/extract code
        logger.info("\n🔍 Step 2: Extracting code...")
        if output_path is None:
            output_path = "output/generated_code.html"
        
        files = await self.extract_and_parse_code(response_text, output_path)
        
        # Step 3: Execute file operations
        logger.info("\n💾 Step 3: Creating files...")
        execution_results = await self.execute_file_operations(files)
        
        # Summary
        logger.info("\n" + "="*60)
        logger.info("📊 SUMMARY")
        logger.info(f"✅ Files created: {len(execution_results['files_created'])}")
        logger.info(f"❌ Files failed: {len(execution_results['files_failed'])}")
        logger.info(f"📦 Total bytes: {execution_results['total_bytes']}")
        logger.info("="*60)
        
        return {
            'success': len(execution_results['files_created']) > 0,
            'response_text': response_text,
            'files': files,
            'execution': execution_results
        }


async def create_with_non_tooling_model(
    model: str,
    prompt: str,
    output_path: Optional[str] = None,
    temperature: float = 0.1
) -> Dict[str, Any]:
    """Convenience function to use non-tooling models.
    
    Example:
        result = await create_with_non_tooling_model(
            model="ollama:codestral",
            prompt="Create a complete Tetris game in HTML",
            output_path="tests/output/codestral/tetris.html"
        )
    
    Args:
        model: Model identifier (e.g., 'ollama:codestral')
        prompt: User instruction
        output_path: Where to save the output
        temperature: Generation temperature
        
    Returns:
        Dict with generation results
    """
    adapter = NonToolingAdapter(model=model, temperature=temperature)
    return await adapter.run(prompt=prompt, output_path=output_path)
