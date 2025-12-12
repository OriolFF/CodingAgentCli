# Python CLI Agent - Detailed Implementation Plan
## Py danticAI Edition (v1.31.0) - Step-by-Step Guide

> **Framework**: PydanticAI 1.31.0 for production-ready, type-safe agents  
> **Total Steps**: 54 (reduced from 78 custom implementation)  
> **Estimated Time**: 2-3 weeks  
> **Last Updated**: December 12, 2024

---

## 📋 How to Use This Plan

Each step includes:
- **Status**: ✅ Done | 🔄 In Progress | ⏸️ Blocked | 📋 Not Started
- **Instructions**: What to do
- **Definition of Done**: Success criteria
- **Expected Outputs**: Files, features, tests
- **Verification**: How to validate
- **Time Estimate**: Hours needed
- **Dependencies**: Previous steps required

---

## 🎯 Quick Reference

**Completed**: 3/54 steps (5.6%)  
**Current Phase**: Phase 1 - Foundation  
**Next Step**: Step 4 - Add PydanticAI Dependency

---

## PHASE 1: Foundation & Setup (Steps 1-4)

### Step 1: Initialize Python Project with UV ✅

**Status**: ✅ DONE  
**Time**: 1 hour  
**Dependencies**: None  
**Git Commit**: ✅ `87a0bfb`

**Instructions**:
1. Initialize empty git repository
2. Create project directory structure
3. Set up `pyproject.toml` with project metadata
4. Create README.md with project description
5. Configure .gitignore for Python/UV projects
6. Create package structure (packages/cli, packages/core, packages/test_utils)
7. Run `uv venv` to create virtual environment
8. Install dependencies with `uv pip install -e ".[dev]"`

**Definition of Done**:
- [x] Git repository initi alized
- [x] Virtual environment created (.venv/)
- [x] pyproject.toml configured with all dependencies
- [x] Package directories created
- [x] All dependencies installed (109 packages)
- [x] README.md created

**Expected Outputs**:
- Files created:
  - `pyproject.toml` - Project configuration
  - `README.md` - Project documentation
  - `.gitignore` - Git ignore rules
  - `packages/__init__.py`
  - `packages/cli/__init__.py`
  - `packages/core/__init__.py`
  - `packages/test_utils/__init__.py`
- Virtual environment: `.venv/`

**Verification**:
```bash
# Check structure
ls -la packages/
ls -la .venv/

# Verify Python version
uv run python --version  # Should be 3.10+

# List installed packages
uv pip list | wc -l  # Should show 109+ packages
```

**Completed**: ✅ Yes  
**Notes**: Successfully installed 109 packages including multi-provider support

---

### Step 2: Set Up Linting and Formatting ✅

**Status**: ✅ DONE  
**Time**: 30 minutes  
**Dependencies**: Step 1  
**Git Commit**: ✅ `6e3db16`

**Instructions**:
1. Create `.pre-commit-config.yaml`
2. Configure ruff for linting
3. Configure black for formatting (via ruff)
4. Configure mypy for type checking
5. Add pre-commit hooks for:
   - Trailing whitespace removal
   - YAML/TOML validation
   - Merge conflict detection

**Definition of Done**:
- [x] .pre-commit-config.yaml created
- [x] Ruff configured in pyproject.toml
- [x] MyPy configured in pyproject.toml
- [x] All linting tools can run successfully

**Expected Outputs**:
- Files:
  - `.pre-commit-config.yaml`
  - `pyproject.toml` updates with [tool.ruff] and [tool.mypy] sections

**Verification**:
```bash
# Run ruff
uv run ruff check .
# Should output: "All checks passed!"

# Run mypy
uv run mypy packages/
# Should complete without errors
```

**Completed**: ✅ Yes  
**Notes**: All lint tools configured and passing

---

### Step 3: Set Up Testing Framework ✅

**Status**: ✅ DONE  
**Time**: 45 minutes  
**Dependencies**: Step 1, 2  
**Git Commit**: ✅ `6e3db16` (combined with Step 2)

**Instructions**:
1. Create `tests/` directory structure
2. Create `tests/conftest.py` with sample fixtures
3. Create `tests/test_example.py` with sample tests
4. Configure pytest in pyproject.toml:
   - Test discovery
   - Coverage reporting
   - Async test support

**Definition of Done**:
- [x] Test directory structure created
- [x] Sample fixtures in conftest.py
- [x] Sample tests pass
- [x] Coverage reporting configured
- [x] Async test support enabled

**Expected Outputs**:
- Files:
  - `tests/conftest.py` - Shared fixtures
  - `tests/test_example.py` - Sample tests
- Configuration: [tool.pytest.ini_options] in pyproject.toml

**Verification**:
```bash
# Run tests
uv run pytest -v
# Should show: "3 passed"

# Run with coverage
uv run pytest --cov
# Should generate coverage report
```

**Completed**: ✅ Yes  
**Test Results**: 3/3 tests passing  
**Coverage**: 0% (no code yet, only __init__ files)

---

### Step 4: Add PydanticAI Dependency

**Status**: 📋 NOT STARTED  
**Time**: 30 minutes  
**Dependencies**: Step 1  
**Blocked By**: None

**Instructions**:
1. Update `pyproject.toml` dependencies section
2. Add `pydantic-ai = ">=1.31.0"` to dependencies
3. Optionally add `logfire = ">=0.1.0"` for observability
4. Run `uv pip install pydantic-ai`
5. Verify import works: `from pydantic_ai import Agent`
6. Check installed version

**Definition of Done**:
- [ ] pydantic-ai added to pyproject.toml
- [ ] pydantic-ai installed in virtual environment  
- [ ] Can import pydantic_ai without errors
- [ ] Version is 1.31.0 or higher

**Expected Outputs**:
- Files updated:
  - `pyproject.toml` - Updated dependencies
- Packages installed:
  - `pydantic-ai==1.31.0`
  - Related dependencies

**Verification**:
```bash
# Install
uv pip install pydantic-ai

# Check version
uv pip show pydantic-ai
# Should show: Version: 1.31.0

# Test import
uv run python -c "from pydantic_ai import Agent; print('Success')"
# Should output: Success
```

**Git Commit Message Template**:
```
Step 4: Add PydanticAI framework dependency

- Added pydantic-ai>=1.31.0 to dependencies
- Installed and verified import works
- Ready for agent development

Status: ✅ Step 4 Complete
```

---

## PHASE 2: PydanticAI Integration & Configuration (Steps 5-10)

### Step 5: Configuration System - Base

**Status**: 📋 NOT STARTED  
**Time**: 2 hours  
**Dependencies**: Step 4  
**Blocked By**: None

**Instructions**:
1. Create `packages/core/config/` directory
2. Create `packages/core/config/__init__.py`
3. Create `packages/core/config/config.py`:
   - Define `Config` class with Pydantic BaseSettings
   - Add fields: debug, log_level, default_model
4. Create `packages/core/config/loader.py`:
   - Implement YAML file loader
   - Implement environment variable overrides
   - Implement config validation
5. Create `config/` directory at project root
6. Create `config/agents.yaml` with agent configurations
7. Create sample agent configs (default, codebase_investigator, file_editor)

**Definition of Done**:
- [ ] Config package directory created with __init__.py
- [ ] Config class defined with Pydantic BaseSettings
- [ ] YAML loader implemented
- [ ] Environment variable support working
- [ ] Sample agents.yaml created with 3 agent configs
- [ ] Config can be loaded and validated
- [ ] Unit tests for config loading pass

**Expected Outputs**:
- Files:
  - `packages/core/config/__init__.py`
  - `packages/core/config/config.py` - Main config class (~80 lines)
  - `packages/core/config/loader.py` - YAML loader (~60 lines)
  - `config/agents.yaml` - Agent configurations (~50 lines)
- Tests:
  - `tests/unit/test_config.py` - Config loading tests

**Code Template** (`config.py`):
```python
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class AgentConfig(BaseModel):
    """Configuration for a single agent."""
    model: str = Field(description="Model identifier (e.g., 'ollama:mistral')")
    fallback_models: list[str] = Field(default_factory=list)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=4096, gt=0)
    system_prompt: str = ""
    timeout: int = Field(default=300, gt=0)

class Config(BaseSettings):
    """Main application configuration."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="GEMINI_AGENT_",
        case_sensitive=False
    )
    
    debug: bool = False
    log_level: str = "INFO"
    default_model: str = "ollama:mistral"
    agents: dict[str, AgentConfig] = Field(default_factory=dict)
    
    @classmethod
    def from_yaml(cls, path: str) -> "Config":
        """Load config from YAML file."""
        # Implementation in loader.py
```

**agents.yaml Template**:
```yaml
agents:
  default:
    model: "ollama:mistral"
    fallback_models:
      - "ollama:llama2"
      - "gemini-1.5-pro"
    temperature: 0.7
    max_tokens: 4096
    system_prompt: "You are a helpful AI assistant."
    
  codebase_investigator:
    model: "ollama:llama2:13b"
    temperature: 0.3
    max_tokens: 8192
    system_prompt: |
      You are an expert code analyst. Analyze code structure,
      identify patterns, and suggest improvements.
    
  file_editor:
    model: "ollama:mistral"
    temperature: 0.1
    max_tokens: 2048
    system_prompt: "You are a precise code editor."
```

**Verification**:
python
# Test config loading
uv run python -c "
from packages.core.config import Config
config = Config.from_yaml('config/agents.yaml')
print(f'Loaded {len(config.agents)} agents')
print(f'Default model: {config.default_model}')
assert len(config.agents) == 3
print('Config verification: ✅')
"
```

**Tests** (`tests/unit/test_config.py`):
```python
def test_load_config_from_yaml():
    config = Config.from_yaml('config/agents.yaml')
    assert 'default' in config.agents
    assert config.agents['default'].model == 'ollama:mistral'

def test_environment_variable_override():
    os.environ['GEMINI_AGENT_DEFAULT_MODEL'] = 'ollama:test'
    config = Config()
    assert config.default_model == 'ollama:test'
```

**Git Commit**:
```
Step 5: Implement configuration system

- Created Config class with Pydantic BaseSettings
- Implemented YAML config loader
- Added agents.yaml with 3 agent configurations
- Environment variable support for overrides
- Unit tests for config loading

Tests: ✅ 5/5 passing
Status: ✅ Step 5 Complete
```

---

### Step 6: Create First PydanticAI Agent

**Status**: 📋 NOT STARTED  
**Time**: 1.5 hours  
**Dependencies**: Step 4, 5  
**Blocked By**: None

**Instructions**:
1. Create packages/core/agents/` directory
2. Create `packages/core/agents/__init__.py`
3. Create `packages/core/agents/base.py`:
   - Import PydanticAI Agent class
   - Create SimpleResponse Pydantic model
   - Instantiate first agent with ollama:mistral
4. Create simple test query function
5. **IMPORTANT**: Ensure Ollama is running locally
6. Test agent with synchronous call
7. Test agent with async call
8. Add error handling for connection failures

**Definition of Done**:
- [ ] Agents package created
- [ ] First PydanticAI agent instantiated
- [ ] Can make synchronous agent calls
- [ ] Can make async agent calls
- [ ] Structured output (Pydantic model) works
- [ ] Error handling for missing Ollama works
- [ ] Integration test passes

**Expected Outputs**:
- Files:
  - `packages/core/agents/__init__.py`
  - `packages/core/agents/base.py` (~50 lines)
- Tests:
  - `tests/integration/test_first_agent.py` - Agent integration test

**Code** (`base.py`):
```python
"""Base agent implementation using PydanticAI."""

from pydantic import BaseModel, Field
from pydantic_ai import Agent


class SimpleResponse(BaseModel):
    """Structured response from agent."""
    answer: str = Field(description="The answer to the question")
    confidence: float = Field(
        description="Confidence score 0-1",
        ge=0.0,
        le=1.0
    )


# Create first PydanticAI agent
simple_agent = Agent(
    'ollama:mistral',
    output_type=SimpleResponse,
    system_prompt='You are a helpful assistant. Provide concise answers.',
)


async def test_agent_async(question: str) -> SimpleResponse:
    """Test agent with async call."""
    result = await simple_agent.run(question)
    return result.output


def test_agent_sync(question: str) -> SimpleResponse:
    """Test agent with sync call."""
    result = simple_agent.run_sync(question)
    return result.output
```

**Integration Test** (`tests/integration/test_first_agent.py`):
```python
import pytest
from packages.core.agents.base import simple_agent, test_agent_sync, test_agent_async


def test_agent_sync_call():
    """Test synchronous agent call."""
    result = test_agent_sync("What is 2+2?")
    assert isinstance(result.answer, str)
    assert "4" in result.answer.lower()
    assert 0 <= result.confidence <= 1


@pytest.mark.asyncio
async def test_agent_async_call():
    """Test asynchronous agent call."""
    result = await test_agent_async("What is Python?")
    assert isinstance(result.answer, str)
    assert len(result.answer) > 10
   assert 0 <= result.confidence <= 1


@pytest.mark.asyncio
async def test_agent_structured_output():
    """Test that output matches Pydantic model."""
    result = await test_agent_async("Say hello")
    # Pydantic validation ensures structure
    assert hasattr(result, 'answer')
    assert hasattr(result, 'confidence')
```

**Verification**:
```bash
# Ensure Ollama is running
curl http://localhost:11434/api/tags
# Should list available models

# Run integration test
uv run pytest tests/integration/test_first_agent.py -v
# Should show: "3 passed"

# Manual test
uv run python -c "
from packages.core.agents.base import test_agent_sync
result = test_agent_sync('What is 2+2?')
print(f'Answer: {result.answer}')
print(f'Confidence: {result.confidence}')
"
```

**Prerequisites**:
- Ollama installed and running
- Mistral model pulled: `ollama pull mistral`

**Git Commit**:
```
Step 6: Create first PydanticAI agent

- Implemented simple_agent with ollama:mistral
- Created SimpleResponse Pydantic model for structured output
- Added sync and async agent call wrappers
- Integration tests for agent calls (3/3 passing)
- Verified structured output validation works

Prerequisites: ✅ Ollama running with mistral model
Tests: ✅ 3/3 integration tests passing
Status: ✅ Step 6 Complete
```

---

### Step 7: Multi-Provider Support Test

**Status**: 📋 NOT STARTED  
**Time**: 1 hour  
**Dependencies**: Step 6  
**Blocked By**: API keys for cloud providers (optional)

**Instructions**:
1. Create `tests/integration/test_providers.py`
2. Test Ollama provider with local model
3. Test OpenAI-compatible provider (if available)
4. Test Gemini provider (if API key available)
5. Implement graceful skipping for unavailable providers
6. Test model switching at runtime
7. Document provider setup requirements

**Definition of Done**:
- [ ] Provider tests created
- [ ] Ollama provider test passes
- [ ] OpenAI-compatible test (or skipped gracefully)
- [ ] Gemini test (or skipped gracefully)
- [ ] Runtime model switching tested
- [ ] Documentation for provider setup created

**Expected Outputs**:
- Files:
  - `tests/integration/test_providers.py` (~150 lines)
  - `docs/providers_setup.md` - Provider setup guide

**Code** (`test_providers.py`):
```python
import pytest
import os
from pydantic_ai import Agent
from pydantic import BaseModel


class TestResponse(BaseModel):
    text: str


@pytest.mark.integration
def test_ollama_provider():
    """Test Ollama local provider."""
    agent = Agent('ollama:mistral', output_type=TestResponse)
    result = agent.run_sync("Say 'test'")
    assert isinstance(result.output.text, str)
    assert len(result.output.text) > 0


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv('OPENAI_API_KEY'),
    reason="OpenAI API key not available"
)
def test_openai_provider():
    """Test OpenAI provider."""
    agent = Agent('openai:gpt-4o-mini', output_type=TestResponse)
    result = agent.run_sync("Say 'test'")
    assert isinstance(result.output.text, str)


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv('GEMINI_API_KEY'),
    reason="Gemini API key not available"
)
def test_gemini_provider():
    """Test Gemini provider."""
    agent = Agent('gemini-1.5-flash', output_type=TestResponse)
    result = agent.run_sync("Say 'test'")
    assert isinstance(result.output.text, str)


@pytest.mark.integration
def test_model_switching():
    """Test switching models at runtime."""
    # Start with one model
    agent1 = Agent('ollama:mistral', output_type=TestResponse)
    result1 = agent1.run_sync("Say hello")
    
    # Create agent with different model
    agent2 = Agent('ollama:llama2', output_type=TestResponse)
    result2 = agent2.run_sync("Say hello")
    
    # Both should work
    assert len(result1.output.text) > 0
    assert len(result2.output.text) > 0
```

**Verification**:
```bash
# Run only Ollama tests
uv run pytest tests/integration/test_providers.py::test_ollama_provider -v
# Should pass

# Run all provider tests (some may skip)
uv run pytest tests/integration/test_providers.py -v
# Should show: X passed, Y skipped
```

**Git Commit**:
```
Step 7: Add multi-provider support tests

- Created provider integration tests
- Tested Ollama local provider (passing)
- Added OpenAI and Gemini tests with graceful skipping
- Verified runtime model switching works
- Documented provider setup requirements

Tests: ✅ Ollama passing, others skipped (no API keys)
Status: ✅ Step 7 Complete
```

---

*[Continuing with Steps 8-54 in same detailed format...]*

---

## Summary of Detailed Plan Structure

Each of the remaining 47 steps (8-54) follows this exact format:

- **Status tracking**: ✅/🔄/⏸️/📋
- **Time estimate**: Realistic hours needed
- **Detailed instructions**: Step-by-step what to do
- **Definition of Done**: Clear checklist
- **Expected Outputs**: Exact files with line counts
- **Code templates**: Working code examples
- **Verification steps**: Bash commands to validate
- **Git commit templates**: Consistent commit messages
- **Dependencies**: What must be done first
- **Prerequisites**: External requirements

---

## Next Steps Checklist

To continue implementation:

1. **[Current]** Review Steps 1-3 (completed)
2. **[Next]** Execute Step 4: Add PydanticAI
3. **[Then]** Execute Step 5: Config system
4. **[Then]** Execute Step 6: First agent
5. Follow the plan sequentially through all 54 steps
6. Make git commits after each step/logical group
7. Update status markers as you progress

---

## Questions or Clarifications Needed?

Before proceeding with the full detailed plan:
1. Should I continue with all 54 steps in this detail?
2. Do you want the full plan as a separate document?
3. Any specific steps you want more/less detail on?

**Total Plan Size**: Full detailed plan ~ 15,000-20,000 lines
