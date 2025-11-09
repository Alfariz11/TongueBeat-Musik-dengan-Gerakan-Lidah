import pygame
import os


class DrumMachine:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

        self.finger_to_drum = [
            'kick',
            'snare',
            'hihat',
            'hightom',
            'crashcymbal'
        ]

        self.drum_sounds = {
            'kick': None,
            'snare': None,
            'hihat': None,
            'hightom': None,
            'crashcymbal': None,
        }

        self.drum_volumes = {
            'kick': 0.5,
            'snare': 0.5,
            'hihat': 0.5,
            'hightom': 0.5,
            'crashcymbal': 0.5,
        }

        self.pattern_sets = {
            0: {
                'kick': {
                    0: 1.0,     # langkah 1
                    8: 0.9,     # langkah 3 (half bar later)
                    # tambahan sedikit variasi untuk feel pop
                    12: 0.7,    # langkah 4 (optional)
                },
                'snare': {
                    4: 1.0,     # beat 2
                    12: 1.0,    # beat 4
                },
                'hihat': {
                    0: 0.5, 1: 0.5,
                    2: 0.5, 3: 0.5,
                    4: 0.5, 5: 0.5,
                    6: 0.5, 7: 0.5,
                    8: 0.5, 9: 0.5,
                    10:0.5, 11:0.5,
                    12:0.5, 13:0.5,
                    14:0.5, 15:0.5,
                },
                'hightom': {
                    14: 0.6,    # fill ringan di akhir
                    15: 0.6,
                },
                'crashcymbal': {
                    0: 1.0,     # aksen pembuka
                },
            },
            1: {
                'kick': {0:1.0, 8:0.9},
                'snare': {4:1.0, 12:1.0},
                'hihat': {i:0.5 for i in range(16)},  # 1/8 note steady
                'crashcymbal': {0:1.0},
            },
            2: {
                'kick': {
                    0: 1.0, 2: 0.6, 4: 0.85, 6: 0.65, 8: 0.9, 11: 0.7, 12: 0.95, 14: 0.6,
                },
                'snare': {
                    4: 1.0, 12: 1.0, 7: 0.5, 15: 0.45,
                },
                'hihat': {
                    0: 0.55, 2: 0.35, 4: 0.45, 6: 0.35, 8: 0.5, 10: 0.35, 12: 0.45, 14: 0.35,
                },
                'hightom': {
                    1: 0.8, 3: 0.65, 5: 0.7, 7: 0.75, 9: 0.65, 11: 0.7, 13: 0.8, 15: 0.85,
                },
                'crashcymbal': {
                    0: 1.0,
                },
            },
        }

        self.current_pattern_set = 0
        self.drum_patterns = self.pattern_sets[self.current_pattern_set]

        self.prev_fist_state = {'Left': False, 'Right': False}

        self.active_fingers = [False] * 5

        self.bpm = 125
        self.swing_amount = 0.05
        self.step_duration_base = 60.0 / self.bpm / 4
        self.last_step_time = 0
        self.current_step = 0

        self.recent_played = []

        self._load_drum_sounds()

    def _load_drum_sounds(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        audios_dir = os.path.join(current_dir, 'audios')

        sound_files = {
            'kick': 'kick.wav',
            'snare': 'snare.wav',
            'hihat': 'hihat.wav',
            'hightom': 'hightom.wav',
            'crashcymbal': 'crashcymbal.wav',
        }

        for drum_name, filename in sound_files.items():
            filepath = os.path.join(audios_dir, filename)
            try:
                if os.path.exists(filepath):
                    sound = pygame.mixer.Sound(filepath)
                    sound.set_volume(self.drum_volumes[drum_name])
                    self.drum_sounds[drum_name] = sound
                else:
                    self.drum_sounds[drum_name] = None
            except Exception:
                self.drum_sounds[drum_name] = None

    def _get_step_duration(self, step):
        if step % 2 == 1:
            return self.step_duration_base * (1.0 + self.swing_amount)
        else:
            return self.step_duration_base * (1.0 - self.swing_amount)

    def change_pattern_set(self, pattern_set_index):
        if pattern_set_index in self.pattern_sets:
            self.current_pattern_set = pattern_set_index
            self.drum_patterns = self.pattern_sets[self.current_pattern_set]
            self.current_step = 0

    def update(self, fingers_extended, current_time, is_fist=False):
        if is_fist and not self.prev_fist_state.get('Right', False):
            next_pattern = (self.current_pattern_set + 1) % len(self.pattern_sets)
            self.change_pattern_set(next_pattern)
        
        self.prev_fist_state['Right'] = is_fist
        self.active_fingers = fingers_extended.copy()

        active_drums = []
        for finger_idx, is_active in enumerate(self.active_fingers):
            if is_active:
                drum_name = self.finger_to_drum[finger_idx]
                active_drums.append(drum_name)

        played_drums = []
        
        step_duration = self._get_step_duration(self.current_step)
        
        if current_time - self.last_step_time >= step_duration:
            self.last_step_time = current_time
            
            for drum_name in active_drums:
                if drum_name in self.drum_patterns:
                    pattern = self.drum_patterns[drum_name]
                    if self.current_step in pattern:
                        velocity = pattern[self.current_step]
                        
                        if self.drum_sounds[drum_name]:
                            actual_volume = self.drum_volumes[drum_name] * velocity
                            self.drum_sounds[drum_name].set_volume(actual_volume)
                            self.drum_sounds[drum_name].play()
                            self.drum_sounds[drum_name].set_volume(self.drum_volumes[drum_name])
                            
                            played_drums.append({
                                'drum': drum_name,
                                'velocity': velocity,
                                'volume': actual_volume
                            })

            if played_drums:
                self.recent_played = played_drums.copy()

            self.current_step = (self.current_step + 1) % 16

        active_patterns = {}
        pattern_steps_flat = {}
        for drum_name in active_drums:
            if drum_name in self.drum_patterns:
                pattern = self.drum_patterns[drum_name]
                active_patterns[drum_name] = pattern
                pattern_steps_flat[drum_name] = list(pattern.keys())

        return {
            'step': self.current_step,
            'played': [d['drum'] for d in played_drums] if played_drums else [],
            'played_details': played_drums,
            'active_drums': active_drums,
            'active_patterns': active_patterns,
            'active_patterns_flat': pattern_steps_flat,
            'fingers_extended': fingers_extended,
            'bpm': self.bpm,
            'pattern_set': self.current_pattern_set
        }

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.step_duration_base = 60.0 / self.bpm / 4

    def set_swing(self, swing_amount):
        self.swing_amount = max(0.0, min(0.2, swing_amount))

    def set_drum_volume(self, drum_name, volume):
        if drum_name in self.drum_volumes:
            self.drum_volumes[drum_name] = max(0.0, min(1.0, volume))
            if self.drum_sounds[drum_name]:
                self.drum_sounds[drum_name].set_volume(self.drum_volumes[drum_name])

    def get_drum_name_for_finger(self, finger_idx):
        if 0 <= finger_idx < len(self.finger_to_drum):
            return self.finger_to_drum[finger_idx]
        return None

    def get_pattern_for_drum(self, drum_name):
        return self.drum_patterns.get(drum_name, {})

