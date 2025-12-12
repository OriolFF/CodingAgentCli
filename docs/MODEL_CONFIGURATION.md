# Model-Optimized Agent Configuration Guide

## Available Models

You have 3 Ollama models with different strengths:

| Model | Size | Best For | Speed |
|-------|------|----------|-------|
| `mistral:latest` | 4.4 GB | General tasks, routing | ⚡️⚡️⚡️ Fast |
| `qwen2.5-coder:14b` | 9.0 GB | Code generation/analysis | ⚡️⚡️ Medium |
| `gpt-oss:20b` | 13 GB | Complex reasoning | ⚡️ Slower |

## Recommended Configuration

### Strategy

**Use the right model for each task**:
- **Coordinator** → `mistral` (fast routing decisions)
- **Code tasks** → `qwen2.5-coder:14b` (specialized for code)
- **Complex tasks** → `gpt-oss:20b` (when you need max quality)

### Agent-Model Mapping

```
┌────────────────────┬──────────────────────┬─────────────┐
│ Agent              │ Recommended Model     │ Why         │
├────────────────────┼──────────────────────┼─────────────┤
│ Coordinator        │ mistral              │ Fast routing │
│ Codebase Analyst   │ qwen2.5-coder:14b   │ Code expert  │
│ File Editor        │ qwen2.5-coder:14b   │ Precision    │
│ Testing Agent      │ qwen2.5-coder:14b   │ Test gen     │
│ Documentation      │ mistral              │ Writing      │
│ Refactoring        │ gpt-oss:20b         │ Complex      │
└────────────────────┴──────────────────────┴─────────────┘
```

### Temperature Settings

**Lower** (0.0-0.2): Deterministic, precise
- File Editor: 0.1
- Refactoring: 0.2
- Coordinator: 0.2

**Medium** (0.2-0.4): Balanced
- Codebase Analyst: 0.3
- Testing: 0.2

**Higher** (0.4-0.6): Creative
- Documentation: 0.5

## Implementation

### Option 1: Use Pre-configured File (Recommended)

```bash
# Copy optimized config
cp .env.optimized .env

# Restart CLI to pick up changes
uv run agent repl
```

### Option 2: Manual Configuration

Edit your `.env` file and add model overrides:

```ini
# In config/agents.yaml
agents:
  codebase_investigator:
    model: "ollama:qwen2.5-coder:14b"
    temperature: 0.3
  
  file_editor:
    model: "ollama:qwen2.5-coder:14b"
    temperature: 0.1
  
  refactoring:
    model: "ollama:gpt-oss:20b"
    temperature: 0.2
```

## Performance Tips

### Memory Usage

Running multiple agents simultaneously:
- **Light** (< 6GB RAM): Use mistral for everything
- **Medium** (8-16GB RAM): Current config (mixed)
- **Heavy** (16GB+ RAM): Can use gpt-oss:20b more

### Speed vs Quality

**Fast mode** (all mistral):
- Response time: ~1-2 seconds
- Quality: Good for most tasks

**Balanced mode** (recommended config):
- Response time: ~3-5 seconds  
- Quality: Excellent for code tasks

**Quality mode** (all gpt-oss:20b):
- Response time: ~5-10 seconds
- Quality: Best possible

## Testing Your Configuration

Try these commands to verify:

```bash
# Should be fast (mistral)
agent> list available agents

# Should use qwen (code analysis)
agent> analyze packages/core/agents/

# Should use qwen (code generation)
agent> generate tests for config.py

# Should use gpt-oss (complex reasoning)
agent> refactor the delegation system for better modularity
```

## Notes

- Configuration loaded from `.env` on startup
- Restart CLI after changing `.env`
- Models auto-downloaded by Ollama if missing
- Check memory usage: `ollama ps`
