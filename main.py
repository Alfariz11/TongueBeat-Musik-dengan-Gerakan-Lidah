import cv2
import pygame
import numpy as np
import time

from visualizer_pygame import VisualizerPygame
from hand_tracker import HandTracker
from arpeggiator import Arpeggiator
from drum_machine import DrumMachine

def main():
    cap = cv2.VideoCapture(0)
    tracker = HandTracker()
    arp = Arpeggiator()
    drum = DrumMachine()
    vis = VisualizerPygame()

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