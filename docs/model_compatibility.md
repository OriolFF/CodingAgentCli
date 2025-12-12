# Model Compatibility Notes

## Structured Output Support

Not all Ollama models support structured outputs (JSON mode) equally well. This affects PydanticAI's ability to enforce Pydantic model outputs.

### Known Issues

**Models with Limited Structured Output Support**:
- `qwen2.5-coder:14b` - Struggles with JSON formatting for structured outputs
- Some coding-specific models may prioritize code generation over JSON compliance

**Models with Good Structured Output Support**:
- `mistral` - Good JSON/structured output support
- `llama2` - Generally reliable for structured outputs
- `gemini-*` - Cloud models with excellent structured output

### Future Implementation Requirements

To handle model compatibility issues, we need to implement:

1. **Model Capability Detection**
   - Check if model supports tool calling
   - Check if model supports structured JSON output
   - Maintain a capabilities matrix

2. **Automatic Fallback Mechanisms**
   - Detect when structured output fails
   - Fall back to text-only mode
   - Parse text responses with regex/LLM extraction

3. **Per-Model Configuration**
   - `supports_tools: bool` in model config
   - `supports_structured_output: bool` in model config
   - `fallback_model: str` for when primary fails

4. **Graceful Degradation**
   - Try structured output first
   - On validation failure, retry with text mode
   - Log compatibility issues for future reference

### Configuration Example (Future)

```yaml
models:
  qwen2.5-coder:
    provider: ollama
    supports_tools: false
    supports_structured_output: false
    fallback_model: mistral
    use_case: code_generation
    
  mistral:
    provider: ollama
    supports_tools: true
    supports_structured_output: true
    use_case: general
```

### Implementation Priority

- **Phase 3** (Steps 11-25): Add tool compatibility detection
- **Phase 4** (Steps 26-32): Implement model capability registry
- **Phase 5** (Steps 33-37): Add automatic fallback logic

---

**Status**: Documented issue, solution planned for future phases
**Impact**: Currently using mistral for general testing to avoid issues
**Tracked In**: This document + future implementation steps
