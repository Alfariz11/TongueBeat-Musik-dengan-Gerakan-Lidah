#!/usr/bin/env python3
"""
Gestune - Hand Gesture Music Controller
Main application entry point with PyQt6 UI

This application uses hand gestures to control music:
- Left hand: Controls arpeggiator (pitch and octave)
- Right hand: Controls drums (each finger triggers different drum)
"""

import sys
import cv2
from PyQt6.QtWidgets import QApplication

from gestune_ui import GestuneUI
from gesture_processor import GestureProcessor


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    
    # Create main window
    window = GestuneUI()
    
    # Initialize gesture processor
    processor = GestureProcessor()
    
    # Connect signals from processor to UI
    processor.frame_processed.connect(window.update_camera_feed)
    processor.hand_detected.connect(window.update_hand_status)
    processor.fps_updated.connect(window.update_fps)
    processor.drum_hit.connect(window.trigger_drum_indicator)
    
    # Connect UI controls to processor
    window.bpm_changed.connect(processor.set_bpm)
    window.pattern_changed.connect(processor.change_pattern)
    
    # Setup cleanup on window close
    def cleanup():
        processor.stop()
        processor.wait()
        cv2.destroyAllWindows()
    
    window.destroyed.connect(cleanup)
    
    # Start processing
    processor.start()
    
    # Show window
    window.show()
    
    # Start event loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
