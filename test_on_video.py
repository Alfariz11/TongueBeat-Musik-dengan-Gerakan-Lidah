"""
Test tongue detection on recorded video
"""

import cv2
import numpy as np
from tongue_detector import TongueDetector

def test_on_video(video_path, show_debug=True):
    """
    Test tongue detection on video file

    Args:
        video_path: Path to video file
        show_debug: Show debug visualizations
    """
    print(f"Testing on video: {video_path}")

    # Initialize detector
    detector = TongueDetector(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    detector.show_debug_window = show_debug

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
    print(f"  Duration: {frame_count/fps:.2f}s")
    print("\nPress 'Q' to quit, 'SPACE' to pause/resume")

    frame_idx = 0
    paused = False
    detection_count = 0

    while True:
        if not paused:
            ret, frame = cap.read()
            if not ret:
                break

            frame_idx += 1

        # Detect face landmarks
        landmarks = detector.detect_face_landmarks(frame)

        if landmarks:
            # Get tongue direction
            direction = detector.get_tongue_direction(
                landmarks, frame.shape, use_confidence=True, frame=frame
            )

            # Get tongue position
            tongue_pos, is_out = detector.detect_tongue_tip(landmarks, frame.shape, frame)

            if is_out:
                detection_count += 1

            # Draw landmarks
            frame = detector.draw_landmarks(frame, landmarks)

            # Draw direction info
            if direction != 'none':
                cv2.putText(frame, f"Direction: {direction.upper()}",
                           (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5,
                           (0, 255, 0), 3)

        # Draw frame info
        cv2.putText(frame, f"Frame: {frame_idx}/{frame_count}",
                   (10, height - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                   (255, 255, 255), 2)
        cv2.putText(frame, f"Detections: {detection_count}",
                   (10, height - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                   (255, 255, 255), 2)

        if paused:
            cv2.putText(frame, "PAUSED",
                       (width//2 - 100, height//2), cv2.FONT_HERSHEY_SIMPLEX, 2,
                       (0, 0, 255), 4)

        # Display
        cv2.imshow("Tongue Detection Test", frame)

        # Show debug window if enabled
        if detector.show_debug_window and detector.debug_mouth_roi is not None:
            debug_roi = detector.debug_mouth_roi
            debug_processed = detector.debug_processed

            # Resize for better visibility
            scale = 4
            debug_roi_large = cv2.resize(debug_roi, None, fx=scale, fy=scale,
                                        interpolation=cv2.INTER_NEAREST)
            debug_processed_large = cv2.resize(debug_processed, None, fx=scale, fy=scale,
                                              interpolation=cv2.INTER_NEAREST)

            # Stack horizontally
            debug_view = np.hstack([debug_roi_large, debug_processed_large])

            # Add labels
            cv2.putText(debug_view, "Original ROI", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)
            cv2.putText(debug_view, "Tongue Segmented",
                       (debug_roi_large.shape[1] + 10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 0), 2)

            cv2.imshow("Tongue Detection Debug", debug_view)

        # Handle keyboard
        key = cv2.waitKey(1 if not paused else 0) & 0xFF
        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord(' '):
            paused = not paused
            print(f"{'Paused' if paused else 'Resumed'}")
        elif key == ord('d') or key == ord('D'):
            detector.show_debug_window = not detector.show_debug_window
            if not detector.show_debug_window:
                cv2.destroyWindow("Tongue Detection Debug")
            print(f"Debug window: {'ON' if detector.show_debug_window else 'OFF'}")

    cap.release()
    cv2.destroyAllWindows()

    print(f"\nTest complete!")
    print(f"  Total frames: {frame_idx}")
    print(f"  Tongue detections: {detection_count}")
    print(f"  Detection rate: {detection_count/frame_idx*100:.1f}%")


if __name__ == "__main__":
    video_path = "video/20251102_011859.mp4"
    test_on_video(video_path, show_debug=True)
