"""
Arpeggiator Controller
Hand #1 controls the arpeggios (raise hand to raise pitch, pinch to change volume)
"""
import pygame
import numpy as np
import array
from typing import List


class Arpeggiator:
    def __init__(self):
        # Larger buffer for smoother playback (but slightly more latency)
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

        # Musical parameters
        self.base_freq = 220.0  # A3
        self.scale = [0, 2, 4, 7, 9, 12, 14, 16]  # Major pentatonic extended
        self.current_note_index = 0
        self.volume = 0.3

        # Timing
        self.bpm = 120
        self.step_duration = 60.0 / self.bpm / 4  # 16th notes
        self.last_step_time = 0

        # Arpeggio pattern
        self.arp_pattern = [0, 2, 4, 6, 4, 2]  # Pattern indices
        self.pattern_index = 0

        # Audio generation
        self.sample_rate = 44100
        self.current_sound = None

    def midi_to_freq(self, midi_note):
        """Convert MIDI note number to frequency"""
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

    def generate_tone(self, frequency, duration=0.3, volume=0.3):
        """Generate a synthesized tone with ADSR envelope"""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)

        # Generate waveform (using multiple harmonics for richer sound)
        wave = np.zeros(samples)

        # Fundamental
        wave += np.sin(2 * np.pi * frequency * t)

        # Harmonics (creating a more interesting timbre)
        wave += 0.5 * np.sin(4 * np.pi * frequency * t)
        wave += 0.25 * np.sin(6 * np.pi * frequency * t)

        # Normalize
        wave = wave / np.max(np.abs(wave))

        # ADSR Envelope
        attack = int(samples * 0.1)
        decay = int(samples * 0.1)
        sustain_level = 0.7
        release = int(samples * 0.3)
        sustain = samples - attack - decay - release

        envelope = np.concatenate([
            np.linspace(0, 1, attack),
            np.linspace(1, sustain_level, decay),
            np.ones(sustain) * sustain_level,
            np.linspace(sustain_level, 0, release)
        ])

        # Apply envelope and volume
        wave = wave * envelope * volume

        # Convert to 16-bit PCM stereo using interleaved samples
        sound_buffer = array.array('h')
        for sample in wave:
            val = int(sample * 32767)
            sound_buffer.append(val)
            sound_buffer.append(val)

        return pygame.mixer.Sound(buffer=sound_buffer)

    def update(self, hand_height, pinch_distance, current_time):
        """Update arpeggiator based on hand position

        Args:
            hand_height: Normalized hand height (0-1)
            pinch_distance: Distance between thumb and index finger
            current_time: Current time in seconds
        """
        # Map hand height to octave shift (0-3 octaves)
        octave_shift = int(hand_height * 3)

        # Map pinch distance to volume (closer = louder)
        # Invert pinch distance: smaller distance = higher volume
        self.volume = np.clip(1.0 - (pinch_distance * 5), 0.1, 0.8)

        # Check if it's time for the next step
        if current_time - self.last_step_time >= self.step_duration:
            self.last_step_time = current_time

            # Get the next note in the pattern
            scale_index = self.arp_pattern[self.pattern_index]
            semitones = self.scale[scale_index % len(self.scale)]

            # Calculate MIDI note
            base_midi = 57  # A3
            midi_note = base_midi + semitones + (octave_shift * 12)

            # Generate and play the note
            frequency = self.midi_to_freq(midi_note)
            sound = self.generate_tone(frequency, duration=0.3, volume=self.volume)

            # Stop previous sound and play new one
            if self.current_sound:
                self.current_sound.stop()

            sound.play()
            self.current_sound = sound

            # Move to next step in pattern
            self.pattern_index = (self.pattern_index + 1) % len(self.arp_pattern)

            return {
                'note': midi_note,
                'frequency': frequency,
                'volume': self.volume,
                'octave': octave_shift
            }

        return None

    def set_bpm(self, bpm):
        """Set the tempo"""
        self.bpm = bpm
        self.step_duration = 60.0 / self.bpm / 4

    def set_pattern(self, pattern: List[int]):
        """Set a new arpeggio pattern"""
        self.arp_pattern = pattern
        self.pattern_index = 0
