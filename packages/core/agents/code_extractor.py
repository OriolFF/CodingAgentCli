"""Code Extractor Micro-Agent

Intelligently extracts clean, executable code from LLM responses.
Handles single and multi-file scenarios.
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pathlib import Path


# Pydantic models for structured output
class ExtractedFile(BaseModel):
    """Represents a single extracted file."""
    file_path: str = Field(description="Path where the file should be created")
    content: str = Field(description="Clean executable code content")
    file_type: str = Field(description="File extension: html, css, js, python, etc.")


class ExtractionResult(BaseModel):
    """Result of code extraction containing one or more files."""
    files: list[ExtractedFile] = Field(description="List of extracted files")
    num_files: int = Field(description="Number of files extracted")
    explanation: Optional[str] = Field(default=None, description="Brief explanation of what was extracted")


# Singleton agent instance
_code_extractor_agent: Optional[Agent] = None


def _create_code_extractor_agent() -> Agent:
    """Create the code extractor agent."""
    from ..config import get_config
    
    config = get_config()
    model = config.get_agent_model("code_extractor")
    temperature = config.get_agent_temperature("code_extractor")
    
    agent = Agent(
        model,
        system_prompt="""You are a code extraction specialist. Extract clean,  executable code from LLM responses.

TASK: Analyze input and extract ALL code files.

MULTI-FILE DETECTION:
- Detect if response contains multiple files (HTML + CSS + JS)
- Look for <link href="..."> or <script src="..."> references
- Use base directory for related files

EXTRACTION RULES:
1. Remove explanatory text, prose, commentary
2. Remove markdown fences (```)
3. Remove JSON wrappers
4. Extract ONLY executable code

OUTPUT FORMAT (JSON):
```json
{
  "files": [
    {
      "file_path": "tests/output/index.html",
      "content": "<!DOCTYPE html>...",
      "file_type": "html"
    }
  ],
  "num_files": 1
}
```

EXAMPLES:
- Input with explanation + HTML → 1 file (clean HTML)
- HTML with <link href="styles.css"> + CSS block → 2 files
- Full web app → 3 files (index.html, styles.css, app.js)

Return ONLY the JSON object, no other text.""",
        retries=1,
    )
    
    return agent


def get_code_extractor_agent() -> Agent:
    """Get or create the singleton code extractor agent."""
    global _code_extractor_agent
    if _code_extractor_agent is None:
        _code_extractor_agent = _create_code_extractor_agent()
    return _code_extractor_agent


async def extract_code_from_response(
    response_text: str,
    requested_file_path: str
) -> ExtractionResult:
    """Extract clean code from LLM response.
    
    Args:
        response_text: Raw LLM response
        requested_file_path: Requested file path (e.g., tests/output/app.html)
        
    Returns:
        ExtractionResult with list of extracted files
    """
    from ..utils.logger import get_logger
    import json
    import re
    
    logger = get_logger(__name__)
    
    agent = get_code_extractor_agent()
    
    # Create context
    base_dir = str(Path(requested_file_path).parent)
    file_extension = Path(requested_file_path).suffix
    
    prompt = f"""Extract code from this response.

Requested file: {requested_file_path}
Base directory: {base_dir}

Response to extract:
{response_text}

Return JSON with extracted files."""
    
    logger.info(f"🔍 Starting intelligent code extraction...")
    try:
        result = await agent.run(prompt)
        output = result.output  # Extract string from AgentRunResult (use .output not .data)
        logger.info(f"📄 Got response from extraction agent ({len(output)} chars)")
        
        # Parse JSON from output
        json_match = re.search(r'\{.*\}', output, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            files = [
                ExtractedFile(**f) for f in data.get('files', [])
            ]
            extraction_result = ExtractionResult(
                files=files,
                num_files=len(files)
            )
            logger.info(f"✅ Extracted {len(files)} file(s)")
            return extraction_result
        else:
            logger.warning("No JSON found, using fallback")
            raise ValueError("No JSON in response")
            
    except Exception as e:
        logger.error(f"❌ Extraction failed: {e}, using fallback")
        # Fallback: return original as single file
        return ExtractionResult(
            files=[ExtractedFile(
                file_path=requested_file_path,
                content=response_text,
                file_type=file_extension.lstrip('.')
            )],
            num_files=1
        )
