# Non-Tooling Model Adapter

## Overview

A wrapper system that enables models **without tool calling support** (like Codestral, CodeLlama) to work with our agent system by converting text-only responses into executable file operations.

## The Problem

Some excellent code generation models don't support tool/function calling:
- ✅ **Codestral** (22B, 80+ languages) - Great code quality, NO tool support
- ✅ **CodeLlama** (13B) - Specialized for code, NO tool support  
- ❌ **Qwen2.5-coder** (14B) - Good code, YES tool support ✓

Our agent system requires tool calling to create files, so models without it fail with:
```
Error: 400 - Does not support tools
```

## The Solution: Text Parsing Adapter

```
┌─────────────────────────────────────────────────┐
│  TRADITIONAL AGENT (Needs Tool Support)         │
├─────────────────────────────────────────────────┤
│  1. Prompt → Model                              │
│  2. Model calls create_file() tool             │
│  3. File created ✓                             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│  NON-TOOLING ADAPTER (Works Without Tools)      │
├─────────────────────────────────────────────────┤
│  1. Prompt → Model (text-only)                  │
│  2. Model returns text with code                │
│  3. Adapter parses FILE: markers OR             │
│     Uses code_extractor agent                   │
│  4. Adapter executes file writes manually ✓     │
└─────────────────────────────────────────────────┘
```

## Architecture

### Components

1. **NonToolingAdapter** (`packages/core/agents/non_tooling_adapter.py`)
   - Wraps text-only models
   - Manages generate → parse → execute workflow
   - Uses existing code_extractor for intelligent parsing

2. **Code Extractor** (already exists!)
   - Your existing `code_extractor.py` 
   - Extracts clean code from text responses
   - Handles multi-file detection

3. **File Operations Tools** (already exists!)
   - `WriteFileTool` for actual file creation
   - Already used by fallback mechanisms

## Usage

### Basic Usage

```python
from packages.core.agents.non_tooling_adapter import create_with_non_tooling_model

# Use Codestral to generate code
result = await create_with_non_tooling_model(
    model="ollama:codestral",
    prompt="Create a complete Tetris game in HTML",
    output_path="tests/output/codestral/tetris.html"
)

print(f"Success: {result['success']}")
print(f"Files created: {result['execution']['files_created']}")
```

### Advanced Usage

```python
from packages.core.agents.non_tooling_adapter import NonToolingAdapter

# Create adapter instance
adapter = NonToolingAdapter(
    model="ollama:codestral",
    temperature=0.1  # Low temp for deterministic code
)

# Generate code
response = await adapter.generate_code(
    "Create a Python Flask API with 3 endpoints"
)

# Parse files (supports FILE: markers OR intelligent extraction)
files = await adapter.extract_and_parse_code(
    response_text=response,
    default_output_path="output/app.py"
)

# Execute file creation
results = await adapter.execute_file_operations(files)
```

## File Marker Format

Models should use this format for multi-file generation:

```
FILE: path/to/index.html
<!DOCTYPE html>
<html>
...
</html>

FILE: path/to/styles.css
body {
  margin: 0;
}

FILE: path/to/app.js
function init() {
  console.log('Ready');
}
```

The adapter will:
1. Parse `FILE:` markers first (fast, explicit)
2. Fallback to code_extractor if no markers (intelligent, handles any format)

## Running Tests

### Test Codestral
```bash
uv run python test_codestral_adapter.py
```

### Compare Codestral vs Qwen
```bash
uv run python test_codestral_adapter.py compare
```

## Workflow Details

### Step 1: Generate (Text-Only)
```python
# Adapter creates agent with text-only system prompt
agent = Agent(
    "ollama:codestral",
    system_prompt="""Generate ONLY text. No tools.
    Use FILE: markers for multiple files..."""
)

# Get text response
response = await agent.run(prompt)
```

### Step 2: Parse/Extract
```python
# Try FILE: marker parsing
files = parse_file_markers(response)

if not files:
    # Fallback to intelligent extraction
    extraction = await extract_code_from_response(
        response_text=response,
        requested_file_path=output_path
    )
    files = {f.file_path: f.content for f in extraction.files}
```

### Step 3: Execute
```python
# Manually write files using existing tools
tool = WriteFileTool()
for path, content in files.items():
    await tool.execute(file_path=path, content=content)
```

## Benefits

### ✅ Advantages
1. **Access to specialized models** - Use Codestral's superior code quality
2. **Reuses existing infrastructure** - Leverages code_extractor and tools
3. **Transparent to user** - Same interface, different backend
4. **Fallback mechanism** - Gracefully handles both formats
5. **No model modification** - Works with models as-is

### ⚠️ Limitations
1. **No interactive tool use** - Can't do multi-step tool workflows
2. **Text parsing overhead** - Slightly slower than native tool calling
3. **Relies on format** - Works best when model follows conventions
4. **Single-shot only** - Can't iteratively refine with tools

## Comparison: Tooling vs Non-Tooling

| Feature | Tool-Supporting Models | Non-Tooling Adapter |
|---------|------------------------|---------------------|
| **Models** | Qwen, GPT, Gemini, Llama3.1 | Codestral, CodeLlama |
| **Code Quality** | Good | Excellent (specialized) |
| **File Creation** | Direct tool call | Text parsing → manual |
| **Multi-step** | ✅ Yes | ❌ No |
| **Speed** | Fast | Slightly slower |
| **Reliability** | High | Medium (format dependent) |

## When to Use Each

### Use Regular Agents (with tools)
- Complex multi-step workflows
- Interactive refinement needed
- When tool-supporting models are sufficient

### Use Non-Tooling Adapter
- ✅ Specialized code models (Codestral)
- ✅ Fill-in-the-middle tasks
- ✅ Single-shot code generation
- ✅ When code quality > workflow flexibility

## Configuration

Add to `.env`:
```bash
# For non-tooling adapter, use any model
# The adapter will handle text-only generation
CODE_GENERATOR_MODEL=ollama:codestral

# Code extractor needs tool support (for parsing)
CODE_EXTRACTOR_MODEL=ollama:llama3.1:8b-instruct-q8_0
```

## Example Output

```
============================================================
🔧 NON-TOOLING ADAPTER WORKFLOW
Model: ollama:codestral
============================================================

📝 Step 1: Generating code...
🤖 Using non-tooling adapter with ollama:codestral
📄 Generated 8421 chars of text

🔍 Step 2: Extracting code...
📝 Parsed file marker: tests/output/tetris.html (8234 chars)
✅ Found 1 files with markers

💾 Step 3: Creating files...
💾 Creating file: tests/output/tetris.html
✅ Created: tests/output/tetris.html (8234 bytes)

============================================================
📊 SUMMARY
✅ Files created: 1
❌ Files failed: 0
📦 Total bytes: 8234
============================================================
```

## Future Enhancements

- [ ] Auto-detect tool support and switch adapters
- [ ] Support more file marker formats (code fences, etc.)
- [ ] Add retry logic for failed parsing
- [ ] Cache parsed results
- [ ] Add streaming support for large files
- [ ] Integrate with delegation system

## Related Files

- `packages/core/agents/non_tooling_adapter.py` - Main adapter
- `packages/core/agents/code_extractor.py` - Intelligent code parsing
- `packages/core/tools/file_operations.py` - File write operations
- `test_codestral_adapter.py` - Test script
