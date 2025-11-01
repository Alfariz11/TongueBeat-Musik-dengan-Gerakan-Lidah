"""
Drum Machine Controller
Hand #2 controls the drums (raise different fingers to change the pattern)
"""
import pygame
import numpy as np
import array


class DrumMachine:
    def __init__(self):
        # Larger buffer for smoother playback (but slightly more latency)
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

        # Drum samples (we'll generate them synthetically)
        self.drum_sounds = {
            'kick': None,
            'snare': None,
            'hihat': None,
            'clap': None,
            'tom': None
        }

        # Generate synthetic drum sounds
        self._generate_drum_sounds()

        # Timing
        self.bpm = 120
        self.step_duration = 60.0 / self.bpm / 4  # 16th notes
        self.last_step_time = 0
        self.current_step = 0

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
                'tom': [7, 15],
            },
            'pattern4': {  # Break beat
                'kick': [0, 3, 8, 11],
                'snare': [4, 10, 13],
                'hihat': [2, 6, 14],
                'clap': [4, 12],
            },
            'pattern5': {  # Minimal
                'kick': [0, 8],
                'snare': [4, 12],
                'hihat': [0, 4, 8, 12],
            }
        }

        self.current_pattern_name = 'pattern1'
        self.current_pattern = self.patterns['pattern1']

        # Finger pattern mapping
        self.finger_patterns = {
            (False, False, False, False, False): 'pattern1',  # No fingers
            (False, True, False, False, False): 'pattern1',   # Index
            (False, True, True, False, False): 'pattern2',    # Index + Middle
            (False, True, True, True, False): 'pattern3',     # Index + Middle + Ring
            (False, True, True, True, True): 'pattern4',      # All except thumb
            (True, True, True, True, True): 'pattern5',       # All fingers
        }

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

    def update(self, fingers_extended, current_time):
        """Update drum machine based on finger positions

        Args:
            fingers_extended: List of 5 booleans for each finger
            current_time: Current time in seconds
        """
        # Select pattern based on fingers
        fingers_tuple = tuple(fingers_extended)

        # Find the best matching pattern
        if fingers_tuple in self.finger_patterns:
            new_pattern = self.finger_patterns[fingers_tuple]
            if new_pattern != self.current_pattern_name:
                self.current_pattern_name = new_pattern
                self.current_pattern = self.patterns[new_pattern]

        # Check if it's time for the next step
        if current_time - self.last_step_time >= self.step_duration:
            self.last_step_time = current_time

            # Play drums for current step
            played_drums = []
            for drum_name, steps in self.current_pattern.items():
                if self.current_step in steps:
                    if self.drum_sounds[drum_name]:
                        self.drum_sounds[drum_name].play()
                        played_drums.append(drum_name)

            # Move to next step
            self.current_step = (self.current_step + 1) % 16

            return {
                'step': self.current_step,
                'pattern': self.current_pattern_name,
                'played': played_drums
            }

        return None

    def set_bpm(self, bpm):
        """Set the tempo"""
        self.bpm = bpm
        self.step_duration = 60.0 / self.bpm / 4

    def get_pattern_name(self):
        """Get current pattern name"""
        return self.current_pattern_name
