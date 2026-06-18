import reapy
from reapy import reascript_api as RPR
import logging
import time
from typing import Optional
from reaper_reapy_mcp.utils.item_utils import get_item_properties

class BaseController:
    """Base controller for interacting with Reaper using reapy."""
    
    def __init__(self, debug: bool = False):
        """
        Initialize the Reaper controller.
        
        Args:
            debug (bool): Enable debug logging
        """
        self.logger = logging.getLogger(__name__)
        self.debug = debug

        # Initialize test data storage for storing MIDI notes during testing
        self._test_midi_items = {}
        
        # Connect to Reaper
        try:
            reapy.connect()
            self.logger.info("Connected to Reaper")
        except Exception as e:
            self.logger.error(f"Failed to connect to Reaper: {e}")
            raise

    def verify_connection(self) -> bool:
        """Verify connection to Reaper."""
        try:
            project = reapy.Project()
            print("Connected to project:", project.name)
            # TODO correct checker
            # return reapy.is_connected()
            return True
        except Exception as e:
            self.logger.error(f"Connection verification failed: {e}")
            return False

    def _validate_track_index(self, track_index: int) -> bool:
        """
        Validate that a track index is within valid range.
        
        Args:
            track_index (int): The track index to validate
            
        Returns:
            bool: True if valid, False if invalid
        """
        try:
            track_index = int(track_index)
            if track_index < 0:
                return False
                
            project = reapy.Project()
            num_tracks = len(project.tracks)
            return track_index < num_tracks
        except Exception:
            return False
            
    def _get_track(self, track_index: int) -> Optional[reapy.Track]:
        """
        Get a track by index with validation.
        
        Args:
            track_index (int): The track index to get
            
        Returns:
            Optional[reapy.Track]: The track if valid, None if invalid
        """
        if not self._validate_track_index(track_index):
            return None
            
        try:
            return reapy.Project().tracks[track_index]
        except Exception:
            return None
    
    def get_selected_items(self):
        """
        Get all selected media items in the project.

        Returns:
            list: A list of dictionaries containing item data with keys:
                - track_index: Index of the track containing the item
                - item_index: Index of the item in its track
                - position: Start time in seconds
                - length: Length in seconds
                - is_midi: Whether the item is a MIDI item
                - name: Item name if available
        """
        try:
            project = reapy.Project()
            selected_items = []

            # Iterate through all tracks to find selected items
            for track_index, track in enumerate(project.tracks):
                for item_index, item in enumerate(track.items):
                    # Use ReaScript API directly for selection check
                    if RPR.IsMediaItemSelected(item.id):
                        # Get item properties
                        properties = get_item_properties(item)
                        # Add track and item index information
                        properties.update({
                            'track_index': track_index,
                            'item_index': item_index,
                            'is_midi': bool(item.active_take and item.active_take.is_midi)
                        })
                        selected_items.append(properties)

            self.logger.info(f"Found {len(selected_items)} selected items")
            return selected_items

        except Exception as e:
            self.logger.error(f"Failed to get selected items: {e}")
            return []
