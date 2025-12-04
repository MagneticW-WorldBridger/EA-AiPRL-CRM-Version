"""
GoHighLevel HTTP Toolset for Google ADK
=======================================

GHL's MCP server uses a NON-STANDARD hybrid approach:
- Accepts JSON-RPC 2.0 POSTs (not standard MCP streaming)
- Returns SSE event streams in response body
- Doesn't support standard MCP session initialization

This module wraps GHL's HTTP API as a proper ADK BaseToolset with
custom GHLTool class that properly exposes parameter schemas.
"""

import json
import os
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path

from dotenv import load_dotenv
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

import httpx
from pydantic import BaseModel
from typing_extensions import override

from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.readonly_context import ReadonlyContext
from google.genai import types


# GHL MCP API Configuration
GHL_MCP_URL = "https://services.leadconnectorhq.com/mcp/"
DEFAULT_TIMEOUT = 30.0


class GHLToolConfig(BaseModel):
    """Configuration for a single GHL tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]


def _json_schema_to_gemini_schema(json_schema: Dict[str, Any]) -> types.Schema:
    """
    Convert a JSON Schema to a Gemini Schema.
    
    Based on how McpTool does it in mcp_tool.py
    """
    if not json_schema:
        return types.Schema(type=types.Type.OBJECT, properties={})
    
    schema_type = json_schema.get("type", "object")
    
    # Map JSON Schema types to Gemini types
    type_mapping = {
        "string": types.Type.STRING,
        "number": types.Type.NUMBER,
        "integer": types.Type.INTEGER,
        "boolean": types.Type.BOOLEAN,
        "array": types.Type.ARRAY,
        "object": types.Type.OBJECT,
    }
    
    gemini_type = type_mapping.get(schema_type, types.Type.STRING)
    
    # Build properties for object types
    properties = {}
    if "properties" in json_schema:
        for prop_name, prop_schema in json_schema["properties"].items():
            prop_type = prop_schema.get("type", "string")
            prop_gemini_type = type_mapping.get(prop_type, types.Type.STRING)
            
            # Handle array types - need to specify items
            if prop_type == "array":
                items_schema = prop_schema.get("items", {"type": "string"})
                items_type = items_schema.get("type", "string") if isinstance(items_schema, dict) else "string"
                items_gemini_type = type_mapping.get(items_type, types.Type.STRING)
                
                properties[prop_name] = types.Schema(
                    type=types.Type.ARRAY,
                    description=prop_schema.get("description", ""),
                    items=types.Schema(type=items_gemini_type),
                )
            else:
                properties[prop_name] = types.Schema(
                    type=prop_gemini_type,
                    description=prop_schema.get("description", ""),
                )
    
    required = json_schema.get("required", [])
    
    return types.Schema(
        type=gemini_type,
        properties=properties if properties else None,
        required=required if required else None,
        description=json_schema.get("description", ""),
    )


async def _call_ghl_mcp(
    tool_name: str,
    arguments: Dict[str, Any],
    pit_token: str,
    location_id: str,
    timeout: float = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    """
    Call a GHL MCP tool using their hybrid JSON-RPC/SSE format.
    """
    headers = {
        "Authorization": f"Bearer {pit_token}",
        "locationId": location_id,
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    
    # Convert numeric timestamps to strings (GHL API requirement)
    processed_args = {}
    for key, value in arguments.items():
        if key in ('query_startTime', 'query_endTime') and isinstance(value, (int, float)):
            processed_args[key] = str(int(value))
        else:
            processed_args[key] = value
    
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": processed_args
        }
    }
    
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(GHL_MCP_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text[:500]}",
                "status": response.status_code,
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
                                    return {"success": True, "data": inner_text}
                        return {"success": True, "data": data}
                    except json.JSONDecodeError:
                        continue
            return {"success": False, "error": "Failed to parse SSE response", "raw": text[:500]}
        else:
            return {"success": True, "data": response.json()}


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


class GHLTool(BaseTool):
    """
    A custom ADK Tool for GoHighLevel MCP tools.
    
    Unlike FunctionTool which inspects function signatures,
    this tool explicitly provides the parameter schema from GHL's
    inputSchema, ensuring the LLM knows exactly what parameters to use.
    """
    
    def __init__(
        self,
        *,
        tool_config: GHLToolConfig,
        pit_token: str,
        location_id: str,
        require_confirmation: Union[bool, Callable[..., bool]] = False,
    ):
        """
        Initialize a GHL Tool.
        
        Args:
            tool_config: The GHL tool configuration with name, description, and schema
            pit_token: GHL Private Integration Token
            location_id: GHL Location ID
            require_confirmation: Whether this tool requires user confirmation
        """
        # Create ADK-friendly name
        tool_name = f"ghl_{tool_config.name.replace('-', '_')}"
        
        super().__init__(
            name=tool_name,
            description=tool_config.description or f"GHL tool: {tool_config.name}",
        )
        
        self._tool_config = tool_config
        self._pit_token = pit_token
        self._location_id = location_id
        self._require_confirmation = require_confirmation
    
    @override
    def _get_declaration(self) -> types.FunctionDeclaration:
        """
        Get the function declaration with proper parameter schema.
        
        This is the key method that tells the LLM what parameters are available.
        We convert GHL's JSON Schema to Gemini's Schema format.
        """
        # Convert the input schema to Gemini format
        parameters = _json_schema_to_gemini_schema(self._tool_config.input_schema)
        
        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=parameters,
        )
    
    @override
    async def run_async(
        self,
        *,
        args: Dict[str, Any],
        tool_context: ToolContext,
    ) -> Any:
        """
        Execute the GHL tool.
        
        Args:
            args: Arguments from the LLM
            tool_context: ADK tool context
            
        Returns:
            Tool execution result
        """
        return await _call_ghl_mcp(
            tool_name=self._tool_config.name,
            arguments=args,
            pit_token=self._pit_token,
            location_id=self._location_id,
        )


class GHLToolset(BaseToolset):
    """
    GoHighLevel Toolset for Google ADK.
    
    Connects to GHL's hybrid MCP server and exposes tools as ADK-compatible
    GHLTools. Each tool properly exposes its parameter schema to the LLM.
    
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
        Get all GHL tools as ADK GHLTools.
        
        Fetches tool definitions from GHL MCP server and wraps them
        as callable ADK tools with proper parameter schemas.
        """
        if self._tools_cache is not None:
            return self._tools_cache
        
        # Fetch tool definitions from GHL
        tool_configs = await _list_ghl_tools(
            pit_token=self._pit_token,
            location_id=self._location_id,
            timeout=self._timeout,
        )
        
        # Convert to ADK GHLTools (with proper schemas!)
        tools = []
        for config in tool_configs:
            # Apply filter if specified (use parent's tool_filter)
            if self.tool_filter:
                if isinstance(self.tool_filter, list) and config.name not in self.tool_filter:
                    continue
            
            # Create custom GHLTool with proper schema
            tool = GHLTool(
                tool_config=config,
                pit_token=self._pit_token,
                location_id=self._location_id,
            )
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
