"""Agents package for PydanticAI agents."""

from .factory import AgentFactory, create_agent
from .registry import AgentRegistry, get_agent_registry

# Lazy imports for specialized agents to avoid requiring OLLAMA_BASE_URL at import time
_specialized_agents_imported = False


def _ensure_specialized_agents_imported():
    """Lazy import of specialized agents."""
    global _specialized_agents_imported, codebase_agent, analyze_codebase, CodeAnalysis
    global file_editor_agent, edit_files, EditResult
    global coordinator_agent, delegate_task, DelegationResult
    global testing_agent, generate_tests, run_test_suite, TestResult
    global documentation_agent, generate_readme, generate_api_docs, DocumentationResult
    global refactoring_agent, refactor_file, extract_common_code, RefactoringResult
    
    if not _specialized_agents_imported:
        from .codebase_investigator import get_codebase_agent, analyze_codebase, CodeAnalysis
        from .file_editor import get_file_editor_agent, edit_files, EditResult
        from .delegation import get_coordinator_agent, delegate_task, DelegationResult
        from .testing_agent import get_testing_agent, generate_tests, run_test_suite, TestResult
        from .documentation_agent import get_documentation_agent, generate_readme, generate_api_docs, DocumentationResult
        from .refactoring_agent import get_refactoring_agent, refactor_file, extract_common_code, RefactoringResult
        
        # Make them available at module level
        globals()['codebase_agent'] = get_codebase_agent()
        globals()['analyze_codebase'] = analyze_codebase
        globals()['CodeAnalysis'] = CodeAnalysis
        globals()['file_editor_agent'] = get_file_editor_agent()
        globals()['edit_files'] = edit_files
        globals()['EditResult'] = EditResult
        globals()['coordinator_agent'] = get_coordinator_agent()
        globals()['delegate_task'] = delegate_task
        globals()['DelegationResult'] = DelegationResult
        globals()['testing_agent'] = get_testing_agent()
        globals()['generate_tests'] = generate_tests
        globals()['run_test_suite'] = run_test_suite
        globals()['TestResult'] = TestResult
        globals()['documentation_agent'] = get_documentation_agent()
        globals()['generate_readme'] = generate_readme
        globals()['generate_api_docs'] = generate_api_docs
        globals()['DocumentationResult'] = DocumentationResult
        globals()['refactoring_agent'] = get_refactoring_agent()
        globals()['refactor_file'] = refactor_file
        globals()['extract_common_code'] = extract_common_code
        globals()['RefactoringResult'] = RefactoringResult
        
        _specialized_agents_imported = True


__all__ = [
    "AgentFactory",
    "create_agent",
    "AgentRegistry",
    "get_agent_registry",
]
