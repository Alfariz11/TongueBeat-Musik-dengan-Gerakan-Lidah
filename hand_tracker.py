import cv2
import mediapipe as mp
import numpy as np


class HandTracker:
    def __init__(self, enable_roi=True):
        self.mp_hands = mp.solutions.hands
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(
            model_complexity=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7,
            max_num_hands=2
        )

        self.results = None
        self.hand_data = {}

        self.smoothing_factor = 0.3
        self.prev_hand_positions = {}

        self.enable_roi = enable_roi
        self.roi_zones = {
            'Left': {
                'x_min': 0.0,
                'x_max': 0.5,
                'y_min': 0.1,
                'y_max': 0.9,
                'color': (100, 200, 255),
                'name': 'ARPEGGIATOR ZONE'
            },
            'Right': {
                'x_min': 0.5,
                'x_max': 1.0,
                'y_min': 0.1,
                'y_max': 0.9,
                'color': (255, 100, 150),
                'name': 'DRUM ZONE'
            }
        }

        self.active_zone_margin = 0.05

    def is_hand_in_roi(self, hand_landmarks, hand_label):
        if not self.enable_roi:
            return True

        wrist = hand_landmarks.landmark[0]

        if hand_label not in self.roi_zones:
            return True

        zone = self.roi_zones[hand_label]

        x_in_zone = (zone['x_min'] - self.active_zone_margin <= wrist.x <=
                     zone['x_max'] + self.active_zone_margin)
        y_in_zone = (zone['y_min'] - self.active_zone_margin <= wrist.y <=
                     zone['y_max'] + self.active_zone_margin)

        return x_in_zone and y_in_zone

    def get_hand_roi_status(self, hand_label):
        if hand_label not in self.hand_data:
            return 'not_detected'

        hand_landmarks = self.hand_data[hand_label]['landmarks']
        if self.is_hand_in_roi(hand_landmarks, hand_label):
            return 'in_zone'
        else:
            return 'out_of_zone'

    def process_frame(self, frame):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        rgb_frame.flags.writeable = False

        self.results = self.hands.process(rgb_frame)

        rgb_frame.flags.writeable = True

        self.hand_data = {}

        if self.results.multi_hand_landmarks:
            for idx, (hand_landmarks, handedness) in enumerate(
                zip(self.results.multi_hand_landmarks, self.results.multi_handedness)
            ):
                hand_label = handedness.classification[0].label

                in_roi = self.is_hand_in_roi(hand_landmarks, hand_label)

                center_x = sum([lm.x for lm in hand_landmarks.landmark]) / 21
                center_y = sum([lm.y for lm in hand_landmarks.landmark]) / 21

                self.hand_data[hand_label] = {
                    'landmarks': hand_landmarks,
                    'handedness': handedness,
                    'in_roi': in_roi,
                    'center_x': center_x,
                    'center_y': center_y,
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

    def draw_roi_zones(self, frame):
        if not self.enable_roi:
            return frame

        h, w = frame.shape[:2]

        for hand_label, zone in self.roi_zones.items():
            x1 = int(zone['x_min'] * w)
            x2 = int(zone['x_max'] * w)
            y1 = int(zone['y_min'] * h)
            y2 = int(zone['y_max'] * h)

            hand_in_zone = hand_label in self.hand_data and self.hand_data[hand_label].get('in_roi', False)

            if hand_in_zone:
                color = zone['color']
                thickness = 3
                alpha = 0.3
            else:
                color = tuple(int(c * 0.5) for c in zone['color'])
                thickness = 2
                alpha = 0.15

            overlay = frame.copy()
            cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
            cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

            label = zone['name']
            status = ""
            if hand_in_zone:
                status = " [ACTIVE]"

            text = f"{label}{status}"
            text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
            text_x = x1 + (x2 - x1 - text_size[0]) // 2
            text_y = y1 + 30

            cv2.rectangle(frame, (text_x - 5, text_y - 25),
                         (text_x + text_size[0] + 5, text_y + 5),
                         (0, 0, 0), -1)
            cv2.putText(frame, text, (text_x, text_y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

            if hand_in_zone:
                hand_data = self.hand_data[hand_label]
                center_x = int(hand_data['center_x'] * w)
                center_y = int(hand_data['center_y'] * h)

                cv2.circle(frame, (center_x, center_y), 10, color, 2)
                cv2.line(frame, (center_x - 15, center_y), (center_x + 15, center_y), color, 2)
                cv2.line(frame, (center_x, center_y - 15), (center_x, center_y + 15), color, 2)

        return frame

    def draw_landmarks(self, frame):
        if self.results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(self.results.multi_hand_landmarks):
                hand_label = self.results.multi_handedness[idx].classification[0].label

                if hand_label in self.roi_zones:
                    color = self.roi_zones[hand_label]['color']
                    landmark_style = self.mp_drawing.DrawingSpec(
                        color=color, thickness=2, circle_radius=3
                    )
                    connection_style = self.mp_drawing.DrawingSpec(
                        color=color, thickness=2
                    )
                else:
                    landmark_style = self.mp_drawing_styles.get_default_hand_landmarks_style()
                    connection_style = self.mp_drawing_styles.get_default_hand_connections_style()

                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    landmark_style,
                    connection_style
                )

                if hand_label in self.hand_data and not self.hand_data[hand_label].get('in_roi', True):
                    wrist = hand_landmarks.landmark[0]
                    h, w = frame.shape[:2]
                    x = int(wrist.x * w)
                    y = int(wrist.y * h)

                    cv2.putText(frame, "OUT OF ZONE!", (x - 60, y - 20),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.circle(frame, (x, y), 15, (0, 0, 255), 3)

        return frame

    def _smooth_value(self, key, new_value):
        if key not in self.prev_hand_positions:
            self.prev_hand_positions[key] = new_value
            return new_value

        smoothed = (self.smoothing_factor * new_value +
                   (1 - self.smoothing_factor) * self.prev_hand_positions[key])
        self.prev_hand_positions[key] = smoothed
        return smoothed

    def get_hand_height(self, hand_label):
        if hand_label in self.hand_data:
            raw_height = 1.0 - self.hand_data[hand_label]['wrist_y']
            return self._smooth_value(f'{hand_label}_height', raw_height)
        return 0.5

    def get_pinch_distance(self, hand_label):
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

    def get_rotation_angle(self, hand_label):
        if hand_label not in self.hand_data:
            return 0.0

        thumb = self.hand_data[hand_label]['thumb_tip']
        index = self.hand_data[hand_label]['index_tip']

        dx = index.x - thumb.x
        dy = index.y - thumb.y
        angle = np.degrees(np.arctan2(dy, dx))

        key = f"{hand_label}_rotation_angle"
        prev_angle = self.prev_hand_positions.get(key, angle)

        delta = angle - prev_angle
        if delta > 180:
            delta -= 360
        elif delta < -180:
            delta += 360

        self.prev_hand_positions[key] = angle

        delta_smoothed = self._smooth_value(f"{hand_label}_rot_delta", delta)
        return delta_smoothed

    def get_fingers_extended(self, hand_label):
        if hand_label not in self.hand_data:
            return [False, False, False, False, False]

        hand = self.hand_data[hand_label]
        landmarks = hand['landmarks'].landmark

        thumb_extended = landmarks[4].x < landmarks[3].x if hand_label == "Right" else landmarks[4].x > landmarks[3].x

        index_extended = landmarks[8].y < landmarks[6].y
        middle_extended = landmarks[12].y < landmarks[10].y
        ring_extended = landmarks[16].y < landmarks[14].y
        pinky_extended = landmarks[20].y < landmarks[18].y

        return [thumb_extended, index_extended, middle_extended, ring_extended, pinky_extended]

    def is_fist(self, hand_label):
        if hand_label not in self.hand_data:
            return False

        fingers = self.get_fingers_extended(hand_label)
        extended_count = sum(fingers)
        
        return extended_count == 0 or extended_count == 1

    def release(self):
        self.hands.close()

