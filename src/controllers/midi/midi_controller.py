import reapy
import logging
from typing import List, Dict, Any, Optional, Union, Tuple

from ..base_controller import BaseController
from reaper_reapy_mcp.utils.item_utils import get_item_by_id_or_index, get_item_properties, select_item, delete_item

class MIDIController(BaseController):
    """Controller for MIDI-related operations in Reaper."""
    
    def _select_item(self, item: reapy.Item) -> bool:
        """
        Helper function to select an item.
        
        Args:
            item (reapy.Item): The item to select
        
        Returns:
            bool: True if the selection was successful, False otherwise
        """
        return select_item(item)
    
    def create_midi_item(self, track_index: int, start_time: float, length: float = 4.0) -> Dict[str, Union[int, str]]:
        """
        Create an empty MIDI item on a track.
        
        Args:
            track_index (int): Index of the track to add the MIDI item to
            start_time (float): Start time in seconds
            length (float): Length of the MIDI item in seconds
            
        Returns:
            dict: {'track_pos_idx': int, 'direct_item_id': str} 
                  track_pos_idx: Track-relative position index (0-based)
                  direct_item_id: REAPER's internal item ID
                  Returns {'track_pos_idx': -1, 'direct_item_id': None} if creation fails
        """
        try:
            # Convert and validate parameters
            try:
                track_index = int(track_index)
                start_time = float(start_time)
                length = float(length)
            except (ValueError, TypeError) as e:
                self.logger.error(f"Invalid parameter type: {e}")
                return {'track_pos_idx': -1, 'direct_item_id': None}
            
            # Validate track index using base controller method
            track = self._get_track(track_index)
            if track is None:
                return {'track_pos_idx': -1, 'direct_item_id': None}
                
            self.logger.debug(f"Creating MIDI item on track {track_index} at position {start_time} with length {length}")
            
            # Create the item
            item = track.add_midi_item(start_time, start_time + length)
            if item is None:
                self.logger.error("Failed to create MIDI item - track.add_midi_item returned None")
                return {'track_pos_idx': -1, 'direct_item_id': None}
                
            take = item.active_take
            if take is None:
                take = item.add_take()
                if take is None:
                    self.logger.error("Failed to add take to MIDI item")
                    return {'track_pos_idx': -1, 'direct_item_id': None}
                self.logger.debug("Added new take to item")
            
            self.logger.debug("Take configured for MIDI")
            
            # Find the index of this item in the track's items collection
            for i, track_item in enumerate(track.items):
                if track_item.id == item.id:
                    self.logger.info(f"Created MIDI item at index {i} with ID: {item.id}")
                    return {'track_pos_idx': i, 'direct_item_id': str(item.id)}
            
            # Fallback - couldn't find index
            self.logger.warning(f"Created MIDI item with ID: {item.id}, but couldn't find index")
            return {'track_pos_idx': -1, 'direct_item_id': str(item.id)}

        except Exception as e:
            self.logger.error(f"Failed to create MIDI item: {e}")
            return {'track_pos_idx': -1, 'direct_item_id': None}
    
    def add_midi_note(self, track_index: int, item_id: Union[int, str], pitch: int, 
                     start_time: float, length: float, velocity: int = 96, channel: int = 0) -> bool:
        """
        Add a MIDI note to a MIDI item.
        
        Args:
            track_index (int): Index of the track containing the MIDI item
            item_id (int or str): ID of the MIDI item
            pitch (int): MIDI note pitch (0-127)
            start_time (float): Start time in seconds (relative to item start)
            length (float): Note length in seconds
            velocity (int): Note velocity (0-127)
            channel (int): MIDI channel (0-15)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            track_index = int(track_index)
            pitch = int(pitch)
            start_time = float(start_time)
            length = float(length)
            velocity = int(velocity)
            channel = int(channel)

            # Try to add the note to Reaper project
            try:
                project = reapy.Project()
                track = project.tracks[track_index]
                
                # Use shared utility to find the item
                item = get_item_by_id_or_index(track, item_id)
                if item is None:
                    return False
                
                take = item.active_take
                if take is None:
                    self.logger.error("Item has no active take")
                    return False
                
                note_start = start_time
                note_end = note_start + length
                
                # Make sure item is selected
                project.select_all_items(False)
                try:
                    self._select_item(item)
                except Exception as e:
                    self.logger.warning(f"Failed to select item, but continuing: {e}")
                
                take.add_note(note_start, note_end, channel=channel, pitch=pitch, velocity=velocity)
                self.logger.info(f"Added MIDI note: pos={note_start}, pitch={pitch}")
                
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to add MIDI note to Reaper: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to add MIDI note: {e}")
            return False
    
    def clear_midi_item(self, track_index, item_id):
        """
        Clear all MIDI notes from a MIDI item.
        
        Args:
            track_index (int): Index of the track containing the MIDI item
            item_id (int or str): ID of the MIDI item to clear
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.logger.debug(f"Clearing MIDI notes from track {track_index}, item {item_id}")
        
        try:
            # Validate track index first
            track_index = int(track_index)
            project = reapy.Project()
            num_tracks = len(project.tracks)
            if track_index < 0 or track_index >= num_tracks:
                self.logger.error(f"Track index {track_index} out of range (project has {num_tracks} tracks)")
                return False
                
            track = project.tracks[track_index]
            
            # Use shared utility to find the item
            item = get_item_by_id_or_index(track, item_id)
            if item is None:
                return False
            
            # Get the current take
            take = item.active_take
            if take is None:
                self.logger.error("Item has no active take")
                return False
            
            # Store the item's position and length
            position = item.position
            length = item.length
            
            # Create a new empty MIDI item at the same position
            new_item = track.add_midi_item(position, position + length)
            if new_item is None:
                self.logger.error("Failed to create new MIDI item")
                return False
            
            # Delete the old item
            if not delete_item(item):
                self.logger.error("Failed to delete old MIDI item")
                return False
            
            # Return the index of the new item
            for i, track_item in enumerate(track.items):
                if track_item.id == new_item.id:
                    self.logger.info(f"Created new empty MIDI item at index {i}")
                    return True
            
            self.logger.error("Failed to find the new MIDI item")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to clear MIDI item: {e}")
            return False
    
    def get_midi_notes(self, track_index, item_id, include_invisible: bool = False):
        """
        Get all MIDI notes from a MIDI item.
        
        Args:
            track_index (int): Index of the track containing the MIDI item
            item_id (int or str): ID of the MIDI item
            include_invisible (bool): If True, include notes outside item bounds (these notes won't sound).
                                     Default False - returns only visible notes within item boundaries.
            
        Returns:
            list: A list of dictionaries containing MIDI note data with keys:
                - pitch (int): MIDI note number
                - start_time (float): Start time in seconds (relative to item start)
                - end_time (float): End time in seconds (relative to item start)
                - velocity (int): Note velocity (0-127)
                - channel (int): MIDI channel
                - is_visible (bool): Whether note is within item bounds (only included if include_invisible=True)
        """
        self.logger.debug(f"Getting MIDI notes from track {track_index}, item {item_id}")
        
        try:                
            # Get actual notes from REAPER
            project = reapy.Project()
            track = project.tracks[track_index]
            
            # Use shared utility to find the item
            item = get_item_by_id_or_index(track, item_id)
            if item is None:
                return []
            
            take = item.active_take
            if take is None:
                self.logger.error("Item has no active take")
                return []
                
            item_start = item.position
            item_length = item.length
            
            # Get all MIDI notes
            notes = []
            for note in take.notes:
                relative_start = note.start - item_start
                relative_end = note.end - item_start
                
                # Check if note is visible (within item bounds)
                is_visible = (0 <= relative_start < item_length) and (0 < relative_end <= item_length)
                
                # Skip invisible notes unless requested
                if not is_visible and not include_invisible:
                    continue
                
                note_data = {
                    'pitch': note.pitch,
                    'start_time': relative_start,
                    'end_time': relative_end,
                    'velocity': note.velocity,
                    'channel': note.channel
                }
                
                # Add visibility flag only when including invisible notes
                if include_invisible:
                    note_data['is_visible'] = is_visible
                    if not is_visible:
                        note_data['_note'] = 'Note outside item bounds - will not sound during playback'
                
                notes.append(note_data)
            
            self.logger.info(f"Found {len(notes)} MIDI notes in item (include_invisible={include_invisible})")
            return notes
            
        except Exception as e:
            self.logger.error(f"Failed to get MIDI notes: {e}")
            return []
    
    def find_midi_notes_by_pitch(self, pitch_min=0, pitch_max=127):
        """
        Find all MIDI notes within a specific pitch range across the project.
        
        Args:
            pitch_min (int): Minimum MIDI pitch to search for (0-127)
            pitch_max (int): Maximum MIDI pitch to search for (0-127)
            
        Returns:
            list: A list of dictionaries containing found MIDI notes with keys:
                - track_index (int): Index of the track containing the note
                - item_id (int or str): ID of the MIDI item containing the note
                - pitch (int): MIDI note number
                - start_time (float): Start time in seconds
                - end_time (float): End time in seconds
                - velocity (int): Note velocity (0-127)
                - channel (int): MIDI channel
        """
        self.logger.debug(f"Finding MIDI notes with pitch between {pitch_min} and {pitch_max}")
        
        try:
            # Find notes in actual REAPER project
            project = reapy.Project()
            matching_notes = []
            
            # Iterate through all tracks
            for track_index, track in enumerate(project.tracks):
                # Iterate through all items on this track
                for item_index, item in enumerate(track.items):
                    take = item.active_take
                    if take is None:
                        continue
                    
                    # Skip non-MIDI takes
                    if not take.is_midi:
                        continue
                    
                    # Remember item start position for relative time calculation
                    item_start = item.position
                    
                    # Make sure item is selected for MIDI operations
                    project.select_all_items(False)
                    try:
                        self._select_item(item)
                    except Exception as e:
                        self.logger.warning(f"Failed to select item, but continuing: {e}")
                    
                    # Get all MIDI notes from this take
                    for note in take.notes:
                        if pitch_min <= note.pitch <= pitch_max:
                            matching_notes.append({
                                'track_index': track_index,
                                'item_id': item_index,  # Use item index for consistency
                                'pitch': note.pitch,
                                'start_time': note.start - item_start,
                                'end_time': note.end - item_start,
                                'velocity': note.velocity,
                                'channel': note.channel
                            })
            
            self.logger.info(f"Found {len(matching_notes)} matching notes in project")
            return matching_notes
            
        except Exception as e:
            self.logger.error(f"Failed to find MIDI notes by pitch: {e}")
            return []
    
    def get_all_midi_items(self):
        """
        Get all MIDI items in the project.
        
        Returns:
            list: A list of dictionaries containing MIDI item data with keys:
                - track_index (int): Index of the track containing the item
                - item_id (int or str): ID of the MIDI item
                - position (float): Start position in seconds
                - length (float): Length in seconds
                - name (str): Name of the MIDI item
        """
        self.logger.debug("Getting all MIDI items in the project")
        
        try:
            # Find MIDI items in actual REAPER project
            project = reapy.Project()
            midi_items = []
            
            # Iterate through all tracks
            for track_index, track in enumerate(project.tracks):
                # Iterate through all items on this track
                for item_index, item in enumerate(track.items):
                    take = item.active_take
                    if take is None:
                        continue
                    
                    # Skip non-MIDI takes
                    if not take.is_midi:
                        continue
                    
                    # Use shared utility to get properties
                    properties = get_item_properties(item)
                    properties.update({
                        'track_index': track_index,
                        'item_id': item_index  # Use item index for consistency
                    })
                    midi_items.append(properties)
            
            self.logger.info(f"Found {len(midi_items)} MIDI items in project")
            return midi_items
            
        except Exception as e:
            self.logger.error(f"Failed to get all MIDI items: {e}")
            return []

    def get_selected_midi_item(self) -> Optional[Dict[str, int]]:
        """
        Get the first selected MIDI item in the current project.
        Returns:
            dict: { 'track_index': int, 'item_id': int } or None if not found
        """
        try:
            from reapy import reascript_api as RPR
            project = reapy.Project()
            for track_index, track in enumerate(project.tracks):
                for item_index, item in enumerate(track.items):
                    if RPR.IsMediaItemSelected(item.id) and item.active_take and item.active_take.is_midi:
                        return {'track_index': track_index, 'item_id': item_index}
            return None
        except Exception as e:
            self.logger.error(f"Failed to get selected MIDI item: {e}")
            return None
