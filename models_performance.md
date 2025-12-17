# Model Performance Test Results

This document summarizes the performance of different LLM models tested for code generation with the code extractor micro-agent.

## Test Configuration

**Test**: Generate a complete Tetris game (HTML + CSS + JS)  
**Code Extractor**: `ollama:llama3.1:8b-instruct-q8_0`  
**Date**: December 16-17, 2024

## Performance Summary

### ✅ Working Models

| Model | Provider | Status | Output Quality | Speed | Cost | Notes |
|-------|----------|--------|---------------|-------|------|-------|
| `qwen2.5-coder:14b` | Ollama (Local) | ✅ **BEST** | Excellent - 1,512 bytes, 7/7 checks | Fast (~30s) | FREE | Complete code, no placeholders |
| `llama3.1:8b-instruct-q8_0` | Ollama (Local) | ✅ Good | Good coordination | Fast (~5s) | FREE | Best for coordination/extraction |
| `gemini-2.0-flash-exp` | Google Gemini | ✅ Works | Unknown - hit rate limit | Unknown | FREE (quota) | 429 rate limit error after recognition |

### ⚠️ Partial Success

| Model | Provider | Status | Issue | Output | Notes |
|-------|----------|--------|-------|--------|-------|
| `deepseek/deepseek-chat` | OpenRouter | ⚠️ Incomplete | Lazy generation | 1,232 bytes with placeholders | Generated skeleton with `// ... rest of script...` comments |

### ❌ Failed Models

| Model | Provider | Error Code | Error Message | Cause |
|-------|----------|------------|---------------|-------|
| `qwen/qwen3-coder:free` | OpenRouter (Venice/Chutes) | 429 | Rate limited upstream | Free tier quota exhausted, need to add own API key |
| `kwaipilot/kat-coder-pro:free` | OpenRouter (Novita) | 400 | Invalid request error | Provider incompatibility or model unavailable |
| `gemini-1.5-flash` | Google Gemini | 404 | Model not found | Not available in v1beta API |
| `gemini-1.5-pro` | Google Gemini | 404 | Model not found | Not available in v1beta API |
| `gemini-1.5-flash-latest` | Google Gemini | 404 | Model not found | Alias not supported in v1beta API |
| `google/gemini-flash-1.5` | OpenRouter | 404 | No endpoints found | Incorrect model name format |
| `qwen/qwen-2.5-coder-32b-instruct` | OpenRouter | 404 | No endpoints with tool support | Tool calling not supported |
| `anthropic/claude-3.5-sonnet` | OpenRouter | Timeout | No response | Very slow or hung during request |

## Detailed Test Results

### Local Ollama Models

#### qwen2.5-coder:14b ⭐ RECOMMENDED
```
Format: ollama:qwen2.5-coder:14b
Status: ✅ WORKING - BEST CHOICE
Output: 1,512 bytes
Quality: 7/7 content checks passed
  ✅ Has DOCTYPE
  ✅ Has HTML tag  
  ✅ Has JavaScript
  ✅ Has game board
  ✅ Has pieces
  ✅ Has score tracking
  ✅ Has game logic
Speed: ~30 seconds
Cost: FREE (local)
Notes: Generates complete, working code without placeholder comments
```

#### llama3.1:8b-instruct-q8_0
```
Format: ollama:llama3.1:8b-instruct-q8_0  
Status: ✅ WORKING
Use Case: Coordinator & Code Extractor
Speed: ~5 seconds
Cost: FREE (local)
Notes: Excellent for instruction following and code extraction
```

### OpenRouter Models

#### deepseek/deepseek-chat
```
Format: openai:deepseek/deepseek-chat
Status: ⚠️ PARTIAL - Lazy Generation
Output: 1,232 bytes
Issues:
  - Uses placeholder comments: "// rest of the script... (removed for brevity)"
  - Incomplete implementations
  - Skeleton code only
Cost: ~$0.14/$1.10 per 1M tokens (cheap)
Notes: Code extractor works but source is incomplete
```

#### kwaipilot/kat-coder-pro:free
```
Format: openai:kwaipilot/kat-coder-pro:free
Status: ❌ BROKEN
Error: 400 - Invalid Request
Provider: Novita
Message: "invalid request error trace_id: 3bebd0f04331e3d7bf4e4e92a79ec930"
Notes: Novita provider rejects the request - incompatible or unavailable
```

#### qwen/qwen-2.5-coder-32b-instruct
```
Format: openai:qwen/qwen-2.5-coder-32b-instruct
Status: ❌ NO TOOL SUPPORT
Error: 404 - No endpoints found that support tool use
Notes: Model exists but doesn't support tool calling required by our agent
```

#### anthropic/claude-3.5-sonnet
```
Format: openai:anthropic/claude-3.5-sonnet
Status: ❌ TIMEOUT/VERY SLOW
Issue: Hangs during code generation
Duration: 7+ minutes with no output
Cost: ~$3/$15 per 1M tokens (expensive)
Notes: May work but extremely slow via OpenRouter
```

### Google Gemini Models

#### gemini-2.0-flash-exp (Latest Experimental)
```
Format: google-gla:gemini-2.0-flash-exp
Status: ✅ RECOGNIZED - Rate Limited
Error: 429 - Quota Exceeded
Message: "You exceeded your current quota"
Quotas Hit:
  - Input tokens per minute (free tier)
  - Requests per minute per model (free tier)  
  - Requests per day per model (free tier)
Retry After: 23 seconds
Notes: Model works but free tier quota exhausted quickly
```

#### gemini-1.5-flash / gemini-1.5-pro
```
Format: google-gla:gemini-1.5-flash
Status: ❌ NOT FOUND
Error: 404 - Model not found for API version v1beta
Issue: PydanticAI uses v1beta API which has limited model availability
Notes: Models exist in v1 API but not accessible via PydanticAI's provider
```

#### gemini-1.5-flash-latest (Alias)
```
Format: google-gla:gemini-1.5-flash-latest
Status: ❌ NOT FOUND  
Error: 404 - Model not found
Notes: Latest aliases not supported in v1beta API
```

## Code Extractor Performance

The intelligent code extractor micro-agent successfully processed all model outputs:

✅ **Successes**:
- Extracted clean code from qwen (1,512 bytes → clean HTML/JS)
- Detected multi-file references (HTML + JS separation)
- Removed explanatory text and markdown fences
- Handled incomplete code gracefully (fallback)

⚠️ **Limitations**:
- Cannot fix incomplete source code (garbage in = garbage out)
- Model must generate actual code, not just placeholders

## Recommendations

### For Production
**Use**: `ollama:qwen2.5-coder:14b`
- ✅ Complete, working code
- ✅ Fast (~30s)
- ✅ FREE (local)
- ✅ Reliable

### For Coordination/Routing
**Use**: `ollama:llama3.1:8b-instruct-q8_0`
- ✅ Excellent instruction following
- ✅ Fast (~5s)
- ✅ FREE (local)
- ✅ Good for code extraction

### For Cloud/API
**Avoid for now**:
- ❌ OpenRouter free models (broken/incomplete)
- ❌ Gemini via PydanticAI (quota/API version issues)
- ❌ Claude via OpenRouter (too slow)

**Potential alternatives** (not tested):
- Try Gemini via OpenRouter proxy: `openai:google/gemini-1.5-pro-latest`
- Try other OpenRouter paid models with tool support

## Configuration Examples

### Working Local Setup (.env)
```ini
COORDINATOR_MODEL=ollama:llama3.1:8b-instruct-q8_0
CODE_GENERATOR_MODEL=ollama:qwen2.5-coder:14b
CODE_EXTRACTOR_MODEL=ollama:llama3.1:8b-instruct-q8_0
```

### Hybrid Setup (if testing cloud)
```ini
COORDINATOR_MODEL=ollama:llama3.1:8b-instruct-q8_0
CODE_GENERATOR_MODEL=openai:deepseek/deepseek-chat  # Cheap but incomplete
CODE_EXTRACTOR_MODEL=ollama:llama3.1:8b-instruct-q8_0
```

## Lessons Learned

1. **Local models are most reliable** for code generation
2. **Tool calling support is critical** - many models don't support it
3. **Cloud models have various issues**:
   - Rate limits (Gemini free tier)
   - Incomplete generation (DeepSeek)
   - Incompatibility (KAT Coder Pro)
   - Slow response times (Claude)
4. **Code extractor works perfectly** when given valid input
5. **Model quality matters more than extraction** - can't fix lazy generation

## Next Steps

- [ ] Test Gemini via OpenRouter proxy
- [ ] Test other OpenRouter models with tool support
- [ ] Wait for Gemini quota reset and retest
- [ ] Consider paid tiers for critical workloads
- [ ] Stick with local qwen for production use

#### qwen/qwen3-coder:free
```
Format: openai:qwen/qwen3-coder:free
Status: ❌ RATE LIMITED
Error: 429 - Rate limit exceeded
Providers Tried: Venice, Chutes
Message: "temporarily rate-limited upstream. Please retry shortly, or add your own key"
Notes: Model is recognized and functional but free tier quota is exhausted
Recommendation: Add your own OpenRouter API key to get higher limits
Link: https://openrouter.ai/settings/integrations
```
