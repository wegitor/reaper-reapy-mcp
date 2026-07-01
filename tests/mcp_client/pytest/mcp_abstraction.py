import pytest
import asyncio
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import Dict, Any
import json

async def mcp_abstraction_run_tool_wrap(session: any, name: str, args: Dict[str, Any]) -> Any:
    print(f"Run tool: {name}")
    answer_data = None
    result = await session.call_tool(name, args)
    for content in result.content:
        if isinstance(content, types.TextContent):
            print(f"Text: {content.text}")
            data = json.loads(content.text)
            assert data["status"] == "success"
            answer_data = data

    return answer_data


async def mcp_abstraction_parse_tool_list(list_to_exec, step_mode = False) -> str:
    """Demonstrates how to parse different types of content in CallToolResult."""
    server_params = StdioServerParameters(
        command="python", args=["-m", "reaper_reapy_mcp"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            result = []
            for list_item in list_to_exec:
                list_item_result = await mcp_abstraction_run_tool_wrap(session, list_item["name"], list_item["args"])
                if step_mode :
                    input("Press enter for the next tool execution")
                result.append(list_item_result)
            return result

