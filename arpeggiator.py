import pygame
import numpy as np
import array


class Arpeggiator:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.sample_rate = 44100
        self.base_midi = 57
        self.volume = 2.0
        self.last_note = None
        self.current_sound = None
        self.bpm = 120
        self.step_duration = 60.0 / self.bpm / 4
        self.last_update_time = 0

    def midi_to_freq(self, midi_note: int):
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))

    def generate_tone(self, frequency, duration=0.3, volume=0.5):
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)

        wave = (
            np.sin(2 * np.pi * frequency * t)
            + 0.5 * np.sin(4 * np.pi * frequency * t)
            + 0.25 * np.sin(6 * np.pi * frequency * t)
        )
        wave /= np.max(np.abs(wave))

        fade_len = int(samples * 0.05)
        envelope = np.ones(samples)
        envelope[:fade_len] = np.linspace(0, 1, fade_len)
        envelope[-fade_len:] = np.linspace(1, 0, fade_len)
        wave *= envelope * volume

        sound_buffer = array.array("h")
        for s in wave:
            val = int(s * 32767)
            sound_buffer.append(val)
            sound_buffer.append(val)

        return pygame.mixer.Sound(buffer=sound_buffer)

    def update(self, hand_height, pinch_distance, current_time, bpm=None):
        if bpm is not None:
            self.bpm = bpm
            self.step_duration = 60.0 / self.bpm / 4

        midi_note = self.base_midi + int(hand_height * 36)
        freq = self.midi_to_freq(midi_note)
        
        self.volume = np.clip((1.0 - pinch_distance) ** 1.5, 0.05, 0.9)

        if current_time - self.last_update_time >= self.step_duration:
            self.last_update_time = current_time
            sound = self.generate_tone(freq, duration=self.step_duration * 1.2, volume=self.volume)
            if self.current_sound:
                self.current_sound.stop()
            sound.set_volume(self.volume)
            sound.play()
            self.current_sound = sound

            return {
                "note": midi_note,
                "frequency": freq,
                "volume": self.volume,
            }

        return None

    def set_bpm(self, bpm):
        self.bpm = bpm
        self.step_duration = 60.0 / self.bpm / 4
