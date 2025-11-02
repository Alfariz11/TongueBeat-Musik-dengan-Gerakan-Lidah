"""
Hand-Controlled Music Generator
Main application that brings together hand tracking, arpeggiator, drums, and visualization

Controls:
- Hand #1 (Left): Controls arpeggiator
  - Raise hand higher = Higher pitch
  - Pinch (thumb + index) = Control volume
- Hand #2 (Right): Controls drums
  - Different finger combinations = Different drum patterns

Press 'Q' to quit
"""
import cv2
import time
import numpy as np
from hand_tracker import HandTracker
from arpeggiator import Arpeggiator
from drum_machine import DrumMachine
from visualizer import Visualizer


class MusicController:
    def __init__(self):
<<<<<<< HEAD
        print("\n[1/5] Initializing Hand Tracker...")
        self.hand_tracker = HandTracker()
        print("      Hand tracker ready!")

        print("\n[2/5] Initializing Arpeggiator...")
        self.arpeggiator = Arpeggiator()
        print("      Arpeggiator ready!")

        print("\n[3/5] Loading Drum Sounds...")
        self.drum_machine = DrumMachine()

        print("\n[4/5] Initializing Visualizer...")
        self.visualizer = Visualizer(width=1280, height=720)
        print("      Visualizer ready!")

        # Camera setup
        print("\n[5/5] Setting up Camera...")
=======
        print("Initializing Hand-Controlled Music Generator...")

        # Initialize components
        self.hand_tracker = HandTracker()
        self.arpeggiator = Arpeggiator()
        self.drum_machine = DrumMachine()
        self.visualizer = Visualizer(width=1280, height=720)

        # Camera setup
>>>>>>> 9178300 (new branch)
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self.camera.isOpened():
            raise RuntimeError("Could not open camera!")

<<<<<<< HEAD
        print("      Camera ready!")

=======
>>>>>>> 9178300 (new branch)
        # Timing
        self.start_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update = time.time()
        self.target_fps = 60  # Target frame rate for smooth performance
        self.frame_time = 1.0 / self.target_fps

        # State
        self.running = True
        self.hand_height_left = 0.5
        self.volume = 0.3
        self.fingers_extended_right = [False] * 5

<<<<<<< HEAD
        print("\n" + "="*60)
        print("  INITIALIZATION COMPLETE!")
        print("="*60)
        print("\n  CONTROLS:")
        print("  " + "-"*56)
        print("  LEFT HAND (Arpeggiator):")
        print("    * Raise hand up/down    -> Change pitch")
        print("    * Pinch thumb & index   -> Control volume")
        print("")
        print("  RIGHT HAND (Drums):")
        print("    * No fingers            -> Pattern 1 (Basic 4/4)")
        print("    * Index finger          -> Pattern 1 (Basic 4/4)")
        print("    * Index + Middle        -> Pattern 2 (With clap)")
        print("    * Index + Middle + Ring -> Pattern 3 (Syncopated)")
        print("    * All except thumb      -> Pattern 4 (Break beat)")
        print("    * All fingers           -> Pattern 5 (Minimal)")
        print("  " + "-"*56)
        print("\n  Press 'Q' or 'ESC' to quit")
        print("  " + "="*56 + "\n")
=======
        print("* Initialization complete!")
        print("\nControls:")
        print("  Left Hand (Arpeggiator):")
        print("    - Raise hand = Higher pitch")
        print("    - Pinch fingers = Change volume")
        print("  Right Hand (Drums):")
        print("    - Change finger positions = Switch drum patterns")
        print("\nPress 'Q' to quit\n")
>>>>>>> 9178300 (new branch)

    def update_fps(self):
        """Calculate FPS"""
        self.frame_count += 1
        current_time = time.time()

        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = current_time

    def process_hands(self, hand_data, current_time):
        """Process hand data and update music controllers"""
        arp_data = None
        drum_data = None

        # Process Left Hand (Arpeggiator)
        if 'Left' in hand_data:
            self.hand_height_left = self.hand_tracker.get_hand_height('Left')
            pinch_distance = self.hand_tracker.get_pinch_distance('Left')

            # Update arpeggiator
            arp_data = self.arpeggiator.update(
                self.hand_height_left,
                pinch_distance,
                current_time
            )

            self.volume = self.arpeggiator.volume

        # Process Right Hand (Drums)
        if 'Right' in hand_data:
            self.fingers_extended_right = self.hand_tracker.get_fingers_extended('Right')

            # Update drum machine
            drum_data = self.drum_machine.update(
                self.fingers_extended_right,
                current_time
            )

        return arp_data, drum_data

    def run(self):
        """Main application loop"""
<<<<<<< HEAD
        print("\n[*] Starting main loop...")
=======
        print("Starting main loop...")
>>>>>>> 9178300 (new branch)

        try:
            while self.running:
                frame_start = time.time()

                # Read camera frame
                ret, frame = self.camera.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                # Flip frame for mirror effect
                frame = cv2.flip(frame, 1)

                # Get current time
                current_time = time.time() - self.start_time

                # Process hand tracking
                hand_data = self.hand_tracker.process_frame(frame)

                # Draw hand landmarks on camera frame
                frame_with_hands = self.hand_tracker.draw_landmarks(frame.copy())

                # Process hands and update music
                arp_data, drum_data = self.process_hands(hand_data, current_time)

                # Render visualization
                vis_frame = self.visualizer.render(
                    frame_with_hands,
                    hand_data,
                    arp_data,
                    drum_data,
                    self.hand_height_left,
                    self.volume,
                    self.fingers_extended_right,
                    self.fps
                )

                # Display
                cv2.imshow('Hand-Controlled Music Generator', vis_frame)

                # Update FPS
                self.update_fps()

                # Frame rate limiting for consistent performance
                frame_elapsed = time.time() - frame_start
                if frame_elapsed < self.frame_time:
                    sleep_time = self.frame_time - frame_elapsed
                    # Use cv2.waitKey for the sleep to maintain responsiveness
                    wait_ms = max(1, int(sleep_time * 1000))
                    key = cv2.waitKey(wait_ms) & 0xFF
                else:
                    key = cv2.waitKey(1) & 0xFF

                # Check for quit
                if key == ord('q') or key == ord('Q') or key == 27:  # Q or ESC
                    print("\nShutting down...")
                    self.running = False
                    break

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")

        finally:
            self.cleanup()

    def cleanup(self):
        """Clean up resources"""
        print("Cleaning up resources...")
        self.camera.release()
        cv2.destroyAllWindows()
        self.hand_tracker.release()
        print("* Cleanup complete!")


def main():
    """Entry point"""
<<<<<<< HEAD
    print("\n" + "=" * 60)
    print("  HAND-CONTROLLED MUSIC GENERATOR")
    print("  Arpeggiator + Drum Machine + Visualizer")
    print("=" * 60)
=======
    print("=" * 60)
    print("  HAND-CONTROLLED MUSIC GENERATOR")
    print("  Arpeggiator + Drum Machine + Visualizer")
    print("=" * 60)
    print()
>>>>>>> 9178300 (new branch)

    try:
        controller = MusicController()
        controller.run()
    except Exception as e:
        print(f"\n[X] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n* Thanks for using Hand-Controlled Music Generator!")
    return 0


if __name__ == "__main__":
    exit(main())
