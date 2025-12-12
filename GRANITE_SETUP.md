# Granite 3.3 Setup Instructions

## Quick Start

Once Ollama finishes pulling granite3.3:8b, run:

```bash
# 1. Switch to Granite configuration
./switch_env.sh granite

# 2. Test file creation
uv run python test_file_editor.py

# 3. If successful, run full E2E tests
cd e2etests && uv run python run_tests.py
```

## Why Granite 3.3?

**IBM Granite 3.3** is specifically optimized for:
- ✅ Tool calling / function calling
- ✅ Instruction following
- ✅ Structured output generation
- ✅ Fast inference (8B parameters)

This should fix the issue where agents **explain** instead of **actually calling tools**.

## Model Assignments with Granite

```
Coordinator:      granite3.3:8b  (tool routing)
File Editor:      granite3.3:8b  (CRITICAL - file operations)
Testing:          granite3.3:8b  (test generation)
Documentation:    granite3.3:8b  (docs generation)

Codebase:         qwen2.5-coder:14b  (code analysis)
Refactoring:      gpt-oss:20b        (complex reasoning)
```

## Configuration Files

- `.env.granite` - Granite 3.3 optimized (recommended for tool calling)
- `.env.optimized` - Mixed models (qwen/gpt-oss/mistral)
- `.env` - Current active configuration

## Switching Configs

```bash
./switch_env.sh granite    # Use Granite 3.3
./switch_env.sh optimized  # Use mixed models
./switch_env.sh generic    # Use all mistral
```

## Expected Improvement

**Before** (with mistral):
```
agent> create sandbox/calc.py
Result: "To create the file, run: mkdir..." ❌
```

**After** (with granite3.3):
```
agent> create sandbox/calc.py
[Calls create_new_file tool]
Result: "Created sandbox/calc.py" ✅
File created: sandbox/calc.py
```

## Verification

After switching to Granite, verify:
1. File actually created in sandbox/
2. Tool calls visible in agent output
3. E2E tests pass (especially Test 9)
