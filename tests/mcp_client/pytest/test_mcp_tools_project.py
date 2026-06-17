import pytest
import asyncio
from mcp_abstraction import mcp_abstraction_parse_tool_list

async def run_tools():
    # Test sequence for project tools
    tool_seq_to_call = [
        {
            "name": "get_tempo",
            "args": {}
        },
        {
            "name": "set_tempo",
            "args": {
                "bpm": 145
            }
        },
        {
            "name": "get_tempo",
            "args": {}
        },
        {
            "name": "get_time_signature",
            "args": {}
        },
        {
            "name": "get_project_time_signature",
            "args": {}
        },
        {
            "name": "set_project_time_signature",
            "args": {
                "numerator": 7,
                "denominator": 8
            }
        },
        {
            "name": "set_time_signature",
            "args": {
                "numerator": 3,
                "denominator": 4,
                "position": "7:1,0"
            }
        },
        {
            "name": "get_project_time_signature",
            "args": {}
        },
        {
            "name": "render_project",
            "args": {
                "output_file": "test_render",
                "file_format": "flac",
                "start_time": 9.0,
                "end_time": 10.0,
                "samplerate": 44100,
                "channels": 2
            }
        }
    ]

    await mcp_abstraction_parse_tool_list(tool_seq_to_call)
@pytest.mark.asyncio
async def test_mcp_tools_project():
    """Test project-related MCP tools."""
    print("Running project tools test. ..")
    await run_tools()
    print("Project tools test completed.")

if __name__ == "__main__":
    asyncio.run(run_tools())
