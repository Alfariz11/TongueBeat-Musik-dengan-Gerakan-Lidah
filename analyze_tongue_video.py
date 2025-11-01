"""
Analyze tongue video to determine optimal ROI and color ranges
"""

import cv2
import numpy as np
import mediapipe as mp
import os

def analyze_video(video_path):
    """
    Analyze video to find optimal tongue detection parameters
    """
    print(f"Analyzing video: {video_path}")

    # Initialize MediaPipe Face Mesh
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return

    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    print(f"Video properties:")
    print(f"  Resolution: {width}x{height}")
    print(f"  FPS: {fps}")
    print(f"  Frame count: {frame_count}")
    print(f"  Duration: {frame_count/fps:.2f}s")

    # Inner mouth landmarks
    inner_mouth_indices = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308]
    upper_lip_center = 13
    lower_lip_center = 14
    mouth_left = 61
    mouth_right = 291

    # Create output directory
    output_dir = "video_analysis"
    os.makedirs(output_dir, exist_ok=True)

    # Sample frames (every N frames)
    sample_interval = max(1, frame_count // 30)  # Get ~30 samples

    print(f"\nAnalyzing frames (sampling every {sample_interval} frames)...")

    frame_idx = 0
    sample_idx = 0

    # Store color statistics
    hsv_colors = []
    ycrcb_colors = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_idx % sample_interval == 0:
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_mesh.process(rgb_frame)

            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                h, w = frame.shape[:2]

                # Get mouth landmarks
                upper_lip = landmarks.landmark[upper_lip_center]
                lower_lip = landmarks.landmark[lower_lip_center]
                left_mouth = landmarks.landmark[mouth_left]
                right_mouth = landmarks.landmark[mouth_right]

                # Check mouth opening
                mouth_opening = abs(upper_lip.y - lower_lip.y)

                if mouth_opening > 0.02:  # Mouth is open
                    # Extract inner mouth region
                    inner_mouth_points = []
                    for idx in inner_mouth_indices:
                        lm = landmarks.landmark[idx]
                        x, y = int(lm.x * w), int(lm.y * h)
                        inner_mouth_points.append((x, y))

                    inner_mouth_points.append((int(upper_lip.x * w), int(upper_lip.y * h)))
                    inner_mouth_points.append((int(lower_lip.x * w), int(lower_lip.y * h)))

                    inner_mouth_points = np.array(inner_mouth_points)
                    x_min, y_min = np.min(inner_mouth_points, axis=0)
                    x_max, y_max = np.max(inner_mouth_points, axis=0)

                    # Add padding
                    padding_x = int((x_max - x_min) * 0.1)
                    padding_y = int((y_max - y_min) * 0.15)

                    x_min = max(0, x_min - padding_x)
                    y_min = max(0, y_min - padding_y)
                    x_max = min(w, x_max + padding_x)
                    y_max = min(h, y_max + padding_y)

                    # Extract ROI
                    mouth_roi = frame[y_min:y_max, x_min:x_max].copy()

                    if mouth_roi.size > 0:
                        # Analyze colors in ROI
                        hsv = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2HSV)
                        ycrcb = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2YCrCb)

                        # Get center region (likely to contain tongue)
                        roi_h, roi_w = mouth_roi.shape[:2]
                        center_y_start = int(roi_h * 0.4)
                        center_y_end = int(roi_h * 0.9)
                        center_x_start = int(roi_w * 0.3)
                        center_x_end = int(roi_w * 0.7)

                        center_roi = mouth_roi[center_y_start:center_y_end, center_x_start:center_x_end]

                        if center_roi.size > 0:
                            hsv_center = cv2.cvtColor(center_roi, cv2.COLOR_BGR2HSV)
                            ycrcb_center = cv2.cvtColor(center_roi, cv2.COLOR_BGR2YCrCb)

                            # Calculate mean colors
                            hsv_mean = cv2.mean(hsv_center)[:3]
                            ycrcb_mean = cv2.mean(ycrcb_center)[:3]

                            hsv_colors.append(hsv_mean)
                            ycrcb_colors.append(ycrcb_mean)

                        # Draw visualization
                        vis_frame = frame.copy()

                        # Draw mouth landmarks
                        for idx in inner_mouth_indices:
                            lm = landmarks.landmark[idx]
                            x, y = int(lm.x * w), int(lm.y * h)
                            cv2.circle(vis_frame, (x, y), 2, (0, 255, 0), -1)

                        # Draw ROI box
                        cv2.rectangle(vis_frame, (x_min, y_min), (x_max, y_max), (0, 255, 255), 2)

                        # Draw center region
                        cv2.rectangle(vis_frame,
                                    (x_min + center_x_start, y_min + center_y_start),
                                    (x_min + center_x_end, y_min + center_y_end),
                                    (255, 0, 255), 2)

                        # Save frame
                        cv2.imwrite(f"{output_dir}/frame_{sample_idx:03d}.jpg", vis_frame)
                        cv2.imwrite(f"{output_dir}/roi_{sample_idx:03d}.jpg", mouth_roi)

                        # Apply current segmentation
                        hsv_roi = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2HSV)
                        ycrcb_roi = cv2.cvtColor(mouth_roi, cv2.COLOR_BGR2YCrCb)
                        y, cr, cb = cv2.split(ycrcb_roi)

                        # Current thresholds
                        lower_tongue_hsv = np.array([0, 20, 60])
                        upper_tongue_hsv = np.array([25, 180, 255])
                        tongue_mask_hsv = cv2.inRange(hsv_roi, lower_tongue_hsv, upper_tongue_hsv)

                        tongue_mask_cr = cv2.inRange(cr, 135, 185)

                        tongue_mask = cv2.bitwise_or(tongue_mask_hsv, tongue_mask_cr)

                        # Save masks
                        cv2.imwrite(f"{output_dir}/mask_hsv_{sample_idx:03d}.jpg", tongue_mask_hsv)
                        cv2.imwrite(f"{output_dir}/mask_cr_{sample_idx:03d}.jpg", tongue_mask_cr)
                        cv2.imwrite(f"{output_dir}/mask_combined_{sample_idx:03d}.jpg", tongue_mask)

                        masked = cv2.bitwise_and(mouth_roi, mouth_roi, mask=tongue_mask)
                        cv2.imwrite(f"{output_dir}/segmented_{sample_idx:03d}.jpg", masked)

                        sample_idx += 1
                        print(f"  Processed frame {frame_idx}/{frame_count} (sample {sample_idx})")

        frame_idx += 1

    cap.release()
    face_mesh.close()

    # Analyze color statistics
    if hsv_colors:
        hsv_colors = np.array(hsv_colors)
        ycrcb_colors = np.array(ycrcb_colors)

        print("\n" + "="*60)
        print("COLOR ANALYSIS RESULTS")
        print("="*60)

        print("\nHSV Color Range (from tongue samples):")
        h_min, s_min, v_min = np.min(hsv_colors, axis=0)
        h_max, s_max, v_max = np.max(hsv_colors, axis=0)
        h_mean, s_mean, v_mean = np.mean(hsv_colors, axis=0)

        print(f"  Hue:        min={h_min:.1f}, max={h_max:.1f}, mean={h_mean:.1f}")
        print(f"  Saturation: min={s_min:.1f}, max={s_max:.1f}, mean={s_mean:.1f}")
        print(f"  Value:      min={v_min:.1f}, max={v_max:.1f}, mean={v_mean:.1f}")

        print("\nYCrCb Color Range (from tongue samples):")
        y_min, cr_min, cb_min = np.min(ycrcb_colors, axis=0)
        y_max, cr_max, cb_max = np.max(ycrcb_colors, axis=0)
        y_mean, cr_mean, cb_mean = np.mean(ycrcb_colors, axis=0)

        print(f"  Y:  min={y_min:.1f}, max={y_max:.1f}, mean={y_mean:.1f}")
        print(f"  Cr: min={cr_min:.1f}, max={cr_max:.1f}, mean={cr_mean:.1f}")
        print(f"  Cb: min={cb_min:.1f}, max={cb_max:.1f}, mean={cb_mean:.1f}")

        print("\n" + "="*60)
        print("RECOMMENDED THRESHOLD VALUES")
        print("="*60)

        # Add margins for robustness
        h_lower = max(0, h_min - 5)
        h_upper = min(180, h_max + 5)
        s_lower = max(0, s_min - 20)
        s_upper = min(255, s_max + 20)
        v_lower = max(0, v_min - 20)
        v_upper = min(255, v_max + 20)

        cr_lower = max(0, cr_min - 10)
        cr_upper = min(255, cr_max + 10)

        print("\nPython code to use in tongue_detector.py:")
        print(f"""
# HSV thresholds (line ~237-238)
lower_tongue_hsv = np.array([{h_lower:.0f}, {s_lower:.0f}, {v_lower:.0f}])
upper_tongue_hsv = np.array([{h_upper:.0f}, {s_upper:.0f}, {v_upper:.0f}])

# Cr channel threshold (line ~243)
tongue_mask_cr = cv2.inRange(cr, {cr_lower:.0f}, {cr_upper:.0f})
""")

        print("\n" + "="*60)
        print(f"Analysis complete! Check '{output_dir}/' for visualizations")
        print("="*60)


if __name__ == "__main__":
    video_path = "video/20251102_011859.mp4"
    analyze_video(video_path)
