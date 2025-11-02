"""
Hand Tracking Module using MediaPipe
Detects and tracks hands for controlling music
"""
import cv2
import mediapipe as mp
import numpy as np


class HandTracker:
<<<<<<< HEAD
    def __init__(self, enable_roi=True):
=======
    def __init__(self):
>>>>>>> 9178300 (new branch)
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Initialize hands detection with better quality settings
        self.hands = self.mp_hands.Hands(
            model_complexity=1,  # Higher quality model (0=lite, 1=full)
            min_detection_confidence=0.7,  # Higher confidence for better accuracy
            min_tracking_confidence=0.7,  # Higher tracking confidence for smoothness
            max_num_hands=2
        )

        self.results = None
        self.hand_data = {}

        # Smoothing parameters
        self.smoothing_factor = 0.3  # Lower = smoother but more lag
        self.prev_hand_positions = {}  # Store previous positions for smoothing

<<<<<<< HEAD
        # ROI (Region of Interest) settings
        self.enable_roi = enable_roi
        self.roi_zones = {
            'Left': {
                'x_min': 0.0,
                'x_max': 0.5,
                'y_min': 0.1,
                'y_max': 0.9,
                'color': (100, 200, 255),  # Blue for arpeggiator
                'name': 'ARPEGGIATOR ZONE'
            },
            'Right': {
                'x_min': 0.5,
                'x_max': 1.0,
                'y_min': 0.1,
                'y_max': 0.9,
                'color': (255, 100, 150),  # Pink for drums
                'name': 'DRUM ZONE'
            }
        }

        # Active detection zones
        self.active_zone_margin = 0.05  # 5% margin for zone detection

    def is_hand_in_roi(self, hand_landmarks, hand_label):
        """Check if hand is in its designated ROI zone"""
        if not self.enable_roi:
            return True

        # Get wrist position as reference point
        wrist = hand_landmarks.landmark[0]

        # Get ROI zone for this hand
        if hand_label not in self.roi_zones:
            return True

        zone = self.roi_zones[hand_label]

        # Check if wrist is within the zone (with margin)
        x_in_zone = (zone['x_min'] - self.active_zone_margin <= wrist.x <=
                     zone['x_max'] + self.active_zone_margin)
        y_in_zone = (zone['y_min'] - self.active_zone_margin <= wrist.y <=
                     zone['y_max'] + self.active_zone_margin)

        return x_in_zone and y_in_zone

    def get_hand_roi_status(self, hand_label):
        """Get ROI status for a hand (in_zone, out_of_zone)"""
        if hand_label not in self.hand_data:
            return 'not_detected'

        hand_landmarks = self.hand_data[hand_label]['landmarks']
        if self.is_hand_in_roi(hand_landmarks, hand_label):
            return 'in_zone'
        else:
            return 'out_of_zone'

=======
>>>>>>> 9178300 (new branch)
    def process_frame(self, frame):
        """Process a frame and detect hands"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False

        # Process the frame
        self.results = self.hands.process(rgb_frame)

        # Convert back to BGR for OpenCV
        rgb_frame.flags.writeable = True

        # Update hand data
        self.hand_data = {}

        if self.results.multi_hand_landmarks:
            for idx, (hand_landmarks, handedness) in enumerate(
                zip(self.results.multi_hand_landmarks, self.results.multi_handedness)
            ):
                # Determine which hand (Left or Right)
                hand_label = handedness.classification[0].label

<<<<<<< HEAD
                # Check if hand is in ROI
                in_roi = self.is_hand_in_roi(hand_landmarks, hand_label)

                # Get hand center (average of all landmarks)
                center_x = sum([lm.x for lm in hand_landmarks.landmark]) / 21
                center_y = sum([lm.y for lm in hand_landmarks.landmark]) / 21

=======
>>>>>>> 9178300 (new branch)
                # Store landmark data
                self.hand_data[hand_label] = {
                    'landmarks': hand_landmarks,
                    'handedness': handedness,
<<<<<<< HEAD
                    'in_roi': in_roi,
                    'center_x': center_x,
                    'center_y': center_y,
=======
>>>>>>> 9178300 (new branch)
                    'wrist_y': hand_landmarks.landmark[0].y,
                    'index_tip_y': hand_landmarks.landmark[8].y,
                    'middle_tip_y': hand_landmarks.landmark[12].y,
                    'ring_tip_y': hand_landmarks.landmark[16].y,
                    'pinky_tip_y': hand_landmarks.landmark[20].y,
                    'thumb_tip': hand_landmarks.landmark[4],
                    'index_tip': hand_landmarks.landmark[8],
                    'middle_tip': hand_landmarks.landmark[12],
                    'ring_tip': hand_landmarks.landmark[16],
                    'pinky_tip': hand_landmarks.landmark[20],
                }

        return self.hand_data

<<<<<<< HEAD
    def draw_roi_zones(self, frame):
        """Draw ROI zones on frame"""
        if not self.enable_roi:
            return frame

        h, w = frame.shape[:2]

        for hand_label, zone in self.roi_zones.items():
            # Calculate pixel coordinates
            x1 = int(zone['x_min'] * w)
            x2 = int(zone['x_max'] * w)
            y1 = int(zone['y_min'] * h)
            y2 = int(zone['y_max'] * h)

            # Check if hand is in this zone
            hand_in_zone = hand_label in self.hand_data and self.hand_data[hand_label].get('in_roi', False)

            # Draw zone with different color if hand is active
            if hand_in_zone:
                color = zone['color']
                thickness = 3
                alpha = 0.3
            else:
                color = tuple(int(c * 0.5) for c in zone['color'])
                thickness = 2
                alpha = 0.15

            # Draw semi-transparent overlay
            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            # Draw border
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            # Draw zone label
            label = zone['name']
            status = ""
            if hand_in_zone:
                status = " [ACTIVE]"

            text = f"{label}{status}"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = x1 + (x2 - x1 - text_size[0]) // 2
            text_y = y1 + 30

            # Draw text background
            cv2.rectangle(frame, (text_x - 5, text_y - 25),
                         (text_x + text_size[0] + 5, text_y + 5),
                         (0, 0, 0), -1)
            cv2.putText(frame, text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            # Draw hand position indicator if in zone
            if hand_in_zone:
                hand_data = self.hand_data[hand_label]
                center_x = int(hand_data['center_x'] * w)
                center_y = int(hand_data['center_y'] * h)

                # Draw crosshair
                cv2.circle(frame, (center_x, center_y), 10, color, 2)
                cv2.line(frame, (center_x - 15, center_y), (center_x + 15, center_y), color, 2)
                cv2.line(frame, (center_x, center_y - 15), (center_x, center_y + 15), color, 2)

        return frame

    def draw_landmarks(self, frame):
        """Draw hand landmarks on frame"""
        if self.results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(self.results.multi_hand_landmarks):
                # Get hand label to determine color
                hand_label = self.results.multi_handedness[idx].classification[0].label

                # Choose color based on ROI zone
                if hand_label in self.roi_zones:
                    color = self.roi_zones[hand_label]['color']
                    # Convert to normalized RGB for MediaPipe
                    landmark_style = self.mp_drawing.DrawingSpec(
                        color=color, thickness=2, circle_radius=3
                    )
                    connection_style = self.mp_drawing.DrawingSpec(
                        color=color, thickness=2
                    )
                else:
                    landmark_style = self.mp_drawing_styles.get_default_hand_landmarks_style()
                    connection_style = self.mp_drawing_styles.get_default_hand_connections_style()

=======
    def draw_landmarks(self, frame):
        """Draw hand landmarks on frame"""
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
>>>>>>> 9178300 (new branch)
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
<<<<<<< HEAD
                    landmark_style,
                    connection_style
                )

                # Draw warning if hand is out of ROI
                if hand_label in self.hand_data and not self.hand_data[hand_label].get('in_roi', True):
                    wrist = hand_landmarks.landmark[0]
                    h, w = frame.shape[:2]
                    x = int(wrist.x * w)
                    y = int(wrist.y * h)

                    # Draw warning
                    cv2.putText(frame, "OUT OF ZONE!", (x - 60, y - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.circle(frame, (x, y), 15, (0, 0, 255), 3)

=======
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
>>>>>>> 9178300 (new branch)
        return frame

    def _smooth_value(self, key, new_value):
        """Apply exponential smoothing to a value"""
        if key not in self.prev_hand_positions:
            self.prev_hand_positions[key] = new_value
            return new_value

        # Exponential smoothing: smoothed = alpha * new + (1 - alpha) * old
        smoothed = (self.smoothing_factor * new_value +
                   (1 - self.smoothing_factor) * self.prev_hand_positions[key])
        self.prev_hand_positions[key] = smoothed
        return smoothed

    def get_hand_height(self, hand_label):
        """Get normalized hand height (0-1, where 1 is top of screen)"""
        if hand_label in self.hand_data:
            # Invert Y since MediaPipe Y is from top to bottom
            raw_height = 1.0 - self.hand_data[hand_label]['wrist_y']
            # Apply smoothing
            return self._smooth_value(f'{hand_label}_height', raw_height)
        return 0.5

    def get_pinch_distance(self, hand_label):
        """Calculate distance between thumb and index finger (for volume control)"""
        if hand_label in self.hand_data:
            thumb = self.hand_data[hand_label]['thumb_tip']
            index = self.hand_data[hand_label]['index_tip']

            # Calculate Euclidean distance
            distance = np.sqrt(
                (thumb.x - index.x)**2 +
                (thumb.y - index.y)**2 +
                (thumb.z - index.z)**2
            )
            # Apply smoothing
            return self._smooth_value(f'{hand_label}_pinch', distance)
        return 0.1

    def get_fingers_extended(self, hand_label):
        """Check which fingers are extended (for drum pattern control)"""
        if hand_label not in self.hand_data:
            return [False, False, False, False, False]

        hand = self.hand_data[hand_label]
        landmarks = hand['landmarks'].landmark

        # Thumb: compare tip to MCP joint
        thumb_extended = landmarks[4].x < landmarks[3].x if hand_label == "Right" else landmarks[4].x > landmarks[3].x

        # Other fingers: compare tip Y to PIP joint Y
        index_extended = landmarks[8].y < landmarks[6].y
        middle_extended = landmarks[12].y < landmarks[10].y
        ring_extended = landmarks[16].y < landmarks[14].y
        pinky_extended = landmarks[20].y < landmarks[18].y

        return [thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended]

    def release(self):
        """Release resources"""
        self.hands.close()
