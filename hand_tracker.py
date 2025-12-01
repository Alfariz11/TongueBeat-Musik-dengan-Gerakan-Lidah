"""
Hand Tracking Module
Enhanced MediaPipe-based hand tracking with ROI zones, gesture recognition,
and smoothing filters for robust real-time control.
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class HandLabel(Enum):
    """Enum for hand labels."""
    LEFT = "Left"
    RIGHT = "Right"


class ROIStatus(Enum):
    """Enum for ROI status."""
    NOT_DETECTED = "not_detected"
    IN_ZONE = "in_zone"
    OUT_OF_ZONE = "out_of_zone"


@dataclass
class ROIZone:
    """Configuration for a Region of Interest zone."""
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    color: Tuple[int, int, int]
    name: str
    
    def contains_point(self, x: float, y: float, margin: float = 0.0) -> bool:
        """Check if a point is within this zone (with optional margin)."""
        return (
            self.x_min - margin <= x <= self.x_max + margin and
            self.y_min - margin <= y <= self.y_max + margin
        )


@dataclass
class HandData:
    """Structured hand tracking data."""
    landmarks: any  # MediaPipe landmarks
    handedness: any  # MediaPipe handedness
    in_roi: bool
    center_x: float
    center_y: float
    wrist_y: float
    finger_tips: Dict[str, any]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for backward compatibility."""
        return {
            'landmarks': self.landmarks,
            'handedness': self.handedness,
            'in_roi': self.in_roi,
            'center_x': self.center_x,
            'center_y': self.center_y,
            'wrist_y': self.wrist_y,
            'index_tip_y': self.landmarks.landmark[8].y,
            'middle_tip_y': self.landmarks.landmark[12].y,
            'ring_tip_y': self.landmarks.landmark[16].y,
            'pinky_tip_y': self.landmarks.landmark[20].y,
            'thumb_tip': self.landmarks.landmark[4],
            'index_tip': self.landmarks.landmark[8],
            'middle_tip': self.landmarks.landmark[12],
            'ring_tip': self.landmarks.landmark[16],
            'pinky_tip': self.landmarks.landmark[20],
        }


class HandTracker:
    """
    Enhanced hand tracking system with MediaPipe.
    
    Features:
    - Dual-hand tracking with left/right classification
    - ROI (Region of Interest) zones for different controls
    - Temporal smoothing for stable tracking
    - Gesture recognition (fist, pinch, finger extension)
    - Visual feedback overlays
    """
    
    # MediaPipe landmark indices
    LANDMARK_WRIST = 0
    LANDMARK_THUMB_TIP = 4
    LANDMARK_THUMB_IP = 3
    LANDMARK_INDEX_TIP = 8
    LANDMARK_INDEX_PIP = 6
    LANDMARK_MIDDLE_TIP = 12
    LANDMARK_MIDDLE_PIP = 10
    LANDMARK_RING_TIP = 16
    LANDMARK_RING_PIP = 14
    LANDMARK_PINKY_TIP = 20
    LANDMARK_PINKY_PIP = 18
    
    # Default configuration
    DEFAULT_DETECTION_CONFIDENCE = 0.7
    DEFAULT_TRACKING_CONFIDENCE = 0.7
    DEFAULT_SMOOTHING_FACTOR = 0.3
    DEFAULT_ROI_MARGIN = 0.05
    
    def __init__(
        self,
        enable_roi: bool = True,
        detection_confidence: float = DEFAULT_DETECTION_CONFIDENCE,
        tracking_confidence: float = DEFAULT_TRACKING_CONFIDENCE,
        smoothing_factor: float = DEFAULT_SMOOTHING_FACTOR,
        max_num_hands: int = 2,
        model_complexity: int = 1
    ):
        """
        Initialize hand tracker.
        
        Args:
            enable_roi: Enable region of interest zones
            detection_confidence: Minimum detection confidence (0-1)
            tracking_confidence: Minimum tracking confidence (0-1)
            smoothing_factor: Temporal smoothing factor (0-1, higher = more smoothing)
            max_num_hands: Maximum number of hands to detect
            model_complexity: MediaPipe model complexity (0=lite, 1=full)
        """
        # Initialize MediaPipe
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        try:
            self.hands = self.mp_hands.Hands(
                model_complexity=model_complexity,
                min_detection_confidence=detection_confidence,
                min_tracking_confidence=tracking_confidence,
                max_num_hands=max_num_hands
            )
            print(f"✅ MediaPipe Hands initialized (complexity={model_complexity})")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize MediaPipe Hands: {e}")
        
        # Tracking state
        self.results: Optional[any] = None
        self.hand_data: Dict[str, HandData] = {}
        
        # Smoothing
        self.smoothing_factor = smoothing_factor
        self.prev_values: Dict[str, float] = {}
        
        # ROI configuration
        self.enable_roi = enable_roi
        self.roi_zones: Dict[str, ROIZone] = {
            HandLabel.LEFT.value: ROIZone(
                x_min=0.0,
                x_max=0.5,
                y_min=0.1,
                y_max=0.9,
                color=(100, 200, 255),  # Blue
                name='ARPEGGIATOR ZONE'
            ),
            HandLabel.RIGHT.value: ROIZone(
                x_min=0.5,
                x_max=1.0,
                y_min=0.1,
                y_max=0.9,
                color=(255, 100, 150),  # Pink
                name='DRUM ZONE'
            )
        }
        self.active_zone_margin = self.DEFAULT_ROI_MARGIN
        
        # Performance tracking
        self.frame_count = 0
        self.detection_count = 0
    
    def process_frame(self, frame: np.ndarray) -> Dict[str, Dict]:
        """
        Process a video frame to detect and track hands.
        
        Args:
            frame: Input BGR frame from camera
            
        Returns:
            Dictionary mapping hand labels to hand data dictionaries
        """
        if frame is None or frame.size == 0:
            return {}
        
        try:
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            rgb_frame.flags.writeable = False
            
            # Process with MediaPipe
            self.results = self.hands.process(rgb_frame)
            
            rgb_frame.flags.writeable = True
            self.frame_count += 1
            
            # Reset hand data
            self.hand_data = {}
            
            # Process detected hands
            if self.results.multi_hand_landmarks and self.results.multi_handedness:
                self.detection_count += len(self.results.multi_hand_landmarks)
                
                for hand_landmarks, handedness in zip(
                    self.results.multi_hand_landmarks,
                    self.results.multi_handedness
                ):
                    hand_label = handedness.classification[0].label
                    
                    # Check if hand is in ROI
                    in_roi = self._is_hand_in_roi(hand_landmarks, hand_label)
                    
                    # Calculate hand center
                    center_x, center_y = self._calculate_hand_center(hand_landmarks)
                    
                    # Extract finger tips
                    finger_tips = {
                        'thumb': hand_landmarks.landmark[self.LANDMARK_THUMB_TIP],
                        'index': hand_landmarks.landmark[self.LANDMARK_INDEX_TIP],
                        'middle': hand_landmarks.landmark[self.LANDMARK_MIDDLE_TIP],
                        'ring': hand_landmarks.landmark[self.LANDMARK_RING_TIP],
                        'pinky': hand_landmarks.landmark[self.LANDMARK_PINKY_TIP]
                    }
                    
                    # Store structured data
                    hand_data = HandData(
                        landmarks=hand_landmarks,
                        handedness=handedness,
                        in_roi=in_roi,
                        center_x=center_x,
                        center_y=center_y,
                        wrist_y=hand_landmarks.landmark[self.LANDMARK_WRIST].y,
                        finger_tips=finger_tips
                    )
                    
                    # Convert to dictionary for backward compatibility
                    self.hand_data[hand_label] = hand_data.to_dict()
            
            return self.hand_data
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            return {}
    
    def _is_hand_in_roi(self, hand_landmarks, hand_label: str) -> bool:
        """
        Check if a hand is within its designated ROI zone.
        
        Args:
            hand_landmarks: MediaPipe hand landmarks
            hand_label: Hand label (Left/Right)
            
        Returns:
            True if hand is in ROI, False otherwise
        """
        if not self.enable_roi:
            return True
        
        if hand_label not in self.roi_zones:
            return True
        
        wrist = hand_landmarks.landmark[self.LANDMARK_WRIST]
        zone = self.roi_zones[hand_label]
        
        return zone.contains_point(wrist.x, wrist.y, self.active_zone_margin)
    
    def _calculate_hand_center(self, hand_landmarks) -> Tuple[float, float]:
        """Calculate the geometric center of the hand."""
        landmarks = hand_landmarks.landmark
        center_x = sum(lm.x for lm in landmarks) / len(landmarks)
        center_y = sum(lm.y for lm in landmarks) / len(landmarks)
        return center_x, center_y
    
    def _smooth_value(self, key: str, new_value: float) -> float:
        """
        Apply exponential smoothing to a value.
        
        Args:
            key: Unique identifier for the value
            new_value: New value to smooth
            
        Returns:
            Smoothed value
        """
        if key not in self.prev_values:
            self.prev_values[key] = new_value
            return new_value
        
        smoothed = (
            self.smoothing_factor * new_value +
            (1 - self.smoothing_factor) * self.prev_values[key]
        )
        self.prev_values[key] = smoothed
        return smoothed
    
    # Gesture Recognition Methods
    
    def get_hand_height(self, hand_label: str) -> float:
        """
        Get smoothed hand height (0-1, inverted so higher hand = higher value).
        
        Args:
            hand_label: Hand label (Left/Right)
            
        Returns:
            Normalized hand height (0-1)
        """
        if hand_label in self.hand_data:
            raw_height = 1.0 - self.hand_data[hand_label]['wrist_y']
            return self._smooth_value(f'{hand_label}_height', raw_height)
        return 0.5
    
    def get_pinch_distance(self, hand_label: str) -> float:
        """
        Get distance between thumb and index finger (pinch gesture).
        
        Args:
            hand_label: Hand label (Left/Right)
            
        Returns:
            3D Euclidean distance between thumb and index tips
        """
        if hand_label in self.hand_data:
            thumb = self.hand_data[hand_label]['thumb_tip']
            index = self.hand_data[hand_label]['index_tip']
            
            distance = np.sqrt(
                (thumb.x - index.x)**2 +
                (thumb.y - index.y)**2 +
                (thumb.z - index.z)**2
            )
            return self._smooth_value(f'{hand_label}_pinch', distance)
        return 0.1
    
    def get_hand_openness(self, hand_label: str) -> float:
        """
        Calculate how open/spread the hand is (0=closed, 1=fully open).
        
        Args:
            hand_label: Hand label (Left/Right)
            
        Returns:
            Openness metric (0-1)
        """
        if hand_label not in self.hand_data:
            return 0.0
        
        landmarks = self.hand_data[hand_label]['landmarks'].landmark
        
        # Calculate average distance from center to fingertips
        center_x = self.hand_data[hand_label]['center_x']
        center_y = self.hand_data[hand_label]['center_y']
        
        fingertip_indices = [
            self.LANDMARK_THUMB_TIP,
            self.LANDMARK_INDEX_TIP,
            self.LANDMARK_MIDDLE_TIP,
            self.LANDMARK_RING_TIP,
            self.LANDMARK_PINKY_TIP
        ]
        
        total_distance = 0.0
        for idx in fingertip_indices:
            tip = landmarks[idx]
            distance = np.sqrt((tip.x - center_x)**2 + (tip.y - center_y)**2)
            total_distance += distance
        
        avg_distance = total_distance / len(fingertip_indices)
        
        # Normalize (typical range is 0.05 to 0.15)
        normalized = (avg_distance - 0.05) / 0.10
        clamped = max(0.0, min(1.0, normalized))
        
        return self._smooth_value(f'{hand_label}_openness', clamped)
    
    def get_rotation_angle(self, hand_label: str) -> float:
        """
        Get hand rotation angle change (in degrees).
        
        Args:
            hand_label: Hand label (Left/Right)
            
        Returns:
            Change in rotation angle (degrees)
        """
        if hand_label not in self.hand_data:
            return 0.0
        
        thumb = self.hand_data[hand_label]['thumb_tip']
        index = self.hand_data[hand_label]['index_tip']
        
        dx = index.x - thumb.x
        dy = index.y - thumb.y
        angle = np.degrees(np.arctan2(dy, dx))
        
        key = f"{hand_label}_rotation_angle"
        prev_angle = self.prev_values.get(key, angle)
        
        # Handle angle wrapping
        delta = angle - prev_angle
        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360
        
        self.prev_values[key] = angle
        
        delta_smoothed = self._smooth_value(f"{hand_label}_rot_delta", delta)
        return delta_smoothed
    
    def get_fingers_extended(self, hand_label: str) -> List[bool]:
        """
        Check which fingers are extended.
        
        Args:
            hand_label: Hand label (Left/Right)
            
        Returns:
            List of 5 booleans [thumb, index, middle, ring, pinky]
        """
        if hand_label not in self.hand_data:
            return [False] * 5
        
        landmarks = self.hand_data[hand_label]['landmarks'].landmark
        
        # Thumb extension (horizontal comparison)
        if hand_label == HandLabel.RIGHT.value:
            thumb_extended = landmarks[self.LANDMARK_THUMB_TIP].x < landmarks[self.LANDMARK_THUMB_IP].x
        else:  # Left hand
            thumb_extended = landmarks[self.LANDMARK_THUMB_TIP].x > landmarks[self.LANDMARK_THUMB_IP].x
        
        # Other fingers (vertical comparison - tip above PIP joint)
        index_extended = landmarks[self.LANDMARK_INDEX_TIP].y < landmarks[self.LANDMARK_INDEX_PIP].y
        middle_extended = landmarks[self.LANDMARK_MIDDLE_TIP].y < landmarks[self.LANDMARK_MIDDLE_PIP].y
        ring_extended = landmarks[self.LANDMARK_RING_TIP].y < landmarks[self.LANDMARK_RING_PIP].y
        pinky_extended = landmarks[self.LANDMARK_PINKY_TIP].y < landmarks[self.LANDMARK_PINKY_PIP].y
        
        return [thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended]
    
    def is_fist(self, hand_label: str) -> bool:
        """
        Check if hand is making a fist gesture.
        
        Args:
            hand_label: Hand label (Left/Right)
            
        Returns:
            True if fist detected, False otherwise
        """
        if hand_label not in self.hand_data:
            return False
        
        fingers = self.get_fingers_extended(hand_label)
        extended_count = sum(fingers)
        
        # Fist: no fingers or only thumb extended
        return extended_count <= 1
    
    def is_pointing(self, hand_label: str) -> bool:
        """
        Check if hand is pointing (only index finger extended).
        
        Args:
            hand_label: Hand label (Left/Right)
            
        Returns:
            True if pointing gesture detected
        """
        if hand_label not in self.hand_data:
            return False
        
        fingers = self.get_fingers_extended(hand_label)
        
        # Pointing: only index finger extended
        return fingers[1] and not any(fingers[i] for i in [2, 3, 4])
    
    def is_peace_sign(self, hand_label: str) -> bool:
        """
        Check if hand is making peace sign (index + middle extended).
        
        Args:
            hand_label: Hand label (Left/Right)
            
        Returns:
            True if peace sign detected
        """
        if hand_label not in self.hand_data:
            return False
        
        fingers = self.get_fingers_extended(hand_label)
        
        # Peace sign: index and middle extended, others closed
        return fingers[1] and fingers[2] and not fingers[3] and not fingers[4]
    
    def is_bpm_unlock_gesture(self, right_pinch_distance: float) -> bool:
        """
        Return True jika pinch kanan cukup rapat untuk unlock BPM.
        Semakin kecil nilai pinch_distance → semakin rapat jari.
        """
        return right_pinch_distance < 0.03   # threshold bisa kamu atur

    def get_hand_roi_status(self, hand_label: str) -> str:
        """
        Get ROI status for a hand.
        
        Args:
            hand_label: Hand label (Left/Right)
            
        Returns:
            ROI status string
        """
        if hand_label not in self.hand_data:
            return ROIStatus.NOT_DETECTED.value
        
        if self.hand_data[hand_label]['in_roi']:
            return ROIStatus.IN_ZONE.value
        else:
            return ROIStatus.OUT_OF_ZONE.value
    
    # Visualization Methods
    
    def draw_roi_zones(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw ROI zones on frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Frame with ROI zones drawn
        """
        if not self.enable_roi:
            return frame
        
        h, w = frame.shape[:2]
        
        for hand_label, zone in self.roi_zones.items():
            # Calculate zone coordinates
            x1 = int(zone.x_min * w)
            x2 = int(zone.x_max * w)
            y1 = int(zone.y_min * h)
            y2 = int(zone.y_max * h)
            
            # Check if hand is in zone
            hand_in_zone = (
                hand_label in self.hand_data and 
                self.hand_data[hand_label].get('in_roi', False)
            )
            
            # Adjust appearance based on activity
            if hand_in_zone:
                color = zone.color
                thickness = 3
                alpha = 0.3
            else:
                color = tuple(int(c * 0.5) for c in zone.color)
                thickness = 2
                alpha = 0.15
            
            # Draw semi-transparent zone
            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
            
            # Draw zone border
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness, cv2.LINE_AA)
            
            # Draw zone label
            label = zone.name
            if hand_in_zone:
                label += " [ACTIVE]"
            
            self._draw_zone_label(frame, x1, x2, y1, label, color)
            
            # Draw hand center crosshair if active
            if hand_in_zone:
                hand_data = self.hand_data[hand_label]
                center_x = int(hand_data['center_x'] * w)
                center_y = int(hand_data['center_y'] * h)
                
                cv2.circle(frame, (center_x, center_y), 10, color, 2, cv2.LINE_AA)
                cv2.line(frame, (center_x - 15, center_y), (center_x + 15, center_y), 
                        color, 2, cv2.LINE_AA)
                cv2.line(frame, (center_x, center_y - 15), (center_x, center_y + 15), 
                        color, 2, cv2.LINE_AA)
        
        return frame
    
    def _draw_zone_label(
        self, 
        frame: np.ndarray, 
        x1: int, 
        x2: int, 
        y1: int, 
        text: str, 
        color: Tuple[int, int, int]
    ):
        """Draw zone label with background."""
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.7
        thickness = 2
        
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_x = x1 + (x2 - x1 - text_size[0]) // 2
        text_y = y1 + 30
        
        # Background rectangle
        padding = 5
        cv2.rectangle(
            frame,
            (text_x - padding, text_y - text_size[1] - padding),
            (text_x + text_size[0] + padding, text_y + padding),
            (0, 0, 0),
            -1
        )
        
        # Text
        cv2.putText(
            frame, text, (text_x, text_y),
            font, font_scale, color, thickness, cv2.LINE_AA
        )
    
    def draw_landmarks(self, frame: np.ndarray) -> np.ndarray:
        """
        Draw hand landmarks and connections on frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Frame with landmarks drawn
        """
        if not self.results or not self.results.multi_hand_landmarks:
            return frame
        
        for idx, hand_landmarks in enumerate(self.results.multi_hand_landmarks):
            hand_label = self.results.multi_handedness[idx].classification[0].label
            
            # Get color for this hand
            if hand_label in self.roi_zones:
                color = self.roi_zones[hand_label].color
                landmark_style = self.mp_drawing.DrawingSpec(
                    color=color, thickness=2, circle_radius=3
                )
                connection_style = self.mp_drawing.DrawingSpec(
                    color=color, thickness=2
                )
            else:
                landmark_style = self.mp_drawing_styles.get_default_hand_landmarks_style()
                connection_style = self.mp_drawing_styles.get_default_hand_connections_style()
            
            # Draw landmarks and connections
            self.mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                self.mp_hands.HAND_CONNECTIONS,
                landmark_style,
                connection_style
            )
            
            # Draw "OUT OF ZONE" warning if applicable
            if hand_label in self.hand_data and not self.hand_data[hand_label].get('in_roi', True):
                wrist = hand_landmarks.landmark[self.LANDMARK_WRIST]
                h, w = frame.shape[:2]
                x = int(wrist.x * w)
                y = int(wrist.y * h)
                
                cv2.putText(
                    frame, "OUT OF ZONE!", (x - 60, y - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2, cv2.LINE_AA
                )
                cv2.circle(frame, (x, y), 15, (0, 0, 255), 3, cv2.LINE_AA)
        
        return frame
    
    def draw_all(self, frame: np.ndarray, show_roi: bool = True, show_landmarks: bool = True) -> np.ndarray:
        """
        Draw all visualizations on frame.
        
        Args:
            frame: Input frame
            show_roi: Whether to draw ROI zones
            show_landmarks: Whether to draw hand landmarks
            
        Returns:
            Frame with all visualizations
        """
        if show_roi:
            frame = self.draw_roi_zones(frame)
        
        if show_landmarks:
            frame = self.draw_landmarks(frame)
        
        return frame
    
    # Utility Methods
    
    def get_stats(self) -> Dict:
        """
        Get tracking statistics.
        
        Returns:
            Dictionary with statistics
        """
        detection_rate = 0.0
        if self.frame_count > 0:
            detection_rate = self.detection_count / self.frame_count
        
        return {
            'frames_processed': self.frame_count,
            'detections': self.detection_count,
            'detection_rate': detection_rate,
            'active_hands': len(self.hand_data),
            'smoothing_factor': self.smoothing_factor
        }
    
    def reset_stats(self):
        """Reset tracking statistics."""
        self.frame_count = 0
        self.detection_count = 0
    
    def set_smoothing(self, factor: float):
        """
        Set smoothing factor.
        
        Args:
            factor: Smoothing factor (0-1)
        """
        self.smoothing_factor = max(0.0, min(1.0, factor))
    
    def set_roi_margin(self, margin: float):
        """
        Set ROI margin.
        
        Args:
            margin: Margin value (0-1)
        """
        self.active_zone_margin = max(0.0, min(0.2, margin))
    
    def enable_roi_zones(self, enable: bool):
        """Enable or disable ROI zones."""
        self.enable_roi = enable
    
    def release(self):
        """Release MediaPipe resources."""
        try:
            if self.hands:
                self.hands.close()
                print("✅ Hand tracker released")
        except Exception as e:
            print(f"Error releasing hand tracker: {e}")
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.release()


# Example usage
if __name__ == "__main__":
    import time
    
    # Initialize tracker
    tracker = HandTracker(
        enable_roi=True,
        detection_confidence=0.7,
        tracking_confidence=0.7,
        smoothing_factor=0.3
    )
    
    # Open camera
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open camera")
        exit()
    
    print("🎥 Camera opened. Press 'q' to quit, 's' for stats")
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Mirror frame
            frame = cv2.flip(frame, 1)
            
            # Process frame
            hand_data = tracker.process_frame(frame)
            
            # Draw visualizations
            frame = tracker.draw_all(frame)
            
            # Display info for each hand
            for hand_label, data in hand_data.items():
                fingers = tracker.get_fingers_extended(hand_label)
                height = tracker.get_hand_height(hand_label)
                pinch = tracker.get_pinch_distance(hand_label)
                
                info_text = (
                    f"{hand_label}: "
                    f"Fingers: {sum(fingers)} | "
                    f"Height: {height:.2f} | "
                    f"Pinch: {pinch:.2f}"
                )
                
                y_pos = 30 if hand_label == "Left" else 60
                cv2.putText(
                    frame, info_text, (10, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
                )
            
            # Show frame
            cv2.imshow('Hand Tracking', frame)
            
            # Handle keys
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                stats = tracker.get_stats()
                print(f"\n📊 Stats: {stats}")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
        tracker.release()
        print("\n✅ Cleanup complete")