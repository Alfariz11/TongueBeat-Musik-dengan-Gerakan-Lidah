#!/usr/bin/env python3
"""
Gestune - Hand Gesture Music Controller
Main application entry point with PyQt6 UI

This application uses hand gestures to control music:
- Left hand: Controls arpeggiator (pitch and volume via pinch)
- Right hand: Controls drums (each finger triggers different drum)

Features:
- Real-time hand tracking with MediaPipe
- Live audio synthesis
- Multiple drum patterns
- Adjustable BPM
- Professional UI with visualizations

Author: Gestune Team
Version: 2.0
"""

import sys
import signal
import cv2
import traceback
from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer, Qt

from gestune_ui import GestuneUI
from gesture_processor import GestureProcessor


class GestuneApplication:
    """
    Main application class that manages the Gestune music controller.
    
    Handles initialization, signal connections, and cleanup of all components.
    """
    
    def __init__(self):
        """Initialize the Gestune application."""
        self.app: Optional[QApplication] = None
        self.window: Optional[GestuneUI] = None
        self.processor: Optional[GestureProcessor] = None
        self.cleanup_done = False
        
    def initialize(self) -> bool:
        """
        Initialize all application components.
        
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Create Qt application
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Gestune")
            self.app.setOrganizationName("Gestune Team")
            
            # Set application style
            self.app.setStyle("Fusion")
            
            print("🎵 Gestune - Hand Gesture Music Controller")
            print("=" * 50)
            
            # Create main window
            print("📱 Creating main window...")
            self.window = GestuneUI()
            
            # Initialize gesture processor
            print("🎮 Initializing gesture processor...")
            self.processor = GestureProcessor()
            
            # Connect signals
            self._connect_signals()
            
            # Setup cleanup handlers
            self._setup_cleanup()
            
            print("✅ Application initialized successfully!")
            print("=" * 50)
            
            return True
            
        except Exception as e:
            print(f"❌ Initialization error: {e}")
            traceback.print_exc()
            return False
    
    def _connect_signals(self):
        """Connect all signals between processor and UI."""
        if not self.processor or not self.window:
            return
        
        # Processor -> UI signals
        self.processor.frame_processed.connect(
            self.window.update_camera_feed,
            Qt.ConnectionType.QueuedConnection
        )
        
        self.processor.hand_detected.connect(
            self.window.update_hand_status,
            Qt.ConnectionType.QueuedConnection
        )
        
        self.processor.fps_updated.connect(
            self.window.update_fps,
            Qt.ConnectionType.QueuedConnection
        )
        
        self.processor.drum_hit.connect(
            self._on_drum_hit,
            Qt.ConnectionType.QueuedConnection
        )
        
        self.processor.note_played.connect(
            self._on_note_played,
            Qt.ConnectionType.QueuedConnection
        )
        
        self.processor.pattern_changed.connect(
            self.window.update_pattern_display,
            Qt.ConnectionType.QueuedConnection
        )
        
        self.processor.detection_count_updated.connect(
            self.window.update_detection_count,
            Qt.ConnectionType.QueuedConnection
        )
        
        self.processor.error_occurred.connect(
            self._on_error,
            Qt.ConnectionType.QueuedConnection
        )
        
        # UI -> Processor signals
        self.window.bpm_changed.connect(
            self.processor.set_bpm,
            Qt.ConnectionType.QueuedConnection
        )

        self.processor.bpm_updated.connect(
            self.window.set_bpm,
            Qt.ConnectionType.QueuedConnection
        )

        
        self.window.pattern_changed.connect(
            self.processor.change_pattern,
            Qt.ConnectionType.QueuedConnection
        )
        
        print("✅ All signals connected")
    
    def _setup_cleanup(self):
        """Setup cleanup handlers for graceful shutdown."""
        if not self.window or not self.processor:
            return
        
        # Connect window close event
        self.window.destroyed.connect(self._cleanup)
        
        # Setup SIGINT handler (Ctrl+C)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Setup SIGTERM handler
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Create timer to allow Qt to process signals
        self.signal_timer = QTimer()
        self.signal_timer.timeout.connect(lambda: None)
        self.signal_timer.start(500)
        
        print("✅ Cleanup handlers registered")
    
    def _signal_handler(self, signum, frame):
        """
        Handle system signals for graceful shutdown.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        print(f"\n⚠️ Received signal {signum}, shutting down...")
        self._cleanup()
        sys.exit(0)
    
    def _on_drum_hit(self, drum_name: str, velocity: float):
        """
        Handle drum hit event.
        
        Args:
            drum_name: Name of the drum that was hit
            velocity: Hit velocity (0-1)
        """
        if self.window:
            self.window.trigger_drum_indicator(drum_name, velocity)
    
    def _on_note_played(self, note: int, volume: float):
        """
        Handle note played event.
        
        Args:
            note: MIDI note number
            volume: Note volume (0-1)
        """
        if self.window:
            self.window.update_arpeggiator_display(note, volume)
    
    def _on_error(self, error_message: str):
        """
        Handle error from gesture processor.
        
        Args:
            error_message: Error message to display
        """
        print(f"❌ Error: {error_message}")
        
        if self.window:
            QMessageBox.critical(
                self.window,
                "Gestune Error",
                f"An error occurred:\n\n{error_message}\n\nPlease check your camera connection.",
                QMessageBox.StandardButton.Ok
            )
    
    def _cleanup(self):
        """Perform cleanup of all resources."""
        if self.cleanup_done:
            return
        
        self.cleanup_done = True
        
        print("\n🧹 Starting cleanup...")
        
        try:
            # Stop signal timer
            if hasattr(self, 'signal_timer') and self.signal_timer:
                self.signal_timer.stop()
            
            # Stop gesture processor
            if self.processor:
                print("🛑 Stopping gesture processor...")
                self.processor.stop()
                self.processor.wait(5000)  # Wait up to 5 seconds
                
                if self.processor.isRunning():
                    print("⚠️ Processor still running, terminating...")
                    self.processor.terminate()
                    self.processor.wait(1000)
            
            # Close all OpenCV windows
            try:
                cv2.destroyAllWindows()
                print("✅ OpenCV windows closed")
            except:
                pass
            
            # Close main window
            if self.window:
                self.window.close()
            
            print("✅ Cleanup complete!")
            
        except Exception as e:
            print(f"⚠️ Error during cleanup: {e}")
            traceback.print_exc()
    
    def run(self) -> int:
        """
        Run the application.
        
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        if not self.app or not self.window or not self.processor:
            print("❌ Application not properly initialized")
            return 1
        
        try:
            # Start gesture processor
            print("🚀 Starting gesture processor...")
            self.processor.start()
            
            # Show main window
            print("🖼️ Showing main window...")
            self.window.show()
            
            # Display usage instructions
            self._show_welcome_message()
            
            # Start Qt event loop
            print("▶️ Application running. Press Ctrl+C or close window to exit.")
            return self.app.exec()
            
        except Exception as e:
            print(f"❌ Runtime error: {e}")
            traceback.print_exc()
            return 1
        
        finally:
            self._cleanup()
    
    def _show_welcome_message(self):
        """Show welcome message with usage instructions."""
        if not self.window:
            return
        
        # Set initial status message
        self.window.statusBar().showMessage(
            "👋 Welcome to Gestune! Position your hands in their respective zones to start playing.",
            5000
        )
        
        # Show welcome dialog
        QTimer.singleShot(500, self._show_welcome_dialog)
    
    def _show_welcome_dialog(self):
        """Show welcome dialog with instructions."""
        if not self.window:
            return
        
        welcome_text = """
<h2>🎵 Welcome to Gestune!</h2>

<p><b>How to use:</b></p>

<p><b>👈 Left Hand - Arpeggiator:</b></p>
<ul>
    <li>Move hand up/down to change pitch</li>
    <li>Pinch thumb and index to control volume</li>
    <li>Stay in the blue zone on the left</li>
</ul>

<p><b>👉 Right Hand - Drums:</b></p>
<ul>
    <li>Extend fingers to activate drums:</li>
    <ul>
        <li>👍 Thumb = Kick</li>
        <li>☝️ Index = Snare</li>
        <li>🖕 Middle = Hi-hat</li>
        <li>💍 Ring = Tom</li>
        <li>🤙 Pinky = Crash</li>
    </ul>
    <li>Make a fist to change patterns</li>
    <li>Stay in the pink zone on the right</li>
</ul>

<p><b>🎛️ Controls:</b></p>
<ul>
    <li>Use the BPM slider to adjust tempo</li>
    <li>Click pattern buttons to switch drum patterns</li>
</ul>

<p><i>Tip: Keep your hands visible and in the colored zones for best results!</i></p>
        """
        
        msg_box = QMessageBox(self.window)
        msg_box.setWindowTitle("Gestune - Quick Start Guide")
        msg_box.setTextFormat(Qt.TextFormat.RichText)
        msg_box.setText(welcome_text)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.exec()


def check_dependencies() -> bool:
    """
    Check if all required dependencies are available.
    
    Returns:
        True if all dependencies available, False otherwise
    """
    missing_deps = []
    
    # Check required modules
    required_modules = [
        ('cv2', 'opencv-python'),
        ('mediapipe', 'mediapipe'),
        ('pygame', 'pygame'),
        ('numpy', 'numpy'),
        ('PyQt6', 'PyQt6')
    ]
    
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
        except ImportError:
            missing_deps.append(package_name)
    
    if missing_deps:
        print("❌ Missing required dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nInstall with: pip install " + " ".join(missing_deps))
        return False
    
    return True


def check_camera() -> bool:
    """
    Check if camera is available.
    
    Returns:
        True if camera available, False otherwise
    """
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("⚠️ Warning: Camera not accessible")
            return False
        cap.release()
        return True
    except:
        print("⚠️ Warning: Cannot check camera availability")
        return False


def print_system_info():
    """Print system information for debugging."""
    import platform
    
    print("\n📊 System Information:")
    print(f"  Python: {sys.version.split()[0]}")
    print(f"  Platform: {platform.system()} {platform.release()}")
    
    try:
        import cv2
        print(f"  OpenCV: {cv2.__version__}")
    except:
        pass
    
    try:
        import mediapipe
        print(f"  MediaPipe: {mediapipe.__version__}")
    except:
        pass
    
    try:
        import pygame
        print(f"  Pygame: {pygame.version.ver}")
    except:
        pass
    
    try:
        from PyQt6.QtCore import PYQT_VERSION_STR
        print(f"  PyQt6: {PYQT_VERSION_STR}")
    except:
        pass
    
    print()


def main():
    """Main application entry point with error handling."""
    try:
        # Print banner
        print("\n" + "=" * 50)
        print("🎵 GESTUNE - Hand Gesture Music Controller")
        print("=" * 50)
        
        # Check dependencies
        print("\n🔍 Checking dependencies...")
        if not check_dependencies():
            return 1
        print("✅ All dependencies available")
        
        # Check camera
        print("\n📷 Checking camera...")
        if not check_camera():
            print("⚠️ Camera check failed - you may experience issues")
        else:
            print("✅ Camera available")
        
        # Print system info
        print_system_info()
        
        # Create and initialize application
        gestune = GestuneApplication()
        
        if not gestune.initialize():
            print("❌ Failed to initialize application")
            return 1
        
        # Run application
        exit_code = gestune.run()
        
        print(f"\n👋 Gestune closed with exit code {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        return 0
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())