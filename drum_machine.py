import pygame
<<<<<<< HEAD
<<<<<<< HEAD
import os
=======
import numpy as np
import array
>>>>>>> 9178300 (new branch)
=======
import os
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)

class DrumMachine:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
<<<<<<< HEAD

<<<<<<< HEAD
<<<<<<< HEAD
        # Drum samples (loaded from assets folder)
=======
        # Drum samples (we'll generate them synthetically)
>>>>>>> 9178300 (new branch)
=======
        self.finger_to_drum = [
            'kick',
            'snare',
            'hihat',
            'hightom',
            'crashcymbal'
        ]

>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)
        self.drum_sounds = {
            'kick': None,
            'snare': None,
            'hihat': None,
<<<<<<< HEAD
            'clap': None,
<<<<<<< HEAD
        }

        # Volume control for each drum
        self.drum_volumes = {
            'kick': 0.8,
            'snare': 0.7,
            'hihat': 0.5,
            'clap': 0.6,
        }

        # Load drum sounds from assets folder
        self._load_drum_sounds()
=======
            'tom': None
        }

        # Generate synthetic drum sounds
        self._generate_drum_sounds()
>>>>>>> 9178300 (new branch)
=======
            'hightom': None,
            'crashcymbal': None,
        }

=======
        self.finger_to_drum = ['kick', 'snare', 'hihat', 'hightom', 'crashcymbal']
        self.drum_sounds = {k: None for k in self.finger_to_drum}
>>>>>>> d7af595 (hapus comment, hapus file .md)
        self.master_gain = 0.3
        self.drum_volumes = {
            'kick': 0.85 * self.master_gain,
            'snare': 0.75 * self.master_gain,
            'hihat': 0.45 * self.master_gain,
            'hightom': 0.55 * self.master_gain,
            'crashcymbal': 0.65 * self.master_gain,
        }
<<<<<<< HEAD
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)

<<<<<<< HEAD
        self.drum_patterns = {
            'kick': {
                0: 1.0,
                4: 0.9,
                7: 0.6,
                8: 0.85,
                10: 0.5,
                12: 0.95,
            },
            'snare': {
                4: 1.0,
                12: 1.0,
                2: 0.3,
                6: 0.35,
                10: 0.4,
                14: 0.3,
=======
=======
>>>>>>> d7af595 (hapus comment, hapus file .md)
        self.pattern_sets = {
            0: {
                'kick': {0: 1.0, 8: 0.9, 12: 0.7},
                'snare': {4: 1.0, 12: 1.0},
                'hihat': {i: 0.5 for i in range(16)},
                'hightom': {14: 0.6, 15: 0.6},
                'crashcymbal': {0: 1.0},
            },
            1: {
<<<<<<< HEAD
                'kick': {0:1.0, 8:0.9},
                'snare': {4:1.0, 12:1.0},
                'hihat': {i:0.5 for i in range(16)},  # 1/8 note steady
                'crashcymbal': {0:1.0},
>>>>>>> db73a75 (better beat pattern (more soon), optimize visualizer (particles spawn))
            },
            'hihat': {
                0: 0.6,
                2: 0.4,
                4: 0.5,
                6: 0.4,
                8: 0.55,
                10: 0.4,
                12: 0.5,
                14: 0.4,
                1: 0.25,
                3: 0.25,
                5: 0.25,
                7: 0.25,
                9: 0.25,
                11: 0.25,
                13: 0.25,
                15: 0.25,
            },
            'hightom': {
                1: 0.7,
                5: 0.6,
                9: 0.65,
                13: 0.75,
                3: 0.4,
                7: 0.45,
                11: 0.5,
                15: 0.8,
            },
            'crashcymbal': {
                0: 1.0,
                8: 0.85,
            },
        }

=======
                'kick': {0: 1.0, 8: 0.9},
                'snare': {4: 1.0, 12: 1.0},
                'hihat': {i: 0.5 for i in range(16)},
                'crashcymbal': {0: 1.0},
            },
            2: {
                'kick': {0: 1.0, 2: 0.6, 4: 0.85, 6: 0.65, 8: 0.9, 11: 0.7, 12: 0.95, 14: 0.6},
                'snare': {4: 1.0, 12: 1.0, 7: 0.5, 15: 0.45},
                'hihat': {0: 0.55, 2: 0.35, 4: 0.45, 6: 0.35, 8: 0.5, 10: 0.35, 12: 0.45, 14: 0.35},
                'hightom': {1: 0.8, 3: 0.65, 5: 0.7, 7: 0.75, 9: 0.65, 11: 0.7, 13: 0.8, 15: 0.85},
                'crashcymbal': {0: 1.0},
            },
        }
        self.current_pattern_set = 0
        self.drum_patterns = self.pattern_sets[self.current_pattern_set]
        self.prev_fist_state = {'Left': False, 'Right': False}
>>>>>>> d7af595 (hapus comment, hapus file .md)
        self.active_fingers = [False] * 5
        self.bpm = 125
        self.swing_amount = 0.05
        self.step_duration_base = 60.0 / self.bpm / 4
        self.last_step_time = 0
        self.current_step = 0
<<<<<<< HEAD

<<<<<<< HEAD
        # Drum patterns (16 steps each)
        # Each pattern is a dict of drum: [steps where it plays]
        self.patterns = {
            'pattern1': {  # Basic 4/4
                'kick': [0, 4, 8, 12],
                'snare': [4, 12],
                'hihat': [0, 2, 4, 6, 8, 10, 12, 14],
            },
            'pattern2': {  # With clap
                'kick': [0, 6, 10],
                'snare': [4, 12],
                'hihat': [0, 2, 4, 6, 8, 10, 12, 14],
                'clap': [4, 12],
            },
            'pattern3': {  # Syncopated
                'kick': [0, 3, 6, 10, 13],
                'snare': [4, 12],
                'hihat': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
<<<<<<< HEAD
                'clap': [7, 15],
=======
                'tom': [7, 15],
>>>>>>> 9178300 (new branch)
            },
            'pattern4': {  # Break beat
                'kick': [0, 3, 8, 11],
                'snare': [4, 10, 13],
<<<<<<< HEAD
                'hihat': [2, 6, 10, 14],
=======
                'hihat': [2, 6, 14],
>>>>>>> 9178300 (new branch)
                'clap': [4, 12],
            },
            'pattern5': {  # Minimal
                'kick': [0, 8],
                'snare': [4, 12],
                'hihat': [0, 4, 8, 12],
            }
=======
=======
>>>>>>> d7af595 (hapus comment, hapus file .md)
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
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)
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

<<<<<<< HEAD
        # Finger pattern mapping
        self.finger_patterns = {
            (False, False, False, False, False): 'pattern1',  # No fingers
            (False, True, False, False, False): 'pattern1',   # Index
            (False, True, True, False, False): 'pattern2',    # Index + Middle
            (False, True, True, True, False): 'pattern3',     # Index + Middle + Ring
            (False, True, True, True, True): 'pattern4',      # All except thumb
            (True, True, True, True, True): 'pattern5',       # All fingers
        }

<<<<<<< HEAD
    def _load_drum_sounds(self):
        """Load drum sounds from assets folder"""
        # Get the path to assets folder
        current_dir = os.path.dirname(os.path.abspath(__file__))
        assets_dir = os.path.join(current_dir, 'assets')

        # Map of drum names to filenames
        sound_files = {
            'kick': 'kick.wav',
            'snare': 'snare.wav',
            'hihat': 'hihat.wav',
            'clap': 'clap.wav',
        }

        # Load each sound file
        loaded_count = 0
        for drum_name, filename in sound_files.items():
            filepath = os.path.join(assets_dir, filename)
            try:
                if os.path.exists(filepath):
                    sound = pygame.mixer.Sound(filepath)
                    # Set volume for this drum
                    sound.set_volume(self.drum_volumes[drum_name])
                    self.drum_sounds[drum_name] = sound
                    loaded_count += 1
                    print(f"  [OK] {drum_name.ljust(8)} - Volume: {self.drum_volumes[drum_name]:.1f}")
                else:
                    print(f"  [WARNING] {filename} not found in assets folder")
                    self.drum_sounds[drum_name] = None
            except Exception as e:
                print(f"  [ERROR] Loading {filename}: {e}")
                self.drum_sounds[drum_name] = None

        print(f"\n  Loaded {loaded_count}/{len(sound_files)} drum sounds successfully")
=======
    def _generate_drum_sounds(self):
        """Generate synthetic drum sounds"""
        sample_rate = 44100

        # Kick drum - low frequency punch
        duration = 0.3
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = 60 * np.exp(-10 * t)  # Pitch envelope
        kick = np.sin(2 * np.pi * freq * t)
        envelope = np.exp(-8 * t)
        kick = kick * envelope * 0.8
        kick_buffer = array.array('h')
        for sample in kick:
            val = int(sample * 32767)
            kick_buffer.append(val)
            kick_buffer.append(val)
        self.drum_sounds['kick'] = pygame.mixer.Sound(buffer=kick_buffer)

        # Snare - noise with tone
        duration = 0.15
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        noise = np.random.uniform(-1, 1, len(t))
        tone = np.sin(2 * np.pi * 200 * t)
        snare = 0.7 * noise + 0.3 * tone
        envelope = np.exp(-20 * t)
        snare = snare * envelope * 0.6
        snare_buffer = array.array('h')
        for sample in snare:
            val = int(sample * 32767)
            snare_buffer.append(val)
            snare_buffer.append(val)
        self.drum_sounds['snare'] = pygame.mixer.Sound(buffer=snare_buffer)

        # Hi-hat - high frequency noise
        duration = 0.08
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        hihat = np.random.uniform(-1, 1, len(t))
        # High-pass filter effect
        hihat = hihat * np.sin(2 * np.pi * 8000 * t)
        envelope = np.exp(-40 * t)
        hihat = hihat * envelope * 0.4
        hihat_buffer = array.array('h')
        for sample in hihat:
            val = int(sample * 32767)
            hihat_buffer.append(val)
            hihat_buffer.append(val)
        self.drum_sounds['hihat'] = pygame.mixer.Sound(buffer=hihat_buffer)

        # Clap - short burst of noise
        duration = 0.1
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        clap = np.random.uniform(-1, 1, len(t))
        # Double hit for clap effect
        envelope = np.exp(-30 * t) + 0.5 * np.exp(-30 * (t - 0.02))
        clap = clap * envelope * 0.5
        clap_buffer = array.array('h')
        for sample in clap:
            val = int(sample * 32767)
            clap_buffer.append(val)
            clap_buffer.append(val)
        self.drum_sounds['clap'] = pygame.mixer.Sound(buffer=clap_buffer)

        # Tom - mid frequency tone
        duration = 0.25
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        freq = 150 * np.exp(-8 * t)
        tom = np.sin(2 * np.pi * freq * t)
        envelope = np.exp(-10 * t)
        tom = tom * envelope * 0.7
        tom_buffer = array.array('h')
        for sample in tom:
            val = int(sample * 32767)
            tom_buffer.append(val)
            tom_buffer.append(val)
        self.drum_sounds['tom'] = pygame.mixer.Sound(buffer=tom_buffer)
>>>>>>> 9178300 (new branch)
=======
    def _get_step_duration(self, step):
        if step % 2 == 1:
            return self.step_duration_base * (1.0 + self.swing_amount)
<<<<<<< HEAD
        else:
            return self.step_duration_base * (1.0 - self.swing_amount)
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)

    def update(self, fingers_extended, current_time):
=======
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
>>>>>>> d7af595 (hapus comment, hapus file .md)
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
            'bpm': self.bpm
        }

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.step_duration_base = 60.0 / self.bpm / 4

<<<<<<< HEAD
<<<<<<< HEAD
    def set_drum_volume(self, drum_name, volume):
        """Set volume for a specific drum (0.0 to 1.0)"""
=======
    def set_swing(self, swing_amount):
        self.swing_amount = max(0.0, min(0.2, swing_amount))

    def set_drum_volume(self, drum_name, volume):
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)
        if drum_name in self.drum_volumes:
            self.drum_volumes[drum_name] = max(0.0, min(1.0, volume))
            if self.drum_sounds[drum_name]:
                self.drum_sounds[drum_name].set_volume(self.drum_volumes[drum_name])

<<<<<<< HEAD
=======
>>>>>>> 9178300 (new branch)
    def get_pattern_name(self):
        """Get current pattern name"""
        return self.current_pattern_name
=======
    def get_drum_name_for_finger(self, finger_idx):
        if 0 <= finger_idx < len(self.finger_to_drum):
            return self.finger_to_drum[finger_idx]
        return None

    def get_pattern_for_drum(self, drum_name):
<<<<<<< HEAD
        return self.drum_patterns.get(drum_name, {})
>>>>>>> d72103c (Refactor arpeggiator and drum machine modules for improved structure and functionality. Removed unnecessary comments, enhanced drum pattern handling, and added audio file loading for drum sounds. Updated visualizer to display detailed drum patterns and velocities. Improved hand tracking and visualization integration.)
=======
        return self.drum_patterns.get(drum_name, {})
>>>>>>> d7af595 (hapus comment, hapus file .md)
