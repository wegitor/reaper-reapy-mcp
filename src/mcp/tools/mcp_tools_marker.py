from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any
import reapy
from reaper_reapy_mcp.utils.position_utils import position_to_time, time_to_measure

def _setup_marker_tools(mcp: FastMCP, controller) -> None:
    @mcp.tool("create_region")
    def create_region(ctx: Context, name: str,
                     start_time: Optional[float] = None, end_time: Optional[float] = None,
                     start_measure: Optional[str] = None, end_measure: Optional[str] = None) -> Dict[str, Any]:
        """Create a region in the project.
        
        Args:
            name: Name of the region
            start_time: Start position in seconds (optional if start_measure is provided)
            end_time: End position in seconds (optional if end_measure is provided)
            start_measure: Start position as "measure:beat,fraction" (optional if start_time is provided)
            end_measure: End position as "measure:beat,fraction" (optional if end_time is provided)
        """
        try:
            # Determine start position
            if start_time is not None:
                time_start = float(start_time)
                measure_start = time_to_measure(time_start)
            elif start_measure is not None:
                time_start = position_to_time(start_measure)
                measure_start = start_measure
            else:
                return {"status": "error", "message": "Either start_time or start_measure must be provided"}
                
            # Determine end position
            if end_time is not None:
                time_end = float(end_time)
                measure_end = time_to_measure(time_end)
            elif end_measure is not None:
                time_end = position_to_time(end_measure)
                measure_end = end_measure
            else:
                return {"status": "error", "message": "Either end_time or end_measure must be provided"}
                
            region_index = controller.create_region(time_start, time_end, name)
            if region_index >= 0:
                return {
                    "status": "success", 
                    "message": f"Created region {region_index}: {name}",
                    "range": {
                        "start": {"time": time_start, "measure": measure_start},
                        "end": {"time": time_end, "measure": measure_end}
                    }
                }
            return {"status": "error", "message": "Failed to create region"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to create region: {str(e)}"}

    @mcp.tool("delete_region")
    def delete_region(ctx: Context, region_index: int) -> Dict[str, Any]:
        """Delete a region from the project."""
        try:
            if controller.delete_region(region_index):
                return {"status": "success", "message": f"Deleted region {region_index}"}
            return {"status": "error", "message": f"Failed to delete region {region_index}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to delete region: {str(e)}"}

    @mcp.tool("create_marker")
    def create_marker(ctx: Context, time: float, name: str) -> Dict[str, Any]:
        """Create a marker in the project."""
        try:
            marker_index = controller.create_marker(time, name)
            if marker_index >= 0:
                return {"status": "success", "message": f"Created marker {marker_index}: {name}"}
            return {"status": "error", "message": "Failed to create marker"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to create marker: {str(e)}"}

    @mcp.tool("delete_marker")
    def delete_marker(ctx: Context, marker_index: int) -> Dict[str, Any]:
        """Delete a marker from the project."""
        try:
            if controller.delete_marker(marker_index):
                return {"status": "success", "message": f"Deleted marker {marker_index}"}
            return {"status": "error", "message": f"Failed to delete marker {marker_index}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to delete marker: {str(e)}"}

    @mcp.tool("get_region_list")
    def get_region_list(ctx: Context) -> Dict[str, Any]:
        """Get a list of all regions in the project.

        Returns:
            Dict containing status and a list of regions, each with:
            - index: region index
            - start: region start position
            - end: region end position
        """
        try:
            regions = []
            project = reapy.Project()

            for i, region in enumerate(project.regions):
                region_info = {
                    "index": i,
                    "start": region.start,
                    "end": region.end
                }
                regions.append(region_info)
            return {
                "status": "success",
                "regions": regions,
                "count": len(regions)
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to get region list: {str(e)}"}

