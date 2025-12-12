# Python CLI Agent Implementation Plan - PydanticAI Edition
## Leveraging PydanticAI for Multi-Provider Agent Framework

> **Goal**: Build a Python-based CLI agent using PydanticAI for model-agnostic architecture with Ollama, OpenAI-compatible APIs, and per-agent model configuration.

> **Current Progress**: 13/54 steps (24%) | Phase 3 In Progress  
> **Last Updated**: December 12, 2024

## 🎯 Why PydanticAI?

**PydanticAI eliminates 24 implementation steps** by providing:
- ✅ Built-in multi-provider support (Ollama, OpenAI, Gemini, Anthropic, LiteLLM)
- ✅ Type-safe agent framework with structured outputs
- ✅ Tool calling with dependency injection
- ✅ MCP (Model Context Protocol) native integration
- ✅ Human-in-the-loop workflows
- ✅ Streaming and async support
- ✅ Production-ready from the Pydantic team

**Result**: 54 focused steps (vs 78 custom implementation) - **31% reduction**

---

## 📊 Progress Tracker

| Phase | Steps | Status | Completion |
|-------|-------|--------|------------|
| Phase 1: Foundation & Setup | 1-4 | ✅ Complete | 4/4 (100%) |
| Phase 2: PydanticAI Integration & Config | 5-10 | ✅ Complete | 6/6 (100%) |
| Phase 3: Core Tools | 11-25 | 🔄 In Progress | 3/15 (20%) |
| Phase 4: Specialized Agents | 26-32 | 📋 Not Started | 0/7 (0%) |
| Phase 5: Services Layer | 33-37 | 📋 Not Started | 0/5 (0%) |
| Phase 6: Safety & Policy | 38-40 | 📋 Not Started | 0/3 (0%) |
| Phase 7: CLI Interface | 41-48 | 📋 Not Started | 0/8 (0%) |
| Phase 8: Testing & Integration | 49-52 | 📋 Not Started | 0/4 (0%) |
| Phase 9: Advanced Features | 53-54 | 📋 Not Started | 0/2 (0%) |
| **TOTAL** | **1-54** | **24% Complete** | **13/54** |

---

## Updated Project Structure

```
gemini-agent-py/
├── packages/
│   ├── cli/                      # CLI package (UI/UX)
│   │   ├── cli.py
│   │   ├── commands/
│   │   ├── ui/
│   │   └── config/
│   ├── core/                     # Core package (backend)
│   │   ├── agents/               # ✅ PydanticAI agents
│   │   │   ├── base.py          # ✅ Done
│   │   │   ├── factory.py       # ✅ Done
│   │   │   ├── codebase_investigator.py
│   │   │   ├── file_editor.py
│   │   │   └── registry.py
│   │   ├── tools/                # ✅ PydanticAI tools (In Progress)
│   │   │   ├── base.py          # ✅ Done
│   │   │   ├── file_operations.py # ✅ Done
│   │   │   ├── search.py        # TODO
│   │   │   ├── shell.py         # TODO
│   │   │   ├── web.py           # TODO
│   │   │   └── mcp_tools.py     # TODO
│   │   ├── services/             # TODO
│   │   ├── config/               # ✅ Done
│   │   │   ├── config.py        # ✅ Done
│   │   │   └── loader.py        # ✅ Done
│   │   └── utils/                # ✅ Done
│   │       ├── logger.py        # ✅ Done
│   │       └── errors.py        # ✅ Done
│   └── test_utils/
├── config/
│   ├── agents.yaml               # ✅ Agent configurations
│   └── policy.toml               # TODO Safety policies
├── tests/                        # ✅ 39 tests passing
│   ├── unit/                     # ✅ 36 tests
│   └── integration/              # ✅ 3 tests
├── docs/                         # ✅ Documentation
│   ├── implementation_plan.md   # ✅ This file
│   └── model_compatibility.md   # ✅ Done
└── pyproject.toml                # ✅ Done
```

---

## Updated Dependencies

```toml
[project.dependencies]
# Core Framework
pydantic-ai = ">=1.31.0"           # ✅ Installed - Main agent framework
pydantic = ">=2.0.0"               # ✅ Installed
pydantic-settings = ">=2.0.0"      # ✅ Installed

# Terminal UI
rich = ">=13.0.0"                  # ✅ Installed
click = ">=8.1.0"                  # ✅ Installed

# Async I/O
httpx = ">=0.25.0"                 # ✅ Installed
aiofiles = ">=23.0.0"              # ✅ Installed

# Provider SDKs (used by PydanticAI)
ollama = ">=0.1.0"                 # ✅ Installed - Local models
openai = ">=1.0.0"                 # ✅ Installed - OpenAI + compatible APIs
google-generativeai = ">=0.3.0"    # ✅ Installed - Gemini
anthropic = ">=0.8.0"              # ✅ Installed - Claude (optional)

# Configuration
pyyaml = ">=6.0.0"                 # ✅ Installed

# Optional: Additional capabilities
logfire = ">=0.1.0"                # Optional - Observability
```

---

## PHASE 1: Foundation & Setup (Steps 1-4) ✅ COMPLETED

### Step 1: Initialize Python Project ✅
**Status**: ✅ Complete  
**Files Created**: `pyproject.toml`, `README.md`, `.gitignore`, `packages/**/__init__.py`  
**Git Commit**: ✅ `87a0bfb` "Step 1: Initialize Python project with UV"  
**Tests**: ✅ 3 initial tests passing
**Files to Create**:
- Update `pyproject.toml` - Add `pydantic-ai` dependency

**Purpose**: Add PydanticAI framework to project

**Actions**:
- Add `pydantic-ai` to dependencies
- Add `logfire` (optional observability)
- Run `uv pip install pydantic-ai`

**Test**: `uv pip list | grep pydantic-ai`
**Verification**: PydanticAI installed and importable

---

## PHASE 2: PydanticAI Integration & Config (Steps 5-10)

### Step 5: Configuration System - Base
**Files to Create**:
- `packages/core/config/config.py` - Main configuration class
- `packages/core/config/loader.py` - YAML/TOML loader
- `config/agents.yaml` - Agent configurations

**Purpose**: Configuration management for agents and models

**agents.yaml** Example:
```yaml
agents:
  default:
    model: ollama:mistral
    fallback_models:
      - ollama:llama2
      - gemini-1.5-pro
    temperature: 0.7
    max_tokens: 4096
    
  codebase_investigator:
    model: ollama:llama2:13b
    temperature: 0.3
    system_prompt: "You are an expert code analyst..."
    
  file_editor:
    model: ollama:mistral
    temperature: 0.1
    system_prompt: "You are a precise code editor..."
```

**Test**: Load and parse YAML config
**Verification**: Config objects validate with Pydantic

---

### Step 6: Create First PydanticAI Agent
**Files to Create**:
- `packages/core/agents/base.py` - Base agent wrapper around PydanticAI

**Purpose**: Create simple agent to verify PydanticAI works

**Content**:
```python
from pydantic_ai import Agent
from pydantic import BaseModel

class SimpleResponse(BaseModel):
    """Structured response from agent."""
    answer: str
    confidence: float

# Create first agent
simple_agent = Agent(
    'ollama:mistral',
    output_type=SimpleResponse,
    system_prompt='You are a helpful assistant.',
)
```

**Test**: Run agent with simple query
**Verification**: Agent responds correctly with Ollama

---

### Step 7: Multi-Provider Support Test
**Files to Create**:
- `tests/integration/test_providers.py` - Test different providers

**Purpose**: Verify all providers work

**Test Cases**:
- Ollama local model
- OpenAI-compatible API
- Gemini (if API key available)

**Test**: Integration tests with each provider
**Verification**: All configured providers respond

---

### Step 8: Agent Configuration Loader
**Files to Create**:
- `packages/core/agents/config.py` - Load agents from YAML
- `packages/core/agents/factory.py` - Agent factory pattern

**Purpose**: Create agents from configuration files

**Content**:
```python
from pydantic_ai import Agent
from ..config import load_agent_config

class AgentFactory:
    """Create PydanticAI agents from configuration."""
    
    @staticmethod
    def create_agent(name: str) -> Agent:
        config = load_agent_config(name)
        return Agent(
            config.model,
            system_prompt=config.system_prompt,
            retries=config.retries,
        )
```

**Test**: Load agents from config
**Verification**: Agents created with correct models

---

### Step 9: Logging System
**Files to Create**:
- `packages/core/utils/logger.py` - Structured logging

**Purpose**: Logging with model/provider context

**Test**: Log at different levels
**Verification**: Logs include model information

---

### Step 10: Error Handling Framework
**Files to Create**:
- `packages/core/utils/errors.py` - Custom exceptions

**Purpose**: Agent-specific error handling

**Exceptions**:
- `AgentError` - Base exception
- `ModelNotAvailableError`
- `ToolExecutionError`
- `ValidationError`

**Test**: Raise and catch exceptions
**Verification**: Exception hierarchy works

---

## PHASE 3: Core Tools with PydanticAI (Steps 11-25)

### Step 11: Tool Base Infrastructure
**Files to Create**:
- `packages/core/tools/base.py` - Tool base classes
- `packages/core/tools/registry.py` - Tool registry

**Purpose**: Infrastructure for managing tools

**Test**: Register mock tool
**Verification**: Registry stores and retrieves tools

---

### Step 12: File Read Tool
**Files to Create**:
- `packages/core/tools/file_ops.py` - File operations

**Purpose**: Read file contents with PydanticAI

**Content**:
```python
from pydantic_ai import RunContext
from pydantic import Field

@agent.tool
async def read_file(ctx: RunContext, path: str) -> str:
    """Read file contents.
    
    Args:
        path: Absolute or relative file path
        
    Returns:
        File contents as string
    """
    async with aiofiles.open(path, 'r') as f:
        return await f.read()
```

**Test**: Read test files
**Verification**: Files read correctly

---

### Step 13: File Write Tool
**Files to Update**:
- `packages/core/tools/file_ops.py` - Add write_file

**Purpose**: Write/create files

**Content**:
```python
@agent.tool
async def write_file(
    ctx: RunContext,
    path: str,
    content: str,
    create_dirs: bool = True
) -> str:
    """Write content to file."""
    if create_dirs:
        os.makedirs(os.path.dirname(path), exist_ok=True)
    
    async with aiofiles.open(path, 'w') as f:
        await f.write(content)
    
    return f"Wrote {len(content)} bytes to {path}"
```

**Test**: Write files
**Verification**: Files created with correct content

---

### Step 14: File Edit Tool
**Files to Update**:
- `packages/core/tools/file_ops.py` - Add edit_file

**Purpose**: Edit files with diffs

**Content**: Uses diff generation for safe edits

**Test**: Edit test files
**Verification**: Edits apply correctly

---

### Step 15-16: Search Tools (ls, glob, grep)
**Files to Create**:
- `packages/core/tools/search.py` - Search tools

**Tools**:
- `list_directory()` - List files
- `glob_search()` - Pattern matching
- `grep_search()` - Content search

**Test**: Search operations
**Verification**: Search results accurate

---

### Step 17: Shell Execution Tool
**Files to Create**:
- `packages/core/tools/shell.py` - Shell command execution

**Purpose**: Execute shell commands safely

**Content**:
```python
from pydantic_ai import RunContext

@agent.tool(retries=0)  # No retries for shell commands
async def execute_shell(
    ctx: RunContext,
    command: str,
    timeout: int = 30
) -> str:
    """Execute shell command.
    
    ⚠️ Requires user approval for dangerous commands.
    """
    # Safety checks
    if any(danger in command for danger in ['rm -rf', 'sudo', '|']):
        raise ValueError("Dangerous command detected")
    
    # Execute
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await asyncio.wait_for(
        process.communicate(),
        timeout=timeout
    )
    return stdout.decode()
```

**Test**: Execute safe commands
**Verification**: Output correct, dangerous commands blocked

---

### Step 18-19: Web Tools
**Files to Create**:
- `packages/core/tools/web.py` - Web operations

**Tools**:
- `fetch_url()` - HTTP GET
- `web_search()` - Search integration

**Test**: Fetch URLs
**Verification**: Content retrieved

---

### Step 20: Memory Tool
**Files to Create**:
- `packages/core/tools/memory.py` - Persistent memory

**Purpose**: Long-term memory with SQLite

**Test**: Store and retrieve memories
**Verification**: Persistence works

---

### Step 21-23: MCP Client Integration
**Files to Create**:
- `packages/core/tools/mcp_client.py` - MCP integration

**Purpose**: Connect to MCP servers using PydanticAI's native support

**Content**:
```python
# PydanticAI has native MCP support
from pydantic_ai.mcp import MCPClient

async def connect_mcp_server(server_url: str):
    """Connect to MCP server and register tools."""
    client = MCPClient(server_url)
    await client.connect()
    return client.get_tools()
```

**Test**: Connect to MCP server
**Verification**: MCP tools available

---

### Step 24: Tool Error Handling
**Files to Create**:
- `packages/core/tools/errors.py` - Tool-specific errors

**Purpose**: Tool execution error handling

**Test**: Trigger tool errors
**Verification**: Errors handled gracefully

---

### Step 25: Modifiable Tools & Human-in-the-Loop
**Files to Create**:
- `packages/core/tools/approval.py` - Tool approval system

**Purpose**: User confirmation for dangerous operations

**Content**:
```python
# PydanticAI supports deferred tool execution
from pydantic_ai import Agent

agent = Agent(
    'ollama:mistral',
    defer_tool_calls=['write_file', 'execute_shell']
)

# Tools requiring approval are deferred
# Implementation in CLI will prompt user
```

**Test**: Mock approval flow
**Verification**: Dangerous tools require approval

---

## PHASE 4: Specialized Agents (Steps 26-32)

### Step 26: Agent Registry
**Files to Create**:
- `packages/core/agents/registry.py` - Central agent registry

**Purpose**: Register and manage all agents

**Content**:
```python
class AgentRegistry:
    """Registry for all PydanticAI agents."""
    
    def __init__(self):
        self._agents: dict[str, Agent] = {}
    
    def register(self, name: str, agent: Agent):
        self._agents[name] = agent
    
    def get(self, name: str) -> Agent:
        return self._agents[name]
    
    def list_agents(self) -> list[str]:
        return list(self._agents.keys())

# Global registry
agent_registry = AgentRegistry()
```

**Test**: Register and retrieve agents
**Verification**: Registry operations work

---

### Step 27: Codebase Investigator Agent
**Files to Create**:
- `packages/core/agents/codebase_investigator.py` - Code analysis agent

**Purpose**: Specialized agent for code analysis

**Content**:
```python
from pydantic_ai import Agent
from pydantic import BaseModel, Field

class CodeAnalysis(BaseModel):
    """Structured code analysis output."""
    summary: str = Field(description="Code overview")
    complexity: int = Field(description="Complexity score 1-10")
    suggestions: list[str] = Field(description="Improvement suggestions")

codebase_agent = Agent(
    'ollama:llama2:13b',  # Larger model for code
    output_type=CodeAnalysis,
    system_prompt='''You are an expert code analyst.
    Analyze code structure, identify patterns, and suggest improvements.
    Focus on architecture, maintainability, and best practices.''',
)

# Register tools specific to this agent
@codebase_agent.tool
async def analyze_directory(path: str) -> dict:
    """Analyze directory structure."""
    # Implementation
```

**Test**: Analyze sample codebase
**Verification**: Quality analysis produced

---

### Step 28: File Editor Agent
**Files to Create**:
- `packages/core/agents/file_editor.py` - Precise file editing agent

**Purpose**: Agent optimized for file edits

**Content**:
```python
from pydantic import BaseModel

class EditResult(BaseModel):
    """Structured edit result."""
    success: bool
    files_modified: list[str]
    changes_made: str

file_editor_agent = Agent(
    'ollama:mistral',
    output_type=EditResult,
    temperature=0.1,  # Very low for precision
    system_prompt='You are a precise code editor. Make minimal, targeted changes.',
)
```

**Test**: Edit files
**Verification**: Edits are precise

---

### Step 29: Agent Delegation System
**Files to Create**:
- `packages/core/agents/delegation.py` - Agent-to-agent delegation

**Purpose**: Delegate tasks to specialized agents

**Content**:
```python
@main_agent.tool
async def delegate_to_specialist(
    ctx: RunContext,
    task_type: str,
    task_description: str
) -> str:
    """Delegate to specialized agent.
    
    Args:
        task_type: 'code_analysis' | 'file_edit' | 'research'
        task_description: What to do
    """
    specialist = agent_registry.get(task_type)
    result = await specialist.run(task_description)
    return result.output
```

**Test**: Delegation workflow
**Verification**: Sub-agents execute correctly

---

### Step 30-32: Additional Specialized Agents
**Files to Create**:
- `packages/core/agents/researcher.py` - Web research agent
- `packages/core/agents/refactorer.py` - Code refactoring agent

**Purpose**: More specialized agents for specific tasks

**Test**: Specialized workflows
**Verification**: Each agent performs well in domain

---

## PHASE 5: Services Layer (Steps 33-37)

### Step 33: File Discovery Service
**Files to Create**:
- `packages/core/services/file_discovery.py`

**Purpose**: Intelligent file discovery

**Test**: Discover relevant files
**Verification**: Ranking algorithm works

---

### Step 34: Git Service  
**Files to Create**:
- `packages/core/services/git_service.py`

**Purpose**: Git operations

**Test**: Git queries
**Verification**: Status, diff work

---

### Step 35: Context Manager Service
**Files to Create**:
- `packages/core/services/context_manager.py`

**Purpose**: Manage conversation context window

**Test**: Context budgeting
**Verification**: Token limits respected

---

### Step 36: File System Service
**Files to Create**:
- `packages/core/services/file_system.py`

**Purpose**: Async file operations with caching

**Test**: File operations
**Verification**: Performance good

---

### Step 37: Shell Execution Service
**Files to Create**:
- `packages/core/services/shell_execution.py`

**Purpose**: Managed shell execution with sandboxing

**Test**: Execute commands
**Verification**: Security measures work

---

## PHASE 6: Safety & Policy (Steps 38-40)

### Step 38: Confirmation Bus
**Files to Create**:
- `packages/core/safety/confirmation.py` - User confirmation system

**Purpose**: Human-in-the-loop confirmations

**Content**: Integrates with PydanticAI's deferred tools

**Test**: Mock confirmation flow
**Verification**: Dangerous operations blocked until approved

---

### Step 39: Policy Engine
**Files to Create**:
- `packages/core/safety/policy_engine.py`
- `config/policy.toml` - Policy rules

**Purpose**: Policy-based restrictions

**policy.toml** Example:
```toml
[tool_restrictions]
write_file.max_size_kb = 1024
execute_shell.allowed_commands = ["ls", "cat", "grep"]
execute_shell.blocked_patterns = ["rm -rf", "sudo"]

[rate_limits]
api_calls_per_minute = 60
```

**Test**: Policy evaluation
**Verification**: Policies enforced

---

### Step 40: Safety Checks
**Files to Create**:
- `packages/core/safety/checks.py` - Content safety

**Purpose**: Input/output safety validation

**Test**: Safety scenarios
**Verification**: Unsafe content blocked

---

## PHASE 7: CLI Interface (Steps 41-48)

### Step 41: CLI Framework Setup
**Files to Create**:
- `packages/cli/cli.py` - Main CLI entry point using Click

**Content**:
```python
import click
from packages.core.agents import agent_registry

@click.group()
def cli():
    """Gemini Agent - AI-powered CLI assistant."""
    pass

@cli.command()
@click.option('--model', default='ollama:mistral')
@click.option('--agent', default='default')
def chat(model, agent):
    """Start interactive chat."""
    # Implementation
```

**Test**: `gemini-agent --help`
**Verification**: CLI commands listed

---

### Step 42: Model Management Commands
**Files to Create**:
- `packages/cli/commands/model.py`

**Commands**:
- `model list` - List available models
- `model test <model>` - Test model connectivity
- `model set <agent> <model>` - Configure agent model

**Test**: Model commands
**Verification**: Models listed correctly

---

### Step 43: Rich Terminal UI
**Files to Create**:
- `packages/cli/ui/layout.py` - Terminal layout with Rich
- `packages/cli/ui/components.py` - Reusable UI components

**Purpose**: Beautiful terminal interface

**Test**: Render UI
**Verification**: Visual quality

---

### Step 44: Interactive Chat Mode
**Files to Create**:
- `packages/cli/commands/chat.py` - Interactive REPL

**Purpose**: Conversational interface with streaming

**Content**:
```python
from pydantic_ai import Agent
from rich.console import Console
from rich.markdown import Markdown

async def interactive_chat(agent: Agent):
    """Interactive chat with streaming."""
    console = Console()
    
    while True:
        user_input = console.input("[bold blue]You:[/] ")
        
        # Stream response
        async with agent.run_stream(user_input) as stream:
            console.print("[bold green]Agent:[/]", end=" ")
            async for text in stream.text():
                console.print(text, end="")
            console.print()
```

**Test**: Chat session
**Verification**: Streaming works smoothly

---

### Step 45: Non-Interactive Mode
**Files to Create**:
- `packages/cli/non_interactive.py`

**Purpose**: Pipe input for scripting

**Test**: `echo "test" | gemini-agent`
**Verification**: Non-interactive execution works

---

### Step 46: Theme System
**Files to Create**:
- `packages/cli/ui/themes.py` - UI themes

**Purpose**: Customizable color schemes

**Test**: Switch themes
**Verification**: Themes apply correctly

---

### Step 47: History Management
**Files to Create**:
- `packages/cli/history.py` - Session history
- `data/history.db` - SQLite storage

**Purpose**: Conversation history persistence

**Test**: Save/load history
**Verification**: History persists across sessions

---

### Step 48: Configuration Commands
**Files to Create**:
- `packages/cli/commands/config.py`

**Commands**:
- `config show`
- `config set <key> <value>`
- `config reset`

**Test**: Config manipulation
**Verification**: Config changes persist

---

## PHASE 8: Testing & Integration (Steps 49-52)

### Step 49: Integration Test Suite
**Files to Create**:
- `tests/integration/test_agents.py` - Agent integration tests
- `tests/integration/test_tools.py` - Tool integration tests
- `tests/integration/test_workflows.py` - End-to-end workflows

**Purpose**: Comprehensive integration testing

**Test**: Full workflows
**Verification**: All scenarios pass

---

### Step 50: Mock Provider for Testing
**Files to Create**:
- `tests/fixtures/mock_provider.py` - Mock LLM responses

**Purpose**: Test without real API calls

**Test**: Run tests offline
**Verification**: All tests pass without APIs

---

### Step 51: Performance Tests
**Files to Create**:
- `tests/performance/test_benchmarks.py`

**Purpose**: Performance validation

**Test**: Benchmark operations
**Verification**: Performance acceptable

---

### Step 52: Documentation
**Files to Create**:
- `docs/index.md` - Main documentation
- `docs/agents.md` - Agent configuration guide
- `docs/tools.md` - Tool development guide  
- `docs/local_setup.md` - Ollama setup guide

**Purpose**: Comprehensive documentation

**Test**: Build docs
**Verification**: Docs complete and accurate

---

## PHASE 9: Advanced Features (Steps 53-54)

### Step 53: Agent Benchmarking
**Files to Create**:
- `packages/cli/commands/benchmark.py` - Model comparison tool
- `tools/benchmark_suite.py` - Benchmark tests

**Purpose**: Compare model performance

**Commands**:
- `benchmark models` - Test all configured models
- `benchmark agent <name>` - Benchmark specific agent

**Test**: Benchmark suite
**Verification**: Performance metrics generated

---

### Step 54: Provider Health Monitoring
**Files to Create**:
- `packages/core/monitoring/health.py` - Health checks
- `packages/cli/commands/status.py` - Status command

**Commands**:
- `status` - Show all provider status
- `status ollama` - Ollama-specific status
- `status models` - Available models

**Test**: Health checks
**Verification**: Status reporting accurate

---

## Summary: 54 Steps vs 78 Original

### Steps Eliminated (24 steps, 31%)

**Provider Abstraction (Steps 5-11 in original)**: ❌ Removed
- PydanticAI handles all provider abstraction

**Model Configuration Management (Steps 10-13 in original)**: ❌ Removed  
- PydanticAI's native model configuration

**Core API Client Layer (Steps 21-28 in original)**: ❌ Removed
- PydanticAI's `Agent.run()` and `Agent.run_stream()`
- Tool schema generation automatic
- Response parsing built-in
- Token management handled

### Implementation Time Estimate

- **Original Plan**: ~3-4 weeks for 78 steps
- **With PydanticAI**: ~2 weeks for 54 steps
- **Time Saved**: ~40% development time

### Lines of Code Estimate

- **Original Plan**: ~5,000 lines custom code
- **With PydanticAI**: ~2,000 lines (60% reduction)
- **Simplified**: Provider layer: 700 lines → 10 lines

---

## Next Steps

1. ✅ Project initialized with UV
2. ✅ Dependencies installed  
3. ✅ Testing framework configured
4. **→ Add PydanticAI** (Step 4)
5. Create first agent with Ollama
6. Build tools using `@agent.tool` decorator
7. Implement CLI interface
8. Test and iterate

---

## Git Commit Strategy

After each step or logical group of steps:
```bash
git add .
git commit -m "Step X: [Description]

- Created [files]
- Implemented [features]
- Tests: [results]

Status: ✅ Step X Complete"
```

This revised plan leverages PydanticAI's production-ready framework to build a powerful, type-safe, multi-provider agent system with significantly less code and complexity.


## 🔑 Key Architecture Changes

### Model Provider Abstraction
- **Support multiple providers**: Ollama, OpenAI, Google Gemini, Anthropic, etc.
- **Per-agent configuration**: Each agent can use a different model
- **Local-first approach**: Prioritize Ollama for offline/privacy
- **Unified interface**: Abstract provider differences

### New Components
1. **Provider Interface Layer** - Abstract model providers
2. **Model Registry** - Register and discover available models
3. **Agent-Model Binding** - Configure which model each agent uses
4. **Provider Adapters** - Ollama, OpenAI, Gemini adapters

---

## Architecture Mapping: Multi-Provider Design

| Component | Original | Model-Agnostic Version |
|-----------|----------|----------------------|
| API Client | Gemini-specific | Provider abstraction |
| Model Config | Single model | Per-agent models |
| Authentication | Google auth | Provider-specific auth |
| Tool schemas | Gemini format | Provider-agnostic JSON |

---

## Project Structure

```
gemini-agent-py/
├── packages/
│   ├── cli/                      # CLI package (UI/UX)
│   │   ├── cli.py
│   │   ├── commands/
│   │   ├── ui/
│   │   └── config/
│   ├── core/                     # Core package (backend)
│   │   ├── providers/            # NEW: Multi-provider support
│   │   │   ├── base.py
│   │   │   ├── ollama.py
│   │   │   ├── openai_compat.py
│   │   │   ├── gemini.py
│   │   │   └── registry.py
│   │   ├── models/               # NEW: Model management
│   │   │   ├── config.py
│   │   │   ├── registry.py
│   │   │   └── schemas.py
│   │   ├── agents/
│   │   ├── tools/
│   │   ├── services/
│   │   └── core/
│   └── test_utils/
├── config/
│   ├── models.yaml               # Model configurations
│   ├── agents.yaml               # Agent-model bindings
│   └── providers.yaml            # Provider credentials
├── tests/
├── docs/
└── pyproject.toml
```

---

## Updated Dependency Stack

```toml
[tool.poetry.dependencies]
python = "^3.10"
rich = "^13.0.0"                    # Terminal UI
click = "^8.1.0"                    # CLI framework
httpx = "^0.25.0"                   # Async HTTP client
pydantic = "^2.0.0"                 # Data validation
aiofiles = "^23.0.0"                # Async file I/O

# Multi-Provider Support
openai = "^1.0.0"                   # OpenAI client (works with compatible APIs)
google-generativeai = "^0.3.0"      # Gemini API
anthropic = "^0.8.0"                # Claude API (optional)
ollama = "^0.1.0"                   # Ollama Python client
litellm = "^1.0.0"                  # Unified LLM interface

# MCP and Extensions
mcp = "^0.1.0"                      # MCP protocol
```

---

## PHASE 1: Foundation & Model Abstraction (Steps 1-15)

### Step 1: Initialize Python Project
**Files Created**:
- `pyproject.toml` - Project configuration and dependencies
- `README.md` - Project documentation
- `.gitignore` - Git ignore patterns
- `setup.py` - Package setup (if needed)

**Purpose**: Set up project structure with multi-provider dependencies

**Actions**:
- Create project directory structure
- Initialize `pyproject.toml` with Poetry
- Add multi-provider dependencies (ollama, openai, google-generativeai, litellm)
- Configure Python 3.10+ requirement
- Set up virtual environment

**Test**: Run `poetry install` and verify all dependencies install
**Verification**: `poetry run python --version` shows Python 3.10+, `poetry show` lists all providers

---

### Step 2: Set Up Linting and Formatting
**Files Created**:
- `.ruff.toml` or `pyproject.toml` [tool.ruff] - Ruff configuration
- `.mypy.ini` or `pyproject.toml` [tool.mypy] - MyPy type checking config
- `.pre-commit-config.yaml` - Pre-commit hooks

**Purpose**: Code quality tools configuration

**Actions**:
- Configure ruff for linting
- Configure black for formatting
- Configure mypy for type checking
- Set up pre-commit hooks

**Test**: Run lint tools on sample file
**Verification**: `ruff check .` and `mypy .` run successfully

---

### Step 3: Set Up Testing Framework  
**Files Created**:
- `pytest.ini` or `pyproject.toml` [tool.pytest] - Pytest configuration
- `tests/conftest.py` - Pytest fixtures and configuration
- `tests/__init__.py` - Test package marker
- `tests/test_example.py` - Sample test

**Purpose**: Testing infrastructure with async support

**Actions**:
- Add pytest, pytest-asyncio, pytest-cov
- Configure test discovery
- Set up coverage reporting
- Create sample test

**Test**: Run `pytest`
**Verification**: Tests pass with coverage report

---

### Step 4: Create Package Structure
**Files Created**:
- `packages/__init__.py`
- `packages/cli/__init__.py`
- `packages/core/__init__.py`
- `packages/test_utils/__init__.py`
- `packages/core/providers/__init__.py` - NEW: Provider package
- `packages/core/models/__init__.py` - NEW: Model management package

**Purpose**: Mono-repo package layout with provider abstraction

**Actions**:
- Create directory structure
- Add `__init__.py` files
- Configure package discovery
- Set up import paths

**Test**: Import packages in Python REPL
**Verification**: `from packages.core.providers import *` succeeds

---

### Step 5: Provider Interface - Base Classes
**Files Created**:
- `packages/core/providers/base.py` - Base provider interface

**Purpose**: Abstract base class for all LLM providers

**Content**:
```python
from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, List, Optional
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class ToolCall(BaseModel):
    name: str
    arguments: Dict

class ModelResponse(BaseModel):
    content: str
    tool_calls: List[ToolCall] = []
    metadata: Dict = {}

class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> ModelResponse:
        """Generate completion"""
        pass
    
    @abstractmethod
    async def stream_generate(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion"""
        pass
    
    @abstractmethod
    def supports_tools(self) -> bool:
        """Check if provider supports function calling"""
        pass
```

**Test**: Verify abstract class cannot be instantiated
**Verification**: Unit test confirms ABC behavior

---

### Step 6: Ollama Provider Implementation
**Files Created**:
- `packages/core/providers/ollama.py` - Ollama provider adapter

**Purpose**: Implement Ollama provider for local LLM execution

**Key Features**:
- Connect to local Ollama instance
- Support tool calling via Ollama's function calling
- Model listing and availability checking
- Streaming support

**Actions**:
- Implement `BaseLLMProvider` interface
- Use `ollama` Python client
- Handle Ollama-specific response format
- Implement tool calling translation

**Test**: Connect to Ollama, generate completion
**Verification**: Integration test with Ollama running locally (llama2, mistral, etc.)

---

### Step 7: OpenAI-Compatible Provider
**Files Created**:
- `packages/core/providers/openai_compat.py` - OpenAI-compatible provider

**Purpose**: Support any OpenAI-compatible API (LM Studio, LocalAI, vLLM, etc.)

**Key Features**:
- Configurable base URL
- OpenAI client library
- Standard OpenAI message format
- Tool calling support

**Actions**:
- Implement `BaseLLMProvider` interface
- Use `openai` Python client with custom base URL
- Support API key authentication
- Handle standard OpenAI response format

**Test**: Connect to OpenAI-compatible endpoint
**Verification**: Test with multiple endpoints (OpenAI, LM Studio, etc.)

---

### Step 8: Gemini Provider Implementation
**Files Created**:
- `packages/core/providers/gemini.py` - Google Gemini provider

**Purpose**: Support Google Gemini models (for cloud fallback)

**Actions**:
- Implement `BaseLLMProvider` interface
- Use `google-generativeai` library
- Handle Gemini-specific features
- Support function calling

**Test**: Generate with Gemini API
**Verification**: Integration test with Gemini API (requires API key)

---

### Step 9: Provider Registry
**Files Created**:
- `packages/core/providers/registry.py` - Provider registration and discovery

**Purpose**: Central registry for all available providers

**Content**:
```python
class ProviderRegistry:
    """Registry for LLM providers"""
    
    def __init__(self):
        self._providers: Dict[str, Type[BaseLLMProvider]] = {}
    
    def register(self, name: str, provider_class: Type[BaseLLMProvider]):
        """Register a provider"""
        self._providers[name] = provider_class
    
    def get(self, name: str, **config) -> BaseLLMProvider:
        """Get configured provider instance"""
        if name not in self._providers:
            raise ValueError(f"Provider {name} not found")
        return self._providers[name](**config)
    
    def list_providers(self) -> List[str]:
        """List all registered providers"""
        return list(self._providers.keys())

# Global registry
provider_registry = ProviderRegistry()
```

**Test**: Register and retrieve providers
**Verification**: Unit tests for registry operations

---

### Step 10: Model Configuration System
**Files Created**:
- `packages/core/models/config.py` - Model configuration classes
- `config/models.yaml` - Model definitions

**Purpose**: Define available models and their configurations

**models.yaml** Example:
```yaml
models:
  # Local Ollama models
  local:
    mistral-7b:
      provider: ollama
      model_name: mistral
      context_window: 8192
      supports_tools: true
      
    llama2-13b:
      provider: ollama
      model_name: llama2:13b
      context_window: 4096
      supports_tools: true
  
  # OpenAI-compatible (LM Studio, etc.)
  openai_compat:
    lmstudio-mixtral:
      provider: openai_compat
      base_url: http://localhost:1234/v1
      model_name: mixtral-8x7b
      context_window: 32768
      supports_tools: true
  
  # Cloud models
  cloud:
    gemini-pro:
      provider: gemini
      model_name: gemini-1.5-pro
      context_window: 1000000
      supports_tools: true
      
    gpt-4:
      provider: openai_compat
      base_url: https://api.openai.com/v1
      model_name: gpt-4-turbo
      context_window: 128000
      supports_tools: true
```

**Test**: Load and parse configuration
**Verification**: Config validation tests

---

### Step 11: Model Registry
**Files Created**:
- `packages/core/models/registry.py` - Model discovery and management

**Purpose**: Registry for available models

**Actions**:
- Load models from config
- Validate model definitions
- Check model availability
- Model fallback logic

**Test**: Register models, check availability
**Verification**: Unit tests for model registration

---

### Step 12: Agent-Model Configuration
**Files Created**:
- `packages/core/models/agent_config.py` - Agent-model bindings
- `config/agents.yaml` - Agent configurations

**Purpose**: Configure which model each agent uses

**agents.yaml** Example:
```yaml
agents:
  default:
    model: local.mistral-7b
    fallback: cloud.gemini-pro
    temperature: 0.7
    max_tokens: 4096
    
  codebase_investigator:
    model: local.llama2-13b  # Larger model for code analysis
    fallback: cloud.gpt-4
    temperature: 0.3
    max_tokens: 8192
    
  file_editor:
    model: local.mistral-7b
    temperature: 0.1  # Low temp for precise edits
    max_tokens: 2048
    
  web_researcher:
    model: openai_compat.lmstudio-mixtral
    temperature: 0.5
    max_tokens: 4096
```

**Test**: Load agent configs, bind to models
**Verification**: Config parsing tests

---

### Step 13: Model Client Factory
**Files Created**:
- `packages/core/models/factory.py` - Create configured model clients

**Purpose**: Factory pattern for model client creation

**Content**:
```python
from typing import Optional
from .config import ModelConfig
from ..providers.registry import provider_registry

class ModelClientFactory:
    """Factory for creating model clients"""
    
    async def create_client(
        self,
        model_id: str,
        fallback_model_id: Optional[str] = None
    ) -> BaseLLMProvider:
        """Create a model client with fallback"""
        
        # Parse model_id (e.g., "local.mistral-7b")
        category, model_name = model_id.split('.')
        
        # Load model config
        config = self.load_model_config(category, model_name)
        
        # Get provider
        provider = provider_registry.get(
            config.provider,
            **config.provider_config
        )
        
        # Check availability
        if not await self.check_availability(provider):
            if fallback_model_id:
                return await self.create_client(fallback_model_id)
            raise RuntimeError(f"Model {model_id} not available")
        
        return provider
```

**Test**: Create clients with fallbacks
**Verification**: Test fallback logic

---

### Step 14: Configuration System - Base
**Files Created**:
- `packages/core/config/config.py` - Main configuration class
- `packages/core/config/loader.py` - Configuration loading
- `config/default.yaml` - Default configuration

**Purpose**: Global configuration management

**Actions**:
- Load YAML/TOML configs
- Environment variable overrides
- Merge configs from multiple sources
- Validation with Pydantic

**Test**: Load configs with precedence
**Verification**: Test config merging

---

### Step 15: Logging System
**Files Created**:
- `packages/core/core/logger.py` - Structured logging

**Purpose**: Logging with provider information

**Actions**:
- Configure Python logging
- Add provider/model context to logs
- File and console handlers
- Debug mode support

**Test**: Log at different levels
**Verification**: Verify log format includes model info

---

## PHASE 2: Core Types & Utilities (Steps 16-20)

### Step 16: Shared Type Definitions
**Files Created**:
- `packages/core/types/base.py` - Base types
- `packages/core/types/messages.py` - Message types
- `packages/core/types/tools.py` - Tool types

**Purpose**: Common types used across providers

**Test**: Type validation with Pydantic
**Verification**: Unit tests for all types

---

### Step 17: Error Handling Framework
**Files Created**:
- `packages/core/utils/errors.py` - Exception hierarchy

**Purpose**: Custom exceptions including provider errors

**New Exceptions**:
- `ProviderError` - Provider-specific errors
- `ModelNotAvailableError` - Model unavailable
- `ToolNotSupportedError` - Tools not supported by model

**Test**: Raise and catch exceptions
**Verification**: Unit tests

---

### Step 18: Utilities - Path Management
**Files Created**:
- `packages/core/utils/paths.py` - Path utilities

**Purpose**: File path resolution

**Test**: Path resolution tests
**Verification**: Edge case handling

---

### Step 19: Git Utilities
**Files Created**:
- `packages/core/utils/git_utils.py` - Git operations

**Purpose**: Git integration

**Test**: Test with git repos
**Verification**: Mock git commands

---

### Step 20: Retry and Fallback Logic
**Files Created**:
- `packages/core/utils/retry.py` - Retry with provider fallback

**Purpose**: Robust error handling with model fallback

**Actions**:
- Exponential backoff
- Provider fallback on failure
- Network error handling
- Rate limit detection

**Test**: Trigger retries and fallbacks
**Verification**: Unit tests verify fallback chain

---

## PHASE 3: Provider-Agnostic API Client (Steps 21-28)

### Step 21: Unified API Client
**Files Created**:
- `packages/core/core/client.py` - Provider-agnostic client

**Purpose**: Unified interface for all providers

**Content**:
```python
class UnifiedLLMClient:
    """Provider-agnostic LLM client"""
    
    def __init__(self, model_id: str, fallback_id: Optional[str] = None):
        self.factory = ModelClientFactory()
        self.model_id = model_id
        self.fallback_id = fallback_id
        self.provider: Optional[BaseLLMProvider] = None
    
    async def initialize(self):
        """Initialize provider client"""
        self.provider = await self.factory.create_client(
            self.model_id,
            self.fallback_id
        )
    
    async def generate(self, messages: List[Message], tools=None):
        """Generate with automatic fallback"""
        try:
            return await self.provider.generate(messages, tools)
        except Exception as e:
            if self.fallback_id:
                # Try fallback
                fallback = await self.factory.create_client(self.fallback_id)
                return await fallback.generate(messages, tools)
            raise
```

**Test**: Generate with different providers
**Verification**: Test provider switching

---

### Step 22: Tool Schema Translation
**Files Created**:
- `packages/core/core/tool_schema.py` - Tool schema converter

**Purpose**: Convert tools to provider-specific format

**Actions**:
- OpenAI function calling format
- Gemini function declaration format
- Ollama tool format
- Generic JSON schema

**Test**: Convert schemas for all providers
**Verification**: Schema validation

---

### Step 23: Response Parser - Universal
**Files Created**:
- `packages/core/core/response_parser.py` - Parse responses from any provider

**Purpose**: Normalize responses across providers

**Actions**:
- Parse OpenAI format
- Parse Gemini format
- Parse Ollama format
- Extract tool calls uniformly

**Test**: Parse responses from each provider
**Verification**: Unit tests with sample responses

---

### Step 24: Token Management
**Files Created**:
- `packages/core/core/token_limits.py` - Provider-aware token counting

**Purpose**: Token counting for different model encodings

**Actions**:
- Use tiktoken for OpenAI models
- Approximate for Ollama models
- Gemini token counting
- Context window management

**Test**: Count tokens accurately
**Verification**: Compare with API counts

---

### Step 25: Prompt Construction
**Files Created**:
- `packages/core/core/prompts.py` - Provider-agnostic prompts

**Purpose**: Build prompts for any provider

**Actions**:
- System prompt templates
- Tool definition injection
- Context formatting
- Provider-specific adjustments

**Test**: Build prompts for each provider
**Verification**: Snapshot tests

---

### Step 26: Content Generator
**Files Created**:
- `packages/core/core/content_generator.py` - Universal content generation

**Purpose**: Generate content with any provider

**Actions**:
- Async generation
- Streaming support
- Tool call handling
- Error recovery

**Test**: Generate with mock providers
**Verification**: Integration tests

---

### Step 27: Chat Session Management
**Files Created**:
- `packages/core/core/gemini_chat.py` → `packages/core/core/chat_session.py`

**Purpose**: Provider-agnostic chat sessions

**Actions**:
- Track conversation history
- Manage context window
- Support checkpoints
- Model switching mid-conversation

**Test**: Multi-turn conversations
**Verification**: Session persistence tests

---

### Step 28: Request Builder
**Files Created**:
- `packages/core/core/request_builder.py` - Build provider-specific requests

**Purpose**: Construct API requests for each provider

**Test**: Build requests for all providers
**Verification**: Request validation

---

## PHASE 4: Tools System (Steps 29-43)

### Step 29: Tool Base Classes
**Files Created**:
- `packages/core/tools/tools.py` - Base tool classes (provider-agnostic)

**Purpose**: Tool interface that works with all providers

**Test**: Create test tool
**Verification**: Tool lifecycle tests

---

### Step 30: Tool Registry
**Files Created**:
- `packages/core/tools/tool_registry.py` - Tool registration

**Purpose**: Register and discover tools

**Test**: Register tools
**Verification**: Registry tests

---

### Step 31: Tool Schema Generator
**Files Created**:
- `packages/core/tools/schema_utils.py` - Generate schemas for all providers

**Purpose**: Multi-format schema generation

**Test**: Generate OpenAI, Gemini, Ollama formats
**Verification**: Schema validation

---

### Step 32: File Read Tool
**Files Created**:
- `packages/core/tools/read_file.py`

**Purpose**: Read files (provider-agnostic)

**Test**: Read various files
**Verification**: File reading tests

---

### Step 33: File Write Tool
**Files Created**:
- `packages/core/tools/write_file.py`

**Purpose**: Write files

**Test**: Write files
**Verification**: Write tests

---

### Step 34: File Edit Tool
**Files Created**:
- `packages/core/tools/edit.py`
- `packages/core/tools/smart_edit.py`

**Purpose**: File editing with diffs

**Test**: Edit files
**Verification**: Edit accuracy tests

---

### Step 35: Search Tools (ls, glob)
**Files Created**:
- `packages/core/tools/ls.py`
- `packages/core/tools/glob.py`

**Purpose**: File search

**Test**: Search patterns
**Verification**: Search tests

---

### Step 36: Content Search (grep)
**Files Created**:
- `packages/core/tools/grep.py`
- `packages/core/tools/rip_grep.py`

**Purpose**: Content search

**Test**: Search content
**Verification**: Search accuracy

---

### Step 37: Shell Execution Tool
**Files Created**:
- `packages/core/tools/shell.py`

**Purpose**: Execute shell commands

**Test**: Safe command execution
**Verification**: Security tests

---

### Step 38: Web Fetch Tool
**Files Created**:
- `packages/core/tools/web_fetch.py`

**Purpose**: Fetch web content

**Test**: Fetch URLs
**Verification**: Integration tests

---

### Step 39: Web Search Tool
**Files Created**:
- `packages/core/tools/web_search.py`

**Purpose**: Web search

**Test**: Search queries
**Verification**: Search tests

---

### Step 40: Memory Tool
**Files Created**:
- `packages/core/tools/memory_tool.py`
- `data/memories.db` - SQLite database

**Purpose**: Persistent memory

**Test**: Store/retrieve
**Verification**: Database tests

---

### Step 41: Read Many Files Tool
**Files Created**:
- `packages/core/tools/read_many_files.py`

**Purpose**: Batch file reading

**Test**: Read multiple files
**Verification**: Performance tests

---

### Step 42: Modifiable Tools Framework
**Files Created**:
- `packages/core/tools/modifiable_tool.py`

**Purpose**: Tools requiring confirmation

**Test**: Confirmation flow
**Verification**: Confirmation tests

---

### Step 43: Tool Error Handling
**Files Created**:
- `packages/core/tools/tool_error.py`

**Purpose**: Tool error handling

**Test**: Error scenarios
**Verification**: Error handling tests

---

## PHASE 5: Agents System (Steps 44-50)

### Step 44: Agent Base Types
**Files Created**:
- `packages/core/agents/types.py` - Agent types with model config

**Purpose**: Agent definitions with model binding

**Content**:
```python
class AgentConfig(BaseModel):
    """Agent configuration"""
    name: str
    model_id: str
    fallback_model_id: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    system_prompt: str = ""
    allowed_tools: List[str] = []
```

**Test**: Create agent configs
**Verification**: Config validation

---

### Step 45: Agent Factory
**Files Created**:
- `packages/core/agents/factory.py` - Create agents with models

**Purpose**: Factory for creating agents with configured models

**Test**: Create agents
**Verification**: Agent initialization

---

### Step 46: Agent Executor
**Files Created**:
- `packages/core/agents/executor.py` - Model-aware execution

**Purpose**: Execute agents with their configured models

**Actions**:
- Load agent config
- Initialize model client
- Execute workflow
- Handle tool calls

**Test**: Execute workflows
**Verification**: Integration tests

---

### Step 47: Agent Registry
**Files Created**:
- `packages/core/agents/registry.py`

**Purpose**: Register agents

**Test**: Register agents
**Verification**: Registry tests

---

### Step 48: Delegation System
**Files Created**:
- `packages/core/agents/delegate_to_agent_tool.py`

**Purpose**: Delegate to sub-agents (each with own model)

**Test**: Delegation flow
**Verification**: Multi-agent tests

---

### Step 49: Specialized Agents
**Files Created**:
- `packages/core/agents/codebase_investigator.py` - Code analysis agent

**Purpose**: Specialized agent with specific model

**Test**: Code analysis
**Verification**: Analysis quality

---

### Step 50: Agent Model Switching
**Files Created**:
- `packages/core/agents/model_switcher.py` - Runtime model switching

**Purpose**: Switch models during execution

**Test**: Model switching
**Verification**: Seamless switching

---

## PHASE 6: Services Layer (Steps 51-55)

### Step 51: File Discovery Service
**Files Created**:
- `packages/core/services/file_discovery_service.py`

**Purpose**: File discovery

**Test**: Discover files
**Verification**: Discovery tests

---

### Step 52: Git Service
**Files Created**:
- `packages/core/services/git_service.py`

**Purpose**: Git operations

**Test**: Git queries
**Verification**: Git tests

---

### Step 53: Context Manager Service
**Files Created**:
- `packages/core/services/context_manager.py`

**Purpose**: Context window management

**Test**: Context fitting
**Verification**: Context tests

---

### Step 54: File System Service
**Files Created**:
- `packages/core/services/file_system_service.py`

**Purpose**: Async file operations

**Test**: File operations
**Verification**: Async tests

---

### Step 55: Shell Execution Service
**Files Created**:
- `packages/core/services/shell_execution_service.py`

**Purpose**: Managed shell execution

**Test**: Execute commands
**Verification**: Security tests

---

## PHASE 7: MCP Integration (Steps 56-58)

### Step 56: MCP Client Base
**Files Created**:
- `packages/core/tools/mcp_client.py`

**Purpose**: MCP protocol support

**Test**: Connect to MCP servers
**Verification**: MCP integration

---

### Step 57: MCP Tool Wrapper
**Files Created**:
- `packages/core/tools/mcp_tool.py`

**Purpose**: Wrap MCP tools

**Test**: Invoke MCP tools
**Verification**: Tool execution

---

### Step 58: MCP Client Manager
**Files Created**:
- `packages/core/tools/mcp_client_manager.py`

**Purpose**: Manage MCP connections

**Test**: Multiple servers
**Verification**: Connection management

---

## PHASE 8: Confirmation & Safety (Steps 59-61)

### Step 59: Confirmation Bus
**Files Created**:
- `packages/core/confirmation_bus/message_bus.py`
- `packages/core/confirmation_bus/types.py`

**Purpose**: User confirmations

**Test**: Confirmation flow
**Verification**: Confirmation tests

---

### Step 60: Policy Engine
**Files Created**:
- `packages/core/policy/policy_engine.py`
- `packages/core/policy/toml_loader.py`
- `config/policy.toml`

**Purpose**: Policy enforcement

**Test**: Policy evaluation
**Verification**: Policy tests

---

### Step 61: Safety Checks
**Files Created**:
- `packages/core/safety/safety.py`

**Purpose**: Content safety

**Test**: Safety checks
**Verification**: Safety tests

---

## PHASE 9: CLI Package (Steps 62-70)

### Step 62: CLI Framework Setup
**Files Created**:
- `packages/cli/cli.py` - Main CLI entry point
- `packages/cli/commands/__init__.py`

**Purpose**: CLI framework

**Test**: CLI help
**Verification**: `--help` works

---

### Step 63: Model Selection CLI
**Files Created**:
- `packages/cli/commands/model.py` - Model management commands

**Purpose**: CLI for model operations

**Commands**:
- `model list` - List available models
- `model test <model>` - Test model connection
- `model set <agent> <model>` - Set agent model

**Test**: Model commands
**Verification**: Model listing works

---

### Step 64: Rich Terminal UI
**Files Created**:
- `packages/cli/ui/layout.py`
- `packages/cli/ui/components.py`
- `packages/cli/ui/themes.py`

**Purpose**: Terminal UI with Rich

**Test**: Display UI
**Verification**: Visual check

---

### Step 65: Interactive Chat Mode
**Files Created**:
- `packages/cli/commands/chat.py`
- `packages/cli/input_processor.py`

**Purpose**: Interactive mode

**Test**: Chat session
**Verification**: Multi-turn conversation

---

### Step 66: Non-Interactive Mode
**Files Created**:
- `packages/cli/non_interactive_cli.py`

**Purpose**: Scripting support

**Test**: Non-interactive execution
**Verification**: Pipe input works

---

### Step 67: Theme System
**Files Created**:
- `packages/cli/ui/themes.py` - Extended themes

**Purpose**: UI customization

**Test**: Switch themes
**Verification**: Visual check

---

### Step 68: Output Formatting
**Files Created**:
- `packages/cli/output_formatter.py`

**Purpose**: Format responses

**Test**: Format samples
**Verification**: Visual check

---

### Step 69: History Management
**Files Created**:
- `packages/cli/history.py`
- `data/history.db` - History storage

**Purpose**: Session history

**Test**: Save/load history
**Verification**: Persistence

---

### Step 70: Configuration CLI Commands
**Files Created**:
- `packages/cli/commands/config.py`

**Purpose**: Config management

**Commands**:
- `config show` - Show config
- `config set <key> <value>`
- `config reset`

**Test**: Config commands
**Verification**: Config modification

---

## PHASE 10: Integration & Testing (Steps 71-75)

### Step 71: Provider Integration Tests
**Files Created**:
- `tests/integration/test_providers.py`
- `tests/integration/test_ollama.py`
- `tests/integration/test_openai_compat.py`

**Purpose**: Test all providers

**Test**: Full provider workflows
**Verification**: All providers work

---

### Step 72: Agent-Model Binding Tests
**Files Created**:
- `tests/integration/test_agent_models.py`

**Purpose**: Test agent-model configurations

**Test**: Different models per agent
**Verification**: Correct model usage

---

### Step 73: Fallback Tests
**Files Created**:
- `tests/integration/test_fallback.py`

**Purpose**: Test model fallback logic

**Test**: Trigger fallbacks
**Verification**: Graceful fallback

---

### Step 74: Mock Multi-Provider API
**Files Created**:
- `tests/fixtures/mock_providers.py`

**Purpose**: Mock all providers for testing

**Test**: Tests without real APIs
**Verification**: All tests pass

---

### Step 75: Documentation
**Files Created**:
- `docs/providers.md` - Provider setup guide
- `docs/models.md` - Model configuration guide
- `docs/agents.md` - Agent configuration guide
- `docs/local_setup.md` - Ollama setup guide

**Purpose**: Comprehensive documentation

**Test**: Build docs
**Verification**: Docs complete

---

## PHASE 11: Advanced Features (Steps 76-78)

### Step 76: Model Benchmarking
**Files Created**:
- `packages/cli/commands/benchmark.py`
- `tools/benchmark.py` - Benchmarking utility

**Purpose**: Compare model performance

**Test**: Benchmark models
**Verification**: Performance metrics

---

### Step 77: Model Auto-Selection
**Files Created**:
- `packages/core/models/auto_select.py`

**Purpose**: Automatically select best available model

**Actions**:
- Check model availability
- Consider task requirements
- Select optimal model
- Fallback chain

**Test**: Auto-selection
**Verification**: Correct selection

---

### Step 78: Provider Health Monitoring
**Files Created**:
- `packages/core/providers/health.py`
- `packages/cli/commands/status.py`

**Purpose**: Monitor provider health

**Commands**:
- `status` - Show all provider status
- `status ollama` - Ollama status
- `status models` - Available models

**Test**: Health checks
**Verification**: Status reporting

---

## Configuration Examples

### `config/models.yaml`

```yaml
models:
  local:
    # Ollama models
    mistral-7b:
      provider: ollama
      model_name: mistral
      context_window: 8192
      supports_tools: true
      priority: 1  # Try first
      
    llama2-13b:
      provider: ollama
      model_name: llama2:13b
      context_window: 4096
      supports_tools: true
      priority: 2
      
  cloud:
    gemini-pro:
      provider: gemini
      model_name: gemini-1.5-pro
      context_window: 1000000
      supports_tools: true
      priority: 10  # Cloud fallback
      api_key_env: GEMINI_API_KEY
```

### `config/agents.yaml`

```yaml
agents:
  default:
    model: local.mistral-7b
    fallback:
      - local.llama2-13b
      - cloud.gemini-pro
    temperature: 0.7
    
  codebase_investigator:
    model: local.llama2-13b  # Larger model for analysis
    fallback:
      - cloud.gemini-pro
    temperature: 0.3
    system_prompt: |
      You are an expert code analyst...
      
  file_editor:
    model: local.mistral-7b
    temperature: 0.1  # Precise edits
```

### `config/providers.yaml`

```yaml
providers:
  ollama:
    base_url: http://localhost:11434
    timeout: 300
    
  openai_compat:
    base_url: http://localhost:1234/v1  # LM Studio
    api_key_env: LMSTUDIO_API_KEY
    
  gemini:
    api_key_env: GEMINI_API_KEY
    region: us-central1
```

---

## Usage Examples

### Start with Local Model
```bash
# Use Ollama by default
gemini-agent chat --model local.mistral-7b

# Specific agent with specific model
gemini-agent chat --agent codebase_investigator --model local.llama2-13b
```

### List Available Models
```bash
gemini-agent model list
# Output:
# LOCAL (Ollama):
#   ✓ mistral-7b (8K context, tools)
#   ✓ llama2-13b (4K context, tools)
# CLOUD:
#   ✓ gemini-pro (1M context, tools)
#   - gpt-4 (not configured)
```

### Test Model Connection
```bash
gemini-agent model test local.mistral-7b
# Testing connection to ollama/mistral...
# ✓ Model available
# ✓ Tool calling supported
# ✓ Response time: 1.2s
```

### Configure Agent Model
```bash
# Set default agent model
gemini-agent config set agents.default.model local.llama2-13b

# Set specific agent
gemini-agent config set agents.codebase_investigator.model cloud.gemini-pro
```

---

## Verification Checklist

### Model Abstraction
- [ ] All providers implement `BaseLLMProvider`
- [ ] Provider registry working
- [ ] Model registry loading from config
- [ ] Per-agent model configuration
- [ ] Fallback chain functional

### Local Execution
- [ ] Ollama provider working
- [ ] OpenAI-compatible provider working
- [ ] Models can be used offline
- [ ] No cloud dependency for basic operations

### Multi-Provider Support
- [ ] All 3 providers (Ollama, OpenAI-compat, Gemini) working
- [ ] Tool calling works on all supporting providers
- [ ] Response parsing unified
- [ ] Schema translation for each provider

### Configuration
- [ ] Models configurable via YAML
- [ ] Agents configurable via YAML
- [ ] Per-agent model assignment
- [ ] Environment variable support

### Testing
- [ ] Unit tests for all providers
- [ ] Integration tests with real models
- [ ] Mock providers for offline testing
- [ ] Fallback testing

---

## Summary

This revised plan provides **78 steps** organized into **11 phases** to build a **model-agnostic CLI agent** with:

1. ✅ **Multi-provider support** (Ollama, OpenAI-compatible, Gemini)
2. ✅ **Local-first execution** (Ollama primary)
3. ✅ **Per-agent model configuration**
4. ✅ **Automatic fallback chains**
5. ✅ **Provider abstraction layer**
6. ✅ **Specific files for each step**
7. ✅ **Complete testing strategy**

Each step includes:
- **Files Created** - Exact file paths and names
- **Purpose** - Why this file exists
- **Actions** - What to implement
- **Test** - How to test it
- **Verification** - Success criteria

The architecture is **production-ready** and fully **model-agnostic** while maintaining all the capabilities of the original Gemini CLI.
