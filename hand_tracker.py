import cv2
import mediapipe as mp
import numpy as np


class HandTracker:
    def __init__(self):
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

                self.hand_data[hand_label] = {
                    'landmarks': hand_landmarks,
                    'handedness': handedness,
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

    def draw_landmarks(self, frame):
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style()
                )
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

    def release(self):
        self.hands.close()
