# Pending Tasks

## 🚨 Critical - Auto-Refactoring System

**Priority**: HIGH  
**Status**: DISABLED (broken)  
**Assigned**: -  
**Created**: 2026-01-05

### Problem
Auto-refactoring system is fundamentally broken and destroys working code by replacing it with placeholders.

### Details
- Location: `packages/core/agents/refactoring_agent.py` - `refactor_file()` function
- Issue: Function doesn't actually read or write files, just returns text descriptions
- Impact: Generated code is replaced with placeholders like `...`, `// rest of code`, etc.
- Documentation: `docs/AUTO_REFACTORING_BROKEN_ANALYSIS.md`

### Root Cause
```python
async def refactor_file(file_path: str):
    # ❌ Never reads the original file
    # ❌ Model generates summary instead of complete code
    # ❌ Never writes refactored code back
    return RefactoringResult(success=True)  # Lies!
```

### Symptoms
- Code size reduced by 80-90% after "refactoring"
- Placeholders appear: `<!-- removed HTML markup -->`, `/* CSS styles */`, `[...]`
- Comments like `// Rest of the JavaScript code`
- Happens with ANY model (qwen, gpt-oss, etc.)

### Fix Required
1. **Read original file** before refactoring
2. **Generate COMPLETE refactored code** (no summaries!)
3. **Validate** no placeholders in output:
   - Check for `...`, `// rest of`, `/* rest of`
   - Verify size not drastically reduced (<50% of original)
4. **Actually write** the refactored file
5. **Test** thoroughly before re-enabling

### Implementation Plan
```python
async def refactor_file(file_path: str, focus: str = None):
    # 1. Read original
    original_code = await read_file(file_path)
    
    # 2. Refactor with strict prompt
    prompt = f"""Refactor this code. Generate COMPLETE code, NO placeholders.

ORIGINAL:
{original_code}

FOCUS: {focus}

RULES:
1. Output COMPLETE refactored code
2. NO "..." or "// rest of" comments
3. Include ALL functions, variables, logic
4. Only fix specific issues"""
    
    refactored = await agent.run(prompt)
    
    # 3. Validate
    if has_placeholders(refactored):
        return RefactoringResult(success=False, description="Placeholders detected")
    if len(refactored) < len(original_code) * 0.5:
        return RefactoringResult(success=False, description="Code too small")
    
    # 4. Write
    await write_file(file_path, refactored)
    return RefactoringResult(success=True)
```

### Testing Checklist
- [ ] Refactor simple Python file (calculator.py)
- [ ] Refactor HTML file with embedded JS/CSS
- [ ] Refactor file with intentional errors
- [ ] Verify code size stays similar (±20%)
- [ ] Verify no placeholders introduced
- [ ] Test with multiple models (qwen, gpt-oss, llama)
- [ ] Integration test with full delegation flow

### Current Status
- **Disabled** in `packages/core/agents/delegation.py` (lines 227-248)
- Code commented out with TODO and reference to analysis doc
- Test files created but refactoring skipped

### Re-enable When
- [ ] refactor_file() properly implemented
- [ ] Validation functions created
- [ ] All tests passing
- [ ] Code review completed

---

## 📊 Other Pending Tasks

### Model Performance Testing

**Priority**: MEDIUM  
**Status**: IN PROGRESS  
**Created**: 2026-01-05

- [x] Test Codestral with non-tooling adapter
- [x] Test Codestral with optimized adapter
- [ ] Test gpt-oss:20b WITHOUT auto-refactoring (retest needed)
- [ ] Compare gpt-oss:20b vs qwen2.5-coder:14b fairly
- [ ] Update `models_performance.md` with findings
- [ ] Document recommended models for different tasks

### Documentation Updates

**Priority**: LOW  
**Status**: PENDING  

- [ ] Consolidate Codestral investigation docs
  - `CODESTRAL_INVESTIGATION.md`
  - `CODESTRAL_OPTIMIZATION_REPORT.md`
  - `GPT_OSS_20B_TEST_CRITICAL_BUG.md`
  - `REFACTORING_MODEL_MISMATCH.md`
  - `AUTO_REFACTORING_BROKEN_ANALYSIS.md`
- [ ] Create single comprehensive "Model Testing Report"
- [ ] Archive/organize old investigation docs

### Test Organization

**Priority**: LOW  
**Status**: COMPLETE ✅  

- [x] Organize tests into integration/benchmarks/debug
- [x] Remove obsolete tests
- [x] Fix import paths
- [x] Create tests/README.md

### Code Quality System

**Priority**: MEDIUM  
**Status**: REVIEW NEEDED  

The quality validation system (`packages/core/utils/code_quality.py`) is working:
- ✅ Detects syntax errors
- ✅ Finds unclosed tags
- ✅ Identifies placeholders
- ❓ Review if rules are too strict or missing important checks

**Action**: Review quality rules for false positives/negatives

---

## 💡 Future Enhancements

### Non-Tooling Adapter Improvements
- [ ] Add support for Ollama FIM mode for Codestral
- [ ] Test with more non-tooling models
- [ ] Add fallback strategies for incomplete responses

### Model Configuration
- [ ] Add per-model configuration profiles
- [ ] Support model-specific prompts
- [ ] Allow runtime model switching

### Testing Infrastructure
- [ ] Add automated regression tests
- [ ] Create benchmark suite for model comparison
- [ ] CI/CD integration for test suite

---

## 📝 Notes

### Lessons Learned

1. **Auto-refactoring is dangerous** without proper implementation
2. **Model mismatch** was a red herring - system was broken regardless
3. **Validation is critical** to prevent code destruction
4. **Test thoroughly** before enabling automated fixes

### Best Practices

1. Always test with auto-refactoring DISABLED first
2. Use same model for generation and refactoring if enabled
3. Validate output size and placeholder absence
4. Keep backups before automated modifications
5. Manual review for critical code changes
