# AUTO-REFACTORING SYSTEM IS FUNDAMENTALLY BROKEN

## Test Results: gpt-oss:20b (Same Model for Both)

**Configuration:**
```bash
CODE_GENERATOR_MODEL=ollama:gpt-oss:20b  ← Generation
REFACTORING_MODEL=ollama:gpt-oss:20b     ← Refactoring (SAME!)
```

**Result:** ❌ **STILL BROKEN** - Same placeholder bug!

## What We Discovered

### Generated Code (Before Refactoring)
- ✅ 6,793 chars of complete Tetris
- ✅ All game logic, shapes, controls
- ⚠️ 2 minor issues (missing HTML/head tags)

### After "Refactor"
- ❌ 1,162 bytes (83% size reduction!)
- ❌ Replaced with placeholders:
  ```html
  <!-- removed HTML markup -->
  /* CSS styles */
  /* body content */
  const COLORS = [...];
  // ... multiple shapes
  // Rest of the JavaScript code
  ```

## Root Cause: Refactoring Agent Design Flaw

### The Problem

From `refactoring_agent.py`:
```python
async def refactor_file(
    file_path: str,
    focus: Optional[str] = None
) -> RefactoringResult:
    agent = get_refactoring_agent()
    
    prompt = f"Refactor the code in: {file_path}"
    prompt += """
    Please:
    1. Analyze the code for quality issues
    2. Identify specific refactoring opportunities
    3. Apply refactorings to improve code quality  ← Says "apply" but...
    ..."""
    
    result = await agent.run(prompt)
    output = result.output  # ← Just TEXT, doesn't modify files!
    
    return RefactoringResult(
        success=True,  # ← Always says success!
        description=output,  # ← Just description
        files_modified=[file_path],  # ← Lies! Doesn't modify
        improvements=[]
    )
```

**THE BUG:**
1. Asks model to "refactor and apply changes"
2. Model generates refactored code OR summary
3. **Returns text description instead of writing files**
4. Original file never gets modified
5. Or worse: model outputs summary with `...` placeholders

### Why Placeholders Appear

The model (whether qwen or gpt-oss) interprets "refactor this code" as:
- "Show me what you would change"
- "Summarize the refactorings"
- "Explain the improvements"

Instead of:
- "Generate the complete refactored code"
- "Write the full implementation"

So it outputs:
```javascript
// Fixed HTML structure
<!-- removed HTML markup -->  ← Summary

// Optimized styles
/* CSS styles */  ← Summary

// Complete game logic
const COLORS = [...];  ← Array summarized
// ... multiple shapes  ← List summarized
// Rest of the JavaScript code  ← Everything else summarized
```

## The Tool Chain is Broken

### What Should Happen
```
1. Read file → Get original code
2. Ask model → "Generate COMPLETE refactored version"
3. Model responds → Full code (no placeholders!)
4. Validate → Check it's actually complete
5. Write file → Replace original
```

### What Actually Happens
```
1. ❌ Never reads original file first
2. Model gets file PATH only (not content!)
3. Model generates summary/description
4. ❌ Never writes anything
5. ❌ Says "success" anyway
```

### Proof from Code

The refactoring agent HAS tools:
```python
@agent.tool
async def analyze_code_quality(ctx, file_path: str):
    tool = ReadFileTool()  ← Can read
    result = await tool.execute(file_path=file_path)
    return f"Code to analyze:\n{result.output}"

@agent.tool
async def refactor_code(ctx, file_path: str, search_text: str, replacement: str):
    tool = EditFileTool()  ← Can edit
    result = await tool.execute(
        file_path=file_path,
        search_text=search_text,
        replace_text=replacement
    )
    return f"Refactoring applied:\n{result.output}"
```

**But `refactor_file()` never actually calls these tools!**

It just runs the agent with a prompt and returns the text response.

## Why Same Model Didn't Fix It

We thought different models were the problem:
- gpt-oss generates → qwen refactors → incompatibility

But the real problem is:
- **The refactoring function is broken regardless of model**
- It never actually writes files
- Just returns descriptions/summaries
- Even the same model can't fix a broken workflow

## How to Actually Fix This

### Option 1: Fix refactor_file() to Actually Refactor

```python
async def refactor_file(
    file_path: str,
    focus: Optional[str] = None
) -> RefactoringResult:
    from ..tools.file_operations import ReadFileTool, WriteFileTool
    
    # 1. READ THE ORIGINAL FILE
    read_tool = ReadFileTool()
    read_result = await read_tool.execute(file_path=file_path)
    if not read_result.success:
        return RefactoringResult(
            success=False,
            description=f"Failed to read {file_path}"
        )
    
    original_code = read_result.output
    
    # 2. ASK MODEL FOR COMPLETE REFACTORED CODE
    agent = get_refactoring_agent()
    prompt = f"""Refactor this code to fix the issues.

ORIGINAL CODE:
{original_code}

FOCUS: {focus}

CRITICAL RULES:
1. Generate the COMPLETE refactored code
2. NO placeholders like "..." or "// rest of code"
3. INCLUDE ALL functions, variables, logic
4. Only fix the specific issues, keep everything else
5. Output ONLY the refactored code, no explanations

Generate the FULL refactored code now:"""
    
    result = await agent.run(prompt)
    refactored_code = result.output
    
    # 3. VALIDATE: No placeholders!
    if any(placeholder in refactored_code for placeholder in ["...", "// rest of", "/* rest of"]):
        return RefactoringResult(
            success=False,
            description="Refactoring produced placeholders instead of complete code"
        )
    
    # 4. VALIDATE: Not much smaller (indicates summarization)
    if len(refactored_code) < len(original_code) * 0.5:
        return RefactoringResult(
            success=False,
            description=f"Refactored code too small ({len(refactored_code)} vs {len(original_code)} original)"
        )
    
    # 5. ACTUALLY WRITE THE FILE
    write_tool = WriteFileTool()
    write_result = await write_tool.execute(
        file_path=file_path,
        content=refactored_code
    )
    
    if not write_result.success:
        return RefactoringResult(
            success=False,
            description=f"Failed to write refactored code: {write_result.error}"
        )
    
    return RefactoringResult(
        success=True,
        description=f"Successfully refactored {file_path}",
        files_modified=[file_path]
    )
```

### Option 2: Disable Auto-Refactoring (IMMEDIATE FIX)

In `delegation.py` line 228-286, comment out the entire quality validation and refactoring section:

```python
# NEW: Quality validation and auto-refactoring
# DISABLED: Refactoring system is broken
# if created_files:
#     ... (all the validation and refactoring code)
```

### Option 3: Make Quality Validation Non-Blocking

Keep validation but don't auto-refactor:

```python
if created_files:
    # Validate quality
    for file_path in created_files:
        quality_report = await validate_file_quality(file_path)
        if quality_report.has_critical_issues:
            print(f"⚠️  Critical issues in {file_path}:")
            for issue in quality_report.issues:
                print(f"   - {issue.description}")
            # LOG but don't refactor
            logger.warning(f"File {file_path} has issues but auto-refactor disabled")
```

## Immediate Action Plan

1. **DISABLE** auto-refactoring immediately (Option 2)
2. **FIX** `refactor_file()` function (Option 1)
3. **ADD** validation to prevent placeholders
4. **TEST** with fixed implementation
5. **RE-ENABLE** once proven working

## Testing After Fix

```bash
# Test with fixed refactoring
CODE_GENERATOR_MODEL=ollama:gpt-oss:20b
REFACTORING_MODEL=ollama:gpt-oss:20b

# Should produce:
# ✅ 6,793 chars generated
# ✅ Quality issues detected
# ✅ Refactoring fixes  ONLY the issues
# ✅ Complete code preserved
# ✅ ~7,000 chars final (not 1,162!)
```

## Conclusion

**The model mismatch was a red herring.**

The REAL problem:
- ❌ `refactor_file()` doesn't actually refactor files
- ❌ Just returns descriptions/summaries
- ❌ No validation prevents placeholders
- ❌ Auto-refactoring destroys working code

**Same model didn't help because the system is fundamentally broken.**

We need to:
1. Disable auto-refactoring NOW
2. Rewrite refactor_file() properly
3. Add comprehensive validation
4. Test thoroughly before re-enabling

**Current recommendation:** Disable auto-refactoring until properly fixed.
