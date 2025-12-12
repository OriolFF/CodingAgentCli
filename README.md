# Gemini Agent Python - Model-Agnostic CLI Agent

A powerful, model-agnostic CLI agent with multi-provider support, designed for local-first execution.

## Features

- 🔌 **Multi-Provider Support**: Ollama, OpenAI-compatible APIs, Google Gemini, Anthropic
- 🏠 **Local-First**: Prioritize Ollama for privacy and offline use
- 🎯 **Per-Agent Models**: Configure different models for different agents
- 🛠️ **Extensive Tools**: File operations, shell execution, web search, and more
- 🔄 **Agent System**: Specialized agents with delegation support
- 🔌 **MCP Integration**: Extend with Model Context Protocol servers

## Architecture

Based on Google's Gemini CLI architecture with enhancements for model-agnosticism:

- **CLI Package**: User-facing terminal interface (Rich UI)
- **Core Package**: Backend orchestration and business logic
  - **Providers**: Abstract LLM provider interfaces
  - **Models**: Model registry and configuration
  - **Agents**: Agent execution and delegation
  - **Tools**: File, shell, web, and custom tools
  - **Services**: File discovery, git, context management

## Quick Start

### Prerequisites

- Python 3.10 or higher
- UV (recommended) or pip
- Ollama (for local models) - https://ollama.ai

### Installation

```bash
# Create virtual environment with UV
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
uv pip install -e ".[dev]"
```

### Configuration

1. Set up your models in `config/models.yaml`
2. Configure agents in `config/agents.yaml`
3. Add provider credentials in `config/providers.yaml`

### Usage

```bash
# Interactive chat with default model
gemini-agent chat

# Use specific model
gemini-agent chat --model local.mistral-7b

# List available models
gemini-agent model list

# Non-interactive mode
echo "Analyze this code" | gemini-agent
```

## Development

```bash
# Run tests
pytest

# Lint code
ruff check .

# Type check
mypy packages

# Format code
black packages tests
```

## Project Status

🚧 **In Development** - Following the 78-step implementation plan

## License

Apache-2.0
