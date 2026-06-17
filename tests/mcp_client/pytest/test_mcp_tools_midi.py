import asyncio
import pytest
from mcp_abstraction import mcp_abstraction_parse_tool_list

async def run_tools():

    tool_seq_to_call = [
        {
            "name" : "create_midi_item",
            "args" : {
                "track_index": 0,
                "start_time": 0.0,
                "length_time": 4.0
            }
        },
        {
            "name" : "clear_midi_item",
            "args" : {
                "track_index": 0,
                "item_id": 0,
            }
        },
        {
            "name" : "create_midi_item",
            "args" : {
                "track_index": 0,
                "start_measure": "3:1,2",
                "length_measure": "1:1,0"
            }
        },
        {
            "name" : "add_midi_note",
            "args" : {
                "track_index": 0,
                "item": 0,
                "pitch": 60,
                "start_time": 0.0,
                "length_time": 1.0,
                "velocity": 100
            }
        },
        {
            "name" : "get_midi_notes",
            "args" : {
                "track_index": 0,
                "item_id": 1,
                "include_invisible": False
            }
        },
        {
            "name" : "add_midi_notes",
            "args" : {
                "track_index": 0,
                "item": 0,
                "notes": [
                    {
                        "pitch": 60,
                        "start_measure": "1:1,000",
                        "length_measure": "0:2,000",
                        "velocity": 100
                    },
                    {
                        "pitch": 64,
                        "start_time": 2.5,
                        "length_time": 0.5
                    }
                ]
            }
        },
        {
            "name" : "get_selected_midi_item",
            "args" : {
                "track_index": 0,
                "item_id": 0,
            }
        },
        {
            "name" : "find_midi_notes_by_pitch",
            "args" : {
                "pitch_min" : 60,
                "pitch_max" : 70,
            }
        },
    ]
    await mcp_abstraction_parse_tool_list(tool_seq_to_call)


@pytest.mark.asyncio
async def test_mcp_tools_midi():
    """Test MIDI-related MCP tools."""
    print("Running MIDI tools test. ..")
    await run_tools()
    print("MIDI tools test completed.")

if __name__ == "__main__":
    asyncio.run(run_tools())
