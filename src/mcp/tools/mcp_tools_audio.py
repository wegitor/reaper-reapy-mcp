from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any, Union
import reapy
from reaper_reapy_mcp.utils.position_utils import position_to_time, time_to_measure

def _setup_audio_tools(mcp: FastMCP, controller) -> None:
        
    @mcp.tool("insert_audio_item")
    def insert_audio_item(ctx: Context, track_index: int, file_path: str, 
                         start_time: Optional[float] = None, start_measure: Optional[str] = None) -> Dict[str, Any]:
        """Insert an audio file as a media item on a track.
        
        Args:
            track_index: Index of the track
            file_path: Path to the audio file
            start_time: Start position in seconds (optional if start_measure is provided)
            start_measure: Start position as "measure:beat,fraction" (optional if start_time is provided)
        """
        try:
            # Determine the time position
            if start_time is not None:
                time_pos = float(start_time)
                measure_pos = time_to_measure(time_pos)
            elif start_measure is not None:
                time_pos = position_to_time(start_measure)
                measure_pos = start_measure
            else:
                return {"status": "error", "message": "Either start_time or start_measure must be provided"}
                
            item_id = controller.insert_audio_item(track_index, file_path, time_pos)
            # Convert any type of item_id to an index
            if isinstance(item_id, str):
                # If it's a string (pointer), find its index in the track
                project = reapy.Project()
                track = project.tracks[track_index]
                for i, item in enumerate(track.items):
                    if str(item.id) == item_id:
                        return {"status": "success", "message": f"Inserted audio item at position {measure_pos} (time: {time_pos:.3f}s)", "item_id": i}
                return {"status": "error", "message": "Failed to find inserted item index"}
            elif isinstance(item_id, int):
                # If it's already an index, use it directly
                if item_id >= 0:
                    return {"status": "success", "message": f"Inserted audio item at position {measure_pos} (time: {time_pos:.3f}s)", "item_id": item_id}
            return {"status": "error", "message": "Failed to insert audio item"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to insert audio item: {str(e)}"}
    
    @mcp.tool("duplicate_item")
    def duplicate_item(ctx: Context, track_index: int, item_id: Union[int, str], 
                      new_time: Optional[float] = None, new_measure: Optional[str] = None) -> Dict[str, Any]:
        """Duplicate an existing item on a track.
        
        Item Identification - Accepts BOTH types:
        - track_pos_idx (integer): Simple index like 0, 1, 2
        - direct_item_id (string): Internal ID like "MediaItem*0x..."
        
        Args:
            track_index: Index of the track
            item_id: EITHER integer track_pos_idx OR string direct_item_id
            new_time: New position in seconds (optional)
            new_measure: New position as "measure:beat,fraction" (optional)
        """
        try:
            # Determine the time position if any position is provided
            if new_time is not None:
                time_pos = float(new_time)
                measure_pos = time_to_measure(time_pos)
                new_position = time_pos
            elif new_measure is not None:
                time_pos = position_to_time(new_measure)
                measure_pos = new_measure
                new_position = time_pos
            else:
                new_position = None
                time_pos = None
                measure_pos = None
                
            new_item_id = controller.duplicate_item(track_index, item_id, new_position)
            # Convert any type of new_item_id to an index
            if isinstance(new_item_id, str):
                # If it's a string (pointer), find its index in the track
                project = reapy.Project()
                track = project.tracks[track_index]
                for i, item in enumerate(track.items):
                    if str(item.id) == new_item_id:
                        if new_position is not None:
                            position_msg = f" at position {measure_pos} (time: {time_pos:.3f}s)"
                        else:
                            position_msg = ""
                        return {"status": "success", "message": f"Duplicated item {item_id}{position_msg}", "item_id": i}
                return {"status": "error", "message": "Failed to find duplicated item index"}
            elif isinstance(new_item_id, int):
                # If it's already an index, use it directly
                if new_item_id >= 0:
                    if new_position is not None:
                        position_msg = f" at position {measure_pos} (time: {time_pos:.3f}s)"
                    else:
                        position_msg = ""
                    return {"status": "success", "message": f"Duplicated item {item_id}{position_msg}", "item_id": new_item_id}
            return {"status": "error", "message": "Failed to duplicate item"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to duplicate item: {str(e)}"}
    
    @mcp.tool("get_item_properties")
    def get_item_properties(ctx: Context, track_index: int, item: Union[int, str]) -> Dict[str, Any]:
        """Get properties of a media item.
        
        Item Identification - Accepts BOTH types:
        - track_pos_idx (integer): Simple index like 0, 1, 2
        - direct_item_id (string): Internal ID like "MediaItem*0x..."
        
        Args:
            track_index: Index of the track
            item_id: EITHER integer track_pos_idx OR string direct_item_id
        """
        try:
            properties = controller.get_item_properties(track_index, item)
            if properties:
                return {"status": "success", "properties": properties}
            return {"status": "error", "message": f"Failed to get properties for item {item}"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get item properties: {str(e)}"}
    
    @mcp.tool("set_item_position")
    def set_item_position(ctx: Context, track_index: int, item_id: Union[int, str], 
                         position_time: Optional[float] = None, 
                         position_measure: Optional[str] = None) -> Dict[str, Any]:
        """Set the position of a media item.
        
        Item Identification - Accepts BOTH types:
        - track_pos_idx (integer): Simple index like 0, 1, 2
        - direct_item_id (string): Internal ID like "MediaItem*0x..."
        
        Args:
            track_index: Index of the track
            item_id: EITHER integer track_pos_idx OR string direct_item_id
            position_time: New position in seconds (optional if position_measure is provided)
            position_measure: New position as "measure:beat,fraction" (optional if position_time is provided)
                           where fraction is milliseconds (e.g., "1:1,500" = measure 1, beat 1, half beat)
        """
        try:
            # Determine the time position
            if position_time is not None:
                time_pos = float(position_time)
                measure_pos = time_to_measure(time_pos)
            elif position_measure is not None:
                time_pos = position_to_time(position_measure)
                measure_pos = position_measure
            else:
                return {"status": "error", "message": "Either position_time or position_measure must be provided"}
                
            if controller.set_item_position(track_index, item_id, time_pos):
                return {"status": "success", "message": f"Set item {item_id} position to {measure_pos} (time: {time_pos:.3f}s)"}
            return {"status": "error", "message": "Failed to set item position"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to set item position: {str(e)}"}
    
    @mcp.tool("set_item_length")
    def set_item_length(ctx: Context, track_index: int, item_id: Union[int, str],
                       length_time: Optional[float] = None,
                       length_measure: Optional[str] = None) -> Dict[str, Any]:
        """Set the length of a media item.
        
        Item Identification - Accepts BOTH types:
        - track_pos_idx (integer): Simple index like 0, 1, 2
        - direct_item_id (string): Internal ID like "MediaItem*0x..."
        
        Args:
            track_index: Index of the track
            item_id: EITHER integer track_pos_idx OR string direct_item_id
            length_time: Length in seconds from start of item (optional if length_measure is provided)
            length_measure: Length as "measure:beat,fraction" from start of item(optional if length_time is provided)
        """
        try:
            # Normalize length_measure: reject explicit zero-length "0:0,0", convert "M:0,0" -> "M+1:1,0"
            if length_measure:
                lm = length_measure.strip()
                if lm in ("0:0,0", "0:0.0"):
                    return {"status": "error", "message": "Invalid length_measure: zero length specified (0:0,0)"}
                if ":0,0" in lm or ":0.0" in lm:
                    try:
                        measure_part = int(lm.split(':')[0])
                        length_measure = f"{measure_part}:1,0"
                    except Exception:
                        return {"status": "error", "message": f"Invalid length_measure format: {length_measure}"}
            
            # Get current item position to calculate length in measures
            props = controller.get_item_properties(track_index, item_id)
            if not props:
                return {"status": "error", "message": "Failed to get item properties"}
                
            current_pos = props.get("position", 0)
            
            # Determine length
            if length_time is not None:
                length = float(length_time)
                length_pos = time_to_measure(current_pos + length)
            elif length_measure is not None:
                end_pos = position_to_time(length_measure)
                length = end_pos - current_pos
                length_pos = length_measure
            else:
                return {"status": "error", "message": "Either length_time or length_measure must be provided"}

            if controller.set_item_length(track_index, item_id, length):
                return {
                    "status": "success",
                    "message": f"Set item {item_id} length to {length_pos} (time: {length:.3f}s)"
                }
            return {"status": "error", "message": "Failed to set item length"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to set item length: {str(e)}"}
    
    @mcp.tool("delete_item")
    def delete_item(ctx: Context, track_index: int, item: Union[int, str]) -> Dict[str, Any]:
        """Delete a media item from a track.
        
        Item Identification - Accepts BOTH types:
        - track_pos_idx (integer): Simple index like 0, 1, 2
        - direct_item_id (string): Internal ID like "MediaItem*0x..."
        
        Args:
            track_index: Index of the track
            item: EITHER integer track_pos_idx OR string direct_item_id
        """
        try:
            if controller.delete_item(track_index, item):
                return {"status": "success", "message": f"Deleted item {item} from track {track_index}"}
            return {"status": "error", "message": "Failed to delete item"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to delete item: {str(e)}"}
    
    @mcp.tool("get_items_in_time_range")
    def get_items_in_time_range(ctx: Context, track_index: int, 
                               start_time: Optional[float] = None, end_time: Optional[float] = None,
                               start_measure: Optional[str] = None, end_measure: Optional[str] = None) -> Dict[str, Any]:
        """Get all items on a track within a time range.
        
        Returns items with BOTH identification methods for each item:
        
        1. track_pos_idx (integer):
           - Simple sequential index: 0, 1, 2, 3...
           - Easy to use in loops and quick operations
           - Changes if items before it are deleted
           
        2. direct_item_id (string):
           - REAPER's permanent internal ID like "MediaItem*0x..."
           - Unique stable reference that never changes
           - Use this for reliable long-term item tracking
        
        You can use either one in subsequent operations like add_midi_note.
        
        Args:
            track_index: 0-based track index (0 = first track, 1 = second, etc.)
            start_time: Start position in seconds (optional if start_measure is provided)
            end_time: End position in seconds (optional if end_measure is provided)
            start_measure: Start position as "measure:beat,fraction" (optional if start_time is provided)
            end_measure: End position as "measure:beat,fraction" (optional if end_time is provided)
            
        Returns:
            Each item includes:
            - track_pos_idx: Integer position index (0, 1, 2...)
            - direct_item_id: String internal ID ("MediaItem*...")
            - position: Item start time in seconds
            - length: Item duration in seconds
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
                
            # Get items with their properties
            project = reapy.Project()
            track = project.tracks[track_index]
            items_info = []
            
            for index, item in enumerate(track.items):
                if time_start <= item.position < time_end or time_start < (item.position + item.length) <= time_end:
                    items_info.append({
                        "track_pos_idx": index,
                        "direct_item_id": str(item.id),
                        "position": item.position,
                        "length": item.length
                    })
            
            return {
                "status": "success", 
                "message": f"Found {len(items_info)} items between {measure_start} and {measure_end}",
                "items": items_info,
                "range": {
                    "start": {"time": time_start, "measure": measure_start},
                    "end": {"time": time_end, "measure": measure_end}
                }
            }
        except Exception as e:
            return {"status": "error", "message": f"Failed to get items in time range: {str(e)}"}
    
    @mcp.tool("get_selected_items")
    def get_selected_items(ctx: Context) -> Dict[str, Any]:
        """Get all selected media items in the project with their properties.
        
        Returns:
            Dict containing status and list of selected items with their properties:
            - track_index: Index of the track containing the item
            - item_index: Index of the item in its track
            - position: Start time in seconds
            - length: Length in seconds from the start of item
            - is_midi: Whether the item is a MIDI item
            - name: Item name if available
        """
        try:
            result = controller.get_selected_items()
            if result and len(result) > 0:
                return {
                    "status": "success", 
                    "message": f"Found {len(result)} selected item(s)",
                    "items": result
                }
            return {"status": "error", "message": "No selected items found"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get selected items: {str(e)}"}


