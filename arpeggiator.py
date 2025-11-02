"""
Arpeggiator Controller (Single Note)
Hand #1 controls one continuous note:
- Raise hand = higher pitch
- Pinch = louder volume
"""

import pygame
import numpy as np
import array


class Arpeggiator:
    def __init__(self):
        # Stereo mixer (lebih aman untuk semua sistem)
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.sample_rate = 44100
        self.base_midi = 57  # A3
        self.last_freq = None
        self.last_note = None
        self.volume = 0.1
        self.current_sound = None
        self.current_freq = 220.0
        self.last_update_time = 0

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
            sound_buffer.append(val)
            sound_buffer.append(val)

        return pygame.mixer.Sound(buffer=sound_buffer)

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
            if self.current_sound:
                self.current_sound.stop()
            sound.play()
            self.current_sound = sound

            return {
                "note": midi_note,
                "frequency": freq,
                "volume": self.volume,
            }

        return None


    def set_bpm(self, bpm):
        """Compatibility only (unused in single-note mode)."""
        self.bpm = bpm