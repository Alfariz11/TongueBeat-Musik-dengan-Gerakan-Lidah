"""
Gesture Processing Module
Handles hand tracking, music generation, and frame processing
"""

import cv2
import numpy as np
import time
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass
from enum import Enum
from PyQt6.QtCore import QThread, pyqtSignal

from hand_tracker import HandTracker
from arpeggiator import Arpeggiator
from drum_machine import DrumMachine


class HandSide(Enum):
    """Enum for hand sides."""
    LEFT = "Left"
    RIGHT = "Right"


@dataclass
class ProcessingStats:
    """Statistics for gesture processing."""
    fps: float = 0.0
    frame_count: int = 0
    hands_detected: int = 0
    total_frames: int = 0
    dropped_frames: int = 0


class GestureProcessor(QThread):
    """
    Background thread for processing hand gestures and generating music.
    Emits signals for UI updates with error handling and performance optimization.
    """
    
    # Signals
    frame_processed = pyqtSignal(object)  # Emit processed frame
    hand_detected = pyqtSignal(str, bool)  # (hand_label, detected)
    fps_updated = pyqtSignal(float)  # FPS value
    drum_hit = pyqtSignal(str, float)  # (drum_name, velocity)
    note_played = pyqtSignal(int, float)  # (midi_note, volume)
    pattern_changed = pyqtSignal(int)  # pattern_index
    error_occurred = pyqtSignal(str)  # error message
    detection_count_updated = pyqtSignal(int)  # number of hands detected
    bpm_updated = pyqtSignal(int)  # current BPM
    
    # Constants
    DEFAULT_CAM_WIDTH = 1280
    DEFAULT_CAM_HEIGHT = 720
    DEFAULT_CAM_FPS = 30
    TARGET_FRAME_TIME = 1.0 / 30  # 30 FPS target
    FPS_UPDATE_INTERVAL = 1.0
    
    # Colors for hand visualization (BGR)
    COLOR_LEFT_HAND = (100, 200, 255)  # Blue for arpeggiator
    COLOR_RIGHT_HAND = (255, 150, 100)  # Orange for drums
    COLOR_LANDMARK = (255, 255, 255)  # White
    
    def __init__(self):
        super().__init__()
        
        # Thread control
        self.running = False
        self.paused = False
        
        # Components
        self.cap: Optional[cv2.VideoCapture] = None
        self.tracker: Optional[HandTracker] = None
        self.arp: Optional[Arpeggiator] = None
        self.drum: Optional[DrumMachine] = None
        
        # Performance tracking
        self.stats = ProcessingStats()
        self.last_fps_time = time.time()
        self.frame_times: List[float] = []
        self.max_frame_times = 30
        
        # State tracking
        self.last_hand_states: Dict[str, bool] = {
            HandSide.LEFT.value: False,
            HandSide.RIGHT.value: False
        }
        
        # Frame processing
        self.last_frame_time = time.time()
        self.frame_skip_counter = 0
        self.max_frame_skip = 2

        # BPM gesture control
        self.bpm_unlocked = False
        self.bpm_lock_threshold = 0.05   # Semakin kecil, semakin ketat
        self.bpm_last_height = None
        self.bpm_last_update_time = 0
        self.bpm_smoothing = 0.15

        
    def setup(self) -> bool:
        """
        Initialize all components with error handling.
        
        Returns:
            True if setup successful, False otherwise
        """
        try:
            # Open camera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.error_occurred.emit("❌ Tidak bisa membuka kamera! Pastikan webcam terhubung.")
                return False
            
            # Set camera properties for optimal performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.DEFAULT_CAM_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.DEFAULT_CAM_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, self.DEFAULT_CAM_FPS)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Minimize latency
            
            # Verify camera settings
            actual_width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            actual_height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            actual_fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            print(f"📷 Camera initialized: {actual_width}x{actual_height} @ {actual_fps}fps")
            
            # Initialize hand tracker
            self.tracker = HandTracker()
            print("👋 Hand tracker initialized")
            
            # Initialize arpeggiator
            self.arp = Arpeggiator(
                waveform='rich_sine',
                attack=0.01,
                release=0.15
            )
            print("🎹 Arpeggiator initialized")
            
            # Initialize drum machine
            self.drum = DrumMachine(
                master_gain=0.4,
                bpm=120,
                swing_amount=0.08
            )
            print("🥁 Drum machine initialized")
            
            print("✅ All components successfully initialized!")
            return True
            
        except Exception as e:
            error_msg = f"❌ Setup error: {str(e)}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
            return False
    
    def run(self):
        """Main processing loop with performance optimization."""
        if not self.setup():
            print("❌ Setup failed! Cannot start processing.")
            return
        
        self.running = True
        self.last_fps_time = time.time()
        
        try:
            while self.running:
                if self.paused:
                    time.sleep(0.1)
                    continue
                
                loop_start = time.time()
                
                # Capture frame
                ret, frame = self.cap.read()
                if not ret:
                    self.stats.dropped_frames += 1
                    time.sleep(0.01)
                    continue
                
                # Mirror frame for intuitive control
                frame = cv2.flip(frame, 1)
                
                # Process frame
                self._process_frame(frame)
                
                # Update statistics
                self.stats.total_frames += 1
                
                # Calculate and maintain frame rate
                frame_time = time.time() - loop_start
                self.frame_times.append(frame_time)
                if len(self.frame_times) > self.max_frame_times:
                    self.frame_times.pop(0)
                
                # Sleep to maintain target frame rate
                sleep_time = max(0, self.TARGET_FRAME_TIME - frame_time)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
        except Exception as e:
            error_msg = f"❌ Processing error: {str(e)}"
            print(error_msg)
            self.error_occurred.emit(error_msg)
        
        finally:
            self.cleanup()
    
    def _process_frame(self, frame: np.ndarray):
        """
        Process a single frame for hand detection and music generation.
        
        Args:
            frame: Input frame from camera
        """
        try:
            # Detect hands
            hand_data = self.tracker.process_frame(frame)
            
            # Track detection count
            hands_detected = len(hand_data)
            self.stats.hands_detected = hands_detected
            self.detection_count_updated.emit(hands_detected)
            
            # Initialize detection status
            left_detected = False
            right_detected = False
            
            # Process each detected hand
            for hand_label, hand_info in hand_data.items():
                if not hand_info or 'landmarks' not in hand_info:
                    continue
                
                if hand_label == HandSide.LEFT.value:
                    left_detected = True
                    self._process_arpeggiator(hand_info, frame.shape)
                    self._draw_hand_on_frame(
                        frame, 
                        hand_info, 
                        self.COLOR_LEFT_HAND,
                        "KIRI: Arpeggiator 🎹"
                    )
                    
                elif hand_label == HandSide.RIGHT.value:
                    right_detected = True

                    # === STEP A: Ambil gesture BPM ===
                    right_pinch = self.tracker.get_pinch_distance("Right")
                    print(f"[DEBUG] Right pinch = {right_pinch:.3f}")
                    right_height = 1.0 - hand_info["wrist_y"]

                    # === STEP B: Lock / Unlock BPM ===
                    if right_pinch < self.bpm_lock_threshold:   # Pinch kecil → unlock
                        self.bpm_unlocked = True
                    else:
                        self.bpm_unlocked = False

                    # === STEP C: Kalau unlock → ubah BPM ===
                    if self.bpm_unlocked:
                        self._update_bpm_from_gesture(right_height)

                    # --------------------------------------------------
                    # Lanjutkan proses Drum seperti biasa
                    # --------------------------------------------------
                    self._process_drums(hand_info, frame.shape)
                    
                    self._draw_hand_on_frame(
                        frame,
                        hand_info,
                        self.COLOR_RIGHT_HAND,
                        "KANAN: Drums 🥁"
                    )
            
            # Setelah loop selesai, cek apakah tangan kiri terdeteksi
            if not left_detected:
                if self.arp:
                    self.arp.mute()

            # Emit hand detection status (only if changed)
            if left_detected != self.last_hand_states[HandSide.LEFT.value]:
                self.hand_detected.emit("left", left_detected)
                self.last_hand_states[HandSide.LEFT.value] = left_detected
            
            if right_detected != self.last_hand_states[HandSide.RIGHT.value]:
                self.hand_detected.emit("right", right_detected)
                self.last_hand_states[HandSide.RIGHT.value] = right_detected
            
            # Draw performance overlay
            self._draw_performance_overlay(frame)
            
            # Emit processed frame
            self.frame_processed.emit(frame)
            
            # Update FPS
            self._update_fps()
            
        except Exception as e:
            print(f"Frame processing error: {e}")
    
    def _process_arpeggiator(self, hand_info: Dict, frame_shape: Tuple):
        """
        Process left hand for arpeggiator control.
        
        Args:
            hand_info: Hand information dictionary
            frame_shape: Shape of the frame (height, width, channels)
        """
        try:
            # Get hand height (wrist y position, inverted)
            hand_height = 1.0 - hand_info['wrist_y']
            
            # Get pinch distance for volume control
            pinch_distance = self.tracker.get_pinch_distance(HandSide.LEFT.value)
            
            # Update arpeggiator
            current_time = time.time()
            result = self.arp.update(hand_height, pinch_distance, current_time)
            
            # Emit note information
            if result:
                self.note_played.emit(result['note'], result['volume'])
                
        except Exception as e:
            print(f"Arpeggiator processing error: {e}")
    
    def _process_drums(self, hand_info: Dict, frame_shape: Tuple):
        """
        Process right hand for drum machine control.
        
        Args:
            hand_info: Hand information dictionary
            frame_shape: Shape of the frame (height, width, channels)
        """
        try:
            # Get which fingers are extended
            fingers_extended = self.tracker.get_fingers_extended(HandSide.RIGHT.value)
            
            # Check if it's a fist (for pattern change)
            is_fist = self.tracker.is_fist(HandSide.RIGHT.value)
            
            # Update drum machine
            current_time = time.time()
            drum_result = self.drum.update(
                fingers_extended, 
                current_time, 
                is_fist,
                hand_side=HandSide.RIGHT.value
            )
            
            # Emit drum hits with velocity
            if drum_result and 'played_details' in drum_result:
                for hit in drum_result['played_details']:
                    self.drum_hit.emit(hit['drum'], hit['velocity'])
            
            # Emit pattern change if detected
            if 'pattern_set' in drum_result:
                current_pattern = drum_result['pattern_set']
                self.pattern_changed.emit(current_pattern)
                
        except Exception as e:
            print(f"Drum processing error: {e}")
    
    def _draw_hand_on_frame(
        self, 
        frame: np.ndarray, 
        hand_info: Dict, 
        color: Tuple[int, int, int],
        label_text: str
    ):
        """
        Draw hand landmarks and connections on frame.
        
        Args:
            frame: Frame to draw on
            hand_info: Hand information dictionary
            color: Color for drawing (BGR)
            label_text: Text label for the hand
        """
        try:
            if 'landmarks' not in hand_info:
                return
            
            landmarks = hand_info['landmarks'].landmark
            h, w = frame.shape[:2]
            
            # Draw hand connections
            self._draw_hand_connections(frame, landmarks, w, h, color)
            
            # Draw landmarks
            self._draw_landmarks(frame, landmarks, w, h, color)
            
            # Draw label
            if len(landmarks) > 0:
                self._draw_hand_label(frame, landmarks[0], w, h, label_text, color)
                
        except Exception as e:
            print(f"Hand drawing error: {e}")
    
    def _draw_hand_connections(
        self, 
        frame: np.ndarray, 
        landmarks, 
        w: int, 
        h: int, 
        color: Tuple[int, int, int]
    ):
        """Draw lines connecting hand landmarks."""
        # MediaPipe hand connections
        connections = [
            # Thumb
            (0, 1), (1, 2), (2, 3), (3, 4),
            # Index finger
            (0, 5), (5, 6), (6, 7), (7, 8),
            # Middle finger
            (0, 9), (9, 10), (10, 11), (11, 12),
            # Ring finger
            (0, 13), (13, 14), (14, 15), (15, 16),
            # Pinky
            (0, 17), (17, 18), (18, 19), (19, 20),
            # Palm
            (5, 9), (9, 13), (13, 17)
        ]
        
        for start_idx, end_idx in connections:
            if start_idx >= len(landmarks) or end_idx >= len(landmarks):
                continue
            
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            
            start_point = (int(start.x * w), int(start.y * h))
            end_point = (int(end.x * w), int(end.y * h))
            
            # Draw connection line
            cv2.line(frame, start_point, end_point, color, 2, cv2.LINE_AA)
    
    def _draw_landmarks(
        self, 
        frame: np.ndarray, 
        landmarks, 
        w: int, 
        h: int, 
        color: Tuple[int, int, int]
    ):
        """Draw individual landmark points."""
        for idx, landmark in enumerate(landmarks):
            x, y = int(landmark.x * w), int(landmark.y * h)
            
            # Draw filled circle for landmark
            cv2.circle(frame, (x, y), 5, color, -1, cv2.LINE_AA)
            
            # Draw white border
            cv2.circle(frame, (x, y), 7, self.COLOR_LANDMARK, 2, cv2.LINE_AA)
            
            # Draw landmark number for key points
            if idx in [0, 4, 8, 12, 16, 20]:  # Wrist and fingertips
                cv2.putText(
                    frame, 
                    str(idx), 
                    (x + 10, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.4, 
                    self.COLOR_LANDMARK, 
                    1, 
                    cv2.LINE_AA
                )
    
    def _draw_hand_label(
        self, 
        frame: np.ndarray, 
        wrist_landmark, 
        w: int, 
        h: int, 
        text: str, 
        color: Tuple[int, int, int]
    ):
        """
        Draw hand label with background box.
        
        Args:
            frame: Frame to draw on
            wrist_landmark: Wrist landmark for positioning
            w: Frame width
            h: Frame height
            text: Label text
            color: Label color (BGR)
        """
        label_x = int(wrist_landmark.x * w)
        label_y = int(wrist_landmark.y * h) - 40
        
        # Text properties
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Background rectangle
        padding = 8
        bg_x1 = label_x - padding
        bg_y1 = label_y - text_size[1] - padding
        bg_x2 = label_x + text_size[0] + padding
        bg_y2 = label_y + padding
        
        # Draw semi-transparent background
        overlay = frame.copy()
        cv2.rectangle(overlay, (bg_x1, bg_y1), (bg_x2, bg_y2), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
        
        # Draw border
        cv2.rectangle(frame, (bg_x1, bg_y1), (bg_x2, bg_y2), color, 2, cv2.LINE_AA)
        
        # Draw text
        cv2.putText(
            frame, 
            text, 
            (label_x, label_y), 
            font, 
            font_scale, 
            color, 
            thickness, 
            cv2.LINE_AA
        )
    
    def _draw_performance_overlay(self, frame: np.ndarray):
        """
        Draw performance information overlay on frame.
        
        Args:
            frame: Frame to draw on
        """
        try:
            h, w = frame.shape[:2]
            overlay = frame.copy()
            
            # Draw semi-transparent background
            cv2.rectangle(overlay, (10, 10), (300, 120), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)
            
            # Prepare text
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2
            color = (0, 255, 0)
            
            # FPS
            fps_text = f"FPS: {self.stats.fps:.1f}"
            cv2.putText(frame, fps_text, (20, 40), font, font_scale, color, thickness, cv2.LINE_AA)
            
            # Hands detected
            hands_text = f"Hands: {self.stats.hands_detected}"
            cv2.putText(frame, hands_text, (20, 70), font, font_scale, color, thickness, cv2.LINE_AA)
            
            # Average frame time
            if self.frame_times:
                avg_frame_time = sum(self.frame_times) / len(self.frame_times)
                time_text = f"Frame: {avg_frame_time*1000:.1f}ms"
                cv2.putText(frame, time_text, (20, 100), font, font_scale, color, thickness, cv2.LINE_AA)
            
        except Exception as e:
            print(f"Overlay drawing error: {e}")
    
    def _update_fps(self):
        """Calculate and emit FPS updates."""
        self.stats.frame_count += 1
        current_time = time.time()
        elapsed = current_time - self.last_fps_time
        
        if elapsed >= self.FPS_UPDATE_INTERVAL:
            self.stats.fps = self.stats.frame_count / elapsed
            self.fps_updated.emit(self.stats.fps)
            self.stats.frame_count = 0
            self.last_fps_time = current_time
    
    # Control Methods
    def set_bpm(self, bpm: int):
        """
        Set BPM for both arpeggiator and drums.
        
        Args:
            bpm: Beats per minute
        """
        try:
            if self.drum:
                self.drum.set_bpm(bpm)
            if self.arp:
                self.arp.set_bpm(bpm)
            print(f"🎵 BPM set to: {bpm}")
            self.bpm_updated.emit(bpm)

        except Exception as e:
            print(f"Error setting BPM: {e}")
        

    def _update_bpm_from_gesture(self, hand_height: float):
        current_time = time.time()

        # Supaya BPM tidak update setiap frame → kasih cooldown 0.1 detik
        if current_time - self.bpm_last_update_time < 0.1:
            return

        # Convert height (0–1) menjadi BPM (40–200)
        raw_bpm = 40 + hand_height * 160   

        # Smoothing biar halus
        if self.bpm_last_height is None:
            smoothed_bpm = raw_bpm
        else:
            smoothed_bpm = (
                self.bpm_smoothing * raw_bpm +
                (1 - self.bpm_smoothing) * self.bpm_last_height
            )

        self.bpm_last_height = smoothed_bpm
        self.bpm_last_update_time = current_time

        # Update ke arpeggiator & drum machine
        bpm_int = int(smoothed_bpm)
        self.set_bpm(bpm_int)

    
    def change_pattern(self, pattern_index: Optional[int] = None):
        """
        Change drum pattern.
        
        Args:
            pattern_index: Specific pattern index, or None to cycle to next
        """
        try:
            if not self.drum:
                return
            
            if pattern_index is not None:
                # Set specific pattern
                self.drum.change_pattern_set(pattern_index)
            else:
                # Cycle to next pattern
                current = self.drum.current_pattern_set
                next_pattern = (current + 1) % len(self.drum.pattern_sets)
                self.drum.change_pattern_set(next_pattern)
            
            self.pattern_changed.emit(self.drum.current_pattern_set)
            print(f"🎼 Pattern changed to: {self.drum.current_pattern_set + 1}")
            
        except Exception as e:
            print(f"Error changing pattern: {e}")
    
    def pause(self):
        """Pause processing."""
        self.paused = True
        print("⏸️ Processing paused")
    
    def resume(self):
        """Resume processing."""
        self.paused = False
        print("▶️ Processing resumed")
    
    def stop(self):
        """Stop processing and cleanup."""
        print("🛑 Stopping gesture processor...")
        self.running = False
    
    def cleanup(self):
        """Clean up resources."""
        try:
            # Release camera
            if self.cap and self.cap.isOpened():
                self.cap.release()
                print("📷 Camera released")
            
            # Cleanup audio components
            if self.arp:
                self.arp.cleanup()
                print("🎹 Arpeggiator cleaned up")
            
            if self.drum:
                self.drum.cleanup()
                print("🥁 Drum machine cleaned up")
            
            # Print final statistics
            print("\n📊 Final Statistics:")
            print(f"  Total frames processed: {self.stats.total_frames}")
            print(f"  Dropped frames: {self.stats.dropped_frames}")
            print(f"  Final FPS: {self.stats.fps:.1f}")
            if self.frame_times:
                avg_time = sum(self.frame_times) / len(self.frame_times)
                print(f"  Average frame time: {avg_time*1000:.1f}ms")
            
            print("✅ Gesture processor stopped successfully")
            
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    def get_stats(self) -> ProcessingStats:
        """
        Get current processing statistics.
        
        Returns:
            ProcessingStats object with current statistics
        """
        return self.stats
    
    def reset_stats(self):
        """Reset processing statistics."""
        self.stats = ProcessingStats()
        self.last_fps_time = time.time()
        print("📊 Statistics reset")


# Example usage
if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    processor = GestureProcessor()
    
    # Connect signals for testing
    processor.fps_updated.connect(lambda fps: print(f"FPS: {fps:.1f}"))
    processor.hand_detected.connect(lambda hand, detected: print(f"{hand}: {'✅' if detected else '❌'}"))
    processor.drum_hit.connect(lambda drum, vel: print(f"🥁 {drum} @ {vel:.2f}"))
    processor.note_played.connect(lambda note, vol: print(f"🎹 Note {note} @ {vol:.2f}"))
    processor.error_occurred.connect(lambda err: print(f"❌ {err}"))
    
    # Start processing
    processor.start()
    
    # Wait for user to quit
    try:
        input("Press Enter to stop...\n")
    except KeyboardInterrupt:
        pass
    
    processor.stop()
    processor.wait()
    
    sys.exit(0)