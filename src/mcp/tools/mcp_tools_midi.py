from mcp.server.fastmcp import FastMCP, Context
from typing import Optional, Dict, Any, List, Union

from reaper_reapy_mcp.utils.position_utils import position_to_time, time_to_measure, measure_length_to_time

def _setup_midi_tools(mcp: FastMCP, controller) -> None:
    @mcp.tool("create_midi_item")
    def create_midi_item(ctx: Context, track_index: int, 
                        start_time: Optional[float] = None, 
                        start_measure: Optional[str] = None,
                        length_time: Optional[float] = None,
                        length_measure: Optional[str] = None) -> Dict[str, Any]:
        """Create an empty MIDI item on a track. 
        
        Important: It is recommended to avoid overlapping MIDI items. Ensure to double-check before creating a new one.

        Returns both track_pos_idx and direct_item_id for flexible item referencing:
        - track_pos_idx: 0-based position index within the track (0, 1, 2, etc.)
        - direct_item_id: REAPER's internal item ID (string pointer)
        
        Both can be used interchangeably in subsequent operations like add_midi_note.
        
        Args:
            track_index: 0-based track index (0 = first track, 1 = second, etc.)
                        Note: REAPER UI shows "Track 1, Track 2" but API uses 0, 1, etc.
            start_time: Start position in seconds (optional if start_measure is provided)
            start_measure: Start position as "measure:beat,fraction" (optional if start_time is provided)
                         where fraction is milliseconds (e.g., "1:1,500" = measure 1, beat 1, half beat)
            length_time: Duration in seconds from start position (from start_time or start_measure)(optional if length_measure is provided).
            length_measure: Duration as "measure:beat,fraction" from start position (e.g., "2:1,000" = 2 measures from start_time or start_measure)(optional if length_time is provided). The range starts from 0:1,0. The value 0:4,0 equals three beats in a 4/4 time signature. Thus, if you want the length of all beats from one measure, then use 1:1,0; for two measures, use 2:1,0; and for three, use 3:1,0.
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
                        
            # Determine the time position
            if start_time is not None:
                time_pos = float(start_time)
                measure_pos = time_to_measure(time_pos)
            elif start_measure is not None:
                time_pos = position_to_time(start_measure)
                measure_pos = start_measure
            else:
                return {"status": "error", "message": "Either start_time or start_measure must be provided"}
                
            # Determine length
            if length_time is not None:
                try:
                    length_val = float(length_time)
                except Exception:
                    return {"status": "error", "message": "Invalid length_time value"}
                if length_val <= 0:
                    return {"status": "error", "message": "Note length must be greater than zero"}
                length = length_val
                end_time = time_pos + length
                length_pos = time_to_measure(end_time)
            elif length_measure is not None:
                try:
                    length = measure_length_to_time(length_measure, time_pos)
                except Exception as e:
                    return {"status": "error", "message": f"Invalid length_measure: {e}"}
                if length <= 0:
                    return {"status": "error", "message": "Note length must be greater than zero"}
                end_time = time_pos + length
                length_pos = time_to_measure(end_time)
            else:
                return {"status": "error", "message": "Either length_time or length_measure must be provided"}

            result = controller.create_midi_item(track_index, time_pos, length)
            if result['track_pos_idx'] >= 0 or result['direct_item_id']:
                return {
                    "status": "success",
                    "message": f"Created MIDI item at position {measure_pos} with length {length_pos}",
                    "track_pos_idx": result['track_pos_idx'],
                    "direct_item_id": result['direct_item_id'],
                    "position": {"time": time_pos, "measure": measure_pos},
                    "end": {"time": end_time, "measure": length_pos}
                }
            return {"status": "error", "message": "Failed to create MIDI item"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to create MIDI item: {str(e)}"}
    
    @mcp.tool("add_midi_note")
    def add_midi_note(ctx: Context, track_index: int, item: Union[int, str], pitch: int, 
                     start_time: Optional[float] = None, 
                     start_measure: Optional[str] = None,
                     length_time: Optional[float] = None,
                     length_measure: Optional[str] = None,
                     velocity: int = 96,
                     relative_start: bool = False) -> Dict[str, Any]:
        """Add a MIDI note to a MIDI item. Reaper format 2.1.00 should be converted to 2:1,000.
        
        Important: Please check MIDI item length in which you want to add the note. 
        If the note extends beyond the item bounds, create another one or resize existing before note adding.
        Double-check the item's starting position before adding it. Notes positioned before the item's position won't be added.

        Item Identification - TWO ways to specify which item:
        
        1. Using track_pos_idx (integer):
           - Pass the simple index number from create_midi_item response
           - Example: item=track_pos_idx=0 for first item, item=track_pos_idx=1 for second item
           - Fast and easy but may change if items are reordered
           
        2. Using direct_item_id (string):
           - Pass the exact string ID from create_midi_item or get_items_in_time_range
           - Example: item=direct_item_id="MediaItem*0x000001234567890A"
           - Stable and reliable, won't change even if items move
        
        The system automatically detects which type you're using.
        
        Note about positioning:
        - start_time and start_measure specify ABSOLUTE position in the project timeline
        - The note will be placed at this absolute position, regardless of item location
        - Example: start_measure="5:1,000" means measure 5 in the project, not 5 measures into the item
        
        Args:
            track_index: 0-based track index (0 = first track, 1 = second, etc.)
                        Important: REAPER UI displays "Track 1" but API uses index 0.
            item: EITHER an integer track_pos_idx (0, 1, 2...) OR a string direct_item_id
            pitch: MIDI note pitch (0-127)
            start_time: ABSOLUTE start position in seconds in the project timeline (optional if start_measure is provided)
            start_measure: ABSOLUTE start position as "measure:beat,fraction" in the project timeline (optional if start_time is provided)
            length_time: Duration in seconds from note start (from start_time or start_measure)(optional if length_measure is provided)
            length_measure: Duration as "measure:beat,fraction" from note start (e.g., "0:2,000" = 2 beats from start_time or start_measure)(optional if length_time is provided). Also remember 2:0,0 is not end of 2 measure and 3:1,0 should be.
            velocity: Note velocity (0-127, default: 96)
            relative_start: If True, start_time/start_measure are interpreted as offsets
                            from the item's start (i.e. relative to item.start). If False
                            (default), they are treated as absolute project positions.
        """
        try:
            # Normalize length_measure: convert M:0,0 -> M+1:1,0, but reject explicit "0:0,0"
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
            
            # Get MIDI item properties for debugging / existence check
            item_props = controller.get_item_properties(track_index, item)
            if not item_props:
                return {"status": "error", "message": "MIDI item does not exist"}
                
            item_start = item_props.get("position", 0)
            item_length = item_props.get("length", 0)
            
            # Determine the start position (absolute vs relative to item start)
            if start_time is not None:
                if relative_start:
                    # treat start_time as offset from item_start
                    time_pos = item_start + float(start_time)
                else:
                    time_pos = float(start_time)
                measure_pos = time_to_measure(time_pos)
            elif start_measure is not None:
                if relative_start:
                    # treat start_measure as a length/offset from item_start
                    offset = measure_length_to_time(start_measure, item_start)
                    time_pos = item_start + offset
                else:
                    time_pos = position_to_time(start_measure)
                measure_pos = time_to_measure(time_pos)
            else:
                return {"status": "error", "message": "Either start_time or start_measure must be provided"}

            # NEW: if using absolute mode, reject notes that start before the item
            if not relative_start and time_pos < item_start:
                return {
                    "status": "error",
                    "message": "Requested note start is before the MIDI item start; note will not be added."
                }

            # Determine the length
            if length_time is not None:
                try:
                    length_val = float(length_time)
                except Exception:
                    return {"status": "error", "message": "Invalid length_time value"}
                if length_val <= 0:
                    return {"status": "error", "message": "Note length must be greater than zero"}
                length = length_val
                end_time = time_pos + length
                end_measure = time_to_measure(end_time)
            elif length_measure is not None:
                try:
                    length = measure_length_to_time(length_measure, time_pos)
                except Exception as e:
                    return {"status": "error", "message": f"Invalid length_measure: {e}"}
                if length <= 0:
                    return {"status": "error", "message": "Note length must be greater than zero"}
                end_time = time_pos + length
                end_measure = time_to_measure(end_time)
            else:
                return {"status": "error", "message": "Either length_time or length_measure must be provided"}

            relative_item_pos = (time_pos - item_start)
            # Enhanced debug info with detailed timing calculations
            debug_info = {
                "item": {
                    "start_time": item_start,
                    "start_measure": time_to_measure(item_start),
                    "length": item_length,
                    "end_time": item_start + item_length,
                    "end_measure": time_to_measure(item_start + item_length)
                },
                "note": {
                    "absolute": {
                        "time_pos": time_pos,
                        "measure_pos": measure_pos,
                        "end_time": end_time,
                        "end_measure": end_measure
                    },
                    "relative": {
                        "start": relative_item_pos,
                        "length": length,
                        "end": relative_item_pos + length
                    },
                    "flags": {
                        "relative_start_mode": relative_start
                    }
                },
                "calculations": {
                    "time_diff": time_pos - item_start,
                    "is_in_bounds": 0 <= relative_item_pos <= item_length,
                    "start_offset": relative_item_pos,
                    "end_offset": relative_item_pos + length
                }
            }

            if controller.add_midi_note(track_index, item, pitch, relative_item_pos, length, velocity):
                return {
                    "status": "success", 
                    "message": f"Added MIDI note (pitch: {pitch}, velocity: {velocity}) to item {item}",
                    "note": {
                        "start": {"time": time_pos, "measure": measure_pos},
                        "length": length,
                        "end": {"time": end_time, "measure": end_measure},
                        "relative_start_mode": relative_start
                    },
                    "debug": debug_info
                }
            return {"status": "error", "message": "Failed to add MIDI note"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to add MIDI note: {str(e)}"}
    
    @mcp.tool("add_midi_notes")
    def add_midi_notes(ctx: Context, track_index: int, item: Union[int, str], notes: List[Dict[str, Any]],
                       relative_start: bool = False) -> Dict[str, Any]:
        """Add multiple MIDI notes to a MIDI item in one operation.
        
        Important: Please check MIDI item length in which you want to add notes. 
        If any note extends beyond the item bounds, create another one or resize existing before note adding.
        
        Item Identification - TWO ways to specify which item:
        
        1. Using track_pos_idx (integer):
           - Simple position number: 0 = first item, 1 = second item, etc.
           - Get this from create_midi_item response field "track_pos_idx"
           - Quick but may become invalid if items are deleted/reordered
           
        2. Using direct_item_id (string):
           - REAPER's internal pointer like "MediaItem*0x000001234567890A"
           - Get this from create_midi_item response field "direct_item_id"
           - Or from get_items_in_time_range response
           - Guaranteed to always point to the same item
        
        Recommendation: Use track_pos_idx for quick scripts, direct_item_id for reliability.
        
        Args:
            track_index: Index of the track
            track_pos_idx: EITHER integer track_pos_idx OR string direct_item_id
            notes: List of note definitions, each containing:
                - pitch: MIDI note pitch (0-127)
                - start_time: Start position in seconds (optional if start_measure provided)
                - start_measure: Start position as "measure:beat,fraction" (optional if start_time provided)
                - length_time: Duration in seconds (optional if length_measure provided)
                - length_measure: Duration as "measure:beat,fraction" (e.g., "0:2,000" = 2 beats)
                - velocity: Note velocity (0-127, optional, default: 96)
                - relative_start: Default mode for all notes. Per-note override supported via note['relative_start'] (bool).
        
        Example:
            notes = [
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
        """
        try:
            # Check if item exists before adding notes
            item_props = controller.get_item_properties(track_index, item)
            if not item_props:
                return {
                    "status": "error",
                    "message": "MIDI item does not exist",
                    "successful_notes": [],
                    "failed_notes": [{"error": "MIDI item does not exist"}]
                }
            
            results = []
            errors = []
            
            for i, note in enumerate(notes):
                try:
                    note_relative = note.get("relative_start", relative_start)
                    result = add_midi_note(ctx, 
                        track_index=track_index,
                        item=item,  # Can be either track_pos_idx or direct_item_id
                        pitch=note["pitch"],
                        start_time=note.get("start_time"),
                        start_measure=note.get("start_measure"),
                        length_time=note.get("length_time"),
                        length_measure=note.get("length_measure"),
                        velocity=note.get("velocity", 96),
                        relative_start=note_relative
                    )
                    
                    if result["status"] == "success":
                        results.append({
                            "index": i,
                            "note": note,
                            "details": result["note"]
                        })
                    else:
                        errors.append({
                            "index": i,
                            "note": note,
                            "error": result.get("message", "unknown error")
                        })
                        
                except Exception as e:
                    errors.append({
                        "index": i,
                        "note": note,
                        "error": str(e)
                    })
            
            return {
                "status": "success" if not errors else "partial" if results else "error",
                "message": f"Added {len(results)} notes, {len(errors)} failed",
                "successful_notes": results,
                "failed_notes": errors
            }
            
        except Exception as e:
            return {"status": "error", "message": f"Failed to add MIDI notes: {str(e)}"}
    
    @mcp.tool("clear_midi_item")
    def clear_midi_item(ctx: Context, track_index: int, item_id: int) -> Dict[str, Any]:
        """Clear all MIDI notes from a MIDI item."""
        try:
            if controller.clear_midi_item(track_index, item_id):
                return {"status": "success", "message": f"Cleared all notes from MIDI item {item_id}"}
            return {"status": "error", "message": "Failed to clear MIDI item"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to clear MIDI item: {str(e)}"}
            
    @mcp.tool("get_midi_notes")
    def get_midi_notes(ctx: Context, track_index: int, item_id: Union[int, str], include_invisible: bool = False) -> Dict[str, Any]:
        """Get all MIDI notes from a MIDI item.
        
        By default, returns only visible notes (within item bounds). 
        Invisible notes exist in the MIDI data but won't sound during playback.
        
        Item Identification - Accepts BOTH types:
        - track_pos_idx (integer): Simple index like 0, 1, 2
        - direct_item_id (string): Internal ID like "MediaItem*0x..."
        
        Args:
            track_index: Index of the track
            item_id: EITHER integer track_pos_idx OR string direct_item_id
            include_invisible: If True, include notes outside item bounds (won't sound). Default: False
        """
        try:
            notes = controller.get_midi_notes(track_index, item_id, include_invisible)
            return {"status": "success", "notes": notes, "count": len(notes)}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get MIDI notes: {str(e)}"}

    @mcp.tool("find_midi_notes_by_pitch")
    def find_midi_notes_by_pitch(ctx: Context, pitch_min: int = 0, pitch_max: int = 127) -> Dict[str, Any]:
        """Find all MIDI notes within a specific pitch range across the project."""
        try:
            notes = controller.find_midi_notes_by_pitch(pitch_min, pitch_max)
            return {"status": "success", "notes": notes}
        except Exception as e:
            return {"status": "error", "message": f"Failed to find MIDI notes by pitch: {str(e)}"}
            
    @mcp.tool("get_selected_midi_item")
    def get_selected_midi_item(ctx: Context) -> Dict[str, Any]:
        """Get the first selected MIDI item in the project."""
        try:
            result = controller.get_selected_midi_item()
            if result:
                return {"status": "success", **result}
            else:
                return {"status": "error", "message": "No selected MIDI item found"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to get selected MIDI item: {str(e)}"}

