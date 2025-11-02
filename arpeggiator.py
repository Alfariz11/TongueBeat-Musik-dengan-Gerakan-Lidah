<<<<<<< HEAD
=======
"""
Arpeggiator Controller (Single Note)
Hand #1 controls one continuous note:
- Raise hand = higher pitch
- Pinch = louder volume
"""

>>>>>>> db5b17e (fix: appregiator note & visual)
import pygame
import numpy as np
import array


class Arpeggiator:
    def __init__(self):
<<<<<<< HEAD
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

        self.base_freq = 220.0
        self.scale = [0, 2, 4, 7, 9, 12, 14, 16]
        self.current_note_index = 0
        self.volume = 0.3

        self.bpm = 120
        self.step_duration = 60.0 / self.bpm / 4
        self.last_step_time = 0

        self.arp_pattern = [0, 2, 4, 6, 4, 2]
        self.pattern_index = 0

=======
        # Stereo mixer (lebih aman untuk semua sistem)
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

>>>>>>> db5b17e (fix: appregiator note & visual)
        self.sample_rate = 44100
        self.base_midi = 57  # A3
        self.last_freq = None
        self.last_note = None
        self.volume = 0.1
        self.current_sound = None
        self.current_freq = 220.0
        self.last_update_time = 0

<<<<<<< HEAD
    def midi_to_freq(self, midi_note):
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

    def generate_tone(self, frequency, duration=0.3, volume=0.3):
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)

        wave = np.zeros(samples)

        wave += np.sin(2 * np.pi * frequency * t)
        wave += 0.5 * np.sin(4 * np.pi * frequency * t)
        wave += 0.25 * np.sin(6 * np.pi * frequency * t)

        wave = wave / np.max(np.abs(wave))

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

        wave = wave * envelope * volume

        sound_buffer = array.array('h')
        for sample in wave:
            val = int(sample * 32767)
=======
    def midi_to_freq(self, midi_note: int):
        """Convert MIDI note number to frequency (Hz)."""
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

    def generate_tone(self, frequency, duration=0.3, volume=0.3):
        """Generate a short waveform tone."""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)

        # Waveform: kombinasi sinus untuk timbre lembut
        wave = (
            np.sin(2 * np.pi * frequency * t)
            + 0.5 * np.sin(4 * np.pi * frequency * t)
            + 0.25 * np.sin(6 * np.pi * frequency * t)
        )
        wave /= np.max(np.abs(wave))

        # Fade in/out ringan agar tidak klik
        fade_len = int(samples * 0.05)
        envelope = np.ones(samples)
        envelope[:fade_len] = np.linspace(0, 1, fade_len)
        envelope[-fade_len:] = np.linspace(1, 0, fade_len)
        wave *= envelope * volume

        # Convert ke stereo PCM
        sound_buffer = array.array("h")
        for s in wave:
            val = int(s * 32767)
>>>>>>> db5b17e (fix: appregiator note & visual)
            sound_buffer.append(val)
            sound_buffer.append(val)

        return pygame.mixer.Sound(buffer=sound_buffer)

<<<<<<< HEAD
    def update(self, hand_height, pinch_distance, current_time):
        octave_shift = int(hand_height * 3)

        self.volume = np.clip(1.0 - (pinch_distance * 5), 0.1, 0.8)

        if current_time - self.last_step_time >= self.step_duration:
            self.last_step_time = current_time

            scale_index = self.arp_pattern[self.pattern_index]
            semitones = self.scale[scale_index % len(self.scale)]

            base_midi = 57
            midi_note = base_midi + semitones + (octave_shift * 12)

            frequency = self.midi_to_freq(midi_note)
            sound = self.generate_tone(frequency, duration=0.3, volume=self.volume)

=======
    def update(self, hand_height, pinch_distance, current_time, bpm=None):
        """
        Main control:
        - hand_height: 0.0–1.0 (tinggi tangan)
        - pinch_distance: jarak jempol–telunjuk
        - bpm: sinkronisasi tempo dari drum machine
        """
        # Update tempo (sinkron ke drum)
        if bpm is not None:
            self.bpm = bpm
            # setiap nada baru di 1/4 beat (16th note = 4x per beat)
            self.step_duration = 60.0 / self.bpm / 4

        # Hitung pitch dari tinggi tangan
        midi_note = self.base_midi + int(hand_height * 36)
        freq = self.midi_to_freq(midi_note)

        # Volume dari pinch
        self.volume = np.clip(pinch_distance * 5, 0.1, 0.8)

        # Ganti nada berdasarkan ketukan (beat timing)
        if current_time - self.last_update_time >= self.step_duration:
            self.last_update_time = current_time

            # Mainkan nada baru
            sound = self.generate_tone(freq, duration=self.step_duration * 1.2, volume=self.volume)
>>>>>>> db5b17e (fix: appregiator note & visual)
            if self.current_sound:
                self.current_sound.stop()
            sound.play()
            self.current_sound = sound

<<<<<<< HEAD
            self.pattern_index = (self.pattern_index + 1) % len(self.arp_pattern)

=======
>>>>>>> db5b17e (fix: appregiator note & visual)
            return {
                "note": midi_note,
                "frequency": freq,
                "volume": self.volume,
            }

        return None

<<<<<<< HEAD
    def set_bpm(self, bpm):
        self.bpm = bpm
        self.step_duration = 60.0 / self.bpm / 4

    def set_pattern(self, pattern: List[int]):
        self.arp_pattern = pattern
        self.pattern_index = 0
=======

    def set_bpm(self, bpm):
        """Compatibility only (unused in single-note mode)."""
        self.bpm = bpm
>>>>>>> db5b17e (fix: appregiator note & visual)
