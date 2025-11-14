"""
Gesture Processing Module
Handles hand tracking, music generation, and frame processing
"""

import cv2
import numpy as np
import time
from PyQt6.QtCore import QThread, pyqtSignal

from hand_tracker import HandTracker
from arpeggiator import Arpeggiator
from drum_machine import DrumMachine


class GestureProcessor(QThread):
    """
    Background thread for processing hand gestures and generating music.
    Emits signals for UI updates.
    """
    
    # Signals
    frame_processed = pyqtSignal(object)  # Emit processed frame
    hand_detected = pyqtSignal(str, bool)  # (hand_label, detected)
    fps_updated = pyqtSignal(float)  # FPS value
    drum_hit = pyqtSignal(str)  # drum name
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.cap = None
        self.tracker = None
        self.arp = None
        self.drum = None
        self.last_time = time.time()
        self.fps_counter = 0
        self.fps = 0
        
    def setup(self):
        """Initialize all components"""
        try:
            # Open camera
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.error_occurred.emit("Tidak bisa membuka kamera!")
                return False
            
            # Set camera resolution for better performance
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            # Initialize components
            self.tracker = HandTracker()
            self.arp = Arpeggiator()
            self.drum = DrumMachine()
            
            print("✅ Semua komponen berhasil diinisialisasi!")
            return True
            
        except Exception as e:
            print(f"❌ Error setup: {str(e)}")
            return False
    
    def run(self):
        """Main processing loop"""
        if not self.setup():
            print("❌ Setup failed!")
            return
            
        self.running = True
        
        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                time.sleep(0.01)
                continue
            
            # Mirror frame for intuitive control
            frame = cv2.flip(frame, 1)
            
            # Detect hands
            hand_data = self.tracker.process_frame(frame)
            
            # Initialize detection status
            left_detected = False
            right_detected = False
            
            # Process each hand
            for hand_label, hand_info in hand_data.items():
                if hand_label == "Left":
                    left_detected = True
                    self._process_arpeggiator(hand_info, frame.shape)
                    self._draw_hand_on_frame(frame, hand_info, (0, 255, 0))
                    
                elif hand_label == "Right":
                    right_detected = True
                    self._process_drums(hand_info, frame.shape)
                    self._draw_hand_on_frame(frame, hand_info, (255, 0, 0))
            
            # Emit hand detection status
            self.hand_detected.emit("left", left_detected)
            self.hand_detected.emit("right", right_detected)
            
            # Calculate and emit FPS
            self.fps_counter += 1
            current_time = time.time()
            if current_time - self.last_time >= 1.0:
                self.fps = self.fps_counter
                self.fps_updated.emit(self.fps)
                self.fps_counter = 0
                self.last_time = current_time
            
            # Emit processed frame
            self.frame_processed.emit(frame)
            
            # Control framerate
            time.sleep(0.01)
        
        # Cleanup
        if self.cap:
            self.cap.release()
        print("🛑 Gesture processor stopped")
    
    def _process_arpeggiator(self, hand_info, frame_shape):
        """Process left hand for arpeggiator"""
        # Get hand height (wrist y position, inverted so higher hand = higher pitch)
        hand_height = 1.0 - hand_info['wrist_y']  # Invert so higher hand = higher value
        
        # Get pinch distance for volume control
        pinch_distance = self.tracker.get_pinch_distance("Left")
        
        # Update arpeggiator
        import time
        current_time = time.time()
        self.arp.update(hand_height, pinch_distance, current_time)
    
    def _process_drums(self, hand_info, frame_shape):
        """Process right hand for drums"""
        # Get which fingers are extended
        fingers_extended = self.tracker.get_fingers_extended("Right")
        
        # Check if it's a fist (for pattern change)
        is_fist = self.tracker.is_fist("Right")
        
        # Update drum machine
        import time
        current_time = time.time()
        drum_result = self.drum.update(fingers_extended, current_time, is_fist)
        
        # Emit drum hits
        if drum_result and 'played' in drum_result:
            for drum_name in drum_result['played']:
                self.drum_hit.emit(drum_name)
    
    def _draw_hand_on_frame(self, frame, hand_info, color):
        """Draw hand landmarks on frame"""
        landmarks = hand_info['landmarks'].landmark
        h, w = frame.shape[:2]
        
        # Draw connections
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)  # Palm
        ]
        
        for start_idx, end_idx in connections:
            start = landmarks[start_idx]
            end = landmarks[end_idx]
            
            start_point = (int(start.x * w), int(start.y * h))
            end_point = (int(end.x * w), int(end.y * h))
            
            cv2.line(frame, start_point, end_point, color, 2)
        
        # Draw landmarks
        for landmark in landmarks:
            x, y = int(landmark.x * w), int(landmark.y * h)
            cv2.circle(frame, (x, y), 5, color, -1)
            cv2.circle(frame, (x, y), 7, (255, 255, 255), 2)
    
    def _process_drums(self, hand_data, detected):
        """Process right hand for drum control"""
        active_drums = []
        
        if detected:
            fingers = self.tracker.get_fingers_extended("Right")
            is_fist = self.tracker.is_fist("Right")
            
            drum_data = self.drum.update(fingers, time.time(), is_fist)
            if drum_data:
                active_drums = drum_data.get("played", [])
    
    def _update_metrics(self):
        """Calculate and emit performance metrics"""
        self.frame_count += 1
        elapsed = time.time() - self.fps_time
        
        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.fps_time = time.time()
        
        current_bpm = self.drum.bpm if self.drum else 120
        current_pattern = self.drum.current_pattern_set if self.drum else 0
        
        self.metrics_updated.emit(self.fps, current_bpm, current_pattern)
    
    def _draw_hands_on_frame(self, frame, hand_data):
        """Draw hand landmarks and labels on frame"""
        h, w = frame.shape[:2]
        
        for hand_label, hand_info in hand_data.items():
            if not hand_info or 'landmarks' not in hand_info:
                continue
            
            landmarks = hand_info['landmarks'].landmark
            
            # Color coding based on hand
            if hand_label == "Left":
                color = (100, 200, 255)  # Blue for arpeggiator
                label_text = "KIRI: Arpeggiator 🎹"
            else:
                color = (255, 150, 100)  # Orange for drums
                label_text = "KANAN: Drums 🥁"
            
            # Draw hand connections
            self._draw_hand_connections(frame, landmarks, w, h, color)
            
            # Draw landmarks
            self._draw_landmarks(frame, landmarks, w, h, color)
            
            # Draw label with background
            self._draw_hand_label(frame, landmarks[0], w, h, label_text, color)
        
        return frame
    
    def _draw_hand_connections(self, frame, landmarks, w, h, color):
        """Draw lines connecting hand landmarks"""
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)  # Palm
        ]
        
        for start, end in connections:
            if start < len(landmarks) and end < len(landmarks):
                x1 = int(landmarks[start].x * w)
                y1 = int(landmarks[start].y * h)
                x2 = int(landmarks[end].x * w)
                y2 = int(landmarks[end].y * h)
                cv2.line(frame, (x1, y1), (x2, y2), color, 2)
    
    def _draw_landmarks(self, frame, landmarks, w, h, color):
        """Draw individual landmark points"""
        for lm in landmarks:
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 5, color, -1)
            cv2.circle(frame, (x, y), 7, (255, 255, 255), 1)
    
    def _draw_hand_label(self, frame, wrist_landmark, w, h, text, color):
        """Draw hand label with background"""
        label_x = int(wrist_landmark.x * w)
        label_y = int(wrist_landmark.y * h) - 30
        
        # Get text size
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        text_size = cv2.getTextSize(text, font, font_scale, thickness)[0]
        
        # Draw background rectangle
        padding = 5
        cv2.rectangle(frame,
                     (label_x - padding, label_y - text_size[1] - padding),
                     (label_x + text_size[0] + padding, label_y + padding),
                     (0, 0, 0), -1)
        
        # Draw border
        cv2.rectangle(frame,
                     (label_x - padding, label_y - text_size[1] - padding),
                     (label_x + text_size[0] + padding, label_y + padding),
                     color, 2)
        
        # Draw text
        cv2.putText(frame, text, (label_x, label_y), font, font_scale, color, thickness)
    
    # Control methods
    def set_bpm(self, bpm):
        """Set BPM for both arpeggiator and drums"""
        if self.drum:
            self.drum.set_bpm(bpm)
        if self.arp:
            self.arp.set_bpm(bpm)
    
    def change_pattern(self):
        """Cycle through drum patterns"""
        if self.drum:
            current = self.drum.current_pattern_set
            next_pattern = (current + 1) % len(self.drum.pattern_sets)
            self.drum.current_pattern_set = next_pattern
            self.drum.drum_patterns = self.drum.pattern_sets[next_pattern]
            print(f"✅ Pattern diganti ke: {next_pattern + 1}")
    
    def stop(self):
        """Stop processing and cleanup"""
        self.running = False
