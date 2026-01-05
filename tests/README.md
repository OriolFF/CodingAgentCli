# Tests Directory

## Structure

```
tests/
├── integration/      # Full agent system tests (use .env config)
├── benchmarks/       # Model comparison tests (hardcoded models)
├── debug/            # Low-level debugging tests
├── unit/             # Unit tests (existing)
└── output/           # Test output files
```

## Integration Tests (uses .env configuration)

Run these to test your current setup with the model configured in `.env`:

```bash
# Test Tetris generation
uv run python tests/integration/test_tetris_game.py

# Test landing page generation
uv run python tests/integration/test_landing_page.py

# Test file editor delegation
uv run python tests/integration/test_file_editor.py

# Test code generator with multiple scenarios
uv run python tests/integration/test_code_generator.py

# Test CV landing page
uv run python tests/integration/test_cv_landing.py
```

**These tests:**
- ✅ Respect .env `CODE_GENERATOR_MODEL` setting
- ✅ Use full delegation system
- ✅ Output to `tests/output/{model_name}/`
- ✅ Good for daily testing of your config

## Benchmark Tests (hardcoded models)

Run these to benchmark specific models regardless of `.env`:

```bash
# Test Codestral with optimized adapter
uv run python tests/benchmarks/test_codestral_optimized.py

# Test Codestral with basic adapter
uv run python tests/benchmarks/test_codestral_adapter.py

# Compare Codestral vs Qwen
uv run python tests/benchmarks/test_codestral_adapter.py compare

# Test OpenRouter cloud models
uv run python tests/benchmarks/test_openrouter_code_gen.py

# OpenRouter test suite
uv run python tests/benchmarks/test_suite_openrouter.py
```

**These tests:**
- ❌ Ignore .env (hardcode models)
- ✅ Good for model comparison
- ✅ Good for performance benchmarking
- ✅ Output to `tests/output/{model}_adapter/`

## Debug Tests

Low-level tests for debugging specific issues:

```bash
# Test Ollama custom settings (num_predict, num_ctx)
uv run python tests/debug/test_ollama_settings.py

# Test code quality validation
uv run python tests/debug/test_code_quality.py
```

## Quick Test Commands

### Test Current Config
```bash
# Run with your .env model
uv run python tests/integration/test_tetris_game.py
```

### Compare Models
```bash
# Set .env to qwen
CODE_GENERATOR_MODEL=ollama:qwen2.5-coder:14b

# Test with qwen (uses .env)
uv run python tests/integration/test_tetris_game.py

# Test with codestral (ignores .env)
uv run python tests/benchmarks/test_codestral_optimized.py

# Compare outputs
ls -lh tests/output/qwen2_5-coder_14b/
ls -lh tests/output/codestral_optimized/
```

## Output Locations

Tests create output in:
```
tests/output/
├── {model_name}/          # From integration tests (model name from .env)
├── codestral_adapter/     # From basic Codestral adapter
├── codestral_optimized/   # From optimized Codestral adapter
├── qwen_adapter/          # From non-tooling adapter with Qwen
└── ...
```

## Test Types Explained

### Integration Tests
- **Purpose**: Test full agent workflow
- **Config**: Use .env settings
- **When**: Daily testing, validating changes
- **Example**: `test_tetris_game.py`

### Benchmark Tests
- **Purpose**: Compare specific models
- **Config**: Hardcoded models (ignore .env)
- **When**: Model evaluation, performance reports
- **Example**: `test_codestral_optimized.py`

### Debug Tests
- **Purpose**: Low-level debugging
- **Config**: Direct API calls, custom settings
- **When**: Troubleshooting issues
- **Example**: `test_ollama_settings.py`

## Running Tests

### Run Single Test
```bash
uv run python tests/integration/test_tetris_game.py
```

### Run All Integration Tests
```bash
for test in tests/integration/test_*.py; do
    echo "Running $test..."
    uv run python "$test"
done
```

### Run With Specific Model (Integration Tests Only)
```bash
# Temporarily override .env
CODE_GENERATOR_MODEL=ollama:qwen2.5-coder:14b uv run python tests/integration/test_tetris_game.py
```

## Cleanup

### Clean Output Directory
```bash
# Remove all test outputs
rm -rf tests/output/*

# Remove specific model outputs
rm -rf tests/output/cogito_14b/
rm -rf tests/output/codestral_*/
```

## Adding New Tests

### Integration Test Template
```python
"""Test description."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # Note: parent.parent

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config, get_config

async def test_something():
    init_config()
    # Your test code
    result = await delegate_task("create something...")
    # Assertions

if __name__ == "__main__":
    asyncio.run(test_something())
```

### Benchmark Test Template
```python
"""Benchmark specific model."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))  # Note: parent.parent

from packages.core.agents.codestral_optimized import create_with_codestral_optimized
from packages.core.config import init_config

async def test_model():
    init_config()  # Load config for OLLAMA_BASE_URL etc
    # Hardcode model - ignore .env
    result = await create_with_codestral_optimized(
        prompt="test prompt",
        output_path="tests/output/benchmark/test.html"
    )
    # Assertions

if __name__ == "__main__":
    asyncio.run(test_model())
```

## Notes

- **Import Path**: All tests in subdirectories use `parent.parent` for sys.path
- **Output Naming**: Integration tests create folders based on .env model name
- **Benchmark Isolation**: Benchmark tests never affect your daily .env config
- **Test Independence**: Each test can run independently
