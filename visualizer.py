import cv2
import numpy as np
from collections import deque
import math
import time

class Visualizer:
    def __init__(self, width=1280, height=720):
        self.width = width
        self.height = height

        self.bg_color = (20, 20, 30)
        self.arp_color = (100, 200, 255)
        self.drum_color = (255, 100, 150)

        self.arp_history = deque(maxlen=100)
        self.drum_history = deque(maxlen=16)

        self.particles = []
        self.max_particles = 300

    def get_current_bpm(self):
        """Ambil nilai BPM dari modul DrumMachine (akan diisi saat render)"""
        return getattr(self, "_current_bpm", 120)

    def draw_background(self, frame):
        frame[:] = self.bg_color
        return frame

    def draw_hand_zones(self, frame, hand_data):
        h, w = frame.shape[:2]

        cv2.rectangle(frame, (0, 0), (w//2, h), (40, 40, 60), -1)
        cv2.putText(frame, "HAND #1: ARPEGGIATOR", (20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (150, 150, 200), 2)
        cv2.putText(frame, "Raise hand = Higher pitch", (20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 150), 1)
        cv2.putText(frame, "Pinch = Volume control", (20, 95),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (120, 120, 150), 1)

        cv2.rectangle(frame, (w//2, 0), (w, h), (60, 40, 40), -1)
        cv2.putText(frame, "HAND #2: DRUMS", (w//2 + 20, 40),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 150, 150), 2)
        cv2.putText(frame, "Each finger = One instrument", (w//2 + 20, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 120, 120), 1)

        return frame

    def draw_arpeggiator_visualization(self, frame, arp_data, hand_height, volume):
        h, w = frame.shape[:2]

        # Tambahan minimal: tetap tambahkan titik agar garis terus berjalan
        if arp_data:
            self.arp_history.append({
            'note': arp_data.get('note', 60),
            'volume': arp_data.get('volume', 0.5),
            'octave': arp_data.get('octave', 0)
        })

            x = w // 4
            y = int(h * (1 - hand_height))
            self.create_particles(x, y, self.arp_color, int(volume * 20))
        else:
            # Jika tidak ada input, duplikasi titik terakhir agar garis terus bergerak
            if len(self.arp_history) > 0:
                self.arp_history.append(self.arp_history[-1])
            else:
                # kalau masih kosong dari awal, mulai dari nilai default
                self.arp_history.append({'note': 60, 'volume': 0.5, 'octave': 0})

        # === Tidak ada perubahan di bawah ini ===
        if len(self.arp_history) > 1:
            points = []
            for i, data in enumerate(self.arp_history):
                x = int((w // 2) * (i / len(self.arp_history)))
                note_normalized = (data['note'] - 57) / 24
                y = int(h - (h * note_normalized * 0.5) - 100)
                points.append((x, y))

            if len(points) > 2:
                points_array = np.array(points, dtype=np.int32)
                cv2.polylines(frame, [points_array], False, self.arp_color, 3)

        hand_y = int(h * (1 - hand_height))
        cv2.line(frame, (10, hand_y), (w//2 - 10, hand_y), (100, 255, 100), 2)

        volume_height = int(volume * 150)
        cv2.rectangle(frame, (w//2 - 60, h - 50 - volume_height),
                    (w//2 - 40, h - 50), (100, 255, 255), -1)
        cv2.putText(frame, "VOL", (w//2 - 70, h - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 200), 1)

        return frame


    def draw_drum_visualization(self, frame, drum_data, fingers_extended):
        h, w = frame.shape[:2]

        finger_to_instrument = [
            'Kick',
            'Snare',
            'Hihat',
            'High Tom',
            'Crash'
        ]
        
        instrument_colors = {
            'kick': (100, 150, 255),
            'snare': (255, 150, 100),
            'hihat': (150, 255, 150),
            'hightom': (255, 200, 100),
            'crashcymbal': (255, 100, 255)
        }

        if drum_data and drum_data.get('played_details'):
            for drum_detail in drum_data['played_details']:
                drum = drum_detail['drum']
                velocity = drum_detail.get('velocity', 1.0)
                x = w * 3 // 4
                y = h // 2
                color = instrument_colors.get(drum, self.drum_color)
                particle_count = int(10 + velocity * 20)
                self.create_particles(x, y, color, particle_count)

        step_width = (w // 2 - 60) // 16
        current_step = drum_data.get('step', 0) if drum_data else 0
        start_x = w//2 + 30
        start_y = h - 220

        for i in range(16):
            x = start_x + (i * step_width)
            y = start_y
            
            is_beat = (i % 4 == 0)
            
            if i == current_step:
                color = (255, 255, 100)
                cv2.rectangle(frame, (x, y), (x + step_width - 2, y + 35), color, -1)
                cv2.circle(frame, (x + step_width // 2, y + 17), step_width // 2 + 3, color, 2)
            else:
                if is_beat:
                    color = (80, 80, 100)
                else:
                    color = (60, 60, 80)
                cv2.rectangle(frame, (x, y), (x + step_width - 2, y + 35), color, 1)

            text_color = (255, 255, 255) if i == current_step else (200, 200, 200)
            cv2.putText(frame, str(i), (x + 3, y + 22),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.35, text_color, 1)
            
            if is_beat:
                cv2.circle(frame, (x + step_width // 2, y - 5), 3, (255, 200, 100), -1)

        finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
        pattern_y_offset = 100
        drum_name_map = ['kick', 'snare', 'hihat', 'hightom', 'crashcymbal']
        
        active_patterns = drum_data.get('active_patterns', {}) if drum_data else {}
        
        pattern_row = 0
        for i, (name, extended) in enumerate(zip(finger_names, fingers_extended)):
            if extended:
                instrument = finger_to_instrument[i]
                drum_name = drum_name_map[i]
                inst_color = instrument_colors.get(drum_name, (100, 255, 100))
                
                y = start_y + pattern_y_offset - (pattern_row * 20)
                
                cv2.rectangle(frame, (start_x - 5, y - 12), (start_x + 140, y + 3), 
                            (inst_color[0] // 3, inst_color[1] // 3, inst_color[2] // 3), -1)
                
                cv2.putText(frame, f"{name:6} ({instrument:10}):",
                           (start_x, y),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.4, inst_color, 1)
                
                pattern = active_patterns.get(drum_name, {})
                
                for step, velocity in pattern.items():
                    step_x = start_x + 150 + (step * (step_width // 2))
                    
                    bar_height = int(8 + velocity * 12)
                    bar_y = y - bar_height - 2
                    
                    if step == current_step:
                        dot_color = (255, 255, 100)
                        bar_color = (255, 255, 150)
                    else:
                        dot_color = tuple(min(255, int(c * (0.5 + velocity * 0.5))) 
                                        for c in inst_color)
                        bar_color = tuple(min(255, int(c * (0.4 + velocity * 0.4))) 
                                        for c in inst_color)
                    
                    cv2.rectangle(frame, 
                                (step_x - 2, bar_y), 
                                (step_x + 1, y - 2),
                                bar_color, -1)
                    
                    cv2.circle(frame, (step_x, y - 5), 3, dot_color, -1)
                    
                    if velocity > 0.7:
                        cv2.putText(frame, f"{velocity:.1f}", 
                                  (step_x - 5, bar_y - 3),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255, 255, 255), 1)
                
                pattern_row += 1

        active_count = sum(fingers_extended)
        bpm = drum_data.get('bpm', 120) if drum_data else 120
        
        info_y = h - 55
        cv2.rectangle(frame, (start_x - 5, info_y), (start_x + 400, h - 5), 
                     (30, 30, 40), -1)
        cv2.rectangle(frame, (start_x - 5, info_y), (start_x + 400, h - 5), 
                     (100, 100, 120), 1)
        
        if active_count > 0:
            status_text = f"Active: {active_count} pattern(s)"
            cv2.putText(frame, status_text,
                       (start_x, h - 35),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 200), 1)
        
        bpm_text = f"BPM: {bpm}"
        cv2.putText(frame, bpm_text,
                   (start_x + 180, h - 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 255, 200), 1)
        
        step_text = f"Step: {current_step}/15"
        cv2.putText(frame, step_text,
                   (start_x + 260, h - 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 255), 1)

        cv2.putText(frame, "Enhanced Step Sequencer (Velocity Visualization):",
                   (start_x, start_y - 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

        return frame

    def create_particles(self, x, y, color, count):
        # Kurangi jumlah partikel per event
        count = min(count, 8)  # misal maksimal 8 per trigger

        # Batasi total partikel aktif
        if len(self.particles) > self.max_particles:
            return  # jangan tambah partikel baru kalau sudah kebanyakan

        for _ in range(count):
            particle = {
                'x': x + np.random.uniform(-3, 3),
                'y': y + np.random.uniform(-3, 3),
                'vx': np.random.uniform(-2, 2),
                'vy': np.random.uniform(-3, 1),
                'life': 1.0,
                'color': color
            }
            self.particles.append(particle)

    def update_particles(self, frame):
        particles_to_remove = []

        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']

            particle['vy'] += 0.3
            particle['vx'] *= 0.98

            particle['life'] -= 0.02

            if particle['life'] > 0:
                alpha = particle['life']
                color = tuple(int(c * alpha) for c in particle['color'])
                size = int(5 * particle['life'])
                cv2.circle(frame, (int(particle['x']), int(particle['y'])),
                          size, color, -1)
            else:
                particles_to_remove.append(particle)

        for particle in particles_to_remove:
            self.particles.remove(particle)

        return frame

<<<<<<< HEAD
    def draw_info(self, frame, fps):
=======
    def draw_info(self, frame, fps, bpm):
        """Draw FPS, BPM, and quit info"""
        # FPS di pojok kanan atas
>>>>>>> db5b17e (fix: appregiator note & visual)
        cv2.putText(frame, f"FPS: {fps:.1f}", (self.width - 150, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

        # BPM tepat di bawah FPS
        cv2.putText(frame, f"BPM: {bpm}", (self.width - 150, 60),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 255, 255), 2)

        # Instruksi quit
        cv2.putText(frame, "Press 'Q' to quit", (self.width - 220, self.height - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        return frame


    def render(self, camera_frame, hand_data, arp_data, drum_data,
<<<<<<< HEAD
               hand_height_left, volume, fingers_extended_right, fps):
=======
               hand_height_left, volume, fingers_extended_right, fps, bpm):
        """Main render function"""
        # Create visualization canvas
>>>>>>> db5b17e (fix: appregiator note & visual)
        vis_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        vis_frame = self.draw_background(vis_frame)
        vis_frame = self.draw_hand_zones(vis_frame, hand_data)

        vis_frame = self.draw_arpeggiator_visualization(vis_frame, arp_data,
                                                         hand_height_left, volume)

        vis_frame = self.draw_drum_visualization(vis_frame, drum_data,
                                                  fingers_extended_right)

        vis_frame = self.update_particles(vis_frame)

        camera_small = cv2.resize(camera_frame, (320, 240))
        vis_frame[self.height-260:self.height-20, 20:340] = camera_small

<<<<<<< HEAD
        vis_frame = self.draw_info(vis_frame, fps)
=======
        # Draw info
        vis_frame = self.draw_info(vis_frame, fps, bpm)
<<<<<<< HEAD
>>>>>>> db5b17e (fix: appregiator note & visual)
=======
>>>>>>> 399c403 (integrated with bpm feature edwin)

        return vis_frame
