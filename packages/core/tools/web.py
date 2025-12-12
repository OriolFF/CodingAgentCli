"""Web and HTTP tools for fetching content."""

import httpx
from typing import Optional, Dict
from .base import BaseTool, ToolResult, ToolError


class FetchUrlTool(BaseTool):
    """Tool for fetching content from URLs via HTTP."""
    
    def __init__(self, timeout: int = 30):
        """Initialize the fetch URL tool.
        
        Args:
            timeout: Default timeout for HTTP requests in seconds
        """
        super().__init__(name="fetch_url")
        self.default_timeout = timeout
    
    async def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> ToolResult:
        """Fetch content from a URL.
        
        Args:
            url: URL to fetch
            method: HTTP method (GET, POST, etc.)
            headers: Optional HTTP headers
            timeout: Request timeout in seconds
            
        Returns:
            ToolResult with response content
            
        Raises:
            ToolError: If request fails
        """
        try:
            timeout_val = timeout or self.default_timeout
            
            self.logger.debug(f"Fetching {method} {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=timeout_val,
                    follow_redirects=True,
                )
                
                # Check status
                response.raise_for_status()
                
                # Get content
                content = response.text
                
                self.logger.info(
                    f"Fetched {len(content)} bytes from {url} "
                    f"(status: {response.status_code})"
                )
                
                return ToolResult(
                    success=True,
                    output=content,
                    metadata={
                        "url": url,
                        "status_code": response.status_code,
                        "content_length": len(content),
                        "content_type": response.headers.get("content-type"),
                    }
                )
                
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP {e.response.status_code}: {url}"
            self.logger.error(error_msg)
            return ToolResult(
                success=False,
                output="",
                error=error_msg,
                metadata={"status_code": e.response.status_code}
            )
        except httpx.TimeoutException:
            error_msg = f"Request timed out after {timeout_val}s: {url}"
            self.logger.error(error_msg)
            return ToolResult(
                success=False,
                output="",
                error=error_msg
            )
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            raise ToolError(self.name, str(e))
