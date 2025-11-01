"""
Drum Machine Controller
Hand #2 controls the drums (raise different fingers to change the pattern)
"""
import pygame
import os


class DrumMachine:
    def __init__(self):
        # Larger buffer for smoother playback (but slightly more latency)
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

        # Drum samples (loaded from assets folder)
        self.drum_sounds = {
            'kick': None,
            'snare': None,
            'hihat': None,
            'clap': None,
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
                'clap': [7, 15],
            },
            'pattern4': {  # Break beat
                'kick': [0, 3, 8, 11],
                'snare': [4, 10, 13],
                'hihat': [2, 6, 10, 14],
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

    def set_drum_volume(self, drum_name, volume):
        """Set volume for a specific drum (0.0 to 1.0)"""
        if drum_name in self.drum_volumes:
            self.drum_volumes[drum_name] = max(0.0, min(1.0, volume))
            if self.drum_sounds[drum_name]:
                self.drum_sounds[drum_name].set_volume(self.drum_volumes[drum_name])

    def get_pattern_name(self):
        """Get current pattern name"""
        return self.current_pattern_name
