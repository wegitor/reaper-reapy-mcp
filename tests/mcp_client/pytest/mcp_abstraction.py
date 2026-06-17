import pytest
import asyncio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import Dict, Any
import json

async def mcp_abstraction_run_tool_wrap(session: any, name: str, args: Dict[str, Any]):
    print(f"Run tool: {name}")
    result = await session.call_tool(name, args)
    for content in result.content:
        if isinstance(content, types.TextContent):
            print(f"Text: {content.text}")
            data = json.loads(content.text)
            assert data["status"] == "success"


async def mcp_abstraction_parse_tool_list(list_to_exec, step_mode = False):
    """Demonstrates how to parse different types of content in CallToolResult."""
    server_params = StdioServerParameters(
        command="python", args=["-m", "reaper_reapy_mcp"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            for list_item in list_to_exec:
                await mcp_abstraction_run_tool_wrap(session, list_item["name"], list_item["args"])
                if step_mode :
                    input("Press enter for the next tool execution")

