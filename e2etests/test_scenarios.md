# E2E Test Scenarios for PydanticAI Agent System

## Test Execution Plan

**Purpose**: Validate all agent capabilities with real-world scenarios  
**Workspace**: `sandbox/` directory (all code generation/manipulation)  
**Method**: Execute sequentially, fix issues, retry until all pass

---

## Test Categories

### Category 1: Code Analysis (Tests 1-8)
### Category 2: Code Generation (Tests 9-16)
### Category 3: File Manipulation (Tests 17-22)
### Category 4: Multi-Agent Workflows (Tests 23-27)
### Category 5: Advanced Features (Tests 28-30)

---

## Test Scenarios

### 📊 Category 1: Code Analysis

#### Test 1: Count Files
**Command**: `how many python files are in the packages/core/agents directory?`  
**Expected**: Actual count with file list  
**Success Criteria**: Returns specific number and lists files

#### Test 2: Find Largest File
**Command**: `which is the largest python file in packages/core/?`  
**Expected**: Filename and size  
**Success Criteria**: Identifies actual largest file with size

#### Test 3: Analyze Code Structure
**Command**: `analyze the structure of @packages/core/agents/delegation.py`  
**Expected**: Description of classes, functions, purpose  
**Success Criteria**: Identifies DelegationResult class, delegate_task function

#### Test 4: Find Dependencies
**Command**: `what dependencies does @packages/core/config/config.py have?`  
**Expected**: List of imports and external packages  
**Success Criteria**: Mentions pydantic, os, Path, etc.

#### Test 5: Code Quality Assessment
**Command**: `assess code quality of @packages/cli/repl.py`  
**Expected**: Strengths, weaknesses, suggestions  
**Success Criteria**: Provides specific feedback

#### Test 6: Find Patterns
**Command**: `find all async functions in packages/core/agents/`  
**Expected**: List of async function names  
**Success Criteria**: Lists actual async functions

#### Test 7: Complexity Analysis
**Command**: `which file in packages/core/agents/ is most complex?`  
**Expected**: File identification with reasoning  
**Success Criteria**: Provides complexity metrics or reasoning

#### Test 8: Documentation Check
**Command**: `check if @packages/core/agents/factory.py has proper docstrings`  
**Expected**: Assessment of documentation coverage  
**Success Criteria**: Reports on docstring presence

---

### 🔨 Category 2: Code Generation

#### Test 9: Simple Function
**Command**: `create a file sandbox/calculator.py with functions add, subtract, multiply, divide`  
**Expected**: File created with 4 functions  
**Success Criteria**: File exists, all functions present with docstrings

#### Test 10: Class Generation
**Command**: `create sandbox/person.py with a Person class that has name, age attributes and a greet() method`  
**Expected**: Person class with attributes and method  
**Success Criteria**: Class definition correct, greet returns greeting

#### Test 11: Data Model
**Command**: `create sandbox/user_model.py with a Pydantic model for User with email validation`  
**Expected**: Pydantic BaseModel with email field  
**Success Criteria**: Imports BaseModel, has EmailStr field

#### Test 12: API Endpoint
**Command**: `generate sandbox/api.py with a simple FastAPI endpoint for GET /health`  
**Expected**: FastAPI app with health endpoint  
**Success Criteria**: Imports FastAPI, defines app, has @app.get("/health")

#### Test 13: Test File
**Command**: `generate pytest tests for sandbox/calculator.py and save as sandbox/test_calculator.py`  
**Expected**: Test file with test functions  
**Success Criteria**: Has test functions for each calculator function

#### Test 14: Utility Functions
**Command**: `create sandbox/string_utils.py with functions: capitalize_words, reverse_string, count_vowels`  
**Expected**: Three utility functions  
**Success Criteria**: All functions implemented correctly

#### Test 15: Configuration Class
**Command**: `create sandbox/app_config.py with a Config class using Pydantic Settings`  
**Expected**: Config class with BaseSettings  
**Success Criteria**: Imports BaseSettings, has model_config

#### Test 16: CLI Script
**Command**: `generate sandbox/hello_cli.py with a click-based CLI that has a hello command`  
**Expected**: Click CLI with hello command  
**Success Criteria**: Imports click, has @click.command

---

### 📝 Category 3: File Manipulation

#### Test 17: Create and Modify
**Command**: `create sandbox/counter.py with a Counter class, then add a reset() method`  
**Expected**: File created, then modified to add method  
**Success Criteria**: reset() method exists after modification

#### Test 18: Refactor Function
**Command**: `in sandbox/calculator.py, add type hints to all functions`  
**Expected**: All functions have type annotations  
**Success Criteria**: Parameters and returns are typed

#### Test 19: Add Docstrings
**Command**: `add docstrings to all functions in sandbox/string_utils.py`  
**Expected**: All functions have docstrings  
**Success Criteria**: Each function has """docstring"""

#### Test 20: Extract to Module
**Command**: `create sandbox/math_ops.py and move add/subtract from calculator.py there`  
**Expected**: New file with 2 functions, original updated  
**Success Criteria**: Functions moved, imports updated

#### Test 21: Rename Variable
**Command**: `in sandbox/person.py, rename 'age' to 'years_old' everywhere`  
**Expected**: All references updated  
**Success Criteria**: No 'age' references remain, 'years_old' used

#### Test 22: Add Error Handling
**Command**: `add try-except error handling to sandbox/calculator.py divide function`  
**Expected**: Divide has ZeroDivisionError handling  
**Success Criteria**: try-except block present

---

### 🔄 Category 4: Multi-Agent Workflows

#### Test 23: Analyze and Generate Tests
**Command**: `analyze sandbox/calculator.py then generate comprehensive tests for it`  
**Expected**: Analysis followed by test generation  
**Success Criteria**: Tests cover edge cases identified in analysis

#### Test 24: Review and Refactor
**Command**: `review sandbox/person.py for improvements, then apply them`  
**Expected**: Suggestions followed by actual changes  
**Success Criteria**: Code quality improved

#### Test 25: Document Generation
**Command**: `create a README.md for the sandbox/ directory describing all modules`  
**Expected**: README with module descriptions  
**Success Criteria**: Lists all .py files with descriptions

#### Test 26: Find and Fix
**Command**: `find potential issues in sandbox/*.py files and fix them`  
**Expected**: Issue identification and fixes  
**Success Criteria**: Specific issues reported and corrected

#### Test 27: Comprehensive Analysis
**Command**: `analyze all files in sandbox/ and create a summary report`  
**Expected**: Report covering all files  
**Success Criteria**: Document created with analysis

---

### 🚀 Category 5: Advanced Features

#### Test 28: Multi-File Comparison
**Command**: `compare @sandbox/calculator.py and @sandbox/math_ops.py`  
**Expected**: Comparison of both files  
**Success Criteria**: Identifies similarities and differences

#### Test 29: Dependency Graph
**Command**: `analyze imports across sandbox/ and show dependencies`  
**Expected**: Dependency visualization or description  
**Success Criteria**: Shows which files import which

#### Test 30: Complete Project
**Command**: `create a complete todo app with: sandbox/todo.py (model), sandbox/todo_cli.py (CLI), sandbox/test_todo.py (tests)`  
**Expected**: Three files creating working todo app  
**Success Criteria**: All files created, interconnected, functional

---

## Execution Instructions

### Phase 1: Manual Validation (This Document)
- Review test scenarios
- Approve or request changes
- Ensure coverage is comprehensive

### Phase 2: Execution
For each test:
1. Execute command via CLI or programmatically
2. Capture result
3. Validate against success criteria
4. If fails: diagnose, fix agent/prompt, retry
5. Log results

### Phase 3: Reporting
- Create execution report: `e2etests/results.md`
- Document failures and fixes
- Calculate pass rate
- Identify improvement areas

---

## Success Metrics

- **Target**: 100% pass rate (30/30)
- **Minimum Acceptable**: 90% (27/30)
- **Key Areas**: 
  - Code generation accuracy
  - File manipulation correctness  
  - Multi-agent coordination
  - Natural language understanding

---

## Notes

- All generated code goes to `sandbox/`
- Tests verify actual agent capabilities
- Real-world scenarios users would attempt
- Mix of simple and complex tasks
- Progressive difficulty within categories
