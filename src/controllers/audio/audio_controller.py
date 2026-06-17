import reapy
import logging
import os
from typing import Union
import time
from reapy import reascript_api as RPR

from ..base_controller import BaseController
from reaper_reapy_mcp.utils.item_utils import get_item_by_id_or_index, get_item_properties, select_item, delete_item

class AudioController(BaseController):
    """Controller for audio-related operations in Reaper."""
    
    def insert_audio_item(self, track_index: int, file_path: str, start_time: float) -> Union[int, str]:
        """
        Insert an audio file as a media item on a track.
        
        Args:
            track_index (int): Index of the track to add the audio item to
            file_path (str): Path to the audio file
            start_time (float): Start time in seconds
            
        Returns:
            int or str: ID of the created item
        """
        try:
            if not os.path.exists(file_path):
                self.logger.error(f"Audio file does not exist: {file_path}")
                return -1
                
            project = reapy.Project()
            track = project.tracks[track_index]
            
            # First, select the track
            # Clear all track selections directly using ReaScript API
            RPR.SetOnlyTrackSelected(track.id)  # This deselects all other tracks and selects only this one
            
            # Set the cursor to the start position
            project.cursor_position = start_time
            
            # Store the number of items before insertion
            num_items_before = len(track.items)
            
            # Insert the media file using the ReaScript API
            RPR.InsertMedia(file_path, 0)  # 0 means "add media to selected tracks"
            
            # Wait a short time for the insertion to complete
            time.sleep(0.1)
            
            # Check if any new items were added
            if len(track.items) <= num_items_before:
                self.logger.error("No new items were added after media insertion")
                return -1
            
            # Find the newly inserted item (should be the last one)
            for i in range(len(track.items) - 1, -1, -1):  # Search from the last item
                item = track.items[i]
                if abs(item.position - start_time) < 0.01:  # Small threshold to account for precision issues
                    self.logger.info(f"Found inserted audio item at position {item.position}, ID: {item.id}")
                    return item.id
            
            # If we couldn't find the item at the exact position, return the last item
            if len(track.items) > num_items_before:
                last_item = track.items[-1]
                self.logger.info(f"Using last inserted item at position {last_item.position}, ID: {last_item.id}")
                return last_item.id
            
            self.logger.warning(f"Couldn't find the inserted audio item at position {start_time}")
            return -1

        except Exception as e:
            self.logger.error(f"Failed to insert audio item: {e}")
            return -1
            
    def get_item_properties(self, track_index, item_id):
        """
        Get properties of a media item.
        
        Args:
            track_index (int): Index of the track containing the item
            item_id (int or str): ID of the item
            
        Returns:
            dict: Dictionary of item properties
        """
        try:                
            # Find the item in the actual project
            project = reapy.Project()
            track = project.tracks[track_index]
            
            # Use shared utility to find the item
            item = get_item_by_id_or_index(track, item_id)
            if item is None:
                return {}
            
            # Use shared utility to get properties
            return get_item_properties(item)
            
        except Exception as e:
            self.logger.error(f"Failed to get item properties: {e}")
            return {}
            
    def set_item_position(self, track_index, item_id, position):
        """
        Set the position of a media item.
        
        Args:
            track_index (int): Index of the track containing the item
            item_id (int or str): ID of the item
            position (float): New position in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:            
            # Update the position in the actual project
            project = reapy.Project()
            track = project.tracks[track_index]
            
            # Use shared utility to find the item
            item = get_item_by_id_or_index(track, item_id)
            if item is None:
                return False
            
            # Set the position
            item.position = position
            self.logger.info(f"Set item position to {position}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set item position: {e}")
            return False
            
    def set_item_length(self, track_index, item_id, length):
        """
        Set the length of a media item.
        
        Args:
            track_index (int): Index of the track containing the item
            item_id (int or str): ID of the item
            length (float): New length in seconds
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:            
            # Update the length in the actual project
            project = reapy.Project()
            track = project.tracks[track_index]
            
            # Use shared utility to find the item
            item = get_item_by_id_or_index(track, item_id)
            if item is None:
                return False
            
            # Set the length
            item.length = length
            self.logger.info(f"Set item length to {length}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to set item length: {e}")
            return False
            
    def duplicate_item(self, track_index, item_id, new_position=None):
        """
        Duplicate a media item.
        
        Args:
            track_index (int): Index of the track containing the item
            item_id (int or str): ID of the item to duplicate
            new_position (float, optional): If provided, the duplicated item will be placed at this position. Otherwise, it will be placed at the original position.
        
        Returns:
            int or str: ID of the duplicated item
        """
        try:            
            # Duplicate in the actual project
            project = reapy.Project()
            track = project.tracks[track_index]
            
            # Use shared utility to find the item
            item = get_item_by_id_or_index(track, item_id)
            if item is None:
                return -1
            
            # Store original item properties
            original_position = item.position
            original_length = item.length
            
            # Determine the position for the duplicated item
            if new_position is not None:
                position = float(new_position)
            else:
                # If no new position specified, place it right after the original item
                position = original_position + original_length
            
            # Check if it's a MIDI item
            is_midi = False
            if item.active_take and item.active_take.is_midi:
                is_midi = True
            
            # Use REAPER's built-in duplication for both MIDI and audio items
            try:
                # Select only the original item
                project.select_all_items(False)
                RPR.SetMediaItemSelected(item.id, True)
                
                # Duplicate the item using REAPER's duplicate command
                RPR.Main_OnCommand(41295, 0)  # Item: Duplicate items
                
                # Small delay to ensure duplication is complete
                time.sleep(0.05)
                
                # Find the duplicated item - REAPER places it right after the original
                duplicated_item = None
                
                # Get all items and look for one that wasn't there before
                current_items = list(track.items)
                
                # Look for the newest item that has the same length as the original
                for track_item in current_items:
                    # Skip the original item
                    if track_item.id == item.id:
                        continue
                    
                    # Look for an item with matching length that's likely the duplicate
                    if abs(track_item.length - original_length) < 0.001:
                        # Check if it's positioned after the original (REAPER's default behavior)
                        if track_item.position >= original_position:
                            duplicated_item = track_item
                            break
                
                # If we still haven't found it, try a different approach
                if duplicated_item is None:
                    # Look for any item that's not the original and has the same length
                    for track_item in current_items:
                        if (track_item.id != item.id and 
                            abs(track_item.length - original_length) < 0.001):
                            duplicated_item = track_item
                            break
                
                if duplicated_item:
                    # Move the duplicated item to the desired position
                    duplicated_item.position = position
                    new_item = duplicated_item
                    
                    if is_midi:
                        self.logger.info(f"Successfully duplicated MIDI item using REAPER duplicate command, moved to position {position}")
                    else:
                        self.logger.info(f"Successfully duplicated audio item using REAPER duplicate command, moved to position {position}")
                else:
                    self.logger.warning("Could not find duplicated item after REAPER duplicate command")
                    return -1
                    
            except Exception as e:
                self.logger.error(f"Failed to duplicate item using REAPER command: {e}")
                return -1
            
            # Get the index of the new item
            for i, track_item in enumerate(track.items):
                if track_item.id == new_item.id:
                    self.logger.info(f"Created duplicated item at index {i}, ID: {new_item.id}")
                    return i
            
            self.logger.warning("Couldn't find the duplicated item")
            return -1
            
        except Exception as e:
            self.logger.error(f"Failed to duplicate item: {e}")
            return -1
            
    def delete_item(self, track_index, item_id):
        """
        Delete a media item.
        
        Args:
            track_index (int): Index of the track containing the item
            item_id (int or str): ID of the item to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Delete from the actual project
            project = reapy.Project()
            track = project.tracks[track_index]
            
            # Use shared utility to find the item
            item = get_item_by_id_or_index(track, item_id)
            if item is None:
                return False
            
            # Use shared utility to delete the item
            return delete_item(item)
            
        except Exception as e:
            self.logger.error(f"Failed to delete item: {e}")
            return False
            
    def get_items_in_time_range(self, track_index, start_time, end_time):
        """
        Get all media items within a specific time range on a track.
        
        Args:
            track_index (int): Index of the track
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            
        Returns:
            list: A list of dictionaries containing media item data
        """
        try:
            project = reapy.Project()
            track = project.tracks[track_index]
            
            items = []
            for item in track.items:
                # Check if item overlaps with time range
                if item.position + item.length >= start_time and item.position <= end_time:
                    # Use shared utility to get properties
                    properties = get_item_properties(item)
                    items.append(properties)
            
            return items
            
        except Exception as e:
            self.logger.error(f"Failed to get items in time range: {e}")
            return []
