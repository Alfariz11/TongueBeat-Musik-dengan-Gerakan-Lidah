import cv2
import pygame
import numpy as np
import time

from visualizer_pygame import VisualizerPygame
from hand_tracker import HandTracker
from arpeggiator import Arpeggiator
from drum_machine import DrumMachine
<<<<<<< HEAD
from visualizer import Visualizer


class MusicController:
    def __init__(self):
<<<<<<< HEAD
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
=======
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)
        self.hand_tracker = HandTracker()
        self.arpeggiator = Arpeggiator()
        self.drum_machine = DrumMachine()
        self.visualizer = Visualizer(width=1280, height=720)

<<<<<<< HEAD
        # Camera setup
>>>>>>> 9178300 (new branch)
=======
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)
        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self.camera.isOpened():
            raise RuntimeError("Could not open camera!")

<<<<<<< HEAD
<<<<<<< HEAD
        print("      Camera ready!")

=======
>>>>>>> 9178300 (new branch)
        # Timing
=======
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)
        self.start_time = time.time()
        self.frame_count = 0
        self.fps = 0
        self.last_fps_update = time.time()
        self.target_fps = 60
        self.frame_time = 1.0 / self.target_fps

        self.running = True
        self.hand_height_left = 0.5
        self.volume = 0.3
        self.fingers_extended_right = [False] * 5

<<<<<<< HEAD
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

=======
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)
    def update_fps(self):
        self.frame_count += 1
        current_time = time.time()

        if current_time - self.last_fps_update >= 1.0:
            self.fps = self.frame_count / (current_time - self.last_fps_update)
            self.frame_count = 0
            self.last_fps_update = current_time

    def process_hands(self, hand_data, current_time):
        arp_data = None
        drum_data = None

        if 'Left' in hand_data:
            self.hand_height_left = self.hand_tracker.get_hand_height('Left')
            pinch_distance = self.hand_tracker.get_pinch_distance('Left')

            arp_data = self.arpeggiator.update(
                self.hand_height_left,
                pinch_distance,
                current_time,
<<<<<<< HEAD
                bpm=self.drum_machine.bpm
=======
                self.drum_machine.bpm
>>>>>>> 399c403 (integrated with bpm feature edwin)
            )

            self.volume = self.arpeggiator.volume

        if 'Right' in hand_data:
            self.fingers_extended_right = self.hand_tracker.get_fingers_extended('Right')

            drum_data = self.drum_machine.update(
                self.fingers_extended_right,
                current_time
            )

        # --- BPM Control via knob rotation (Right Hand + Pinch active) ---
        rotation = self.hand_tracker.get_rotation_angle('Right')
        # --- BPM control via vertical motion ---
        pinch = self.hand_tracker.get_pinch_distance('Right')

        # Kalau pinch aktif (tanda kamu "pegang" knob)
        if pinch < 0.03:
            hand_height_right = self.hand_tracker.get_hand_height('Right')

            # Mapping tinggi tangan (0–1) ke BPM range (60–200)
            new_bpm = int(60 + hand_height_right * (200 - 60))
            new_bpm = np.clip(new_bpm, 60, 200)

            if new_bpm != self.drum_machine.bpm:
                self.drum_machine.set_bpm(new_bpm)
                print(f"[BPM Control] Height={hand_height_right:.2f} → BPM={self.drum_machine.bpm}")

        # Kalau pinch dilepas → kunci BPM (tidak berubah)

        return arp_data, drum_data

    def run(self):
<<<<<<< HEAD
        """Main application loop"""
<<<<<<< HEAD
        print("\n[*] Starting main loop...")
=======
        print("Starting main loop...")
>>>>>>> 9178300 (new branch)

=======
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)
        try:
            while self.running:
                frame_start = time.time()

                ret, frame = self.camera.read()
                if not ret:
                    break

                frame = cv2.flip(frame, 1)

                current_time = time.time() - self.start_time

                hand_data = self.hand_tracker.process_frame(frame)

                frame_with_hands = frame.copy()
                frame_with_hands = self.hand_tracker.draw_roi_zones(frame_with_hands)
                frame_with_hands = self.hand_tracker.draw_landmarks(frame_with_hands)

                arp_data, drum_data = self.process_hands(hand_data, current_time)

<<<<<<< HEAD
=======
                # Render visualization
                self.visualizer._current_bpm = self.drum_machine.bpm

>>>>>>> db5b17e (fix: appregiator note & visual)
                vis_frame = self.visualizer.render(
                    frame_with_hands,
                    hand_data,
                    arp_data,
                    drum_data,
                    self.hand_height_left,
                    self.volume,
                    self.fingers_extended_right,
                    self.fps,
                    self.drum_machine.bpm  # <== tambahkan ini
                )

<<<<<<< HEAD
=======

                # Display
>>>>>>> db5b17e (fix: appregiator note & visual)
                cv2.imshow('Hand-Controlled Music Generator', vis_frame)

                self.update_fps()

                frame_elapsed = time.time() - frame_start
                if frame_elapsed < self.frame_time:
                    sleep_time = self.frame_time - frame_elapsed
                    wait_ms = max(1, int(sleep_time * 1000))
                    key = cv2.waitKey(wait_ms) & 0xFF
                else:
                    key = cv2.waitKey(1) & 0xFF

                if key == ord('q') or key == ord('Q') or key == 27:
                    self.running = False
                    break

        except KeyboardInterrupt:
            pass

        finally:
            self.cleanup()

    def cleanup(self):
        self.camera.release()
        cv2.destroyAllWindows()
        self.hand_tracker.release()


def main():
<<<<<<< HEAD
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

=======
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)
    try:
        controller = MusicController()
        controller.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return 1
=======

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    arp = Arpeggiator()
    drum = DrumMachine()
    vis = VisualizerPygame()
>>>>>>> be369e5 (refactor: integrate pygame for visualizer)

    clock = pygame.time.Clock()
    running = True
    bpm = drum.bpm
    fps = 0

    print("[INFO] Starting Pygame visualizer...")

    while running:
        ret, frame = cap.read()
        if not ret:
            break

        hand_data = tracker.process_frame(frame)
        hand_height_right = 0.0
        volume = 0.0
        arp_data = None

        if "Right" in hand_data and hand_data["Right"]:
            hand_height_right = tracker.get_hand_height("Right")
            pinch_right = tracker.get_pinch_distance("Right")
            volume = max(0.0, min(1.0, 1.0 - pinch_right)) if pinch_right else 0.5
            arp_data = arp.update(hand_height_right, volume, time.time())
            if arp_data and arp_data.get("note") != arp.last_note:
                vis.spawn_particles_at_hand(hand_data, "Right", color=(100, 200, 255), intensity=6)
        else:
            if arp.current_sound:
                arp.current_sound.fadeout(200)
            arp_data = None

        fingers_left = tracker.get_fingers_extended("Left")
        is_fist_left = tracker.is_fist("Left")
        drum_data = drum.update(fingers_left, time.time(), is_fist_left)
        if drum_data and drum_data.get("played_details"):
            vis.spawn_particles_at_hand(hand_data, "Left", color=(255, 150, 100), intensity=10)

        vis.draw_background()
        vis.draw_arpeggiator(arp_data, hand_height_right, volume)
        vis.draw_drum_visualization(drum_data)
        vis.draw_drum_velocity_bars(drum_data)
        vis.draw_camera_feed(frame, hand_data)

        fps = clock.get_fps()
        vis.draw_info(fps, bpm)
        vis.update_particles()
        vis.update_display()

        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (
                event.type == pygame.KEYDOWN and event.key == pygame.K_q
            ):
                running = False

    print("[INFO] Exiting...")
    cap.release()
    pygame.quit()


if __name__ == "__main__":
    main()