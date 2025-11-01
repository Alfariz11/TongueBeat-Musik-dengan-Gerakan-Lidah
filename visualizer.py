"""
Audio Reactive Visualizer
Creates visual feedback for the music generation
"""
import cv2
import numpy as np
from collections import deque


class Visualizer:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height

        # Visual parameters
        self.bg_color = (20, 20, 30)
        self.arp_color = (100, 200, 255)
        self.drum_color = (255, 100, 150)

        # History for waveform effect
        self.arp_history = deque(maxlen=100)
        self.drum_history = deque(maxlen=16)

        # Particle system for visual effects
        self.particles = []

    def draw_background(self, frame):
        """Draw background with gradient"""
        frame[:] = self.bg_color
        return frame

    def draw_hand_zones(self, frame, hand_data):
        """Draw visual zones for each hand"""
        h, w = frame.shape[:2]

        # Draw left side for Hand #1 (Arpeggiator)
        cv2.rectangle(frame, (0, 0), (w//2, h), (40, 40, 60), -1)
        cv2.putText(frame, "HAND #1: ARPEGGIATOR", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150, 150, 200), 2)
        cv2.putText(frame, "Raise hand = Higher pitch", (20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 150), 1)
        cv2.putText(frame, "Pinch = Volume control", (20, 95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 150), 1)

        # Draw right side for Hand #2 (Drums)
        cv2.rectangle(frame, (w//2, 0), (w, h), (60, 40, 40), -1)
        cv2.putText(frame, "HAND #2: DRUMS", (w//2 + 20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 150, 150), 2)
        cv2.putText(frame, "Raise fingers = Change pattern", (w//2 + 20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 120, 120), 1)

        return frame

    def draw_arpeggiator_visualization(self, frame, arp_data, hand_height, volume):
        """Draw visualization for arpeggiator"""
        h, w = frame.shape[:2]

        if arp_data:
            self.arp_history.append({
                'note': arp_data['note'],
                'volume': arp_data['volume'],
                'octave': arp_data['octave']
            })

            # Create particle effect
            x = w // 4
            y = int(h * (1 - hand_height))
            self.create_particles(x, y, self.arp_color, int(volume * 20))

        # Draw waveform history
        if len(self.arp_history) > 1:
            points = []
            for i, data in enumerate(self.arp_history):
                x = int((w // 2) * (i / len(self.arp_history)))
                note_normalized = (data['note'] - 57) / 24  # Normalize note range
                y = int(h - (h * note_normalized * 0.5) - 100)
                points.append((x, y))

            # Draw smooth curve
            if len(points) > 2:
                points_array = np.array(points, dtype=np.int32)
                cv2.polylines(frame, [points_array], False, self.arp_color, 3)

        # Draw hand height indicator
        hand_y = int(h * (1 - hand_height))
        cv2.line(frame, (10, hand_y), (w//2 - 10, hand_y), (100, 255, 100), 2)

        # Draw volume meter
        volume_height = int(volume * 150)
        cv2.rectangle(frame, (w//2 - 60, h - 50),
                     (w//2 - 40, h - 50 - volume_height), (100, 255, 255), -1)
        cv2.putText(frame, "VOL", (w//2 - 70, h - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 200), 1)

        return frame

    def draw_drum_visualization(self, frame, drum_data, fingers_extended):
        """Draw visualization for drum machine"""
        h, w = frame.shape[:2]

        if drum_data and drum_data['played']:
            self.drum_history.append(drum_data['step'])

            # Create particles for each drum hit
            for drum in drum_data['played']:
                x = w * 3 // 4
                y = h // 2
                self.create_particles(x, y, self.drum_color, 15)

        # Draw step sequencer
        step_width = (w // 2 - 40) // 16
        current_step = drum_data['step'] if drum_data else 0

        for i in range(16):
            x = w//2 + 20 + (i * step_width)
            y = h - 150

            # Highlight current step
            if i == current_step:
                color = (255, 255, 100)
                cv2.rectangle(frame, (x, y), (x + step_width - 2, y + 30), color, -1)
            elif i in self.drum_history:
                color = (150, 100, 100)
                cv2.rectangle(frame, (x, y), (x + step_width - 2, y + 30), color, -1)
            else:
                color = (60, 60, 80)
                cv2.rectangle(frame, (x, y), (x + step_width - 2, y + 30), color, 1)

        # Draw finger status
        finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
        for i, (name, extended) in enumerate(zip(finger_names, fingers_extended)):
            x = w//2 + 20
            y = h - 100 + (i * 20)
            color = (100, 255, 100) if extended else (100, 100, 100)
            cv2.putText(frame, f"{name}: {'UP' if extended else 'DOWN'}",
                       (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)

        # Draw pattern name
        if drum_data:
            cv2.putText(frame, f"Pattern: {drum_data['pattern']}",
                       (w//2 + 20, h - 180),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 200, 200), 2)

        return frame

    def create_particles(self, x, y, color, count):
        """Create particle effects"""
        for _ in range(count):
            particle = {
                'x': x,
                'y': y,
                'vx': np.random.uniform(-5, 5),
                'vy': np.random.uniform(-5, 5),
                'life': 1.0,
                'color': color
            }
            self.particles.append(particle)

    def update_particles(self, frame):
        """Update and draw particles"""
        particles_to_remove = []

        for particle in self.particles:
            # Update position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']

            # Update velocity (gravity and friction)
            particle['vy'] += 0.3
            particle['vx'] *= 0.98

            # Update life
            particle['life'] -= 0.02

            # Draw particle
            if particle['life'] > 0:
                alpha = particle['life']
                color = tuple(int(c * alpha) for c in particle['color'])
                size = int(5 * particle['life'])
                cv2.circle(frame, (int(particle['x']), int(particle['y'])),
                          size, color, -1)
            else:
                particles_to_remove.append(particle)

        # Remove dead particles
        for particle in particles_to_remove:
            self.particles.remove(particle)

        return frame

    def draw_info(self, frame, fps):
        """Draw FPS and other info"""
        cv2.putText(frame, f"FPS: {fps:.1f}", (self.width - 150, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        cv2.putText(frame, "Press 'Q' to quit", (self.width - 200, self.height - 20),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        return frame

    def render(self, camera_frame, hand_data, arp_data, drum_data,
               hand_height_left, volume, fingers_extended_right, fps):
        """Main render function"""
        # Create visualization canvas
        vis_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Draw background and zones
        vis_frame = self.draw_background(vis_frame)
        vis_frame = self.draw_hand_zones(vis_frame, hand_data)

        # Draw arpeggiator visualization
        vis_frame = self.draw_arpeggiator_visualization(vis_frame, arp_data,
                                                         hand_height_left, volume)

        # Draw drum visualization
        vis_frame = self.draw_drum_visualization(vis_frame, drum_data,
                                                  fingers_extended_right)

        # Update and draw particles
        vis_frame = self.update_particles(vis_frame)

        # Draw camera feed (small corner)
        camera_small = cv2.resize(camera_frame, (320, 240))
        vis_frame[self.height-260:self.height-20, 20:340] = camera_small

        # Draw info
        vis_frame = self.draw_info(vis_frame, fps)

        return vis_frame
