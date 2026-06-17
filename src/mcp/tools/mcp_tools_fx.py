
from mcp import types
from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any, List, Union

def _setup_fx_tools(mcp: FastMCP, controller) -> None:
    """Setup FX-related MCP tools."""

    @mcp.tool("add_fx")
    def add_fx(ctx: Context, track_index: int, fx_name: str) -> Dict[str, Any]:
        """Add an FX to a track."""
        try:
            fx_index = controller.add_fx(track_index, fx_name)
            if fx_index >= 0:
                return {"status": "success", "message": f"Added FX {fx_name} to track {track_index} at index {fx_index}"}
            return {"status": "error", "message": f"Failed to add FX to track {track_index}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to add FX: {str(e)}"}

    @mcp.tool("remove_fx")
    def remove_fx(ctx: Context, track_index: int, fx_index: int) -> Dict[str, Any]:
        """Remove an FX from a track."""
        try:
            if controller.remove_fx(track_index, fx_index):
                return {"status": "success", "message": f"Removed FX {fx_index} from track {track_index}"}
            return {"status": "error", "message": f"Failed to remove FX from track {track_index}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to remove FX: {str(e)}"}

    @mcp.tool("set_fx_param")
    def set_fx_param(ctx: Context, track_index: int, fx_index: int, param_name: str, value: float) -> Dict[str, Any]:
        """Set an FX parameter value."""
        try:
            if controller.set_fx_param(track_index, fx_index, param_name, value):
                return {"status": "success", "message": f"Set parameter {param_name} to {value} for FX {fx_index} on track {track_index}"}
            return {"status": "error", "message": "Failed to set FX parameter"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to set FX parameter: {str(e)}"}

    @mcp.tool("get_fx_param")
    def get_fx_param(ctx: Context, track_index: int, fx_index: int, param_name: str) -> Dict[str, Any]:
        """Get an FX parameter value."""
        try:
            value = controller.get_fx_param(track_index, fx_index, param_name)
            return {"status": "success", "message": f"Parameter {param_name} value: {value}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get FX parameter: {str(e)}"}
            
    @mcp.tool("get_fx_param_list")
    def get_fx_param_list(ctx: Context, track_index: int, fx_index: int) -> Dict[str, Any]:
        """Get a list of all parameters for an FX."""
        try:
            param_list = controller.get_fx_param_list(track_index, fx_index)
            if param_list:
                return {"status": "success", "message": f"Retrieved {len(param_list)} parameters", "parameters": param_list}
            return {"status": "error", "message": f"Failed to get parameters for FX {fx_index} on track {track_index}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get FX parameter list: {str(e)}"}
            
    @mcp.tool("get_fx_list")
    def get_fx_list(ctx: Context, track_index: int) -> Dict[str, Any]:
        """Get a list of all FX on a track."""
        try:
            fx_list = controller.get_fx_list(track_index)
            # If controller returns None -> treat as failure.
            if fx_list is None:
                return {"status": "error", "message": f"Failed to get FX list for track {track_index}"}
            # Empty list is a successful response with count 0.
            return {
                "status": "success",
                "message": f"Retrieved {len(fx_list)} FX on track {track_index}",
                "fx_list": fx_list,
                "count": len(fx_list)
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to get FX list: {str(e)}"}
            
    @mcp.tool("get_available_fx_list")
    def get_available_fx_list(ctx: Context) -> Dict[str, Any]:
        """Get a list of all available FX plugins in Reaper."""
        try:
            fx_list = controller.get_available_fx_list()
            if fx_list:
                return {"status": "success", "message": f"Retrieved {len(fx_list)} available FX plugins", "fx_list": fx_list}
            return {"status": "error", "message": "Failed to get available FX list"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get available FX list: {str(e)}"}

    @mcp.tool("toggle_fx")
    def toggle_fx(ctx: Context, track_index: int, fx_index: int, enable: Optional[bool] = None) -> Dict[str, Any]:
        """Toggle or set the enable/disable state of an FX."""
        try:
            if controller.toggle_fx(track_index, fx_index, enable):
                state = "enabled" if enable else "disabled" if enable is not None else "toggled"
                return {"status": "success", "message": f"{state} FX {fx_index} on track {track_index}"}
            return {"status": "error", "message": "Failed to toggle FX"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to toggle FX: {str(e)}"}

