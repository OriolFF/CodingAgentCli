# Tool Calling with PydanticAI and Ollama

## 🎯 The Problem We Solved

**Issue**: Agents were explaining what to do instead of actually doing it.

**Example**:
```
User: "create sandbox/calc.py"
Agent: "To create the file, run: mkdir sandbox..." ❌
Expected: [Actually creates the file using tools] ✅
```

## 🔬 Research Findings

### Root Cause

Models like Mistral, Qwen, and Granite generate **text BEFORE tool calls**. When PydanticAI sees this text, it assumes that's the final response and skips tool execution.

**From PydanticAI documentation**:
> "If the LLM generates any text content before attempting to make a tool call, PydanticAI might interpret this text as the final response, especially in streaming modes."

### The Solution: Llama 3.1

**Llama 3.1 8B-Instruct** is specifically recommended for tool calling because:

1. ✅ **Calls tools FIRST, explains AFTER**
2. ✅ **Trained for function calling** (Meta's focus)
3. ✅ **Recommended by PydanticAI docs**
4. ✅ **Proven with Ollama compatibility**
5. ✅ **Fast inference** (8B parameters)

## 📊 Model Comparison

| Model | Tool Calling | Code Quality | Speed | Verdict |
|-------|-------------|--------------|-------|---------|
| **Llama 3.1 8B** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | **BEST** |
| Granite 3.3 | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | Explains too much |
| Mistral | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Explains too much |
| Qwen 2.5-Coder | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Great for analysis |
| GPT-OSS 20B | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | Good reasoning |

## 🚀 Quick Setup

### 1. Pull Llama 3.1

```bash
ollama pull llama3.1
```

### 2. Switch Configuration

```bash
./switch_env.sh llama
```

This sets:
- **General tasks** (coordinator, file_editor, testing, docs) → Llama 3.1
- **Code tasks** (codebase, refactoring) → Qwen 2.5-Coder

### 3. Test

```bash
uv run python test_file_editor.py
```

You should see the file actually created!

## 📋 Recommended Models by Task

### For PydanticAI + Ollama:

**Tool Calling** (critical):
- ✅ Llama 3.1 8B-Instruct (BEST)
- ✅ Mistral Nemo
- ✅ Firefunction v2
- ✅ Command-R+

**Code Analysis**:
- ✅ Qwen 2.5-Coder (14B)
- ✅ CodeLlama 13B
- ✅ Deepseek Coder

**Complex Reasoning**:
- ✅ GPT-OSS 20B
- ✅ Llama 3.1 70B (if you have resources)

## 🎨 Configuration Presets

```bash
# Recommended: Llama 3.1 + Qwen
./switch_env.sh llama

# Experimental: Granite + Qwen  
./switch_env.sh granite

# Legacy: Mistral + Qwen
./switch_env.sh optimized

# Custom
./switch_env.sh llama3.1 qwen2.5-coder:14b
```

## 🐛 Troubleshooting

### Agent still explaining instead of acting?

1. **Check model**: Must be Llama 3.1 or compatible
   ```bash
   grep COORDINATOR_MODEL .env
   ```

2. **Verify Ollama has the model**:
   ```bash
   ollama list | grep llama3.1
   ```

3. **Check logs** for tool calls:
   ```bash
   # Enable debug logging
   echo "LOG_LEVEL=DEBUG" >> .env
   ```

4. **Test directly**:
   ```bash
   uv run python test_file_editor.py
   ls -la sandbox/  # File should exist
   ```

### File not created?

Check if tool was called:
```python
result = await delegate_task("create file")
print(result.agents_used)  # Should show ['file_editor']
# If file_editor but no file → tool not called
# If no file_editor → routing issue
```

## 📚 References

- [PydanticAI Tool Documentation](https://ai.pydantic.dev/tools/)
- [Ollama Function Calling](https://ollama.com/blog/tool-support)
- [Llama 3.1 Release](https://ollama.com/library/llama3.1)

## ✅ Success Criteria

You'll know it's working when:

1. **Tool calls visible**: Logs show tool being invoked
2. **Files created**: sandbox/ directory has actual files
3. **No explanations**: Agent doesn't say "To create the file..."
4. **E2E tests pass**: Especially Test 9 (file creation)
