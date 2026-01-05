# Refactoring Model Analysis - Critical Finding

## Question: Did refactoring use the same model as code generation?

**Answer**: ❌ **NO** - And this explains the bug!

## Configuration

From your `.env`:
```bash
CODE_GENERATOR_MODEL=ollama:gpt-oss:20b
REFACTORING_MODEL=ollama:qwen2.5-coder:14b
```

## What Happened

### Step 1: Code Generation (gpt-oss:20b)
```
Model: gpt-oss:20b
Output: 5,931 chars of complete Tetris code
Quality: ✅ Excellent - full implementation
Issues: Minor (unclosed HTML tag, one comment)
```

### Step 2: Refactoring (qwen2.5-coder:14b)
```
Model: qwen2.5-coder:14b (DIFFERENT MODEL!)
Input: 5,931 chars of gpt-oss code
Output: 520 bytes of placeholders
Quality: ❌ DESTROYED - replaced code with "..."
```

## The Problem

**Two different models with different behaviors:**

1. **gpt-oss:20b**:
   - Generated complete, working code
   - 5,931 chars with full Tetris implementation
   - All game logic, shapes, rendering
   - Only minor formatting issues

2. **qwen2.5-coder:14b** (refactoring):
   - Asked to fix gpt-oss code
   - Instead of fixing issues
   - **Replaced everything with placeholders**
   - Likely because it didn't understand gpt-oss's code style

## Why This Happened

### Hypothesis 1: Model Incompatibility
Different models have different coding styles and patterns. Qwen may have:
- Not understood gpt-oss's code structure
- Defaulted to generating "summary" placeholders
- Treated the task as "explain code" instead of "fix code"

### Hypothesis 2: Prompt Mismatch
The refactoring agent's prompt might be:
- Optimized for Qwen's patterns
- Not suitable for fixing another model's code
- Causing Qwen to summarize instead of fix

### Hypothesis 3: Tool Calling Difference
- gpt-oss generated text response
- Qwen tried to use tools for refactoring
- Tool responses might have been misinterpreted

## Evidence from Code

From `refactoring_agent.py`:
```python
def _create_refactoring_agent() -> Agent:
    config = get_config()
    model_instance = config.get_model_instance("refactoring")
    # ☝️ Uses REFACTORING_MODEL from .env
    
    agent = Agent(
        model_instance,
        system_prompt="""You are an expert software engineer...
        When refactoring:
        - Make small, incremental changes
        - Preserve existing functionality  ← ❌ Failed!
        - Improve readability and maintainability
        ..."""
    )
```

**The prompt says "preserve functionality" but Qwen destroyed it!**

## Root Cause Analysis

### Configuration Flow
```
1. Test starts with CODE_GENERATOR_MODEL=gpt-oss:20b
2. gpt-oss generates great code ✓
3. Quality validation finds minor issues ✓
4. Refactoring triggered with REFACTORING_MODEL=qwen:14b ✓
5. Qwen receives gpt-oss code to fix ✗
6. Qwen doesn't fix - it REPLACES with placeholders ✗
```

### The Mismatch
```
gpt-oss code style:
  - Compact, dense JavaScript
  - Specific naming conventions
  - Particular code structure

qwen interprets it as:
  - "Too complex to show fully"
  - Generates summary with "..."
  - Loses actual implementation
```

## Why Same-Model Refactoring Would Be Better

### If REFACTORING_MODEL=gpt-oss:20b:
```
✓ Same model understands its own code
✓ Can make targeted fixes
✓ Preserves implementation details
✓ Consistent code style
```

### Current Setup (Different Models):
```
✗ Qwen doesn't understand gpt-oss patterns
✗ Treats code as "foreign"
✗ Defaults to safe "summary" approach
✗ Loses implementation
```

## Recommendations

### Option 1: Use Same Model for Refactoring (RECOMMENDED)
```bash
# .env
CODE_GENERATOR_MODEL=ollama:gpt-oss:20b
REFACTORING_MODEL=ollama:gpt-oss:20b  # Same model!
```

**Benefits:**
- ✅ Model fixes its own code
- ✅ Understands its patterns
- ✅ Preserves implementation
- ✅ Consistent style

### Option 2: Disable Auto-Refactoring
```python
# In delegation.py
AUTO_REFACTOR_ENABLED = False  # Temp disable

# Or add config option
ENABLE_AUTO_REFACTOR=false  # .env
```

**Benefits:**
- ✅ Prevents code destruction
- ✅ Manual review of issues
- ✅ Safe for production

### Option 3: Improve Refactoring Prompt
Make the prompt explicitly preserve code:
```python
system_prompt="""...
CRITICAL RULES:
1. NEVER replace code with placeholders like "..."
2. NEVER use comments like "// rest of code here"
3. ONLY modify the specific lines with issues
4. KEEP all implementation details
5. If you can't fix it, return the original unchanged
..."""
```

### Option 4: Add Validation
```python
def validate_refactoring_result(original, refactored):
    # Safety checks
    if len(refactored) < len(original) * 0.5:
        raise ValueError("Refactoring destroyed code!")
    
    if "..." in refactored and "..." not in original:
        raise ValueError("Introduced placeholders!")
    
    if "// rest of" in refactored.lower():
        raise ValueError("Used lazy placeholders!")
    
    return refactored
```

## Immediate Actions

1. ✅ **Set REFACTORING_MODEL=gpt-oss:20b** in .env
2. ✅ **Retest** with same model for both
3. ✅ **Add validation** to prevent future destruction
4. ✅ **Document** model compatibility requirements

## Conclusion

**Answer to your question**: 

❌ **NO**, refactoring did NOT use the same model:
- Code generation: `gpt-oss:20b`
- Refactoring: `qwen2.5-coder:14b`

**This model mismatch caused the bug:**
- gpt-oss generated good code
- qwen didn't understand it
- qwen replaced it with placeholders
- Code was destroyed

**Solution**: Use the same model for both generation and refactoring, or disable auto-refactoring entirely.
