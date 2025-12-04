"""
GoHighLevel HTTP Toolset for Google ADK
=======================================

GHL's MCP server uses a NON-STANDARD hybrid approach:
- Accepts JSON-RPC 2.0 POSTs (not standard MCP streaming)
- Returns SSE event streams in response body
- Doesn't support standard MCP session initialization

This module wraps GHL's HTTP API as a proper ADK BaseToolset.
"""

import json
import asyncio
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

import httpx
from pydantic import BaseModel

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.function_tool import FunctionTool
from google.adk.agents.readonly_context import ReadonlyContext


# GHL MCP API Configuration
GHL_MCP_URL = "https://services.leadconnectorhq.com/mcp/"
DEFAULT_TIMEOUT = 30.0


class GHLToolConfig(BaseModel):
    """Configuration for a single GHL tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]


async def _call_ghl_mcp(
    tool_name: str,
    arguments: Dict[str, Any],
    pit_token: str,
    location_id: str,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Call a GHL MCP tool using their hybrid JSON-RPC/SSE format.
    
    Args:
        tool_name: The GHL MCP tool name (e.g., "contacts_get-contacts")
        arguments: Tool arguments
        pit_token: GHL Private Integration Token
        location_id: GHL Location ID
        timeout: Request timeout in seconds
        
    Returns:
        Parsed response from GHL
    """
    headers = {
        "Authorization": f"Bearer {pit_token}",
        "locationId": location_id,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(GHL_MCP_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            return {
                "status": "error",
                "error": f"HTTP {response.status_code}",
                "details": response.text[:500]
            }
        
        # Parse SSE response
        text = response.text
        if text.startswith("event:"):
            for line in text.split("\n"):
                if line.startswith("data:"):
                    json_str = line[5:].strip()
                    try:
                        data = json.loads(json_str)
                        # Navigate through nested structure
                        if "result" in data and "content" in data["result"]:
                            content = data["result"]["content"]
                            if content and len(content) > 0:
                                inner_text = content[0].get("text", "")
                                try:
                                    inner_data = json.loads(inner_text)
                                    # Check for another level of nesting
                                    if "content" in inner_data:
                                        inner_content = inner_data["content"]
                                        if inner_content and len(inner_content) > 0:
                                            final_text = inner_content[0].get("text", "")
                                            return json.loads(final_text)
                                    return inner_data
                                except json.JSONDecodeError:
                                    return {"status": "success", "data": inner_text}
                        return {"status": "success", "data": data}
                    except json.JSONDecodeError:
                        continue
            return {"status": "error", "raw": text}
        else:
            return {"status": "success", "data": response.json()}


async def _list_ghl_tools(
    pit_token: str,
    location_id: str,
    timeout: float = DEFAULT_TIMEOUT,
) -> List[GHLToolConfig]:
    """Fetch available tools from GHL MCP server."""
    headers = {
        "Authorization": f"Bearer {pit_token}",
        "locationId": location_id,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(GHL_MCP_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            raise ConnectionError(f"Failed to list tools: HTTP {response.status_code}")
        
        text = response.text
        tools = []
        
        if text.startswith("event:"):
            for line in text.split("\n"):
                if line.startswith("data:"):
                    json_str = line[5:].strip()
                    try:
                        data = json.loads(json_str)
                        if "result" in data and "tools" in data["result"]:
                            for tool in data["result"]["tools"]:
                                tools.append(GHLToolConfig(
                                    name=tool["name"],
                                    description=tool.get("description", ""),
                                    input_schema=tool.get("inputSchema", {})
                                ))
                    except json.JSONDecodeError:
                        continue
        
        return tools


def _create_ghl_tool_function(
    tool_config: GHLToolConfig,
    pit_token: str,
    location_id: str,
):
    """Create a callable function for a GHL tool."""
    
    async def tool_function(**kwargs) -> Dict[str, Any]:
        """Dynamically generated GHL tool function."""
        # GHL requires certain parameters as strings (timestamps, IDs)
        processed_args = {}
        for key, value in kwargs.items():
            # Convert numeric timestamps to strings (GHL API requirement)
            if key in ('query_startTime', 'query_endTime') and isinstance(value, (int, float)):
                processed_args[key] = str(int(value))
            else:
                processed_args[key] = value
        
        return await _call_ghl_mcp(
            tool_name=tool_config.name,
            arguments=processed_args,
            pit_token=pit_token,
            location_id=location_id,
        )
    
    # Set function metadata for ADK
    tool_function.__name__ = f"ghl_{tool_config.name.replace('-', '_')}"
    tool_function.__doc__ = tool_config.description or f"GHL tool: {tool_config.name}"
    
    return tool_function


class GHLToolset(BaseToolset):
    """
    GoHighLevel Toolset for Google ADK.
    
    Connects to GHL's hybrid MCP server and exposes tools as ADK-compatible
    FunctionTools. Handles GHL's non-standard JSON-RPC/SSE protocol.
    
    Usage:
        toolset = GHLToolset()  # Uses env vars
        agent = Agent(tools=[toolset], ...)
        
        # Or with explicit credentials:
        toolset = GHLToolset(pit_token="...", location_id="...")
    """
    
    def __init__(
        self,
        pit_token: Optional[str] = None,
        location_id: Optional[str] = None,
        tool_filter: Optional[List[str]] = None,
        tool_name_prefix: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        """
        Initialize GHL Toolset.
        
        Args:
            pit_token: GHL Private Integration Token. Defaults to GHL_PIT_TOKEN env var.
            location_id: GHL Location ID. Defaults to GHL_LOCATION_ID env var.
            tool_filter: Optional list of tool names to include. None = all tools.
            tool_name_prefix: Optional prefix for tool names.
            timeout: Request timeout in seconds.
        """
        # Call parent __init__ to set tool_filter and tool_name_prefix
        super().__init__(tool_filter=tool_filter, tool_name_prefix=tool_name_prefix)
        
        self._pit_token = pit_token or os.getenv("GHL_PIT_TOKEN")
        self._location_id = location_id or os.getenv("GHL_LOCATION_ID")
        self._timeout = timeout
        self._tools_cache: Optional[List[BaseTool]] = None
        
        if not self._pit_token:
            raise ValueError("GHL_PIT_TOKEN is required")
        if not self._location_id:
            raise ValueError("GHL_LOCATION_ID is required")
    
    async def get_tools(
        self,
        readonly_context: Optional[ReadonlyContext] = None,
    ) -> List[BaseTool]:
        """
        Get all GHL tools as ADK FunctionTools.
        
        Fetches tool definitions from GHL MCP server and wraps them
        as callable ADK tools.
        """
        if self._tools_cache is not None:
            return self._tools_cache
        
        # Fetch tool definitions from GHL
        tool_configs = await _list_ghl_tools(
            pit_token=self._pit_token,
            location_id=self._location_id,
            timeout=self._timeout,
        )
        
        # Convert to ADK FunctionTools
        tools = []
        for config in tool_configs:
            # Apply filter if specified (use parent's tool_filter)
            if self.tool_filter:
                if isinstance(self.tool_filter, list) and config.name not in self.tool_filter:
                    continue
            
            # Create the tool function
            func = _create_ghl_tool_function(
                tool_config=config,
                pit_token=self._pit_token,
                location_id=self._location_id,
            )
            
            # Wrap as FunctionTool
            tool = FunctionTool(func=func)
            tools.append(tool)
        
        self._tools_cache = tools
        return tools
    
    async def close(self) -> None:
        """Clean up resources."""
        self._tools_cache = None


# Convenience functions
def create_ghl_toolset(
    pit_token: Optional[str] = None,
    location_id: Optional[str] = None,
    tool_filter: Optional[List[str]] = None,
) -> GHLToolset:
    """Create a GHL Toolset with optional filtering."""
    return GHLToolset(
        pit_token=pit_token,
        location_id=location_id,
        tool_filter=tool_filter,
    )


def create_ghl_contacts_toolset() -> GHLToolset:
    """Pre-configured toolset for contact operations only."""
    return GHLToolset(tool_filter=[
        "contacts_get-contacts",
        "contacts_get-contact",
        "contacts_create-contact",
        "contacts_update-contact",
        "contacts_upsert-contact",
        "contacts_add-tags",
        "contacts_remove-tags",
        "contacts_get-all-tasks",
    ])


def create_ghl_crm_toolset() -> GHLToolset:
    """Pre-configured toolset for full CRM operations."""
    return GHLToolset(tool_filter=[
        # Contacts
        "contacts_get-contacts",
        "contacts_get-contact",
        "contacts_create-contact",
        "contacts_update-contact",
        "contacts_upsert-contact",
        "contacts_add-tags",
        "contacts_remove-tags",
        "contacts_get-all-tasks",
        # Conversations
        "conversations_search-conversation",
        "conversations_get-messages",
        "conversations_send-a-new-message",
        # Opportunities
        "opportunities_search-opportunity",
        "opportunities_get-pipelines",
        "opportunities_get-opportunity",
        "opportunities_update-opportunity",
        # Location
        "locations_get-location",
        "locations_get-custom-fields",
    ])

