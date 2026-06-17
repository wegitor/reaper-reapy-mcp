import asyncio
import pytest
from mcp_abstraction import mcp_abstraction_parse_tool_list

async def run_tools():
    # Test sequence for marker tools
    tool_seq_to_call = [
        {
            "name": "create_region",
            "args": {
                "name": "Test Region",
                "start_time": 0.0,
                "end_time": 10.0
            }
        },
        {
            "name": "create_marker",
            "args": {
                "time": 5.0,
                "name": "Test Marker"
            }
        },
        {
            "name": "get_region_list",
            "args": {}
        },
        {
            "name": "delete_region",
            "args": {
                "region_index": 1
            }
        },
        {
            "name": "delete_marker",
            "args": {
                "marker_index": 1
            }
        }
    ]
    await mcp_abstraction_parse_tool_list(tool_seq_to_call)


@pytest.mark.asyncio
async def test_mcp_tools_marker():
    """Test marker-related MCP tools."""
    print("Running marker tools test. ..")
    await run_tools()
    print("Marker tools test completed.")

if __name__ == "__main__":
    asyncio.run(run_tools())
