# E2E Test Execution Report (Hybrid File Creation)

**Date**: 2025-12-12 15:20:48  
**Tests Executed**: 10  
**Passed**: 10 ✅  
**Failed**: 0 ❌  
**Pass Rate**: 100.0%

---

## Test Results


### Test 1 (analysis): ✅ PASS

**Command**: `how many python files are in the packages/core/agents directory?`  
**Criteria**: Returns specific number  
**Agents Used**:   

---

### Test 2 (analysis): ✅ PASS

**Command**: `which is the largest python file in packages/core/?`  
**Criteria**: Identifies largest file  
**Agents Used**:   

---

### Test 3 (generation): ✅ PASS

**Command**: `create a file sandbox/calculator.py with functions add, subtract, multiply, divide`  
**Criteria**: File with 4 functions  
**Agents Used**: file_editor  

**Files Created**: sandbox/calculator.py  

**sandbox/calculator.py Quality**:  
- Lines: 10  
- Functions: 4  
- Classes: 0  
- Docstrings: ❌  
- Type hints: ❌  

---

### Test 4 (generation): ✅ PASS

**Command**: `create sandbox/person.py with a Person class that has name, age attributes and a greet() method`  
**Criteria**: Person class file  
**Agents Used**:   

**Files Created**: sandbox/person.py  

**sandbox/person.py Quality**:  
- Lines: 7  
- Functions: 2  
- Classes: 1  
- Docstrings: ❌  
- Type hints: ❌  

---

### Test 5 (generation): ✅ PASS

**Command**: `create sandbox/user_model.py with a Pydantic model for User with email validation`  
**Criteria**: Pydantic model file  
**Agents Used**:   

**Files Created**: sandbox/user_model.py  

**sandbox/user_model.py Quality**:  
- Lines: 10  
- Functions: 1  
- Classes: 1  
- Docstrings: ❌  
- Type hints: ❌  

---

### Test 6 (generation): ✅ PASS

**Command**: `create sandbox/string_utils.py with functions: capitalize_words, reverse_string, count_vowels`  
**Criteria**: 3 utility functions  
**Agents Used**: file_editor  

**Files Created**: sandbox/string_utils.py  

**sandbox/string_utils.py Quality**:  
- Lines: 8  
- Functions: 3  
- Classes: 0  
- Docstrings: ❌  
- Type hints: ❌  

---

### Test 7 (generation): ✅ PASS

**Command**: `create sandbox/api.py with a simple FastAPI endpoint for GET /health`  
**Criteria**: FastAPI file  
**Agents Used**:   

**Files Created**: sandbox/api.py  

**sandbox/api.py Quality**:  
- Lines: 5  
- Functions: 1  
- Classes: 0  
- Docstrings: ❌  
- Type hints: ❌  

---

### Test 8 (generation): ✅ PASS

**Command**: `generate sandbox/hello_cli.py with a click-based CLI that has a hello command`  
**Criteria**: Click CLI file  
**Agents Used**: file_editor  

**Files Created**: sandbox/hello_cli.py  

**sandbox/hello_cli.py Quality**:  
- Lines: 5  
- Functions: 1  
- Classes: 0  
- Docstrings: ❌  
- Type hints: ❌  

---

### Test 9 (generation): ✅ PASS

**Command**: `create sandbox/test_calculator.py with pytest tests for calculator functions`  
**Criteria**: Test file  
**Agents Used**: codebase_investigator, file_editor  

**Files Created**: sandbox/test_calculator.py  

**sandbox/test_calculator.py Quality**:  
- Lines: 7  
- Functions: 3  
- Classes: 0  
- Docstrings: ❌  
- Type hints: ❌  

---

### Test 10 (generation): ✅ PASS

**Command**: `create sandbox/app_config.py with a Config class using Pydantic Settings`  
**Criteria**: Config file  
**Agents Used**:   

**Files Created**: sandbox/app_config.py  

**sandbox/app_config.py Quality**:  
- Lines: 8  
- Functions: 0  
- Classes: 1  
- Docstrings: ❌  
- Type hints: ❌  

---

## Summary

- **Pass Rate**: 100.0%
- **Status**: ✅ ALL TESTS PASSED
- **Total Files Created**: 8

## Files in Sandbox

- No files created
