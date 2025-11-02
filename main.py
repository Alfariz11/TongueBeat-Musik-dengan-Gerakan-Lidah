import cv2
import time
import numpy as np
from hand_tracker import HandTracker
from arpeggiator import Arpeggiator
from drum_machine import DrumMachine
from visualizer import Visualizer


class MusicController:
    def __init__(self):
        self.hand_tracker = HandTracker()
        self.arpeggiator = Arpeggiator()
        self.drum_machine = DrumMachine()
        self.visualizer = Visualizer(width=1280, height=720)

        self.camera = cv2.VideoCapture(0)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        if not self.camera.isOpened():
            raise RuntimeError("Could not open camera!")

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
        self.prev_fist_left = False

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
            is_fist_left = self.hand_tracker.is_fist('Left')

            arp_data = self.arpeggiator.update(
                self.hand_height_left,
                pinch_distance,
                current_time,
                self.drum_machine.bpm
            )

            self.volume = self.arpeggiator.volume

            if is_fist_left and not self.prev_fist_left:
                next_pattern = (self.drum_machine.current_pattern_set + 1) % len(self.drum_machine.pattern_sets)
                self.drum_machine.change_pattern_set(next_pattern)
            
            self.prev_fist_left = is_fist_left

        if 'Right' in hand_data:
            self.fingers_extended_right = self.hand_tracker.get_fingers_extended('Right')
            is_fist_right = self.hand_tracker.is_fist('Right')

            drum_data = self.drum_machine.update(
                self.fingers_extended_right,
                current_time,
                is_fist_right
            )

            pinch = self.hand_tracker.get_pinch_distance('Right')
            if pinch < 0.03:
                hand_height_right = self.hand_tracker.get_hand_height('Right')
                new_bpm = int(60 + hand_height_right * (200 - 60))
                new_bpm = np.clip(new_bpm, 60, 200)

                if new_bpm != self.drum_machine.bpm:
                    self.drum_machine.set_bpm(new_bpm)
                    self.arpeggiator.set_bpm(new_bpm)

        return arp_data, drum_data

    def run(self):
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

                vis_frame = self.visualizer.render(
                    frame_with_hands,
                    hand_data,
                    arp_data,
                    drum_data,
                    self.hand_height_left,
                    self.volume,
                    self.fingers_extended_right,
                    self.fps,
                    self.drum_machine.bpm
                )

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
    try:
        controller = MusicController()
        controller.run()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
