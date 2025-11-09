import pygame
import numpy as np
import cv2
import time
from collections import deque


class VisualizerPygame:
    def __init__(self, width=1280, height=720):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Visualizer (Pygame)")

        # Partikel
        self.particles = []
        self.max_particles = 200

        # Warna
        self.bg_color = (20, 20, 30)
        self.arp_color = (100, 200, 255)
        self.zone_left_color = (40, 40, 60)
        self.zone_right_color = (60, 40, 40)
        self.text_color = (180, 180, 200)

        # Font
        self.font_small = pygame.font.SysFont("Arial", 18)
        self.font_large = pygame.font.SysFont("Arial", 24)

        # History arpeggiator
        self.arp_history = deque(maxlen=100)
        self.last_time = time.time()

    # ===========================================================
    # === BAGIAN DASAR VISUALISASI ===
    # ===========================================================

    def draw_background(self):
        self.screen.fill(self.bg_color)
        pygame.draw.rect(self.screen, self.zone_left_color, (0, 0, self.width // 2, self.height))
        pygame.draw.rect(self.screen, self.zone_right_color, (self.width // 2, 0, self.width // 2, self.height))

        self._draw_text("HAND #1: ARPEGGIATOR", (20, 20), self.text_color, self.font_large)
        self._draw_text("Raise hand = Higher pitch", (20, 50))
        self._draw_text("Pinch = Volume control", (20, 70))

        self._draw_text("HAND #2: DRUMS", (self.width // 2 + 20, 20), self.text_color, self.font_large)
        self._draw_text("Each finger = One instrument", (self.width // 2 + 20, 50))

    # ===========================================================
    # === ARPEGGIATOR VISUAL (GARIS) ===
    # ===========================================================

    def draw_arpeggiator(self, arp_data, hand_height, volume):
        note = arp_data.get("note", 60) if arp_data else 60
        self.arp_history.append(note)

        # Buat daftar titik (garis history)
        if len(self.arp_history) > 2:
            points = []
            for i, n in enumerate(self.arp_history):
                x = int((self.width // 2) * (i / len(self.arp_history)))
                y = int(self.height * (1 - (n - 57) / 24 * 0.5) - 100)
                points.append((x, y))
            pygame.draw.lines(self.screen, self.arp_color, False, points, 3)

        # Garis tinggi tangan (indikator live)
        y_hand = int(self.height * (1 - hand_height))
        pygame.draw.line(self.screen, (100, 255, 100),
                         (10, y_hand), (self.width // 2 - 10, y_hand), 2)

        # Volume bar
        vol_h = int((1 - volume) * 150)
        vol_rect = (self.width // 2 - 60, self.height - 50 - vol_h, 20, vol_h)
        pygame.draw.rect(self.screen, (100, 255, 255), vol_rect)
        self._draw_text("VOL", (self.width // 2 - 70, self.height - 25))

    # ===========================================================
    # === DRUM VISUALIZATION (16 STEP SEQUENCER) ===
    # ===========================================================
    def draw_drum_visualization(self, drum_data):
        h = self.height
        w = self.width
        start_x = w // 2 + 40
        start_y = h - 220
        step_width = (w // 2 - 100) // 16

        current_step = drum_data.get("step", 0) if drum_data else 0
        bpm = drum_data.get("bpm", 120) if drum_data else 120
        pattern_set = drum_data.get("pattern_set", 0) if drum_data else 0

        # --- Step grid ---
        for i in range(16):
            x = start_x + i * step_width
            y = start_y
            is_beat = (i % 4 == 0)

            if i == current_step:
                color = (255, 255, 100)
                pygame.draw.rect(self.screen, color, (x, y, step_width - 2, 35))
                pygame.draw.circle(
                    self.screen,
                    color,
                    (x + step_width // 2, y + 17),
                    step_width // 2 + 3,
                    2,
                )
            else:
                color = (80, 80, 100) if is_beat else (60, 60, 80)
                pygame.draw.rect(self.screen, color, (x, y, step_width - 2, 35), 1)

            # step number
            num_color = (255, 255, 255) if i == current_step else (180, 180, 180)
            self._draw_text(str(i), (x + 3, y + 10), num_color)

            # beat dots
            if is_beat:
                pygame.draw.circle(
                    self.screen,
                    (255, 200, 100),
                    (x + step_width // 2, y - 6),
                    3,
                )

        # --- Info di bawah step sequencer ---
        info_y = h - 55
        pygame.draw.rect(self.screen, (30, 30, 40), (start_x - 5, info_y, 450, 50))
        pygame.draw.rect(self.screen, (100, 100, 120), (start_x - 5, info_y, 450, 50), 1)

        self.draw_drum_velocity_bars(drum_data)
        self._draw_text(f"BPM: {bpm}", (start_x + 180, h - 35))
        self._draw_text(f"Step: {current_step}/15", (start_x + 260, h - 35))
        self._draw_text(f"Pattern Set: {pattern_set + 1}", (start_x, h - 15))

    # ===========================================================
    # === DRUM VELOCITY BARS (Pattern Strength Visualization) ===
    # ===========================================================
    def draw_drum_velocity_bars(self, drum_data):
        if not drum_data or "active_patterns" not in drum_data:
            return

        h = self.height
        w = self.width
        start_x = w // 2 + 40
        start_y = h - 260
        step_width = (w // 2 - 100) // 16

        current_step = drum_data.get("step", 0)
        active_patterns = drum_data.get("active_patterns", {})

        # Warna instrumen
        instrument_colors = {
            "kick": (100, 150, 255),
            "snare": (255, 150, 100),
            "hihat": (150, 255, 150),
            "hightom": (255, 200, 100),
            "crashcymbal": (255, 100, 255),
        }

        # Susun instrumen per baris
        instrument_names = list(instrument_colors.keys())
        spacing = 22

        for row, drum_name in enumerate(instrument_names):
            pattern = active_patterns.get(drum_name, {})
            base_y = start_y + row * spacing

            # Label instrumen
            self._draw_text(
                drum_name.capitalize(), (start_x - 65, base_y - 6), instrument_colors[drum_name]
            )

            for step in range(16):
                x = start_x + step * step_width
                velocity = pattern.get(step, 0.0)
                bar_height = int(velocity * 15)

                # Warna bar
                if step == current_step:
                    color = (255, 255, 150)
                elif velocity > 0:
                    c = instrument_colors[drum_name]
                    color = tuple(int(v * (0.4 + 0.6 * velocity)) for v in c)
                else:
                    color = (60, 60, 70)

                # Gambar bar kecil
                if velocity > 0:
                    rect = (x, base_y - bar_height, step_width - 2, bar_height)
                    pygame.draw.rect(self.screen, color, rect)
                else:
                    pygame.draw.rect(
                        self.screen, color, (x, base_y - 2, step_width - 2, 2)
                    )

    # ===========================================================
    # === PARTICLE SYSTEM (Lightweight visual effects) ===
    # ===========================================================
    def spawn_particles(self, zone="arp", color=(255, 255, 255), intensity=5):
        """Spawn particles when note or drum is triggered."""
        if len(self.particles) > self.max_particles:
            return

        if zone == "arp":
            base_x = self.width // 4
            base_y = self.height // 2
        else:  # zone == "drum"
            base_x = self.width * 3 // 4
            base_y = self.height // 2

        for _ in range(intensity):
            self.particles.append({
                "x": base_x + np.random.uniform(-40, 40),
                "y": base_y + np.random.uniform(-30, 30),
                "vx": np.random.uniform(-1.5, 1.5),
                "vy": np.random.uniform(-2, 2),
                "life": np.random.uniform(0.8, 1.2),
                "color": color
            })

    def update_particles(self):
        """Update and draw all active particles."""
        for p in list(self.particles):
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.05  # gravity
            p["life"] -= 0.02

            if p["life"] <= 0:
                self.particles.remove(p)
                continue

            alpha = max(0, min(255, int(255 * p["life"])))
            color = (min(255, int(p["color"][0] * p["life"])),
                     min(255, int(p["color"][1] * p["life"])),
                     min(255, int(p["color"][2] * p["life"])))

            size = int(3 + 4 * p["life"])
            pygame.draw.circle(self.screen, color, (int(p["x"]), int(p["y"])), size)

    def spawn_particles_at_hand(self, hand_data, which="Left", color=(255, 255, 255), intensity=6):
        """Spawn particles near a real hand position (from Mediapipe landmarks)."""
        if len(self.particles) > self.max_particles:
            return

        cx, cy = None, None

        if hand_data and which in hand_data and hand_data[which]:
            landmarks = hand_data[which]["landmarks"]

            # Jika masih berupa NormalizedLandmarkList dari Mediapipe
            if hasattr(landmarks, "landmark"):
                pts = [(lm.x, lm.y) for lm in landmarks.landmark]
            # Jika sudah list biasa [(x, y), ...]
            else:
                pts = [(lm[0], lm[1]) for lm in landmarks]

            if pts:
                pts = np.array(pts)
                cx = int((1.0 - np.mean(pts[:, 0])) * self.width)
                cy = int(np.mean(pts[:, 1]) * self.height)

        # fallback jika deteksi gagal
        if cx is None or cy is None:
            cx = self.width // 4 if which == "Left" else self.width * 3 // 4
            cy = self.height // 2

        for _ in range(intensity):
            self.particles.append({
                "x": cx + np.random.uniform(-20, 20),
                "y": cy + np.random.uniform(-20, 20),
                "vx": np.random.uniform(-1.2, 1.2),
                "vy": np.random.uniform(-1.5, 1.5),
                "life": np.random.uniform(0.8, 1.2),
                "color": color
            })

    # ===========================================================
    # === KAMERA FEED ===
    # ===========================================================

    def draw_camera_feed(self, frame, hand_data=None):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        target_width, target_height = 200, 150
        frame = cv2.resize(frame, (target_width, target_height))

        if hand_data:
            for hand_label, data in hand_data.items():
                if not data or "landmarks" not in data:
                    continue

                # Ambil daftar titik dari Mediapipe
                landmarks = data["landmarks"]
                if hasattr(landmarks, "landmark"):
                    points = [(int(lm.x * target_width), int(lm.y * target_height))
                            for lm in landmarks.landmark]
                else:
                    points = [(int(x * target_width), int(y * target_height))
                            for x, y in landmarks]

                # Hubungan antar-jari (sama seperti di Mediapipe)
                connections = [
                    (0, 1), (1, 2), (2, 3), (3, 4),
                    (0, 5), (5, 6), (6, 7), (7, 8),
                    (5, 9), (9, 10), (10, 11), (11, 12),
                    (9, 13), (13, 14), (14, 15), (15, 16),
                    (13, 17), (17, 18), (18, 19), (19, 20),
                    (0, 17)
                ]

                for i1, i2 in connections:
                    cv2.line(frame, points[i1], points[i2], (0, 255, 0), 1)

                for (x, y) in points:
                    cv2.circle(frame, (x, y), 2, (255, 0, 0), -1)

        frame = np.rot90(frame)
        surf = pygame.surfarray.make_surface(frame)
        cam_w, cam_h = surf.get_size()
        self.screen.blit(surf, (5, self.height - cam_h - 5))

    # ===========================================================
    # === INFO TEKS (FPS, BPM) ===
    # ===========================================================

    def draw_info(self, fps, bpm):
        self._draw_text(f"FPS: {fps:.1f}", (self.width - 150, 20))
        self._draw_text(f"BPM: {bpm}", (self.width - 150, 45))
        self._draw_text("Press Q or close window to quit", (self.width - 300, self.height - 25))

    # ===========================================================
    # === HELPER ===
    # ===========================================================

    def _draw_text(self, text, pos, color=None, font=None):
        font = font or self.font_small
        color = color or (200, 200, 200)
        surf = font.render(text, True, color)
        self.screen.blit(surf, pos)

    def update_display(self):
        pygame.display.flip()
