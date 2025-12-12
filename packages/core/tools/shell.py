"""Shell command execution tool with safety checks."""

import asyncio
import shlex
from typing import Optional
from .base import BaseTool, ToolResult, ToolError


class ShellExecutionTool(BaseTool):
    """Tool for executing shell commands safely.
    
    This tool provides a controlled way to run shell commands with
    safety checks and timeouts.
    """
    
    # Dangerous patterns that should not be executed
    DANGEROUS_PATTERNS = [
        'rm -rf',
        'sudo',
        'chmod 777',
        'mkfs',
        '> /dev/',
        'dd if=',
        'wget',
        'curl',
        'nc ',
        'ncat',
    ]
    
    def __init__(self, allow_dangerous: bool = False):
        """Initialize the shell execution tool.
        
        Args:
            allow_dangerous: Whether to allow potentially dangerous commands
        """
        super().__init__(name="execute_shell")
        self.allow_dangerous = allow_dangerous
    
    async def execute(
        self,
        command: str,
        timeout: int = 30,
        working_dir: Optional[str] = None,
    ) -> ToolResult:
        """Execute a shell command.
        
        Args:
            command: Shell command to execute
            timeout: Maximum execution time in seconds
            working_dir: Working directory for command execution
            
        Returns:
            ToolResult with command output
            
        Raises:
            ToolError: If command execution fails
        """
        try:
            # Safety check
            if not self.allow_dangerous:
                for pattern in self.DANGEROUS_PATTERNS:
                    if pattern in command.lower():
                        return ToolResult(
                            success=False,
                            output="",
                            error=f"Dangerous command pattern detected: '{pattern}'. Command blocked for safety."
                        )
            
            # Log command
            self.logger.info(f"Executing command: {command}")
            
            # Create subprocess
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=working_dir,
            )
            
            # Wait for completion with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Command timed out after {timeout} seconds"
                )
            
            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            # Check exit code
            success = process.returncode == 0
            
            # Combine output
            output = stdout_text
            if stderr_text and not success:
                output += f"\n\nSTDERR:\n{stderr_text}"
            
            self.logger.debug(
                f"Command completed with exit code {process.returncode}"
            )
            
            return ToolResult(
                success=success,
                output=output,
                metadata={
                    "command": command,
                    "exit_code": process.returncode,
                    "stdout_length": len(stdout_text),
                    "stderr_length": len(stderr_text),
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to execute command '{command}': {e}")
            raise ToolError(self.name, str(e))
