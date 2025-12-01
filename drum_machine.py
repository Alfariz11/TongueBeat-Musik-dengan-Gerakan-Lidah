import pygame
import os
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

@dataclass
class DrumHit:
    """Represents a single drum hit event."""
    drum: str
    velocity: float
    volume: float
    step: int
    timestamp: float

class HandSide(Enum):
    """Enum for hand sides."""
    LEFT = "Left"
    RIGHT = "Right"

class DrumMachine:
    """
    Advanced drum machine with pattern sequencing, swing, and gesture control.
    """
    
    # Class-level constants
    DRUM_TYPES = ['kick', 'snare', 'hihat', 'hightom', 'crashcymbal']
    MAX_STEPS = 16
    MIN_BPM = 40
    MAX_BPM = 300
    
    def __init__(
        self,
        master_gain: float = 0.3,
        bpm: int = 120,
        swing_amount: float = 0.05,
        num_channels: int = 16
    ):
        """
        Initialize the drum machine.
        
        Args:
            master_gain: Master volume multiplier (0.0 - 1.0)
            bpm: Beats per minute (40-300)
            swing_amount: Swing/shuffle amount (0.0 - 0.2)
            num_channels: Number of mixer channels for polyphony
        """
        # Initialize pygame mixer with optimized settings
        try:
            pygame.mixer.init(
                frequency=44100, 
                size=-16, 
                channels=2, 
                buffer=512  # Reduced buffer for lower latency
            )
            pygame.mixer.set_num_channels(num_channels)
        except pygame.error as e:
            raise RuntimeError(f"Failed to initialize audio mixer: {e}")
        
        # Drum configuration
        self.finger_to_drum = self.DRUM_TYPES.copy()
        self.drum_sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self.drum_channels: Dict[str, Optional[pygame.mixer.Channel]] = {
            drum: None for drum in self.DRUM_TYPES
        }
        
        # Volume settings
        self.master_gain = max(0.0, min(1.0, master_gain))
        self.drum_volumes = {
            'kick': 0.85,
            'snare': 0.75,
            'hihat': 0.45,
            'hightom': 0.55,
            'crashcymbal': 0.65,
        }
        
        # Pattern definitions
        self._initialize_patterns()
        
        # State tracking
        self.prev_fist_state: Dict[str, bool] = {
            HandSide.LEFT.value: False,
            HandSide.RIGHT.value: False
        }
        self.active_fingers: List[bool] = [False] * len(self.DRUM_TYPES)
        self.previous_fingers: List[bool] = [False] * len(self.DRUM_TYPES)
        
        # Timing
        self.bpm = self._clamp_bpm(bpm)
        self.swing_amount = max(0.0, min(0.2, swing_amount))
        self.step_duration_base = 60.0 / self.bpm / 4
        self.last_step_time = 0.0
        self.current_step = 0
        
        # Performance tracking
        self.recent_played: List[DrumHit] = []
        self.play_history: List[DrumHit] = []
        self.max_history = 100
        
        # Load sounds
        self._load_drum_sounds()
        
    def _initialize_patterns(self):
        """Initialize all drum patterns."""
        self.pattern_sets: Dict[int, Dict[str, Dict[int, float]]] = {
            # Pattern 0: Basic rock beat
            0: {
                'kick': {
                    0: 1.0, 
                    5: 0.7, 
                    8: 0.9, 
                    11: 0.6
                },
                'snare': {
                    4: 1.0,
                    12: 1.0
                },
                'hihat': {
                    **{i: 0.45 for i in range(16)},
                    **{3: 0.25, 7: 0.25, 11: 0.25, 15: 0.25}
                },
                'hightom': {},
                'crashcymbal': {
                    0: 0.9
                },
            },
            # Pattern 1: Simple beat
            1: {
                'kick': {
                    0: 1.0,
                    4: 1.0,
                    8: 1.0,
                    12: 1.0
                },
                'snare': {
                    4: 0.9,
                    12: 0.9
                },
                'hihat': {
                    2: 0.6,
                    6: 0.6,
                    10: 0.6,
                    14: 0.6,
                    **{i: 0.35 for i in range(16)}
                },
                'hightom': {
                    7: 0.5,
                    15: 0.6
                },
                'crashcymbal': {
                    0: 1.0
                },
            },
            # Pattern 2: Complex/funky beat
            2: {
                'kick': {
                    0: 1.0,
                    3: 0.55,
                    7: 0.85,
                    10: 0.6,
                    14: 0.75
                },
                'snare': {
                    4: 1.0,
                    12: 1.0,
                    6: 0.35,  
                    15: 0.3    
                },
                'hihat': {
                    **{i: 0.4 for i in range(16)},
                    2: 0.55, 
                    6: 0.55,
                    10: 0.55,
                    14: 0.55
                },
                'hightom': {
                    9: 0.45
                },
                'crashcymbal': {},
            },
        }
        self.current_pattern_set = 0
        self.drum_patterns = self.pattern_sets[self.current_pattern_set]
    
    def _clamp_bpm(self, bpm: int) -> int:
        """Clamp BPM to valid range."""
        return max(self.MIN_BPM, min(self.MAX_BPM, bpm))
    
    def _load_drum_sounds(self):
        """Load drum samples from disk with error handling."""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        audios_dir = os.path.join(current_dir, 'audios')
        
        sound_files = {
            'kick': 'kick.wav',
            'snare': 'snare.wav',
            'hihat': 'hihat.wav',
            'hightom': 'hightom.wav',
            'crashcymbal': 'crashcymbal.wav',
        }
        
        loaded_count = 0
        for drum_name, filename in sound_files.items():
            filepath = os.path.join(audios_dir, filename)
            try:
                if os.path.exists(filepath):
                    sound = pygame.mixer.Sound(filepath)
                    # Apply master gain to base volume
                    sound.set_volume(self.drum_volumes[drum_name] * self.master_gain)
                    self.drum_sounds[drum_name] = sound
                    loaded_count += 1
                else:
                    print(f"Warning: Sound file not found: {filepath}")
                    self.drum_sounds[drum_name] = None
            except pygame.error as e:
                print(f"Error loading {drum_name}: {e}")
                self.drum_sounds[drum_name] = None
        
        if loaded_count == 0:
            print("Warning: No drum sounds loaded!")
        else:
            print(f"Loaded {loaded_count}/{len(sound_files)} drum sounds")
    
    def _get_step_duration(self, step: int) -> float:
        """
        Calculate step duration with swing applied.
        
        Args:
            step: Current step number (0-15)
            
        Returns:
            Duration in seconds for this step
        """
        if step % 2 == 1:
            return self.step_duration_base * (1.0 + self.swing_amount)
        return self.step_duration_base * (1.0 - self.swing_amount)
    
    def _play_drum(
        self, 
        drum_name: str, 
        velocity: float, 
        current_time: float
    ) -> Optional[DrumHit]:
        """
        Play a drum sound with specified velocity.
        
        Args:
            drum_name: Name of the drum to play
            velocity: Hit velocity (0.0-1.0)
            current_time: Current timestamp
            
        Returns:
            DrumHit object if played successfully, None otherwise
        """
        if drum_name not in self.drum_sounds or self.drum_sounds[drum_name] is None:
            return None
        
        try:
            # Calculate actual volume
            base_volume = self.drum_volumes[drum_name] * self.master_gain
            actual_volume = base_volume * velocity
            actual_volume = max(0.0, min(1.0, actual_volume))
            
            # Set volume and play
            sound = self.drum_sounds[drum_name]
            sound.set_volume(actual_volume)
            
            # Try to use dedicated channel, fall back to any available
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(sound)
                self.drum_channels[drum_name] = channel
            else:
                # Force play if no channel available
                sound.play()
            
            # Create hit record
            hit = DrumHit(
                drum=drum_name,
                velocity=velocity,
                volume=actual_volume,
                step=self.current_step,
                timestamp=current_time
            )
            
            return hit
            
        except pygame.error as e:
            print(f"Error playing {drum_name}: {e}")
            return None
    
    def change_pattern_set(self, pattern_set_index: int):
        """
        Change to a different pattern set.
        
        Args:
            pattern_set_index: Index of the pattern set to switch to
        """
        if pattern_set_index in self.pattern_sets:
            self.current_pattern_set = pattern_set_index
            self.drum_patterns = self.pattern_sets[self.current_pattern_set]
            self.current_step = 0
            print(f"Switched to pattern set {pattern_set_index}")
        else:
            print(f"Warning: Pattern set {pattern_set_index} does not exist")
    
    def update(
        self, 
        fingers_extended: List[bool], 
        current_time: float, 
        is_fist: bool = False,
        hand_side: str = "Right"
    ) -> Dict:
        """
        Update drum machine state based on hand tracking input.
        
        Args:
            fingers_extended: List of 5 booleans indicating which fingers are extended
            current_time: Current timestamp in seconds
            is_fist: Whether hand is making a fist gesture
            hand_side: Which hand is being tracked ("Left" or "Right")
            
        Returns:
            Dictionary containing current state and played drums
        """
        # Handle pattern switching with fist gesture
        if is_fist and not self.prev_fist_state.get(hand_side, False):
            next_pattern = (self.current_pattern_set + 1) % len(self.pattern_sets)
            self.change_pattern_set(next_pattern)
        
        self.prev_fist_state[hand_side] = is_fist
        
        # Update active fingers
        self.previous_fingers = self.active_fingers.copy()
        self.active_fingers = fingers_extended.copy()
        
        # Detect newly activated fingers (for manual triggering)
        newly_activated = []
        for i, (current, previous) in enumerate(zip(self.active_fingers, self.previous_fingers)):
            if current and not previous:
                newly_activated.append(i)
        
        # Get active drums
        active_drums = []
        for finger_idx, is_active in enumerate(self.active_fingers):
            if is_active and finger_idx < len(self.finger_to_drum):
                drum_name = self.finger_to_drum[finger_idx]
                active_drums.append(drum_name)
        
        # Sequencer update
        played_drums: List[DrumHit] = []
        step_duration = self._get_step_duration(self.current_step)
        
        if current_time - self.last_step_time >= step_duration:
            self.last_step_time = current_time
            
            # Play drums according to pattern
            for drum_name in active_drums:
                if drum_name in self.drum_patterns:
                    pattern = self.drum_patterns[drum_name]
                    if self.current_step in pattern:
                        velocity = pattern[self.current_step]
                        hit = self._play_drum(drum_name, velocity, current_time)
                        if hit:
                            played_drums.append(hit)
            
            # Update history
            if played_drums:
                self.recent_played = played_drums.copy()
                self.play_history.extend(played_drums)
                
                # Trim history if too long
                if len(self.play_history) > self.max_history:
                    self.play_history = self.play_history[-self.max_history:]
            
            # Advance step
            self.current_step = (self.current_step + 1) % self.MAX_STEPS
        
        # Build active patterns info
        active_patterns = {}
        pattern_steps_flat = {}
        for drum_name in active_drums:
            if drum_name in self.drum_patterns:
                pattern = self.drum_patterns[drum_name]
                active_patterns[drum_name] = pattern
                pattern_steps_flat[drum_name] = list(pattern.keys())
        
        return {
            'step': self.current_step,
            'played': [hit.drum for hit in played_drums],
            'played_details': [
                {
                    'drum': hit.drum,
                    'velocity': hit.velocity,
                    'volume': hit.volume,
                    'step': hit.step
                }
                for hit in played_drums
            ],
            'active_drums': active_drums,
            'active_patterns': active_patterns,
            'active_patterns_flat': pattern_steps_flat,
            'fingers_extended': fingers_extended,
            'newly_activated': newly_activated,
            'bpm': self.bpm,
            'pattern_set': self.current_pattern_set,
            'swing_amount': self.swing_amount,
            'time': current_time
        }
    
    def trigger_drum_manual(
        self, 
        drum_name: str, 
        velocity: float = 1.0,
        current_time: Optional[float] = None
    ) -> Optional[DrumHit]:
        """
        Manually trigger a drum sound outside of the sequencer.
        
        Args:
            drum_name: Name of drum to trigger
            velocity: Hit velocity (0.0-1.0)
            current_time: Optional timestamp
            
        Returns:
            DrumHit object if successful
        """
        if current_time is None:
            current_time = pygame.time.get_ticks() / 1000.0
        
        return self._play_drum(drum_name, velocity, current_time)
    
    def set_bpm(self, bpm: int):
        """
        Set the BPM (beats per minute).
        
        Args:
            bpm: New BPM value (40-300)
        """
        self.bpm = self._clamp_bpm(bpm)
        self.step_duration_base = 60.0 / self.bpm / 4
    
    def set_swing(self, swing_amount: float):
        """
        Set the swing/shuffle amount.
        
        Args:
            swing_amount: Swing amount (0.0-0.2)
        """
        self.swing_amount = max(0.0, min(0.2, swing_amount))
    
    def set_drum_volume(self, drum_name: str, volume: float):
        """
        Set the volume for a specific drum.
        
        Args:
            drum_name: Name of the drum
            volume: Volume level (0.0-1.0, relative to master)
        """
        if drum_name in self.drum_volumes:
            self.drum_volumes[drum_name] = max(0.0, min(1.0, volume))
            if self.drum_sounds.get(drum_name):
                # Apply master gain
                actual_volume = self.drum_volumes[drum_name] * self.master_gain
                self.drum_sounds[drum_name].set_volume(actual_volume)
    
    def set_master_gain(self, gain: float):
        """
        Set the master gain/volume.
        
        Args:
            gain: Master gain (0.0-1.0)
        """
        self.master_gain = max(0.0, min(1.0, gain))
        
        # Update all drum volumes
        for drum_name in self.drum_sounds:
            if self.drum_sounds[drum_name]:
                actual_volume = self.drum_volumes[drum_name] * self.master_gain
                self.drum_sounds[drum_name].set_volume(actual_volume)
    
    def get_drum_name_for_finger(self, finger_idx: int) -> Optional[str]:
        """
        Get the drum name associated with a finger index.
        
        Args:
            finger_idx: Finger index (0-4)
            
        Returns:
            Drum name or None if invalid index
        """
        if 0 <= finger_idx < len(self.finger_to_drum):
            return self.finger_to_drum[finger_idx]
        return None
    
    def get_pattern_for_drum(self, drum_name: str) -> Dict[int, float]:
        """
        Get the current pattern for a specific drum.
        
        Args:
            drum_name: Name of the drum
            
        Returns:
            Dictionary mapping step numbers to velocities
        """
        return self.drum_patterns.get(drum_name, {})
    
    def add_custom_pattern(self, pattern_index: int, pattern: Dict[str, Dict[int, float]]):
        """
        Add a custom pattern set.
        
        Args:
            pattern_index: Index for the new pattern
            pattern: Pattern dictionary
        """
        self.pattern_sets[pattern_index] = pattern
        print(f"Added custom pattern at index {pattern_index}")
    
    def clear_pattern(self, drum_name: str):
        """
        Clear the pattern for a specific drum in current pattern set.
        
        Args:
            drum_name: Name of drum to clear
        """
        if drum_name in self.drum_patterns:
            self.drum_patterns[drum_name] = {}
    
    def reset_sequencer(self):
        """Reset the sequencer to step 0."""
        self.current_step = 0
        self.last_step_time = 0.0
    
    def get_stats(self) -> Dict:
        """
        Get performance statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'total_hits': len(self.play_history),
            'recent_hits': len(self.recent_played),
            'current_pattern': self.current_pattern_set,
            'current_step': self.current_step,
            'bpm': self.bpm,
            'swing': self.swing_amount,
            'active_drums': sum(self.active_fingers),
            'loaded_sounds': sum(1 for s in self.drum_sounds.values() if s is not None)
        }
    
    def stop_all(self):
        """Stop all currently playing drum sounds."""
        for channel in self.drum_channels.values():
            if channel and channel.get_busy():
                channel.fadeout(50)  # 50ms fadeout
        self.drum_channels = {drum: None for drum in self.DRUM_TYPES}
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_all()
        self.drum_sounds.clear()
        try:
            pygame.mixer.quit()
        except:
            pass
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()


# Example usage and testing
if __name__ == "__main__":
    import time
    
    # Create drum machine
    drum_machine = DrumMachine(
        master_gain=0.4,
        bpm=120,
        swing_amount=0.08
    )
    
    try:
        print("Drum Machine Test")
        print(f"Stats: {drum_machine.get_stats()}")
        
        # Simulate finger tracking
        start_time = time.time()
        
        # Activate kick, snare, and hihat (fingers 0, 1, 2)
        fingers = [True, True, True, False, False]
        
        for i in range(64):  # Run for 4 bars (64 steps)
            current_time = time.time() - start_time
            
            # Toggle pattern every 2 bars
            is_fist = (i % 32) == 31
            
            result = drum_machine.update(fingers, current_time, is_fist=is_fist)
            
            if result['played']:
                print(f"Step {result['step']:2d}: {', '.join(result['played'])}")
            
            time.sleep(0.05)
        
        print(f"\nFinal stats: {drum_machine.get_stats()}")
        
    finally:
        drum_machine.cleanup()