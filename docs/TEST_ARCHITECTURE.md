# How Tests Work: .env vs Hardcoded Models

## The Confusion

You noticed that when `.env` is set to use `cogito`, but running `test_codestral_optimized.py` uses `codestral` instead. **This is by design!**

## Two Types of Tests

### Type 1: Config-Based Tests (Uses .env)

**Examples:**
- `test_tetris_game.py`
- `test_landing_page.py`
- `test_cv_landing.py`

**How they work:**
```python
# test_tetris_game.py
async def test_tetris():
    init_config()  # Loads from .env
    
    # Uses delegation system (respects .env)
    result = await delegate_task(command)
```

**Flow:**
```
1. init_config() → Reads .env file
2. delegate_task() → Uses CODE_GENERATOR_MODEL from .env
3. If .env says cogito → Uses cogito
4. If .env says qwen → Uses qwen
```

**These tests RESPECT your .env configuration.**

---

### Type 2: Model-Specific Tests (Hardcoded)

**Examples:**
- `test_codestral_adapter.py`
- `test_codestral_optimized.py`
- `test_openrouter_code_gen.py`

**How they work:**
```python
# test_codestral_optimized.py
async def test_codestral_optimized():
    init_config()  # Loads .env for other settings
    
    # HARDCODED model - ignores .env
    result = await create_with_codestral_optimized(
        prompt=prompt,
        output_path=str(output_file)
    )
```

**Inside the adapter:**
```python
# codestral_optimized.py
class CodestralOptimizedAdapter:
    def __init__(self, temperature: float = 0.0):
        # HARDCODED: Always uses codestral
        self.model = "ollama:codestral"  # ← Ignores .env!
        self.temperature = temperature
```

**Flow:**
```
1. init_config() → Reads .env (for other settings)
2. Adapter hardcodes model → model = "ollama:codestral"
3. ALWAYS uses codestral regardless of .env
```

**These tests IGNORE your .env CODE_GENERATOR_MODEL.**

---

## Why This Design?

### Purpose of Model-Specific Tests

These tests are designed to **benchmark and compare specific models**:

1. **Test Codestral specifically** - Compare its performance
2. **Test OpenRouter models** - Test cloud APIs
3. **Compare models side-by-side** - Qwen vs Codestral vs others
4. **Validate adapters** - Test non-tooling adapter with Codestral

### Example: Comparison Testing

```python
# You want to compare Qwen vs Codestral
# .env might be set to use cogito for daily work
# But you want to test these two specifically

# Test 1: Force Qwen
result_qwen = await create_with_non_tooling_model(
    model="ollama:qwen2.5-coder:14b",  # Hardcoded
    prompt="Create calculator"
)

# Test 2: Force Codestral
result_codestral = await create_with_codestral_optimized(
    # Always uses codestral internally
    prompt="Create calculator"
)

# Compare results
compare(result_qwen, result_codestral)
```

---

## Complete Test Comparison

| Test File | Model Source | Respects .env? | Purpose |
|-----------|-------------|----------------|---------|
| `test_tetris_game.py` | .env CONFIG | ✅ YES | Test current config |
| `test_landing_page.py` | .env CONFIG | ✅ YES | Test current config |
| `test_codestral_adapter.py` | HARDCODED | ❌ NO | Test Codestral specifically |
| `test_codestral_optimized.py` | HARDCODED | ❌ NO | Test optimized Codestral |
| `test_openrouter_code_gen.py` | HARDCODED | ❌ NO | Test OpenRouter models |
| `run_test_suite.py` | .env CONFIG | ✅ YES | Test suite with current config |

---

## How to Use Each Type

### When to Use Config-Based Tests

```bash
# Set your model in .env
CODE_GENERATOR_MODEL=ollama:cogito:14b

# Run test - uses cogito
uv run python test_tetris_game.py

# Change .env
CODE_GENERATOR_MODEL=ollama:qwen2.5-coder:14b

# Run again - now uses qwen
uv run python test_tetris_game.py
```

**Use for:**
- Testing your current setup
- Daily development workflow
- Validating config changes

### When to Use Model-Specific Tests

```bash
# .env can have any model (doesn't matter)
CODE_GENERATOR_MODEL=ollama:cogito:14b

# Always tests Codestral (ignores .env)
uv run python test_codestral_optimized.py

# Still uses Codestral (not cogito!)
```

**Use for:**
- Benchmarking specific models
- Comparing model performance
- Testing new model adapters
- Creating performance reports

---

## The Code Flow Explained

### Config-Based Test Flow

```python
# test_tetris_game.py

from packages.core.agents.delegation import delegate_task
from packages.core.config import init_config, get_config

async def test_tetris():
    # 1. Load config from .env
    init_config()
    
    # 2. delegate_task internally does:
    #    config = get_config()
    #    model = config.get_agent_model("code_generator")
    #    # ^ This reads CODE_GENERATOR_MODEL from .env
    
    # 3. Uses whatever model is in .env
    result = await delegate_task(command)
```

### Hardcoded Test Flow

```python
# test_codestral_optimized.py

from packages.core.agents.codestral_optimized import create_with_codestral_optimized

async def test_codestral_optimized():
    # 1. Load config (for other settings like OLLAMA_BASE_URL)
    init_config()
    
    # 2. create_with_codestral_optimized internally does:
    #    adapter = CodestralOptimizedAdapter()
    #    # Inside adapter.__init__:
    #    self.model = "ollama:codestral"  # HARDCODED!
    
    # 3. ALWAYS uses codestral, ignores .env
    result = await create_with_codestral_optimized(prompt=prompt)
```

---

## How to Make Tests Respect .env (If Desired)

If you want the Codestral tests to respect `.env`, you can modify them:

### Option 1: Add Model Parameter

```python
# Modified codestral_optimized.py
class CodestralOptimizedAdapter:
    def __init__(self, model: str = None, temperature: float = 0.0):
        from ..config import get_config
        
        if model is None:
            # No model provided - read from .env
            config = get_config()
            model = config.get_agent_model("code_generator")
        
        self.model = model  # Now respects .env if no param
        self.temperature = temperature
```

### Option 2: Create Config-Aware Version

```python
# test_codestral_from_env.py
async def test_codestral_from_config():
    config = get_config()
    model = config.get_agent_model("code_generator")
    
    # Use whatever model is in .env
    adapter = NonToolingAdapter(model=model)
    result = await adapter.run(prompt=prompt)
```

---

## Practical Guide

### Scenario 1: "I want to test my current config"

```bash
# Use config-based tests
uv run python test_tetris_game.py
uv run python test_landing_page.py
uv run python run_test_suite.py
```

**These read from .env**

### Scenario 2: "I want to specifically test Codestral"

```bash
# Use model-specific tests
uv run python test_codestral_optimized.py
uv run python test_codestral_adapter.py
```

**These ignore .env and force Codestral**

### Scenario 3: "I want to compare Codestral vs my config"

```bash
# Step 1: Set .env to cogito
CODE_GENERATOR_MODEL=ollama:cogito:14b

# Step 2: Test cogito (from .env)
uv run python test_tetris_game.py  # Uses cogito

# Step 3: Test codestral (hardcoded)
uv run python test_codestral_optimized.py  # Uses codestral

# Step 4: Compare outputs in tests/output/
# - tests/output/cogito_14b/
# - tests/output/codestral_optimized/
```

---

## Summary

**Why tests ignore .env:**
1. Model-specific tests are for **benchmarking**
2. They need to **force a specific model** for comparison
3. They're designed to test **adapters and model capabilities**
4. Config-based tests exist for **testing your actual setup**

**The design is intentional:**
- ✅ Config-based tests → Use for daily work
- ✅ Model-specific tests → Use for research/comparison
- ✅ Both have their place in the test suite

**Your .env still matters:**
- Used by: `test_tetris_game.py`, `test_landing_page.py`, `run_test_suite.py`
- Ignored by: `test_codestral_*.py`, `test_openrouter_*.py`

This separation allows you to have a working daily config (e.g., cogito) while still being able to benchmark other models (codestral) without changing `.env`.
