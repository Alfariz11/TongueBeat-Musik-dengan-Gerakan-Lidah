import pygame
import numpy as np
import threading
import time
import os

class AudioEngine:
    def __init__(self, assets_path=None):
        # Initialize mixer with appropriate settings
        # Check if mixer is already initialized to avoid errors
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        if assets_path is None:
            # Robustly find assets folder relative to this script
            base_dir = os.path.dirname(os.path.abspath(__file__))
            # Changed from "assets" to "audios" to match existing project structure
            self.assets_path = os.path.join(base_dir, "audios")
        else:
            self.assets_path = assets_path
        
        # Load Drums
        self.drums = {}
        # Map drum names to existing filenames if they differ, or just use the names
        # Existing files: kick.wav, snare.wav, hihat.wav, crashcymbal.wav, hightom.wav
        # The user code asked for: kick, snare, hihat, clap. 
        # I will map 'clap' to 'crashcymbal' or just load what's available.
        # Let's try to load the requested ones, and maybe map clap to crash if clap doesn't exist.
        
        drum_files = {
            'kick': 'kick.wav',
            'snare': 'snare.wav',
            'hihat': 'hihat.wav',
            'clap': 'crashcymbal.wav' # Fallback/Mapping
        }

        for name, filename in drum_files.items():
            path = os.path.join(self.assets_path, filename)
            if os.path.exists(path):
                self.drums[name] = pygame.mixer.Sound(path)
                # Adjust volumes to match JS
                if name == 'kick': self.drums[name].set_volume(0.5)
                elif name == 'hihat': self.drums[name].set_volume(0.8)
            else:
                print(f"Warning: Could not find {path}")

        # Synth State
        self.scale = self._generate_scale_frequencies()
        self.synth_sounds = self._precompute_synth_sounds()
        self.active_arpeggios = {} # hand_index -> {pattern, current_note_index, ...}
        
        # Drum Pattern State
        self.drum_pattern = {
            'kick':  [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0],
            'snare': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
            'hihat': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
            'clap':  [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0]
        }
        self.active_drums = set()
        
        # Scheduler State
        self.bpm = 100
        self.step_duration = (60 / self.bpm) / 4 # 16th notes
        self.current_step = 0
        self.running = True
        self.lock = threading.RLock()
        
        # Start Scheduler Thread
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()

    def _generate_scale_frequencies(self):
        # C Minor Pentatonic: C, Eb, F, G, Bb
        # Generate a few octaves
        base_freqs = [130.81, 155.56, 174.61, 196.00, 233.08] # C3 - Bb3
        scale = []
        for i in range(3): # 3 Octaves
            multiplier = 2**i
            for f in base_freqs:
                scale.append(f * multiplier)
        return scale

    def _precompute_synth_sounds(self):
        sounds = []
        sample_rate = 44100
        duration = 0.2 # Short blip for arpeggio
        
        for freq in self.scale:
            # Generate Sine Wave
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = np.sin(2 * np.pi * freq * t)
            
            # Simple Envelope (Attack/Decay)
            envelope = np.concatenate([
                np.linspace(0, 1, int(sample_rate * 0.01)), # Attack
                np.linspace(1, 0, int(sample_rate * (duration - 0.01))) # Decay
            ])
            wave = wave * envelope
            
            # Convert to 16-bit PCM
            audio = (wave * 32767).astype(np.int16)
            # Stereo
            stereo = np.column_stack((audio, audio))
            
            sound = pygame.sndarray.make_sound(stereo)
            sounds.append(sound)
        return sounds

    def _scheduler_loop(self):
        next_step_time = time.time()
        while self.running:
            current_time = time.time()
            if current_time >= next_step_time:
                self._play_step(self.current_step)
                self.current_step = (self.current_step + 1) % 16
                next_step_time += self.step_duration
            else:
                time.sleep(0.001)

    def _play_step(self, step):
        with self.lock:
            # Play Drums
            for drum_name in self.active_drums:
                if drum_name in self.drum_pattern and self.drum_pattern[drum_name][step]:
                    if drum_name in self.drums:
                        self.drums[drum_name].play()
            
            # Play Arpeggios
            for hand_idx, arp_data in self.active_arpeggios.items():
                # Simple Up/Down pattern logic
                # For now, just play the root note or a simple interval
                # The JS version does a complex pattern. Let's do a simple chord arpeggio.
                # Root, +3 (min 3rd), +5 (4th), +7 (5th) indices in our scale?
                # Let's just play the note corresponding to the hand height for now, 
                # or a simple sequence based on the step.
                
                root_idx = arp_data['note_index']
                # Create a pattern: Root, +1, +2, +1 (relative to scale index)
                offsets = [0, 2, 4, 2] 
                offset = offsets[step % 4]
                
                note_idx = root_idx + offset
                if 0 <= note_idx < len(self.synth_sounds):
                    vol = arp_data.get('volume', 0.5)
                    sound = self.synth_sounds[note_idx]
                    sound.set_volume(vol)
                    sound.play()

    def update_drums(self, active_drums_set):
        with self.lock:
            self.active_drums = active_drums_set

    def start_arpeggio(self, hand_idx, note_index):
        with self.lock:
            self.active_arpeggios[hand_idx] = {'note_index': note_index, 'volume': 0.5}

    def update_arpeggio(self, hand_idx, note_index, volume):
        with self.lock:
            if hand_idx in self.active_arpeggios:
                self.active_arpeggios[hand_idx]['note_index'] = note_index
                self.active_arpeggios[hand_idx]['volume'] = volume
            else:
                self.start_arpeggio(hand_idx, note_index)

    def stop_arpeggio(self, hand_idx):
        with self.lock:
            if hand_idx in self.active_arpeggios:
                del self.active_arpeggios[hand_idx]
    
    def set_bpm(self, bpm):
        with self.lock:
            self.bpm = bpm
            self.step_duration = (60 / self.bpm) / 4

    def cleanup(self):
        self.running = False
        self.scheduler_thread.join()
        # Do not quit mixer here if other parts might use it, but usually it's fine
        # pygame.mixer.quit() 
