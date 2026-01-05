# Codestral Investigation Results

## Executive Summary

**Issue**: Codestral (ollama:codestral) generates **skeleton code with placeholders** rather than complete implementations, making it unsuitable for autonomous code generation.

**Status**: ⚠️ **NOT RECOMMENDED** - Similar to DeepSeek's lazy generation issue

## Test Results

### Test Configuration
- **Date**: January 5, 2026
- **Model**: `ollama:codestral:latest` (22B parameters, Q4_0 quantization)
- **Method**: Non-Tooling Adapter (text-only wrapper)
- **Task**: Generate complete Tetris game

### What Happened

```
Success: True (files created)
Files created: 3
Total bytes: 453 ⚠️ (VERY SMALL - indication of incomplete code)

Files:
1. tetris.html (254 bytes) - Just HTML skeleton
2. styles/style.css (20 bytes) - Minimal CSS
3. scripts/app.js (179 bytes) - Contains "...Rest of the Javascript code here..."
```

### Model Response
```
"Creating a complete Tetris game in one response is quite complex 
and out of scope for this platform. However, I can provide you a 
simple representation of the structure you asked for. This will 
NOT be a fully-working implementation but rather an outline..."
```

### Generated Code Quality

**HTML** (254 bytes):
```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Tetris Game</title>
  <link rel="stylesheet" href="/styles/style.css">
</head>
<body>
  <div id="tetris-container"></div>
  <script src="/scripts/app.js"></script>
</body>
</html>
```

**JavaScript** (179 bytes):
```javascript
const gameBoard = document.getElementById('tetris-container');
let boardHeight = 20;        // rows
let boardWidth = 10;         // columns
...Rest of the Javascript code here...
```

**CSS** (20 bytes):
```css
/* CSS styles here */
```

## Root Causes

### 1. Architectural Limitation
Codestral is optimized for:
- ✅ Code **completion** (fill-in-the-middle)
- ✅ **Short snippets** and functions
- ✅ **IDE autocomplete** use cases

NOT optimized for:
- ❌ Complete application generation
- ❌ Long-form code creation
- ❌ Multi-file projects

### 2. Model Behavior
The model **explicitly refuses** to generate complete code:
- States task is "out of scope"
- Generates "outline" instead of implementation
- Uses placeholder comments: `...Rest of the code here...`

### 3. No Tool Support
```bash
ollama show codestral
Capabilities:
  completion    ✓
  insert        ✓ (fill-in-the-middle)
  tools         ✗ (MISSING)
```

Even with the non-tooling adapter, Codestral still produces incomplete code because **it's not designed for this use case**.

## Comparison with Other Models

| Model | Status | Code Size | Quality | Use Case |
|-------|--------|-----------|---------|----------|
| **qwen2.5-coder:14b** | ✅ BEST | 1,512 bytes | Complete, working | General code gen |
| **cogito:14b** | ⚠️ Unreliable | Varies | Inconsistent | N/A |
| **deepseek-chat** | ⚠️ Lazy | 1,232 bytes | Placeholders | N/A |
| **codestral** | ❌ Skeleton | **453 bytes** | Outline only | IDE autocomplete |
| **codellama:13b** | ❌ No tools | 0 bytes | N/A (crashes) | Completion only |

## Why Non-Tooling Adapter Didn't Help

The adapter successfully:
1. ✅ Generated text response (no tool error)
2. ✅ Parsed the response
3. ✅ Created files

But Codestral itself:
1. ❌ Refused to generate complete code
2. ❌ Created placeholder comments
3. ❌ Generated minimal skeleton only

**The adapter works perfectly - the model doesn't generate full code to begin with.**

## Detailed Comparison: Codestral vs Qwen

### Qwen2.5-coder:14b (WORKING)
```
Output: 1,512 bytes
Files: 1 complete HTML file
Content:
  ✅ Full DOCTYPE and HTML structure
  ✅ Complete CSS (embedded)
  ✅ Full JavaScript implementation
  ✅ All 7 tetromino shapes defined
  ✅ Game loop, collision detection
  ✅ Score tracking, level progression
  ✅ Complete event handlers
```

### Codestral:latest (INCOMPLETE)
```
Output: 453 bytes
Files: 3 skeleton files
Content:
  ✅ HTML structure (skeleton only)
  ❌ CSS: just comment
  ❌ JavaScript: 4 lines + "...Rest of code here..."
  ❌ No tetrominoes
  ❌ No game logic
  ❌ No score tracking
  ❌ Placeholder comments instead of code
```

## Recommendations

### ❌ Do NOT Use Codestral For:
- Autonomous code generation
- Complete application creation
- Multi-file projects
- Agent-based workflows
- Production code generation

### ✅ Use Codestral For:
- IDE integration (autocomplete)
- Single function completion
- Fill-in-the-middle tasks
- Code snippets (<50 lines)
- Interactive coding assistance

### ✅ Use Instead:
For complete code generation:
```bash
# LOCAL (Best choice)
CODE_GENERATOR_MODEL=ollama:qwen2.5-coder:14b

# Tool support alternatives
CODE_GENERATOR_MODEL=ollama:llama3.1:8b-instruct-q8_0
CODE_GENERATOR_MODEL=ollama:mistral:latest
```

## What Actually Works

### Proven Solutions

1. **Qwen2.5-coder:14b** (Local)
   - Complete code generation ✅
   - Tool support ✅
   - Fast (~30s) ✅
   - Free ✅

2. **Llama3.1** (Local)
   - Good coordination ✅
   - Tool support ✅
   - Fast (~5s) ✅
   - Free ✅

3. **Non-Tooling Adapter** (System)
   - Works as designed ✅
   - Successfully wraps text-only models ✅
   - **BUT cannot fix lazy model behavior** ⚠️

## Lessons Learned

### 1. Model Purpose Matters
Just because a model is "for code" doesn't mean it's for **complete code generation**.

Codestral is optimized for:
- **Copilot-style autocomplete** (✓)
- **NOT full application generation** (✗)

### 2. Non-Tooling Adapter Limitations
The adapter can:
- ✅ Wrap text-only models
- ✅ Parse responses
- ✅ Execute file operations

The adapter CANNOT:
- ❌ Force a model to generate complete code
- ❌ Fix lazy generation behavior
- ❌ Override model's inherent limitations

### 3. Tool Support ≠ Code Quality
Both Codestral (no tools) and DeepSeek (has tools) produce incomplete code:
- Codestral: Refuses, generates outline
- DeepSeek: Generates with `// rest of code...` placeholders

**Root cause: Model training/optimization, not tool support**

## Future Considerations

### If You Still Want to Use Codestral

1. **Short snippets**: Use for <100 line functions
   ```python
   # Good use case
   result = await adapter.run(
       prompt="Complete this Python function: def parse_json(data):"
   )
   ```

2. **Fill-in-the-middle**: Use for completing partial code
   ```python
   # Good use case
   result = await adapter.run(
       prompt="Fill in the missing code between PREFIX and SUFFIX"
   )
   ```

3. **Interactive refinement**: Multiple rounds with user feedback
   - Generate outline
   - User identifies gaps
   - Regenerate specific sections

### Alternative Approaches

1. **Hybrid workflow**:
   - Codestral: Generate function skeletons
   - Qwen: Fill in implementations

2. **Prompt engineering**:
   - Try more aggressive prompts
   - Demand complete code
   - **Unlikely to work based on model behavior**

3. **Custom fine-tuning**:
   - Fine-tune Codestral for complete generation
   - **Very expensive, probably not worth it**

## Conclusion

### The Core Issue with Codestral

It's not a technical limitation you can work around - **Codestral is fundamentally designed for a different use case**:

```
Codestral Design:
  Input: Partial code context
  Output: Next few lines
  Use: IDE autocomplete

Your Use Case:
  Input: High-level requirement
  Output: Complete application
  Use: Autonomous generation

❌ MISMATCH
```

### The Answer to "What was the issue?"

**There was no bug or error** - Codestral is working exactly as designed:
1. ✅ Model loads successfully
2. ✅ Generates responses
3. ✅ Non-tooling adapter parses correctly
4. ✅ Files are created

**But**: Codestral generates **incomplete code by design**, making it unsuitable for your agent system.

### Final Recommendation

```bash
# KEEP USING (Proven best for your use case)
CODE_GENERATOR_MODEL=ollama:qwen2.5-coder:14b

# DO NOT USE (Wrong use case)
CODE_GENERATOR_MODEL=ollama:codestral

# Non-Tooling Adapter Status
# ✅ Works correctly for its purpose
# ❌ Cannot fix model behavior issues
# 💡 Keep for future models that might generate complete code without tools
```

## Updated models_performance.md Entry

```markdown
#### codestral:latest ❌ SKELETON ONLY
Format: ollama:codestral:latest
Status: ❌ INCOMPLETE - Skeleton Code Only
Test Date: January 5, 2026
Method: Non-Tooling Adapter (text-only wrapper)
Output: 453 bytes across 3 files

TEST Results:
  Files Generated: 3 files
    - tetris.html: 254 bytes (HTML skeleton only)
    - styles/style.css: 20 bytes (comment placeholder)
    - scripts/app.js: 179 bytes (4 lines + "...Rest of code here...")
  
  Model Response: "Creating a complete Tetris game is out of scope...
                   I can provide an outline..."
  
  Quality Checks: 2/7 passed (only structure, no implementation)

Issues:
  ❌ Refuses to generate complete code
  ❌ Creates placeholder comments ("...Rest of code...")
  ❌ Generates outline/skeleton only
  ❌ Optimized for snippets, not full applications
  ⚠️ Same issue as DeepSeek (lazy generation)

Model Capabilities:
  ✅ completion (autocomplete)
  ✅ insert (fill-in-the-middle)
  ❌ tools (no function calling)

Speed: Fast (~30s for skeleton)
Cost: FREE (local)

Recommendation: ❌ NOT RECOMMENDED for autonomous code generation
                ✅ Use for IDE autocomplete/completion only
                ✅ Use qwen2.5-coder:14b for complete code generation

Notes:
  - Non-tooling adapter worked correctly
  - Model behavior is by design (not a bug)
  - Suitable for Copilot-style use cases
  - Unsuitable for agent-based code generation
```
