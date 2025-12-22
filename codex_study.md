# OpenAI Codex Study

**Repository**: https://github.com/openai/codex  
**Analysis Date**: December 17, 2024

## Overview

OpenAI Codex is a lightweight coding agent that runs in the terminal. It emphasizes **security through sandboxing** and **flexible execution policies**.

## Architecture

### Key Components

1. **CLI** - User interface (TUI/interactive)
2. **Core** - Backend logic
3. **Sandbox** - Isolated execution environment
4. **Execpolicy** - Rules engine for command approval
5. **AGENTS.md** - Memory/context system

## Memory System: AGENTS.md

Similar to Gemini's GEMINI.md but with a **hierarchical override pattern**:

1. **Global**: `~/.codex/AGENTS.md` - personal guidance
2. **Repository root → current directory**: Inherits instructions
3. **Override mechanism**: `AGENTS.override.md` replaces inherited instructions

**Key insight**: Override pattern allows fine-grained control per directory.

## Security Architecture

### Approval Policies

| Mode | Description | Use Case |
|------|-------------|----------|
| **Read-only** | No edits allowed | Safe browsing, code review |
| **Agent** (Default for trusted) | Writes inside workspace | Normal development |
| **Full Access** | No restrictions | Automation (risky) |

**Trust system**: Directories must be explicitly trusted before allowing writes.

### Sandbox Modes

```
--sandbox read-only           # Reads only
--sandbox workspace-write     # Writes in workspace
--dangerously-bypass          # No sandbox (YOLO)
```

**Workspace-write** sandbox:
- Edits allowed inside working directory + `/tmp`
- Network disabled by default
- Requires approval to leave workspace

### Execpolicy: Rules Engine

**Location**: `~/.codex/rules/*.rules`

**Syntax** (Starlark):
```starlark
prefix_rule(
    pattern = ["git", ["push", "fetch"]],
    decision = "prompt",  # allow | prompt | forbidden
    match = [["git", "push", "origin", "main"]],
    not_match = [["git", "status"]],
)
```

**Features**:
- Prefix matching with alternatives
- Strictest rule wins (forbidden > prompt > allow)
- Built-in unit tests (`match`/`not_match`)
- Preview with `codex execpolicy check`
- TUI whitelisting during usage

**Brilliance**: Users can create rules **during** usage by whitelisting prompted commands!

## Session Management

**Resume sessions**:
```bash
codex resume                 # Picker UI
codex resume --last          # Most recent
codex resume <SESSION_ID>    # Specific session
```

Sessions stored in `~/.codex/sessions/` with:
- Original working directory
- Git branch context

## Execution Modes

| Command | Purpose | Example |
|---------|---------|---------|
| `codex` | Interactive TUI | `codex` |
| `codex "..."` | Initial prompt | `codex "fix lint errors"` |
| `codex exec "..."` | Non-interactive | `codex exec "explain utils.ts"` |

**Flags**:
- `--model/-m`: Select model
- `--ask-for-approval/-a`: Approval mode
- `--sandbox`: Sandbox mode
- `--full-auto`: Trusted workspace auto-mode

## Approval + Sandbox Combos

| Intent | Flags | Effect |
|--------|-------|--------|
| Safe browsing | `--sandbox read-only --ask-for-approval on-request` | Requires approval for all changes |
| CI/automation | `--sandbox read-only --ask-for-approval never` | Read-only, no prompts |
| Normal dev | `--full-auto` | Workspace writes, prompt for risky actions |
| YOLO | `--yolo` | No sandbox, no prompts ⚠️ |

## Configuration

**File**: `~/.codex/config.toml`

**Profiles**:
```toml
[profiles.full_auto]
approval_policy = "on-request"
sandbox_mode = "workspace-write"

[profiles.readonly_quiet]
approval_policy = "never"
sandbox_mode = "read-only"
```

## Key Features

1. ✅ **AGENTS.md** - Hierarchical memory with override
2. ✅ **Execpolicy** - Programmable rules engine
3. ✅ **Sandbox** - Isolated execution (read-only, workspace-write)
4. ✅ **Trust system** - Explicit directory approval
5. ✅ **Session resume** - Continue where you left off
6. ✅ **Non-interactive mode** - `codex exec` for scripts
7. ✅ **MCP integration** - Extend with MCP servers
8. ✅ **Custom prompts** - Slash commands
9. ✅ **GitHub Action** - CI/CD integration
10. ✅ **TypeScript SDK** - Programmatic access

## Example Prompts

```bash
codex "Refactor Dashboard to React Hooks"       # Rewrites, tests, shows diff
codex "Generate SQL migrations for users table" # Creates and runs migrations
codex "Write unit tests for utils/date.ts"      # Generates and validates tests
codex "Bulk-rename *.jpeg -> *.jpg with git mv" # Safely renames with git
codex "Explain this regex: ^(?=.*[A-Z]).{8,}$"  # Human explanation
```

## Design Principles

1. **Security First**: Sandbox + approval by default
2. **Progressive Trust**: Start restricted, grant access as needed
3. **Rule-based Control**: Execpolicy for fine-grained permissions
4. **Session Continuity**: Resume complex conversations
5. **Automation Ready**: Non-interactive mode for scripts

## Insights for Our CLI

### ✅ Should Adopt

1. **AGENTS.md with Override**
   - Better than Gemini's simple inheritance
   - Per-directory customization
   - `AGENTS.override.md` = powerful pattern

2. **Execpolicy Rules Engine**
   - Programmable command approval
   - Whitelist during usage (brilliant UX!)
   - Unit tests built-in

3. **Sandbox Modes**
   - Read-only for safety
   - Workspace-write for development
   - Clear trust boundaries

4. **Session Resume**
   - Save/restore conversations
   - Track working directory + git context

5. **Non-interactive Mode**
   - For CI/CD and automation
   - `codex exec` equivalent

### 📊 Comparison to Our System

| Feature | Codex | Our CLI |
|---------|-------|---------|
| **Memory** | AGENTS.md (hierarchical + override) | None yet |
| **Security** | Sandbox + execpolicy | Basic approval.py |
| **Sessions** | Resume by ID/last | No session management |
| **Automation** | `codex exec` non-interactive | Script-based only |
| **Models** | Single (OpenAI) | Multi-model coordination |
| **Delegation** | Single agent + tools | Multi-agent system |

### 🎯 Key Differences

**Codex**:
- Security-focused (sandbox, execpolicy, trust)
- Single agent with extensive tooling
- Production-ready automation

**Our System**:
- Quality-focused (validation, refactoring)
- Multi-agent with specialization
- Model flexibility (local + cloud)

## Recommendations

1. **Implement AGENTS.md**
   - Use Codex's override pattern (better than Gemini)
   - `AGENTS.override.md` for directory-specific rules

2. **Add Execpolicy-style Rules**
   - Programmable approval system
   - TUI whitelisting during usage
   - Rules in `~/.agent/rules/*.rules`

3. **Enhance Sandbox**
   - Read-only mode for safety
   - Workspace-write for normal use
   - Track trusted directories

4. **Add Session Management**
   - Save conversation state
   - Resume by ID or --last
   - Track git context

5. **Create Non-interactive Mode**
   - `agent exec "..."` for scripts
   - No TUI, just execution
   - For CI/CD pipelines

## Conclusion

Codex prioritizes **security and automation** with sophisticated sandboxing and programmable rules. The execpolicy rules engine is particularly innovative - allowing users to build whitelists during usage is brilliant UX.

**Best practices to steal**:
1. AGENTS.override.md pattern
2. Execpolicy rules engine
3. Workspace sandboxing
4. Session resumption
5. Non-interactive automation mode

Combined with our multi-agent architecture and quality validation, we could build something uniquely powerful.
