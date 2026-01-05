# GPT-OSS:20B Test Results

**Date**: January 5, 2026  
**Model**: `ollama:gpt-oss:20b` (13GB, local)  
**Test**: Tetris Game Generation  
**Result**: ⚠️ **CRITICAL BUG DISCOVERED**

## Test Summary

### Initial Generation
✅ **Model generated code successfully**
- Response length: 5,931 chars
- Created initial HTML with embedded JavaScript
- Code appeared to contain complete Tetris implementation

### Quality Validation
⚠️ **Found issues:**
1. Unclosed `<html>` tag in index.html
2. Placeholder comment `// ...` in tetris.js

### Auto-Refactoring
❌ **REFACTORING BUG DISCOVERED**

The auto-refactoring system **destroyed** the generated code:

**Before refactoring** (5,931 chars):
- Complete Tetris game
- All shapes, logic, rendering
- Working code

**After refactoring** (520 bytes total):
```html
<!-- index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Tetris</title>
<style>...</style>  ← PLACEHOLDER!
</head>
<body>
<div id="game">...</div>
</body>
```

```javascript
// tetris.js
// ... js code here ...  ← PLACEHOLDER!
// const canvas = document.getElementById('tetris');
// ...
```

## Root Cause

The **refactoring agent** replaced actual code with placeholder comments:
- ✅ Detected issues correctly
- ❌ Instead of fixing issues, **replaced code with `...`**
- ❌ Destroyed working implementation

## Comparison: gpt-oss:20b vs Other Models

| Model | Initial Generation | Refactoring | Final Result |
|-------|-------------------|-------------|--------------|
| **qwen2.5-coder:14b** | ✅ 1,512 bytes complete | N/A | ✅ Working |
| **cogito:14b** | ⚠️ Skeleton/refuses | N/A | ❌ Broken |
| **codestral** | ❌ 453 bytes skeleton | N/A | ❌ Placeholders |
| **gpt-oss:20b** | ✅ 5,931 bytes complete | ❌ **BROKE IT** | ❌ **Destroyed** |

## Critical Issue

**The refactoring system is broken!**

When it detects issues, it should:
1. ✅ Identify problems
2. ✅ Request fixes from model
3. ✅ Apply fixes to specific lines
4. ✅ Keep working code intact

Instead it:
1. ✅ Identifies problems
2. ❌ **Replaces entire code with placeholders**
3. ❌ **Destroys working implementation**

## What Should Have Happened

**Expected flow:**
```
1. Generate code (5,931 chars) ✓
2. Detect unclosed tag ✓
3. Ask model to fix unclosed tag ✗
4. Apply fix ✗
5. Validate ✗
6. Return working code ✗
```

**What actually happened:**
```
1. Generate code (5,931 chars) ✓
2. Detect issues ✓
3. Replace everything with "..." ✗
4. Return broken 520 bytes ✗
```

## Files Created

```
tests/output/gpt-oss_20b/
├── index.html (437 bytes) - BROKEN (placeholders)
└── tetris.js (83 bytes) - BROKEN (placeholders)
```

## Recommendations

### Immediate Actions

1. ✅ **DISABLE auto-refactoring** until fixed
2. ✅ **Review refactoring agent code**
3. ✅ **Add validation** to prevent code destruction
4. ✅ **Keep original files** as backup before refactoring

### For gpt-oss:20b Model

**Initial assessment**: ✅ **Promising**
- Generated 5,931 chars of complete code
- Larger output than most models
- Code structure looked complete
- Only minor issues (unclosed tag)

**Recommendation**: 
- ⚠️ Test again **without auto-refactoring**
- ✅ Likely capable of good code generation
- ❌ Auto-refactoring broke it, not the model

## Action Items

### Fix Auto-Refactoring System

```python
# Current (BROKEN):
def refactor(file_path, issues):
    # Replaces entire file with placeholders ❌
    new_content = "..."
    write_file(file_path, new_content)

# Should be:
def refactor(file_path, issues):
    # Fix specific issues only ✓
    content = read_file(file_path)
    for issue in issues:
        content = fix_specific_issue(content, issue)
    write_file(file_path, content)
```

### Prevent Code Destruction

```python
def validate_refactoring(original, refactored):
    # Sanity checks
    if len(refactored) < len(original) * 0.5:
        raise Error("Refactoring destroyed code!")
    if "..." in refactored and "..." not in original:
        raise Error("Introduced placeholders!")
```

## Conclusion

**gpt-oss:20b**: ✅ Generated good code initially  
**Auto-refactoring**: ❌ **CRITICAL BUG** - destroyed working code

**Next steps:**
1. Fix refactoring system
2. Retest gpt-oss:20b without auto-refactoring
3. Compare actual code quality vs other models

**Current Status**: Cannot evaluate gpt-oss:20b fairly due to refactoring bug
