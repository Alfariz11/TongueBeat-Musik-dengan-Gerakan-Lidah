"""
TongueBeat - Play Drums with Your Tongue!
Main application that combines tongue detection and drum control
"""

import cv2
import numpy as np
import time
from tongue_detector import TongueDetector
from drum_controller import DrumController


class TongueBeat:
    """Main application class for TongueBeat"""

    def __init__(self, camera_index=None):
        """
        Initialize TongueBeat application

        Args:
            camera_index: Index of camera to use (None = auto-detect and prompt)
        """
        self.cap = None
        self.tongue_detector = None
        self.drum_controller = None
        self.camera_index = camera_index

        self.window_name = "TongueBeat - Drum with Your Tongue!"
        self.running = False

        # UI settings
        self.camera_width = 640
        self.camera_height = 480
        self.ui_width = 400
        self.total_width = self.camera_width + self.ui_width

        # Control mode: 'direction' or 'position'
        self.control_mode = 'direction'

        # Confidence mode for direction detection
        self.use_confidence = True

        # FPS tracking
        self.fps = 0
        self.frame_count = 0
        self.start_time = time.time()

    @staticmethod
    def detect_available_cameras(max_test=10):
        """
        Detect all available cameras on the system

        Args:
            max_test: Maximum number of camera indices to test

        Returns:
            List of tuples (index, name, resolution)
        """
        print("Detecting available cameras...")
        available_cameras = []

        for index in range(max_test):
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                # Get camera properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

                # Try to read a frame to verify camera works
                ret, frame = cap.read()
                if ret and frame is not None:
                    # Get camera name (if available)
                    backend = cap.getBackendName()
                    name = f"Camera {index} ({backend})"

                    available_cameras.append((index, name, (width, height)))
                    print(f"  Found: {name} - {width}x{height}")

                cap.release()

        return available_cameras

    @staticmethod
    def preview_camera(camera_index, duration=3):
        """
        Show a preview of the selected camera

        Args:
            camera_index: Index of camera to preview
            duration: Preview duration in seconds

        Returns:
            True if preview successful, False otherwise
        """
        cap = cv2.VideoCapture(camera_index)
        if not cap.isOpened():
            print(f"Error: Could not open camera {camera_index}")
            return False

        print(f"\nPreviewing Camera {camera_index} for {duration} seconds...")
        print("Press 'Q' to skip preview")

        preview_window = f"Camera {camera_index} Preview"
        start_time = time.time()

        while (time.time() - start_time) < duration:
            ret, frame = cap.read()
            if not ret:
                break

            # Flip for mirror effect
            frame = cv2.flip(frame, 1)

            # Add text overlay
            remaining = int(duration - (time.time() - start_time))
            cv2.putText(frame, f"Preview: {remaining}s remaining (Press Q to skip)",
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                       (0, 255, 0), 2)

            cv2.imshow(preview_window, frame)

            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q') or cv2.waitKey(1) & 0xFF == ord('Q'):
                break

        cap.release()
        cv2.destroyWindow(preview_window)
        return True

    def select_camera(self):
        """
        Interactive camera selection menu

        Returns:
            Selected camera index, or None if cancelled
        """
        cameras = self.detect_available_cameras()

        if not cameras:
            print("\nError: No cameras detected!")
            print("Please check your camera connections and try again.")
            return None

        if len(cameras) == 1:
            print(f"\nOnly one camera found: {cameras[0][1]}")
            response = input("Use this camera? (Y/n): ").strip().lower()
            if response == '' or response == 'y':
                return cameras[0][0]
            else:
                return None

        # Multiple cameras - show selection menu
        print("\n" + "="*60)
        print("CAMERA SELECTION")
        print("="*60)
        print(f"\nFound {len(cameras)} camera(s):\n")

        for i, (index, name, resolution) in enumerate(cameras, 1):
            print(f"  [{i}] {name}")
            print(f"      Resolution: {resolution[0]}x{resolution[1]}")
            print()

        print("  [P] Preview cameras before selecting")
        print("  [Q] Quit")
        print("="*60)

        while True:
            choice = input("\nSelect camera (number), P to preview, or Q to quit: ").strip().upper()

            if choice == 'Q':
                return None
            elif choice == 'P':
                # Preview mode
                print("\n" + "="*60)
                print("CAMERA PREVIEW MODE")
                print("="*60)
                for i, (index, name, resolution) in enumerate(cameras, 1):
                    print(f"\n[{i}] {name}")
                    response = input("Preview this camera? (Y/n/q to quit preview): ").strip().lower()
                    if response == 'q':
                        break
                    elif response == '' or response == 'y':
                        self.preview_camera(index, duration=3)
                print("\nReturning to camera selection...")
            else:
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(cameras):
                        selected_index = cameras[choice_num - 1][0]
                        selected_name = cameras[choice_num - 1][1]
                        print(f"\nSelected: {selected_name}")
                        return selected_index
                    else:
                        print(f"Invalid choice. Please enter a number between 1 and {len(cameras)}")
                except ValueError:
                    print("Invalid input. Please enter a number, P, or Q")

    def initialize(self):
        """Initialize camera, detector, and drum controller"""
        print("\nInitializing TongueBeat...")

        # Select camera if not specified
        if self.camera_index is None:
            self.camera_index = self.select_camera()
            if self.camera_index is None:
                print("No camera selected. Exiting...")
                return False

        # Initialize camera
        print(f"\nOpening camera {self.camera_index}...")
        self.cap = cv2.VideoCapture(self.camera_index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_height)

        if not self.cap.isOpened():
            print(f"Error: Could not open camera {self.camera_index}")
            return False

        # Initialize tongue detector
        self.tongue_detector = TongueDetector(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

        # Initialize drum controller
        self.drum_controller = DrumController(
            audio_dir="audios",
            image_dir="images"
        )

        # Read a test frame to get actual camera resolution
        ret, test_frame = self.cap.read()
        if ret:
            self.actual_height = test_frame.shape[0]
            self.actual_width = test_frame.shape[1]
            print(f"Actual camera resolution: {self.actual_width}x{self.actual_height}")
        else:
            self.actual_height = self.camera_height
            self.actual_width = self.camera_width

        # Setup drum pads for UI area using actual frame height
        self.drum_controller.setup_drum_pads(
            screen_width=self.ui_width,
            screen_height=self.actual_height
        )

        print("Initialization complete!")
        return True

    def create_ui_panel(self, frame_height=None):
        """
        Create UI panel for drum pads

        Args:
            frame_height: Height of the frame to match (defaults to self.camera_height)

        Returns:
            ui_panel: numpy array with drum pad visuals
        """
        # Use actual frame height if provided, otherwise use expected camera height
        height = frame_height if frame_height is not None else self.camera_height

        # Create blank panel
        ui_panel = np.ones((height, self.ui_width, 3), dtype=np.uint8) * 40

        # Draw drum pads
        for pad in self.drum_controller.drum_pads:
            x, y = pad.position
            w, h = pad.size

            # Draw pad image if available
            if pad.image is not None:
                try:
                    ui_panel[y:y+h, x:x+w] = pad.image
                except:
                    pass  # Skip if dimensions don't match

            # Draw border (thicker if active)
            border_color = (0, 255, 0) if pad.is_active else (100, 100, 100)
            border_thickness = 4 if pad.is_active else 2
            cv2.rectangle(ui_panel, (x, y), (x+w, y+h), border_color, border_thickness)

            # Draw pad name
            text_y = y + h - 10
            cv2.putText(ui_panel, pad.name.upper(),
                       (x + 10, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                       (255, 255, 255), 2)

        return ui_panel

    def draw_info_overlay(self, frame, direction, tongue_pos, debug_info=None):
        """
        Draw information overlay on camera frame

        Args:
            frame: Camera frame
            direction: Current tongue direction
            tongue_pos: Tongue tip position tuple or None
            debug_info: Optional dict with debug information (dx, dy, etc.)

        Returns:
            frame: Frame with overlay
        """
        # Semi-transparent overlay at top
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (frame.shape[1], 100), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        # Draw title
        cv2.putText(frame, "TongueBeat",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                   (0, 255, 255), 2)

        # Draw FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}",
                   (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                   (255, 255, 255), 1)

        # Draw control mode
        mode_text = f"Mode: {self.control_mode.upper()}"
        cv2.putText(frame, mode_text,
                   (150, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                   (255, 255, 255), 1)

        # Draw confidence mode and blob detection status
        confidence_text = f"Confidence: {'ON' if self.use_confidence else 'OFF'}"
        confidence_color = (0, 255, 0) if self.use_confidence else (128, 128, 128)
        cv2.putText(frame, confidence_text,
                   (350, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                   confidence_color, 1)

        # Draw blob detection status
        blob_text = f"Blob: {'ON' if self.tongue_detector and self.tongue_detector.use_blob_detection else 'OFF'}"
        blob_color = (0, 255, 0) if self.tongue_detector and self.tongue_detector.use_blob_detection else (128, 128, 128)
        cv2.putText(frame, blob_text,
                   (600, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                   blob_color, 1)

        # Draw direction indicator
        if direction != 'none':
            direction_color = (0, 255, 0) if direction != 'none' else (128, 128, 128)
            cv2.putText(frame, f"Direction: {direction.upper()}",
                       (350, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                       direction_color, 2)

        # Draw debug info
        if debug_info:
            debug_text = f"dx: {debug_info.get('dx', 0):.1f} dy: {debug_info.get('dy', 0):.1f}"
            cv2.putText(frame, debug_text,
                       (10, 85), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                       (255, 255, 0), 1)

        # Draw instructions at bottom
        instructions = [
            "Move tongue: LEFT/RIGHT/UP/DOWN",
            "M: mode | C: confidence | B: blob | D: debug | Q: quit"
        ]

        y_pos = frame.shape[0] - 40
        for instruction in instructions:
            cv2.putText(frame, instruction,
                       (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                       (255, 255, 255), 1)
            y_pos += 20

        return frame

    def process_frame(self, frame):
        """
        Process single frame for tongue detection and drum control

        Args:
            frame: Input camera frame

        Returns:
            frame: Processed frame with visualizations
            direction: Detected tongue direction
            tongue_pos: Tongue position tuple or None
            debug_info: Dictionary with debug information
        """
        # Detect face landmarks
        landmarks = self.tongue_detector.detect_face_landmarks(frame)

        direction = 'none'
        tongue_pos = None
        debug_info = {'dx': 0, 'dy': 0}

        if landmarks:
            # Detect tongue direction with confidence setting (pass frame for blob detection)
            direction = self.tongue_detector.get_tongue_direction(
                landmarks, frame.shape, use_confidence=self.use_confidence, frame=frame
            )

            # Get tongue position (pass frame for blob detection)
            tongue_pos, is_out = self.tongue_detector.detect_tongue_tip(landmarks, frame.shape, frame)

            # Calculate debug info (dx, dy from mouth center)
            if tongue_pos:
                h, w = frame.shape[:2]
                upper_lip = landmarks.landmark[self.tongue_detector.upper_lip_center]
                lower_lip = landmarks.landmark[self.tongue_detector.lower_lip_center]
                left_mouth = landmarks.landmark[self.tongue_detector.mouth_left]
                right_mouth = landmarks.landmark[self.tongue_detector.mouth_right]

                mouth_center_x = int(((left_mouth.x + right_mouth.x) / 2) * w)
                mouth_center_y = int(((upper_lip.y + lower_lip.y) / 2) * h)

                debug_info['dx'] = tongue_pos[0] - mouth_center_x
                debug_info['dy'] = tongue_pos[1] - mouth_center_y

            # Draw landmarks for visualization
            frame = self.tongue_detector.draw_landmarks(frame, landmarks)

            # Trigger drum based on control mode
            if is_out:
                if self.control_mode == 'direction':
                    # Trigger by direction
                    triggered_pad = self.drum_controller.trigger_by_direction(direction)
                elif self.control_mode == 'position' and tongue_pos:
                    # Map tongue position to UI panel coordinates
                    # (This mode requires tongue to point at drum pads)
                    ui_x = int((tongue_pos[0] / frame.shape[1]) * self.ui_width)
                    ui_y = tongue_pos[1]
                    triggered_pad = self.drum_controller.trigger_by_position(ui_x, ui_y)

        return frame, direction, tongue_pos, debug_info

    def run(self):
        """Main application loop"""
        if not self.initialize():
            return

        print("\n" + "="*50)
        print("TongueBeat is now running!")
        print("="*50)
        print(f"\nUsing: Camera {self.camera_index}")
        print(f"Resolution: {self.actual_width}x{self.actual_height}")
        print("\nControls:")
        print("  - Move your tongue LEFT/RIGHT/UP/DOWN to play drums")
        print("  - Press 'M' to switch control modes")
        print("  - Press 'C' to toggle confidence mode (reduces false triggers)")
        print("  - Press 'B' to toggle blob detection (more accurate)")
        print("  - Press 'D' to toggle debug window (see tongue segmentation)")
        print("  - Press 'Q' to quit")
        print("\nDirection Mapping:")
        print("  - UP: Kick drum")
        print("  - LEFT: Hi-hat")
        print("  - RIGHT: Crash cymbal")
        print("  - CENTER/DOWN: Snare")
        print("="*50 + "\n")

        self.running = True

        try:
            while self.running:
                # Read frame
                ret, frame = self.cap.read()
                if not ret:
                    print("Error: Failed to capture frame")
                    break

                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)

                # Process frame
                frame, direction, tongue_pos, debug_info = self.process_frame(frame)

                # Draw info overlay
                frame = self.draw_info_overlay(frame, direction, tongue_pos, debug_info)

                # Create UI panel with matching frame height
                ui_panel = self.create_ui_panel(frame_height=frame.shape[0])

                # Combine camera and UI
                combined = np.hstack([frame, ui_panel])

                # Calculate FPS
                self.frame_count += 1
                if self.frame_count % 10 == 0:
                    elapsed = time.time() - self.start_time
                    self.fps = self.frame_count / elapsed

                # Display
                cv2.imshow(self.window_name, combined)

                # Show debug window if enabled
                if self.tongue_detector.show_debug_window:
                    if self.tongue_detector.debug_mouth_roi is not None:
                        debug_roi = self.tongue_detector.debug_mouth_roi
                        debug_processed = self.tongue_detector.debug_processed

                        # Resize for better visibility
                        scale = 3
                        debug_roi_large = cv2.resize(debug_roi, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)
                        debug_processed_large = cv2.resize(debug_processed, None, fx=scale, fy=scale, interpolation=cv2.INTER_NEAREST)

                        # Stack horizontally
                        debug_view = np.hstack([debug_roi_large, debug_processed_large])

                        # Add labels
                        cv2.putText(debug_view, "Original ROI", (10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                        cv2.putText(debug_view, "Tongue Segmented", (debug_roi_large.shape[1] + 10, 30),
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

                        cv2.imshow("Tongue Detection Debug", debug_view)

                # Reset active pads after a short delay
                self.drum_controller.reset_all_active()

                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    print("\nQuitting TongueBeat...")
                    break
                elif key == ord('m') or key == ord('M'):
                    # Toggle control mode
                    self.control_mode = 'position' if self.control_mode == 'direction' else 'direction'
                    print(f"Control mode changed to: {self.control_mode}")
                elif key == ord('c') or key == ord('C'):
                    # Toggle confidence mode
                    self.use_confidence = not self.use_confidence
                    print(f"Confidence mode: {'ON' if self.use_confidence else 'OFF'}")
                elif key == ord('b') or key == ord('B'):
                    # Toggle blob detection
                    self.tongue_detector.use_blob_detection = not self.tongue_detector.use_blob_detection
                    mode_name = "Blob Detection" if self.tongue_detector.use_blob_detection else "Landmark-based"
                    print(f"Detection mode: {mode_name}")
                elif key == ord('d') or key == ord('D'):
                    # Toggle debug window
                    self.tongue_detector.show_debug_window = not self.tongue_detector.show_debug_window
                    if not self.tongue_detector.show_debug_window:
                        cv2.destroyWindow("Tongue Detection Debug")
                    print(f"Debug window: {'ON' if self.tongue_detector.show_debug_window else 'OFF'}")

        except KeyboardInterrupt:
            print("\nInterrupted by user")

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up resources...")

        if self.cap:
            self.cap.release()

        if self.tongue_detector:
            self.tongue_detector.release()

        if self.drum_controller:
            self.drum_controller.cleanup()

        cv2.destroyAllWindows()
        print("Goodbye!")


def main():
    """Entry point"""
    import sys

    # Check for command-line arguments
    camera_index = None
    if len(sys.argv) > 1:
        try:
            camera_index = int(sys.argv[1])
            print(f"Using camera index from command-line: {camera_index}")
        except ValueError:
            print(f"Invalid camera index: {sys.argv[1]}")
            print("Usage: python tonguebeat.py [camera_index]")
            return

    app = TongueBeat(camera_index=camera_index)
    app.run()


if __name__ == "__main__":
    main()
