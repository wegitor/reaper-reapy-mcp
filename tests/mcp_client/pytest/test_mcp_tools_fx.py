import asyncio
import re
import pytest
from mcp_abstraction import mcp_abstraction_parse_tool_list

TRACK_NAME = "Test Track 1"
FX_NAME = "ReaEQ (Cockos)"
FX_DISPLAY = "VST: ReaEQ (Cockos)"
PARAM_NAME = "Global Gain"
SET_PARAM_VALUE = 0.6
FLOAT_TOLERANCE = 1e-6


def assert_message(result, substring, fail_msg=None):
    assert isinstance(result, dict), "Result must be a dict"
    assert "message" in result, f"Missing message in result: {result}"
    if fail_msg:
        assert substring in result["message"], fail_msg
    else:
        assert substring in result["message"], f"Expected message containing '{substring}', got '{result['message']}'"


def assert_fx_list(result, expected_count=None, expected_name=None, expected_enabled=None):
    fx_list = result.get("fx_list", [])
    assert isinstance(fx_list, list), f"Expected fx_list to be a list, got {type(fx_list)}"
    if expected_count is not None:
        assert len(fx_list) == expected_count, f"Expected {expected_count} FX, got {len(fx_list)}"
    if expected_count and len(fx_list) > 0:
        if expected_name is not None:
            assert fx_list[0].get("name") == expected_name, f"Expected FX name '{expected_name}', got '{fx_list[0].get('name')}'"
        if expected_enabled is not None:
            assert fx_list[0].get("enabled") is expected_enabled, f"Expected enabled={expected_enabled}, got {fx_list[0].get('enabled')}"
    return fx_list


def parse_numeric_value(result):
    assert isinstance(result, dict), "Result must be a dict"
    if "value" in result:
        numeric = result["value"]
        assert isinstance(numeric, (int, float)), f"Expected numeric value, got {type(numeric)}"
        return numeric

    message = result.get("message", "")
    match = re.search(r"[-+]?\d*\.?\d+", message)
    assert match, f"Could not parse numeric value from message: {message}"
    return float(match.group())


def assert_float_equal(actual, expected, tolerance=FLOAT_TOLERANCE, msg=""):
    """Assert two float values are equal within tolerance."""
    assert abs(actual - expected) <= tolerance, (
        f"{msg}Expected {expected}, but got {actual} "
        f"(difference: {abs(actual - expected)})"
    )


def find_parameter_in_list(params, param_name):
    """Find a parameter by name in the parameter list."""
    for param in params:
        if param.get("name") == param_name or param_name in param.get("name", ""):
            return param
    return None


async def run_tools():
    tool_seq = [
        {"name": "create_track", "args": {"name": TRACK_NAME}},
        {"name": "get_available_fx_list", "args": {}},
        {"name": "get_fx_list", "args": {"track_index": 0}},
        {"name": "add_fx", "args": {"track_index": 0, "fx_name": FX_NAME}},
        {"name": "get_fx_list", "args": {"track_index": 0}},
        {"name": "get_fx_param_list", "args": {"track_index": 0, "fx_index": 0}},
        {"name": "get_fx_param", "args": {"track_index": 0, "fx_index": 0, "param_name": PARAM_NAME}},
        {"name": "set_fx_param", "args": {"track_index": 0, "fx_index": 0, "param_name": PARAM_NAME, "value": SET_PARAM_VALUE}},
        {"name": "get_fx_param", "args": {"track_index": 0, "fx_index": 0, "param_name": PARAM_NAME}},
        {"name": "toggle_fx", "args": {"track_index": 0, "fx_index": 0, "enable": False}},
        {"name": "get_fx_list", "args": {"track_index": 0}},
        {"name": "toggle_fx", "args": {"track_index": 0, "fx_index": 0, "enable": True}},
        {"name": "get_fx_list", "args": {"track_index": 0}},
        {"name": "toggle_fx", "args": {"track_index": 0, "fx_index": 0}},  # toggle without explicit enable
        {"name": "get_fx_list", "args": {"track_index": 0}},
        {"name": "remove_fx", "args": {"track_index": 0, "fx_index": 0}},
        {"name": "get_fx_list", "args": {"track_index": 0}},
    ]

    results = await mcp_abstraction_parse_tool_list(tool_seq)
    assert results is not None, "API returned no results"
    assert len(results) == len(tool_seq), f"Unexpected number of tool results: {len(results)} != {len(tool_seq)}"

    # create track
    assert_message(results[0], "Created track 0", f"Failed to create track: {results[0]}")

    # available fx list
    available = results[1].get("fx_list")
    assert isinstance(available, list), "Expected available FX list"
    assert FX_NAME in available, f"Expected {FX_NAME} in available FX list"

    # no FX initially on new track
    assert_message(results[2], "Retrieved 0 FX on track 0")
    assert_fx_list(results[2], expected_count=0)

    # add fx
    assert_message(results[3], "Added FX", f"Failed to add FX: {results[3]}")

    # verify fx added
    assert_message(results[4], "Retrieved 1 FX on track 0")
    fx_after_add = assert_fx_list(results[4], expected_count=1, expected_enabled=True)
    assert fx_after_add[0].get("name") == FX_DISPLAY, f"Expected added FX display name '{FX_DISPLAY}', got '{fx_after_add[0].get('name')}'"

    # parameter list
    params = results[5].get("parameters", [])
    assert isinstance(params, list), "Expected FX parameter list"
    assert params, "Expected at least one parameter for the added FX"

    # verify parameter exists in list with initial value
    param_from_list = find_parameter_in_list(params, PARAM_NAME)
    assert param_from_list is not None, f"Expected parameter '{PARAM_NAME}' in parameter list"
    initial_value_from_list = param_from_list.get("value")
    assert isinstance(initial_value_from_list, (int, float)), f"Expected numeric initial value in parameter list, got {type(initial_value_from_list)}"

    # get initial parameter value
    assert_message(results[6], "Parameter Global Gain value", f"Failed to read initial FX parameter: {results[6]}")
    initial_param_value = parse_numeric_value(results[6])
    assert_float_equal(initial_param_value, initial_value_from_list, msg="Initial parameter value from get_fx_param does not match value from parameter list: ")

    # set/get parameter
    assert_message(results[7], "Set parameter", f"Failed to set FX parameter: {results[7]}")
    assert_message(results[8], "Parameter Global Gain value", f"Failed to read FX parameter after set: {results[8]}")
    updated_param_value = parse_numeric_value(results[8])
    assert_float_equal(updated_param_value, SET_PARAM_VALUE, msg="Parameter value after set does not match expected value: ")
    assert updated_param_value != initial_param_value, (
        f"Expected FX parameter value to change after setting it; "
        f"initial={initial_param_value}, updated={updated_param_value}. "
        "If these values match, update the test or choose a different "
        "parameter/value for this assertion."
    )

    # disable fx
    assert_message(results[9], "disabled FX 0 on track 0", f"Failed to disable FX: {results[9]}")
    assert_fx_list(results[10], expected_count=1, expected_enabled=False)

    # enable fx
    assert_message(results[11], "enabled FX 0 on track 0", f"Failed to enable FX: {results[11]}")
    assert_fx_list(results[12], expected_count=1, expected_enabled=True)

    # toggle fx (no explicit enable)
    assert_message(results[13], "toggled FX 0 on track 0", f"Failed to toggle FX: {results[13]}")
    assert_fx_list(results[14], expected_count=1, expected_enabled=False)

    # remove fx
    assert_message(results[15], "Removed FX 0 from track 0", f"Failed to remove FX: {results[15]}")
    assert_message(results[16], "Retrieved 0 FX on track 0", f"Failed to verify FX removal: {results[16]}")
    assert_fx_list(results[16], expected_count=0)

    return results


@pytest.mark.asyncio
async def test_mcp_tools_fx():
    """Test FX-related MCP tools."""
    print("Running FX tools test. ..")
    await run_tools()
    print("FX tools test completed.")


if __name__ == "__main__":
    # Keep runnable directly
    asyncio.run(run_tools())

