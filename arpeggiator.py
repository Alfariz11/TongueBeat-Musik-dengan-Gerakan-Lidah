import pygame
import numpy as np
from typing import Optional, Dict, Tuple
from collections import OrderedDict

class Arpeggiator:
    def __init__(
        self,
        waveform: str = 'rich_sine',
        attack: float = 0.01,
        release: float = 0.1,
        max_cache_size: int = 50,
        polyphony: int = 4
    ):
        """
        Initialize the arpeggiator with configurable parameters.
        
        Args:
            waveform: Type of waveform ('sine', 'rich_sine', 'square', 'saw')
            attack: Attack time in seconds
            release: Release time in seconds
            max_cache_size: Maximum number of cached sounds
            polyphony: Number of simultaneous notes
        """
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(polyphony * 2)  # Double channels for crossfade
        except pygame.error as e:
            raise RuntimeError(f"Failed to initialize audio: {e}")
        
        self.sample_rate = 44100
        self.base_midi = 57
        self.volume = 0.2
        self.last_note = None
        self.current_channels = []  # Track multiple channels for smooth transition
        
        # Timing - synchronized with drum beat
        self.bpm = 120
        self.beat_duration = 60.0 / self.bpm  # One full beat duration
        self.note_duration = self.beat_duration * 1.5  # Extend note for overlap
        self.last_update_time = 0
        
        # Waveform parameters
        self.waveform = waveform
        self.attack = attack
        self.release = release * 2  # Longer release for smooth transition
        
        # Volume settings
        self.master_volume = 0.3  # Master volume multiplier (reduced from default)
        
        # Note caching
        self.note_cache: OrderedDict[Tuple[float, float], pygame.mixer.Sound] = OrderedDict()
        self.max_cache_size = max_cache_size
        
        # Polyphony
        self.polyphony = polyphony
        
        # Crossfade settings
        self.crossfade_duration = 0.05  # 50ms crossfade
        
    def midi_to_freq(self, midi_note: int) -> float:
        """Convert MIDI note number to frequency in Hz."""
        return 440.0 * (2.0 ** ((midi_note - 69) / 12.0))
    
    def generate_waveform(self, frequency: float, t: np.ndarray) -> np.ndarray:
        """Generate different waveform types."""
        if self.waveform == 'sine':
            return np.sin(2 * np.pi * frequency * t)
        
        elif self.waveform == 'rich_sine':
            # Add harmonics for richer sound
            wave = (
                0.5 * np.sin(2 * np.pi * frequency * t) +
                0.25 * np.sin(4 * np.pi * frequency * t) +
                0.125 * np.sin(6 * np.pi * frequency * t) +
                0.0625 * np.sin(8 * np.pi * frequency * t)
            )
            return wave
        
        elif self.waveform == 'square':
            return np.sign(np.sin(2 * np.pi * frequency * t))
        
        elif self.waveform == 'saw':
            return 2 * (t * frequency - np.floor(t * frequency + 0.5))
        
        else:
            # Default to sine
            return np.sin(2 * np.pi * frequency * t)
    
    def apply_envelope(self, wave: np.ndarray, samples: int) -> np.ndarray:
        """Apply ADSR-style envelope to the waveform with smooth attack and release."""
        envelope = np.ones(samples)
        
        # Smooth attack with exponential curve
        attack_samples = int(samples * self.attack)
        if attack_samples > 0:
            attack_curve = np.linspace(0, 1, attack_samples)
            # Use exponential curve for smoother attack
            attack_curve = attack_curve ** 2
            envelope[:attack_samples] = attack_curve
        
        # Smooth release with exponential curve
        release_samples = int(samples * self.release)
        if release_samples > 0:
            release_curve = np.linspace(1, 0, release_samples)
            # Use exponential curve for smoother release
            release_curve = release_curve ** 2
            envelope[-release_samples:] = release_curve
        
        return wave * envelope
    
    def generate_tone(
        self, 
        frequency: float, 
        duration: float = 0.5, 
        volume: float = 1.0
    ) -> pygame.mixer.Sound:
        """Generate a tone with the specified parameters."""
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples, False)
        
        # Generate waveform
        wave = self.generate_waveform(frequency, t)
        
        # Normalize
        max_val = np.max(np.abs(wave))
        if max_val > 0:
            wave = wave / max_val
        
        # Apply envelope
        wave = self.apply_envelope(wave, samples)
        
        # Apply volume
        wave *= volume
        
        # Convert to 16-bit stereo
        wave_16bit = (wave * 32767).astype(np.int16)
        stereo = np.repeat(wave_16bit.reshape(-1, 1), 2, axis=1)
        
        return pygame.mixer.Sound(stereo.tobytes())
    
    def get_or_generate_tone(
        self, 
        frequency: float, 
        duration: float, 
        volume: float
    ) -> pygame.mixer.Sound:
        """Get cached tone or generate new one."""
        # Round frequency and duration for cache key
        cache_key = (round(frequency, 1), round(duration, 3))
        
        if cache_key not in self.note_cache:
            # Generate at full volume, we'll adjust when playing
            sound = self.generate_tone(frequency, duration, 1.0)
            
            # Manage cache size
            if len(self.note_cache) >= self.max_cache_size:
                # Remove oldest entry (FIFO)
                self.note_cache.popitem(last=False)
            
            self.note_cache[cache_key] = sound
        
        return self.note_cache[cache_key]
    
    def stop_all_sounds(self):
        """Stop all currently playing sounds with smooth fadeout."""
        # Fadeout all active channels smoothly
        for channel in self.current_channels:
            if channel and channel.get_busy():
                channel.fadeout(100)  # 100ms fadeout for smooth stop
        self.current_channels.clear()
    
    def update(
        self, 
        hand_height: float, 
        pinch_distance: float, 
        current_time: float,
        bpm: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Update arpeggiator state based on hand tracking data.
        
        Args:
            hand_height: Normalized hand height (0-1)
            pinch_distance: Normalized pinch distance (0-1)
            current_time: Current time in seconds
            bpm: Optional BPM to update tempo
            
        Returns:
            Dictionary with note info if a note was played, None otherwise
        """
        # Update BPM if provided
        if bpm is not None:
            self.set_bpm(bpm)
        
        # Calculate MIDI note with clamping
        midi_note = np.clip(
            self.base_midi + int(hand_height * 36), 
            0, 
            127
        )
        
        # Calculate volume from pinch distance
        self.volume = np.clip((1.0 - pinch_distance) ** 1.5, 0.05, 0.9)
        
        # Apply master volume scaling
        actual_volume = self.volume * self.master_volume
        
        # Check if we should play a new note (one note per beat)
        time_elapsed = current_time - self.last_update_time
        note_changed = midi_note != self.last_note
        should_trigger = time_elapsed >= self.beat_duration
        
        # Allow immediate note change if note changed significantly and enough time passed
        if should_trigger or (note_changed and time_elapsed > self.beat_duration * 0.25):
            self.last_update_time = current_time
            self.last_note = midi_note
            
            # Get frequency
            freq = self.midi_to_freq(midi_note)
            
            # Get or generate sound with duration matching beat
            try:
                sound = self.get_or_generate_tone(
                    freq, 
                    duration=self.note_duration,
                    volume=1.0  # We'll set volume when playing
                )
                
                # Clean up finished channels
                self.current_channels = [
                    ch for ch in self.current_channels 
                    if ch and ch.get_busy()
                ]
                
                # Find available channel
                channel = pygame.mixer.find_channel()
                if channel:
                    # Fade out old channels smoothly
                    fadeout_time = int(self.crossfade_duration * 1000)  # Convert to ms
                    for old_channel in self.current_channels:
                        if old_channel and old_channel.get_busy():
                            old_channel.fadeout(fadeout_time)
                    
                    # Play new sound with reduced volume
                    sound.set_volume(actual_volume)
                    channel.play(sound)
                    
                    # Add to active channels
                    self.current_channels.append(channel)
                    
                    # Keep only recent channels (limit to 3 for memory)
                    if len(self.current_channels) > 3:
                        oldest = self.current_channels.pop(0)
                        if oldest and oldest.get_busy():
                            oldest.stop()
                
                return {
                    "note": midi_note,
                    "frequency": freq,
                    "volume": self.volume,
                    "time": current_time
                }
                
            except pygame.error as e:
                print(f"Audio playback error: {e}")
                return None
        
        return None
    
    def set_bpm(self, bpm: int):
        """Update the BPM and recalculate beat duration."""
        old_bpm = self.bpm
        self.bpm = max(20, min(300, bpm))  # Clamp BPM to reasonable range
        self.beat_duration = 60.0 / self.bpm  # One beat duration
        self.note_duration = self.beat_duration * 1.5  # Extend note for smooth overlap
        
        # Only clear cache if BPM changed significantly
        if abs(old_bpm - self.bpm) > 5:
            self.clear_cache()
    
    def set_waveform(self, waveform: str):
        """Change waveform type and clear cache."""
        if waveform in ['sine', 'rich_sine', 'square', 'saw']:
            self.waveform = waveform
            self.clear_cache()
    
    def set_base_note(self, midi_note: int):
        """Set the base MIDI note."""
        self.base_midi = np.clip(midi_note, 0, 127)
    
    def clear_cache(self):
        """Clear the note cache."""
        self.note_cache.clear()
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_all_sounds()
        self.clear_cache()
        try:
            pygame.mixer.quit()
        except:
            pass
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()


# Example usage
if __name__ == "__main__":
    import time
    
    # Create arpeggiator with rich sine wave
    arp = Arpeggiator(
        waveform='rich_sine',
        attack=0.01,
        release=0.15,
        polyphony=4
    )
    
    try:
        # Simulate hand tracking data
        start_time = time.time()
        
        for i in range(100):
            current_time = time.time() - start_time
            
            # Simulate varying hand height and pinch
            hand_height = 0.5 + 0.3 * np.sin(current_time * 2)
            pinch_distance = 0.3 + 0.2 * np.sin(current_time * 3)
            
            result = arp.update(hand_height, pinch_distance, current_time)
            
            if result:
                print(f"Playing: MIDI {result['note']}, "
                      f"Freq {result['frequency']:.1f}Hz, "
                      f"Vol {result['volume']:.2f}")
            
            time.sleep(0.05)
    
    finally:
        arp.cleanup()