import pygame
import threading
import numpy as np
import math
import time

class ContinuousOscillator:
    def __init__(self, sample_rate=44100, volume=0.5):
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=1)
        
        self.sample_rate = sample_rate
        self.volume = volume
        
        # oscillator state
        self.frequency = 7000
        self.phase = 0.0
        self.running = False

        # thread
        self.thread = threading.Thread(target=self._audio_loop)
        self.thread.daemon = True

    def start(self):
        self.running = True
        self.thread.start()

    def stop(self):
        self.running = False

    def set_frequency(self, freq):
        self.frequency = freq

    def set_volume(self, vol):
        self.volume = vol

    def _audio_loop(self):
        """Continuous real-time audio loop"""
        buffer_size = 512

        while self.running:
            t = np.arange(buffer_size)
            step = (2 * np.pi * self.frequency) / self.sample_rate

            # continuous phase
            phase_array = self.phase + t * step
            wave = np.sin(phase_array)

            # simpan phase terakhir untuk continuity
            self.phase = (self.phase + buffer_size * step) % (2 * np.pi)

            # apply volume
            wave *= self.volume

            # convert ke 16-bit
            audio = (wave * 32767).astype(np.int16).tobytes()

            sound = pygame.mixer.Sound(buffer=audio)
            pygame.mixer.Sound.play(sound)

            time.sleep(buffer_size / self.sample_rate)
