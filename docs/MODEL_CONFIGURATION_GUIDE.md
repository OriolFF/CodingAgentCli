# Model Configuration Guide

## 📍 Location

**File**: `packages/core/config/model_configuration.py`

## 🎯 Purpose

Centralized configuration for all Ollama models, including:
- Context window sizes (`num_ctx`)
- Output token limits (`num_predict`)
- Temperature settings
- Model descriptions and notes

## 📝 How to Add/Modify Model Settings

### Add a New Model

Edit `packages/core/config/model_configuration.py`:

```python
MODEL_CONFIGS: Dict[str, ModelConfig] = {
    # ... existing models ...
    
    # Your new model
    "your-model:tag": ModelConfig(
        num_ctx=32768,        # Context window size
        num_predict=-1,       # -1 = unlimited output
        temperature=0.7,      # 0.0-1.0
        description="Description of the model and when to use it"
    ),
}
```

### Modify Existing Model

Find the model in `MODEL_CONFIGS` and update its values:

```python
"gpt-oss:20b": ModelConfig(
    num_ctx=65536,     # Increase context from 32K to 64K
    num_predict=-1,
    temperature=0.7,
    description="..."
),
```

## 🔧 Configuration Options

### Context Window (`num_ctx`)

**Common Values:**
- `4096` - Very small (simple snippets)
- `8192` - Small (single files, Codestral)
- `16384` - Medium (standard tasks)
- `32768` - Large (complex apps, gpt-oss:20b, qwen)
- `65536` - Extra large (very complex projects)
- `131072` - Maximum (128K, full context)

### Output Tokens (`num_predict`)

- `-1` - **Unlimited** (recommended for code generation)

### Temperature

- `0.0` - **Deterministic**
- `0.5` - **Conservative** (Codestral)
- `0.7` - **Balanced** (recommended)
- `1.0` - **Creative**

## 📊 Current Configurations

### Large Context (32K+)
- `gpt-oss:20b` - 32K context
- `qwen2.5-coder:14b` - 32K context

### Medium Context (16K)
- `llama3.1:8b-instruct-q8_0` - 16K
- `codellama:13b` - 16K

### Small Context (8K)
- `codestral` - 8K (completion specialist)
- `cogito:14b` - 8K
- `mistral` - 8K
- `granite3.3` - 8K

## 🚀 Usage

Configuration is **automatically applied**:

```bash
# .env
CODE_GENERATOR_MODEL=ollama:gpt-oss:20b
```

Automatically uses: `num_ctx=32768, temperature=0.7`

## 🧪 Testing

```bash
uv run python packages/core/config/model_configuration.py
```

## 📖 Helper Functions

```python
from packages.core.config.model_configuration import get_model_config

config = get_model_config("gpt-oss:20b")
print(config.num_ctx)        # 32768
```

## 🔗 Related Files

- **Configuration**: `packages/core/config/model_configuration.py`
- **Usage**: `packages/core/agents/code_generator.py`
- **Environment**: `.env`
