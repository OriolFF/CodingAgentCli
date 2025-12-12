"""Persistent memory tool using SQLite."""

import sqlite3
import aiosqlite
import json
from pathlib import Path
from typing import Optional, Any, List, Dict
from datetime import datetime
from .base import BaseTool, ToolResult, ToolError


class MemoryTool(BaseTool):
    """Tool for storing and retrieving persistent memories.
    
    Uses SQLite for simple persistent storage of agent memories.
    """
    
    def __init__(self, db_path: str = ".agent_memory.db"):
        """Initialize the memory tool.
        
        Args:
            db_path: Path to SQLite database file
        """
        super().__init__(name="memory")
        self.db_path = db_path
        self._initialized = False
    
    async def _ensure_initialized(self):
        """Ensure database tables exist."""
        if self._initialized:
            return
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.execute("""
                CREATE INDEX IF NOT EXISTS idx_memories_key 
                ON memories(key)
            """)
            await db.commit()
        
        self._initialized = True
    
    async def execute(
        self,
        operation: str,
        key: Optional[str] = None,
        value: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """Execute a memory operation.
        
        Args:
            operation: Operation type ('store', 'retrieve', 'delete', 'list')
            key: Memory key
            value: Value to store (for 'store' operation)
            metadata: Optional metadata dictionary
            
        Returns:
            ToolResult with operation results
            
        Raises:
            ToolError: If operation fails
        """
        try:
            await self._ensure_initialized()
            
            if operation == "store":
                return await self._store(key, value, metadata)
            elif operation == "retrieve":
                return await self._retrieve(key)
            elif operation == "delete":
                return await self._delete(key)
            elif operation == "list":
                return await self._list()
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Unknown operation: {operation}"
                )
                
        except Exception as e:
            self.logger.error(f"Memory operation failed: {e}")
            raise ToolError(self.name, str(e))
    
    async def _store(
        self,
        key: str,
        value: Any,
        metadata: Optional[Dict[str, Any]]
    ) -> ToolResult:
        """Store a memory."""
        value_json = json.dumps(value)
        metadata_json = json.dumps(metadata) if metadata else None
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                INSERT INTO memories (key, value, metadata, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    metadata = excluded.metadata,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, value_json, metadata_json))
            await db.commit()
        
        self.logger.info(f"Stored memory: {key}")
        
        return ToolResult(
            success=True,
            output=f"Stored memory with key: {key}",
            metadata={"key": key, "operation": "store"}
        )
    
    async def _retrieve(self, key: str) -> ToolResult:
        """Retrieve a memory."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT value, metadata, created_at, updated_at FROM memories WHERE key = ?",
                (key,)
            ) as cursor:
                row = await cursor.fetchone()
        
        if not row:
            return ToolResult(
                success=False,
                output="",
                error=f"Memory not found: {key}"
            )
        
        value = json.loads(row[0])
        metadata = json.loads(row[1]) if row[1] else None
        
        self.logger.info(f"Retrieved memory: {key}")
        
        return ToolResult(
            success=True,
            output=json.dumps(value, indent=2),
            metadata={
                "key": key,
                "value": value,
                "custom_metadata": metadata,
                "created_at": row[2],
                "updated_at": row[3],
            }
        )
    
    async def _delete(self, key: str) -> ToolResult:
        """Delete a memory."""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "DELETE FROM memories WHERE key = ?",
                (key,)
            )
            await db.commit()
            deleted = cursor.rowcount > 0
        
        if not deleted:
            return ToolResult(
                success=False,
                output="",
                error=f"Memory not found: {key}"
            )
        
        self.logger.info(f"Deleted memory: {key}")
        
        return ToolResult(
            success=True,
            output=f"Deleted memory: {key}",
            metadata={"key": key, "operation": "delete"}
        )
    
    async def _list(self) -> ToolResult:
        """List all memory keys."""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute(
                "SELECT key, created_at, updated_at FROM memories ORDER BY updated_at DESC"
            ) as cursor:
                rows = await cursor.fetchall()
        
        memories = [
            {
                "key": row[0],
                "created_at": row[1],
                "updated_at": row[2],
            }
            for row in rows
        ]
        
        output = "\n".join(f"- {m['key']}" for m in memories)
        
        self.logger.info(f"Listed {len(memories)} memories")
        
        return ToolResult(
            success=True,
            output=output or "No memories stored",
            metadata={"count": len(memories), "memories": memories}
        )
