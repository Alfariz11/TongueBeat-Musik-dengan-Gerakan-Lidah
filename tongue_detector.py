"""
Tongue Tip Detection Module using MediaPipe Face Mesh
Detects and tracks tongue tip position for drum control
"""

import cv2
import mediapipe as mp
import numpy as np


class TongueDetector:
    """
    Detects tongue tip position using MediaPipe Face Mesh landmarks
    """

    def __init__(self, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        """
        Initialize MediaPipe Face Mesh

        Args:
            min_detection_confidence: Minimum confidence for face detection
            min_tracking_confidence: Minimum confidence for landmark tracking
        """
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )

        # MediaPipe Face Mesh LIPS landmarks (from FACEMESH_LIPS)
        # Complete lips contour for accurate mouth region extraction
        self.lips_indices = [
            61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291,
            185, 40, 39, 37, 0, 267, 269, 270, 409,
            78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308,
            191, 80, 81, 82, 13, 312, 311, 310, 415
        ]

        # Upper lip landmarks (outer contour)
        self.upper_lip_indices = [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291]
        # Lower lip landmarks (outer contour)
        self.lower_lip_indices = [146, 91, 181, 84, 17, 314, 405, 321, 375, 291]
        # Inner mouth landmarks (where tongue appears)
        self.inner_mouth_indices = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]

        # Key reference points
        self.upper_lip_center = 13   # Upper lip center
        self.lower_lip_center = 14   # Lower lip center (tongue tip often appears here)
        self.mouth_left = 61         # Left mouth corner
        self.mouth_right = 291       # Right mouth corner

        # ORB detector for blob-based tongue detection (more accurate)
        self.orb = cv2.ORB_create()
        self.use_blob_detection = True  # Use blob detection for better accuracy
        self.show_debug_window = False  # Show preprocessing debug window

        self.tongue_detected = False
        self.tongue_position = None
        self.mouth_open_threshold = 0.015  # Relative to face size (lowered for better detection)

        # Store preprocessed images for debugging
        self.debug_mouth_roi = None
        self.debug_processed = None
        self.debug_mask = None

        # Smoothing with EMA (Exponential Moving Average)
        self.smoothed_tongue_x = None
        self.smoothed_tongue_y = None
        self.ema_alpha = 0.3  # Lower = more smoothing (0.1-0.5 recommended)

        # Multi-frame confidence for direction
        self.direction_history = []
        self.confidence_frames = 3  # Require same direction for 3 frames
        self.max_history = 5  # Keep last 5 frames

    def detect_face_landmarks(self, frame):
        """
        Detect facial landmarks from frame

        Args:
            frame: Input video frame (BGR format)

        Returns:
            landmarks: List of facial landmark coordinates, or None if no face detected
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process the frame
        results = self.face_mesh.process(rgb_frame)

        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0]
        return None

    def smooth_tongue_position(self, new_x, new_y):
        """
        Apply EMA smoothing to tongue position for stable tracking

        Args:
            new_x: New x coordinate
            new_y: New y coordinate

        Returns:
            smoothed_x, smoothed_y: Smoothed coordinates
        """
        if self.smoothed_tongue_x is None:
            # First detection, initialize
            self.smoothed_tongue_x = new_x
            self.smoothed_tongue_y = new_y
        else:
            # Apply EMA: smoothed = alpha * new + (1 - alpha) * smoothed
            self.smoothed_tongue_x = self.ema_alpha * new_x + (1 - self.ema_alpha) * self.smoothed_tongue_x
            self.smoothed_tongue_y = self.ema_alpha * new_y + (1 - self.ema_alpha) * self.smoothed_tongue_y

        return int(self.smoothed_tongue_x), int(self.smoothed_tongue_y)

    def get_confident_direction(self, current_direction):
        """
        Apply multi-frame confidence to direction detection

        Args:
            current_direction: Direction detected in current frame

        Returns:
            confident_direction: Direction with confidence, or 'none'
        """
        # Add current direction to history
        self.direction_history.append(current_direction)

        # Keep only recent history
        if len(self.direction_history) > self.max_history:
            self.direction_history.pop(0)

        # Check if we have enough frames
        if len(self.direction_history) < self.confidence_frames:
            return 'none'

        # Get last N frames for confidence check
        recent_directions = self.direction_history[-self.confidence_frames:]

        # Count occurrences
        direction_counts = {}
        for d in recent_directions:
            direction_counts[d] = direction_counts.get(d, 0) + 1

        # Find most common direction
        most_common = max(direction_counts.items(), key=lambda x: x[1])
        direction, count = most_common

        # Require majority (at least 2 out of 3 frames)
        if count >= (self.confidence_frames - 1) and direction != 'none':
            return direction

        return 'none'

    def extract_mouth_region(self, frame, landmarks):
        """
        Extract INNER mouth region from frame using landmarks
        Focuses only on the area inside lips to avoid lipstick interference

        Args:
            frame: Input frame
            landmarks: MediaPipe face landmarks

        Returns:
            mouth_roi: Cropped inner mouth region
            roi_info: Dictionary with ROI coordinates for mapping back
        """
        h, w = frame.shape[:2]

        # Get INNER mouth landmarks only (not outer lips)
        inner_mouth_points = []
        for idx in self.inner_mouth_indices:
            lm = landmarks.landmark[idx]
            x, y = int(lm.x * w), int(lm.y * h)
            inner_mouth_points.append((x, y))

        # Also include key reference points
        upper_lip = landmarks.landmark[self.upper_lip_center]
        lower_lip = landmarks.landmark[self.lower_lip_center]
        inner_mouth_points.append((int(upper_lip.x * w), int(upper_lip.y * h)))
        inner_mouth_points.append((int(lower_lip.x * w), int(lower_lip.y * h)))

        # Find bounding box of INNER mouth region
        inner_mouth_points = np.array(inner_mouth_points)
        x_min, y_min = np.min(inner_mouth_points, axis=0)
        x_max, y_max = np.max(inner_mouth_points, axis=0)

        # Smaller padding to focus on inner mouth only
        padding_x = int((x_max - x_min) * 0.1)
        padding_y = int((y_max - y_min) * 0.15)

        x_min = max(0, x_min - padding_x)
        y_min = max(0, y_min - padding_y)
        x_max = min(w, x_max + padding_x)
        y_max = min(h, y_max + padding_y)

        # Extract ROI
        mouth_roi = frame[y_min:y_max, x_min:x_max].copy()

        roi_info = {
            'x': x_min,
            'y': y_min,
            'w': x_max - x_min,
            'h': y_max - y_min,
            'inner_top': int(upper_lip.y * h) - y_min,  # Relative to ROI
            'inner_bottom': int(lower_lip.y * h) - y_min
        }

        return mouth_roi, roi_info

    def preprocess_for_tongue(self, mouth_roi):
        """
        Preprocess mouth ROI to highlight tongue and suppress lips/lipstick

        Args:
            mouth_roi: Extracted mouth region

        Returns:
            processed: Preprocessed image for better tongue detection
        """
        if mouth_roi is None or mouth_roi.size == 0:
            return None

        # Convert to multiple color spaces for better tongue segmentation
        hsv = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2HSV)
        ycrcb = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2YCrCb)

        # Tongue typically has:
        # - HSV: H: 0-20 (red-pink), S: 30-150, V: 80-220
        # - YCrCb: Cr channel is useful for detecting reddish tones
        # - Lipstick is usually more saturated and darker/brighter

        # Extract channels
        h, s, v = cv2.split(hsv)
        y, cr, cb = cv2.split(ycrcb)

        # Create mask for tongue-like colors
        # OPTIMIZED: Based on actual video analysis of user's tongue
        # These values are calibrated from analyzing real tongue samples
        lower_tongue_hsv = np.array([0, 74, 139])
        upper_tongue_hsv = np.array([16, 162, 208])
        tongue_mask_hsv = cv2.inRange(hsv, lower_tongue_hsv, upper_tongue_hsv)

        # Cr channel (YCrCb) - optimized for this specific use case
        # Tongue typically has Cr values between 142-179 (from video analysis)
        tongue_mask_cr = cv2.inRange(cr, 142, 179)

        # Combine masks
        tongue_mask = cv2.bitwise_or(tongue_mask_hsv, tongue_mask_cr)

        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        tongue_mask = cv2.morphologyEx(tongue_mask, cv2.MORPH_CLOSE, kernel)
        tongue_mask = cv2.morphologyEx(tongue_mask, cv2.MORPH_OPEN, kernel)

        # Apply mask to original
        masked = cv2.bitwise_and(mouth_roi, mouth_roi, mask=tongue_mask)

        # Enhance details
        try:
            enhanced = cv2.detailEnhance(masked, sigma_s=10, sigma_r=0.15)
        except:
            enhanced = masked

        return enhanced

    def detect_tongue_with_blob(self, mouth_roi, roi_info, landmarks, frame_shape):
        """
        Detect tongue tip using color segmentation + ORB blob detection

        Args:
            mouth_roi: Extracted mouth region
            roi_info: ROI coordinate information
            landmarks: MediaPipe face landmarks
            frame_shape: Original frame shape

        Returns:
            tongue_tip: (x, y) coordinates in original frame, or None
            is_detected: Boolean indicating detection success
        """
        if mouth_roi is None or mouth_roi.size == 0:
            return None, False

        h, w = frame_shape[:2]

        # Check mouth opening
        upper_lip = landmarks.landmark[self.upper_lip_center]
        lower_lip = landmarks.landmark[self.lower_lip_center]
        mouth_opening_px = abs((lower_lip.y - upper_lip.y) * h)

        # Require minimum mouth opening (8 pixels like original repo)
        if mouth_opening_px < 8:
            return None, False

        # Preprocess to highlight tongue and suppress lips
        processed = self.preprocess_for_tongue(mouth_roi)
        if processed is None:
            return None, False

        # Store for debugging
        if self.show_debug_window:
            self.debug_mouth_roi = mouth_roi.copy()
            self.debug_processed = processed.copy()

        # Convert to grayscale for ORB
        gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding to highlight tongue features
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Detect ORB keypoints on thresholded image
        keypoints = self.orb.detect(thresh, None)

        if not keypoints:
            # Fallback: try on original processed image
            keypoints = self.orb.detect(processed, None)

        if not keypoints:
            return None, False

        # Filter keypoints: only consider those in the inner mouth area
        # (below upper lip line, above lower lip line)
        valid_keypoints = []
        inner_top = roi_info.get('inner_top', 0)
        inner_bottom = roi_info.get('inner_bottom', mouth_roi.shape[0])

        for kp in keypoints:
            x_kp, y_kp = kp.pt
            # Only consider keypoints in the inner mouth region
            if inner_top < y_kp < inner_bottom:
                valid_keypoints.append(kp)

        if not valid_keypoints:
            return None, False

        # Find the keypoint with lowest y-coordinate (deepest point)
        # This is typically the tongue tip when mouth is open
        lowest_y = -1
        tongue_kp = None

        for kp in valid_keypoints:
            x_kp, y_kp = kp.pt
            if y_kp > lowest_y:
                lowest_y = y_kp
                tongue_kp = kp

        if tongue_kp is None or lowest_y < 1:
            return None, False

        # Map keypoint back to original frame coordinates
        tongue_x = int(tongue_kp.pt[0] + roi_info['x'])
        tongue_y = int(tongue_kp.pt[1] + roi_info['y'])

        return (tongue_x, tongue_y), True

    def calculate_mouth_opening(self, landmarks, frame_shape):
        """
        Calculate mouth opening distance

        Args:
            landmarks: MediaPipe face landmarks
            frame_shape: Shape of the video frame (height, width)

        Returns:
            mouth_opening: Normalized mouth opening distance
        """
        h, w = frame_shape[:2]

        # Get upper and lower lip center points
        upper_lip_center = landmarks.landmark[13]  # Upper lip center
        lower_lip_center = landmarks.landmark[14]  # Lower lip center

        # Calculate vertical distance
        mouth_opening = abs(upper_lip_center.y - lower_lip_center.y)

        return mouth_opening

    def detect_tongue_tip(self, landmarks, frame_shape, frame=None):
        """
        Detect tongue tip position from facial landmarks
        Uses blob detection for more accurate tongue tracking

        Args:
            landmarks: MediaPipe face landmarks
            frame_shape: Shape of the video frame (height, width, channels)
            frame: Optional - original frame for blob detection

        Returns:
            tongue_tip: (x, y) coordinates of tongue tip in pixel space, or None
            is_tongue_out: Boolean indicating if tongue is detected as out
        """
        h, w = frame_shape[:2]

        # Check if mouth is open enough
        mouth_opening = self.calculate_mouth_opening(landmarks, frame_shape)

        if mouth_opening < self.mouth_open_threshold:
            # Reset smoothing when tongue not detected
            self.smoothed_tongue_x = None
            self.smoothed_tongue_y = None
            self.tongue_detected = False
            return None, False

        tongue_tip = None
        is_detected = False

        # Try blob detection if frame is provided and enabled
        if self.use_blob_detection and frame is not None:
            try:
                mouth_roi, roi_info = self.extract_mouth_region(frame, landmarks)
                tongue_tip, is_detected = self.detect_tongue_with_blob(
                    mouth_roi, roi_info, landmarks, frame_shape
                )
            except Exception as e:
                # Fall back to landmark-based method if blob detection fails
                is_detected = False

        # Fallback to landmark-based detection
        if not is_detected:
            # Get mouth boundary landmarks
            upper_lip = landmarks.landmark[self.upper_lip_center]
            lower_lip = landmarks.landmark[self.lower_lip_center]
            left_mouth = landmarks.landmark[self.mouth_left]
            right_mouth = landmarks.landmark[self.mouth_right]

            # Calculate mouth center
            mouth_center_x = (left_mouth.x + right_mouth.x) / 2
            mouth_center_y = (upper_lip.y + lower_lip.y) / 2

            # Get all inner mouth points
            inner_mouth_points = []
            for idx in self.inner_mouth_indices:
                lm = landmarks.landmark[idx]
                inner_mouth_points.append((lm.x, lm.y, lm.z))

            if inner_mouth_points:
                # Find the point that is furthest from the mouth center
                max_distance = 0
                tongue_tip_norm = None

                for x, y, z in inner_mouth_points:
                    # Check if point is within reasonable mouth region
                    if (left_mouth.x - 0.03 < x < right_mouth.x + 0.03 and
                        upper_lip.y - 0.03 < y < lower_lip.y + 0.08):

                        # Calculate distance from mouth center
                        distance = np.sqrt((x - mouth_center_x)**2 + (y - mouth_center_y)**2)

                        if distance > max_distance:
                            max_distance = distance
                            tongue_tip_norm = (x, y, z)

                # Check if we found a significant tongue protrusion
                if tongue_tip_norm and max_distance > 0.01:
                    # Convert to pixel coordinates
                    tongue_tip_x = int(tongue_tip_norm[0] * w)
                    tongue_tip_y = int(tongue_tip_norm[1] * h)
                    tongue_tip = (tongue_tip_x, tongue_tip_y)
                    is_detected = True

        # Apply smoothing if detected
        if is_detected and tongue_tip:
            smoothed_x, smoothed_y = self.smooth_tongue_position(tongue_tip[0], tongue_tip[1])
            self.tongue_detected = True
            self.tongue_position = (smoothed_x, smoothed_y)
            return (smoothed_x, smoothed_y), True

        # Reset smoothing when tongue not detected
        self.smoothed_tongue_x = None
        self.smoothed_tongue_y = None
        self.tongue_detected = False
        return None, False

    def get_tongue_direction(self, landmarks, frame_shape, use_confidence=True, frame=None):
        """
        Determine tongue movement direction (left, right, up, down, center)

        Args:
            landmarks: MediaPipe face landmarks
            frame_shape: Shape of the video frame
            use_confidence: Whether to use multi-frame confidence (default: True)
            frame: Optional - original frame for blob detection

        Returns:
            direction: String indicating direction ('left', 'right', 'up', 'down', 'center', 'none')
        """
        tongue_tip, is_out = self.detect_tongue_tip(landmarks, frame_shape, frame)

        if not is_out or tongue_tip is None:
            current_direction = 'none'
        else:
            h, w = frame_shape[:2]

            # Get mouth center as reference (average of upper and lower lip + left and right corners)
            upper_lip = landmarks.landmark[self.upper_lip_center]
            lower_lip = landmarks.landmark[self.lower_lip_center]
            left_mouth = landmarks.landmark[self.mouth_left]
            right_mouth = landmarks.landmark[self.mouth_right]

            mouth_center_x = int(((left_mouth.x + right_mouth.x) / 2) * w)
            mouth_center_y = int(((upper_lip.y + lower_lip.y) / 2) * h)

            # Calculate relative position
            dx = tongue_tip[0] - mouth_center_x
            dy = tongue_tip[1] - mouth_center_y

            # Define thresholds for direction detection (in pixels)
            # Lowered thresholds for better sensitivity
            horizontal_threshold = w * 0.015  # 1.5% of frame width
            vertical_threshold = h * 0.015    # 1.5% of frame height

            # Determine primary direction based on which component is stronger
            if abs(dx) < horizontal_threshold and abs(dy) < vertical_threshold:
                current_direction = 'center'
            elif abs(dx) > abs(dy):
                # Horizontal movement is dominant
                current_direction = 'left' if dx < 0 else 'right'
            else:
                # Vertical movement is dominant
                current_direction = 'up' if dy < 0 else 'down'

        # Apply multi-frame confidence if enabled
        if use_confidence:
            return self.get_confident_direction(current_direction)
        else:
            return current_direction

    def draw_landmarks(self, frame, landmarks):
        """
        Draw facial landmarks on frame for visualization

        Args:
            frame: Input frame to draw on
            landmarks: MediaPipe face landmarks

        Returns:
            frame: Frame with landmarks drawn
        """
        h, w = frame.shape[:2]

        # Draw mouth region landmarks (outer lips)
        for idx in self.upper_lip_indices + self.lower_lip_indices:
            lm = landmarks.landmark[idx]
            x, y = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (x, y), 2, (0, 255, 0), -1)

        # Draw mouth center reference point
        upper_lip = landmarks.landmark[self.upper_lip_center]
        lower_lip = landmarks.landmark[self.lower_lip_center]
        left_mouth = landmarks.landmark[self.mouth_left]
        right_mouth = landmarks.landmark[self.mouth_right]

        mouth_center_x = int(((left_mouth.x + right_mouth.x) / 2) * w)
        mouth_center_y = int(((upper_lip.y + lower_lip.y) / 2) * h)
        cv2.circle(frame, (mouth_center_x, mouth_center_y), 5, (255, 255, 0), -1)

        # Draw mouth ROI bounding box if blob detection is enabled
        if self.use_blob_detection:
            try:
                mouth_roi, roi_info = self.extract_mouth_region(frame, landmarks)
                x, y, w_roi, h_roi = roi_info['x'], roi_info['y'], roi_info['w'], roi_info['h']
                cv2.rectangle(frame, (x, y), (x + w_roi, y + h_roi), (0, 255, 255), 1)
                cv2.putText(frame, "ROI", (x, y - 5),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
            except:
                pass

        # Draw tongue tip if detected
        if self.tongue_detected and self.tongue_position:
            # Draw line from mouth center to tongue tip
            cv2.line(frame, (mouth_center_x, mouth_center_y),
                    self.tongue_position, (255, 0, 255), 2)

            # Draw tongue tip with different color based on detection method
            color = (0, 0, 255) if self.use_blob_detection else (255, 0, 0)
            cv2.circle(frame, self.tongue_position, 8, color, -1)

            label = "TONGUE (BLOB)" if self.use_blob_detection else "TONGUE (LM)"
            cv2.putText(frame, label,
                       (self.tongue_position[0] - 50, self.tongue_position[1] - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 2)

        # Draw inner mouth landmarks for debugging (only if not using blob)
        if not self.use_blob_detection:
            for idx in self.inner_mouth_indices:
                lm = landmarks.landmark[idx]
                x, y = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (x, y), 3, (255, 0, 0), -1)

        return frame

    def release(self):
        """Release MediaPipe resources"""
        self.face_mesh.close()
