"""Agents package for PydanticAI agents."""

from .factory import AgentFactory, create_agent
from .registry import AgentRegistry, get_agent_registry

# Lazy imports for specialized agents to avoid requiring OLLAMA_BASE_URL at import time
_specialized_agents_imported = False


def _ensure_specialized_agents_imported():
    """Lazy import of specialized agents."""
    global _specialized_agents_imported, codebase_agent, analyze_codebase, CodeAnalysis
    global file_editor_agent, edit_files, EditResult
    
    if not _specialized_agents_imported:
        from .codebase_investigator import get_codebase_agent, analyze_codebase, CodeAnalysis
        from .file_editor import get_file_editor_agent, edit_files, EditResult
        
        # Make them available at module level
        globals()['codebase_agent'] = get_codebase_agent()
        globals()['analyze_codebase'] = analyze_codebase
        globals()['CodeAnalysis'] = CodeAnalysis
        globals()['file_editor_agent'] = get_file_editor_agent()
        globals()['edit_files'] = edit_files
        globals()['EditResult'] = EditResult
        
        _specialized_agents_imported = True


__all__ = [
    "AgentFactory",
    "create_agent",
    "AgentRegistry",
    "get_agent_registry",
]
