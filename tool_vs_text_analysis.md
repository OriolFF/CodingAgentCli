# Tool vs Text Model Interaction: Gemini CLI & Codex Analysis

**Question**: How do these CLIs handle models with/without tool support?  
**Date**: December 17, 2024

## TL;DR - The Answer

**Both Gemini CLI and Codex REQUIRE tool calling** - they don't have text-only fallbacks for their core workflows. This is fundamentally different from our hybrid approach.

---

## Gemini CLI: Tool-First Architecture

### Model Compatibility

**Gemini models with tool support**:
- gemini-3-pro (preview)
- gemini-2.5-pro
- gemini-2.5-flash
- gemini-2.0-flash

**Key insight**: Gemini CLI is designed **ONLY**  for Gemini models, all of which support function calling.

### Tool Execution Flow

```
1. User prompt
   ↓
2. Model decides → FunctionCall
   ↓
3. Core parses FunctionCall
   ↓
4. Tool validation
   ↓
5. User confirmation (if needed)
   ↓
6. Tool execution
   ↓
7. FunctionResponse → back to model
   ↓
8. Final response to user
```

**Critical**: The flow EXPECTS `FunctionCall` objects. No fallback for text-only responses.

### Tool Choice Options

From AI SDK integration:
- `'auto'` - Model decides whether to call function
- `'none'` - Disables function calling
- `'required'` - Ensures tool call is made

**Important**: When set to `'auto'`, model can choose NOT to use tools and just return text!

### Model Fallback

Gemini CLI has automatic **model fallback**:
- `gemini-2.5-pro` → `gemini-2.5-flash` (if overloaded)
- Handles 429/503 rate limit errors

BUT this is **model** fallback, not **tool** fallback. Both models support tools.

---

## Codex: Function Calling with Multi-Model Support

### Model Compatibility

**Primary models**:
- `gpt-5-codex` (default)
- `gpt-5`
- `gpt-5.1-codex`
- `gpt-5.2`

**Extended via OpenAI API compatibility**:
- OpenRouter
- Gemini
- Ollama
- Mistral
- Deepseek
- XAI
- Groq

**Key insight**: Can use ANY model with OpenAI-compatible API + function calling support.

### Agent Loop Logic

From `src/utils/agent/agent-loop.ts`:
- Manages interaction with OpenAI API
- Handles different response types **including `function_call`**
- MCP integration for additional tools

**Critical**: The agent loop is built around `function_call` responses.

### Non-interactive Mode

```bash
codex exec "explain this code"
```

Even in headless/automation mode, **still uses tool calling**.

---

## The Critical Difference: Our Approach vs Theirs

| Aspect | Gemini CLI | Codex | Our System (Before) | Our System (Now) |
|--------|------------|-------|---------------------|------------------|
| **Tool Strategy** | Required | Required | Optional (with fallback) | Mixed |
| **Model Compatibility** | Gemini only | OpenAI-compatible only | Any model | Any model |
| **Tool Support** | Always available | Always available | Sometimes missing | Sometimes missing |
| **Fallback** | Model swap (pro→flash) | None documented | Code extraction | Code extraction |
| **Code Generation** | Via tools | Via tools | Via tools → fallback | **Text-only** |

---

## What This Means for Our Decision

### Their Philosophy: "Tool Calling is Table Stakes"

Both Gemini CLI and Codex **assume** models support function calling:

1. **Gemini CLI**: Uses only Gemini models (all have tools)
2. **Codex**: Uses OpenAI-compatible models (all have tools)

They **don't support** models without tool calling... they just *don't use those models*.

### Our Philosophy: "Universal Compatibility"

We want to support **any model**, including:
- ✅ Models with tool support (qwen, llama3.1, gpt, claude)
- ✅ Models WITHOUT tool support (cogito, codellama, etc.)

**This is fundamentally different!**

---

## The Key Insight

### What We Learned

**Gemini CLI and Codex DON'T solve the "tool vs text" problem** - they **avoid it** by only using models with tool support!

When we removed tools from code_generator, we made a **strategic architectural choice** they didn't:

```
Their approach:  Require tool support → Limit model compatibility
Our approach:    Text-only generation → Universal compatibility
```

### Why This Makes Sense

#### For Code Generation Specifically:

**Tool calling adds complexity without much value**:
```python
# With tools - model must:
1. Decide to use create_file tool
2. Format parameters correctly
3. Tool execution creates file

# Text-only - model just:
1. Generate code as text
2. We extract and write it
```

**Benefits of text-only for code gen**:
- ✅ Works with ALL models
- ✅ Simpler (no tool formatting overhead)
- ✅ Better code quality (model focuses on code, not tool syntax)
- ✅ No API compatibility issues

#### For Other Operations (File editing, analysis):

**Tool calling provides structure**:
```python
# Editing needs:
- Precise file path
- Exact search/replace text
- Confirmation of action

# Tools ensure this structure!
```

---

## Recommendations Based on Findings

### ✅ What We Should Keep

1. **Text-only code generation** (code_generator)
   - Neither CLI does this, but it's our competitive advantage
   - Enables universal model compatibility

2. **Tool calling for operations** (file_editor, refactoring, etc.)
   - Following their pattern
   - Ensures structured, reliable operations

### ✅ What We Should Add

1. **Tool choice flexibility** (from Gemini)
   ```python
   tool_choice='auto'      # Model decides
   tool_choice='required'  # Force tool use
   tool_choice='none'      # Disable tools
   ```

2. **Model capability detection**
   ```python
   if model_supports_tools(model_name):
       use_tools()
   else:
       use_text_only()
   ```

3. **Per-agent tool configuration**
   ```ini
   # .env
   CODE_GENERATOR_USE_TOOLS=false      # Text-only
   FILE_EDITOR_USE_TOOLS=true          # Tools required
   REFACTORING_USE_TOOLS=true          # Tools required
   COORDINATOR_USE_TOOLS=true          # Tools are delegation!
   ```

---

## Conclusion: We Made the Right Choice

### Their Constraint
Gemini CLI and Codex are **constrained** to models with tool support. This works because:
- Gemini CLI: All Gemini models have tools
- Codex: All OpenAI(-compatible) models have tools

### Our Advantage

By removing tools from code_generator, we:
- ✅ Support **any** model (cogito, codellama, etc.)
- ✅ Simplify code generation
- ✅ Improve code quality (no tool syntax overhead)
- ✅ Maintain structure where needed (other agents keep tools)

**This is actually a BETTER architecture** for our use case!

---

## Final Answer to the Question

**Q: How do Gemini CLI and Codex handle models without tool support?**

**A: They don't. They only use models WITH tool support.**

This is their design constraint, not a feature to copy.

Our hybrid approach (text-only code gen + tool-based operations) is **more flexible** and **more compatible** than either of theirs.
