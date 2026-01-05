# Code Extractor & File Creation Issues - Investigation

## Iteration 1: File Creation in Wrong Location

**Test**: Explicit 3-file request  
**Model**: gpt-oss:20b  
**Result**: Files created in wrong locations

**Files Created:**
- `sandbox/tetris/styles.css` ❌ (should be `tests/output/gpt-oss_20b/styles.css`)
- `sandbox/tetris/game.js` ❌ (should be `tests/output/gpt-oss_20b/game.js`)
- `tests/output/index.html` ❌ (should be `tests/output/gpt-oss_20b/index.html`)

**Root Cause**: Code extractor agent not using `base_dir` correctly for file paths

**Fix Applied**: Enhanced extraction prompt to explicitly instruct using `{base_dir}/` prefix for ALL files

## Iteration 2: Coordinator Not Executing Tools

**Test**: After code extractor fix  
**Model**: gpt-oss:20b  
**Result**: Coordinator explains what it would do instead of doing it

**Coordinator Output:**
```
**generate_code("Tetris game with Classic gameplay", "html", "sandbox/index.html")**
{" name": "generate_code", "parameters": {...}}
```

**Problem**: Instead of CALLING the tool, it's DESCRIBING the tool call in markdown

**Root Cause**: Coordinator prompt may be too verbose about file paths, confusing the model into "explanation mode"

## Analysis

### Issue 1: Code Extractor Path Bug

**Before Fix:**
```python
prompt = f"""Extract code from this response.
Requested file: {requested_file_path}
Base directory: {base_dir}
..."""
```

Model interpreted this loosely and used paths like:
- `sandbox/tetris/styles.css` (invented location)
- `index.html` (no directory)

**After Fix:**
```python
prompt = f"""Extract code files from this response.
REQUESTED FILE: {requested_file_path}
BASE DIRECTORY: {base_dir}

🚨 CRITICAL: ALL file_path values MUST start with: {base_dir}/

EXAMPLES:
- Main HTML: {requested_file_path}
- CSS file: {base_dir}/styles.css
- JS file: {base_dir}/game.js
..."""
```

This should be clearer, but we haven't tested if it works yet.

### Issue 2: Coordinator Tool Execution

The coordinator is not executing tools when given very explicit file paths in the prompt.

**Test prompt had:**
```
1. tests/output/gpt-oss_20b/index.html - Main HTML structure
2. tests/output/gpt-oss_20b/styles.css - All CSS styling
3. tests/output/gpt-oss_20b/game.js - All JavaScript game logic
```

**Coordinator response:**
```
generate_code("Tetris game...", "html", "sandbox/index.html")
```

The coordinator:
1. Ignored the explicit file paths
2. Used "sandbox/index.html" instead
3. Didn't actually call the tool (just explained it)

**Hypothesis**: The very detailed prompt with explicit paths confused the model into thinking it should explain rather than execute.

## Next Steps

### Option 1: Simplify Test Prompt

Instead of:
```python
command = f"""Create a complete working Tetris game using these THREE separate files:

1. {output_dir}/index.html - Main HTML structure
2. {output_dir}/styles.css - All CSS styling  
3. {output_dir}/game.js - All JavaScript game logic
..."""
```

Try:
```python
command = f"""Create a complete working Tetris game in {output_dir}/.

Use THREE separate files (HTML, CSS, JS) with proper linking.
Requirements: ...
"""
```

Let the coordinator and code generator figure out the exact file names.

### Option 2: Fix Coordinator Prompt

The coordinator's system prompt might need adjustment to handle explicit file paths better.

### Option 3: Test Code Extractor Fix First

Before changing the test, verify the code extractor fix works by checking if it would correctly parse a multi-file response and use base_dir properly.

## Recommendations

1. **Simplify the test prompt** - Don't be too prescriptive about exact file paths
2. **Test code extractor separately** - Create a unit test for extraction logic
3. **Add validation** - Check that extracted files use correct base_dir
4. **Iterate gradually** - Fix one issue at a time

## Status

- [x] Identified code extractor path bug
- [x] Fixed code extractor prompt
- [ ] Tested code extractor fix
- [ ] Identified coordinator tool execution issue
- [ ] Fixed coordinator behavior
- [ ] Successfully created 3 files in correct location

## Files Modified

- `packages/core/agents/code_extractor.py` - Enhanced extraction prompt
- `tests/integration/test_tetris_game.py` - Made prompt more explicit (may need to revert)
