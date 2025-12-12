# PydanticAI Agent CLI - Quick Start

## Installation

```bash
# Install in development mode
uv pip install -e .
```

## Usage

### Interactive REPL

Start the interactive shell:

```bash
uv run agent repl
```

Or use the shortcut:

```bash
uv run agent-repl
```

### Commands

**System Commands** (start with `/`):
```
/help              Show comprehensive help
/agents            List all available agents
/config            Display configuration
/history           Show command history
/clear             Clear screen
/exit              Exit CLI
```

**Agent Commands** (no prefix):
Just type natural language:

```
analyze packages/core/config/config.py
generate tests for packages/core/tools/
create a README for this project
refactor delegation.py to improve readability
```

### Single Command Execution

Run a single command without entering REPL:

```bash
uv run agent run analyze config.py
```

### List Agents

```bash
uv run agent agents
```

## Examples

### Code Analysis
```
agent> analyze packages/core/agents/delegation.py
```

### Generate Tests
```
agent> generate comprehensive tests for the delegation system
```

### Documentation
```
agent> create a README explaining the agent system
```

### Refactoring
```
agent> refactor repl.py to extract the display logic
```

## Features

✅ **Rich Formatting** - Beautiful terminal output with syntax highlighting  
✅ **Tab Completion** - Command auto-completion  
✅ **Command History** - Navigate previous commands with arrow keys  
✅ **Multiple Agents** - 7 specialized agents coordinated automatically  
✅ **Async Execution** - Non-blocking agent operations  
✅ **Error Handling** - Graceful error messages  

## Configuration

Configuration is loaded from:
1. `.env` file (create from `.env.example`)
2. Environment variables
3. Default values

View current config:
```
agent> /config
```

## Troubleshooting

**Command not found: agent**
- Use `uv run agent` instead
- Or activate virtual environment first

**OLLAMA_BASE_URL not set**
- Copy `.env.example` to `.env`
- Default is `http://localhost:11434/v1`

**Agents not responding**
- Ensure Ollama is running: `ollama serve`
- Check config with `/config` command
