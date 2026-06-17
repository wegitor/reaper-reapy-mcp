import logging
import os
import time

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.reaper_controller import ReaperController

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)  # Set to DEBUG for detailed output

    try:
        # Create Reaper controller
        controller = ReaperController(debug=True)

        # Test MIDI and item operations
        logger.info("Testing MIDI and item operations...")
        
        # Create a MIDI track
        midi_track_index = controller.create_track("MIDI Track")
        logger.info(f"Created MIDI track {midi_track_index}")
        
        # Create a MIDI item with enhanced debugging
        logger.info("Creating MIDI item...")
        midi_item_id = controller.create_midi_item(midi_track_index, 0.0, 4.0)
        logger.info(f"Created MIDI item with ID: {midi_item_id}")
        
        # Small delay to ensure item is fully created
        time.sleep(0.5)
        
        # Add MIDI notes - C major chord
        logger.info(f"Adding MIDI notes to item ID: {midi_item_id}")
        
        # Try adding a single note first with more verbose logging
        note_result = controller.add_midi_note(midi_track_index, midi_item_id, 60, 0.0, 1.0, 100)  # C
        logger.info(f"Result of adding C note: {note_result}")
        
        # Continue only if first note was added successfully
        if note_result:
            controller.add_midi_note(midi_track_index, midi_item_id, 64, 0.0, 1.0, 100)  # E
            controller.add_midi_note(midi_track_index, midi_item_id, 67, 0.0, 1.0, 100)  # G
            logger.info("Added MIDI notes (C major chord)")
        else:
            logger.error("Failed to add first note, not attempting remaining notes")
        
        # Create another MIDI item and duplicate it
        logger.info("Creating second MIDI item...")
        midi_item2_id = controller.create_midi_item(midi_track_index, 4.0, 2.0)
        logger.info(f"Created second MIDI item with ID: {midi_item2_id}")
        
        # Small delay to ensure item is fully created
        time.sleep(0.5)
        
        # Add a MIDI note with verification
        logger.info(f"Adding note to second MIDI item ID: {midi_item2_id}")
        note2_result = controller.add_midi_note(midi_track_index, midi_item2_id, 72, 0.0, 0.5, 90)  # C an octave up
        logger.info(f"Result of adding note to second item: {note2_result}")
        
        # Keep Reaper open for inspection
        logger.info("Test completed. Please check Reaper to verify the MIDI items were created correctly.")

    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()