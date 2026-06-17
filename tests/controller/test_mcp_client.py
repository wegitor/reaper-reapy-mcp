import logging
import os
import sys

# Add the parent directory to sys.path to import the reaper_controller module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reaper_controller import ReaperController

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    try:
        # Create Reaper controller
        controller = ReaperController(debug=True)
        
        # Test basic operations
        logger.info("Testing basic operations...")
        
        # Create a track
        track_index = controller.create_track("Test Track")
        logger.info(f"Created track {track_index}")
        
        # Set track color
        controller.set_track_color(track_index, "#FF0000")
        logger.info(f"Set track {track_index} color to red")
        
        # Add an FX
        fx_index = controller.add_fx(track_index, "ReaEQ")
        logger.info(f"Added ReaEQ to track {track_index} at index {fx_index}")
        
        # Set FX parameter
        controller.set_fx_param(track_index, fx_index, "Gain", 6.0)
        logger.info(f"Set ReaEQ gain to 6.0")
        
        # Get FX parameter list
        param_list = controller.get_fx_param_list(track_index, fx_index)
        logger.info(f"Got FX parameter list with {len(param_list)} parameters")
        for param in param_list[:3]:  # Log first few parameters only
            logger.info(f"  Parameter: {param['name']} = {param['value']}")
            
        # Get FX list on track
        fx_list = controller.get_fx_list(track_index)
        logger.info(f"Track {track_index} has {len(fx_list)} FX plugins")
        for fx in fx_list:
            logger.info(f"  FX: {fx['name']} (enabled: {fx['enabled']})")
            
        # Get available FX list
        available_fx = controller.get_available_fx_list()
        total_fx = len(available_fx)
        logger.info(f"Found {total_fx} available FX plugins in Reaper")
        # Log a few example plugins
        if total_fx > 0:
            sample_size = min(5, total_fx)
            logger.info(f"Sample of available plugins: {', '.join(available_fx[:sample_size])}")
        
        # Set project tempo
        controller.set_tempo(120.0)
        logger.info("Set tempo to 120 BPM")
        
        # Create a region
        region_index = controller.create_region(0.0, 10.0, "Test Region")
        logger.info(f"Created region {region_index}")
        
        # Create a marker
        marker_index = controller.create_marker(5.0, "Test Marker")
        logger.info(f"Created marker {marker_index}")
        
        # Control master track
        controller.set_master_volume(0.8)
        controller.set_master_pan(-0.5)
        logger.info("Set master volume to 0.8 and pan to -0.5")
        
        # Test MIDI and item operations
        logger.info("Testing MIDI and item operations...")
        
        # Create a MIDI track
        midi_track_index = controller.create_track("MIDI Track")
        logger.info(f"Created MIDI track {midi_track_index}")
        
        # Create a MIDI item
        midi_item_id = controller.create_midi_item(midi_track_index, 0.0, 4.0)
        logger.info(f"Created MIDI item {midi_item_id}")
        
        # Add MIDI notes - C major chord
        controller.add_midi_note(midi_track_index, midi_item_id, 60, 0.0, 1.0, 100)  # C
        controller.add_midi_note(midi_track_index, midi_item_id, 64, 0.0, 1.0, 100)  # E
        controller.add_midi_note(midi_track_index, midi_item_id, 67, 0.0, 1.0, 100)  # G
        logger.info("Added MIDI notes (C major chord)")
        
        # Create another MIDI item and duplicate it
        midi_item2_id = controller.create_midi_item(midi_track_index, 4.0, 2.0)
        logger.info(f"Created second MIDI item {midi_item2_id}")
        
        # Add a MIDI note
        controller.add_midi_note(midi_track_index, midi_item2_id, 72, 0.0, 0.5, 90)  # C an octave up
        logger.info("Added MIDI note to second item")
        
        # Duplicate the MIDI item
        duplicated_item_id = controller.duplicate_item(midi_track_index, midi_item2_id)
        logger.info(f"Duplicated MIDI item, new ID: {duplicated_item_id}")
        
        # Create an audio track
        audio_track_index = controller.create_track("Audio Track")
        logger.info(f"Created audio track {audio_track_index}")
        
        # Try to insert an audio item (provide a path to an existing audio file)
        # Note: This will only work if the audio file exists
        audio_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "test_audio.wav")
        if os.path.exists(audio_file_path):
            audio_item_id = controller.insert_audio_item(audio_track_index, audio_file_path, 0.0)
            logger.info(f"Inserted audio item {audio_item_id}")
            
            # Get item properties
            properties = controller.get_item_properties(audio_track_index, audio_item_id)
            logger.info(f"Audio item properties: {properties}")
            
            # Move the item
            controller.set_item_position(audio_track_index, audio_item_id, 2.0)
            logger.info("Moved audio item to position 2.0")
        else:
            logger.warning(f"Audio file not found: {audio_file_path}. Skipping audio item test.")
        
        # Get items in time range
        items = controller.get_items_in_time_range(midi_track_index, 0.0, 10.0)
        logger.info(f"Found {len(items)} items in time range 0-10 seconds on MIDI track")
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}")
        raise

if __name__ == "__main__":
    main()