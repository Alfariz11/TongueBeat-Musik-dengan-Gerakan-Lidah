"""
Drum Controller Module
Maps tongue movements to drum pads and plays corresponding sounds
"""

import pygame
import os
import time
from pathlib import Path


class DrumPad:
    """Represents a single drum pad with position and sound"""

    def __init__(self, name, sound_file, image_file, position, size):
        """
        Initialize drum pad

        Args:
            name: Name of the drum (e.g., 'kick', 'snare')
            sound_file: Path to audio file
            image_file: Path to image file
            position: (x, y) tuple for top-left corner
            size: (width, height) tuple
        """
        self.name = name
        self.position = position
        self.size = size
        self.sound = None
        self.image = None
        self.is_active = False
        self.last_trigger_time = 0
        self.cooldown = 0.15  # Minimum time between triggers (seconds)

        # Load sound
        if os.path.exists(sound_file):
            self.sound = pygame.mixer.Sound(sound_file)
        else:
            print(f"Warning: Sound file not found: {sound_file}")

        # Load image
        if os.path.exists(image_file):
            import cv2
            self.image = cv2.imread(image_file)
            self.image = cv2.resize(self.image, size)
        else:
            print(f"Warning: Image file not found: {image_file}")

    def contains_point(self, x, y):
        """
        Check if a point is within this drum pad

        Args:
            x, y: Point coordinates

        Returns:
            bool: True if point is inside pad
        """
        px, py = self.position
        w, h = self.size

        return px <= x <= px + w and py <= y <= py + h

    def trigger(self):
        """
        Trigger the drum sound if cooldown period has passed

        Returns:
            bool: True if sound was played
        """
        current_time = time.time()

        if current_time - self.last_trigger_time >= self.cooldown:
            if self.sound:
                self.sound.play()
                self.last_trigger_time = current_time
                self.is_active = True
                return True

        return False

    def reset_active(self):
        """Reset active state (for visual feedback)"""
        self.is_active = False


class DrumController:
    """Controls drum pads and maps tongue movements to sounds"""

    def __init__(self, audio_dir="audios", image_dir="images"):
        """
        Initialize drum controller

        Args:
            audio_dir: Directory containing drum sound files
            image_dir: Directory containing drum pad images
        """
        # Initialize pygame mixer
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.audio_dir = Path(audio_dir)
        self.image_dir = Path(image_dir)

        self.drum_pads = []
        self.active_pad = None

        # Direction to drum mapping
        self.direction_map = {
            'center': 'snare',
            'left': 'hihat',
            'right': 'crash',
            'up': 'kick',
            'down': 'snare'
        }

    def setup_drum_pads(self, screen_width, screen_height):
        """
        Set up drum pad positions on screen

        Args:
            screen_width: Width of display area
            screen_height: Height of display area
        """
        # Drum pad configuration
        # Layout:
        #        [Crash]
        # [HiHat] [Snare] [Tom1]
        # [Kick] [Tom2] [Tom3]

        pad_width = screen_width // 4
        pad_height = screen_height // 4

        drum_configs = [
            # Top row
            {
                'name': 'crash',
                'sound': 'crashcymbal.wav',
                'image': 'crash.png',
                'position': (screen_width // 2 - pad_width // 2, 10),
                'size': (pad_width, pad_height)
            },
            # Middle row
            {
                'name': 'hihat',
                'sound': 'hihat.wav',
                'image': 'kick.png',  # Using kick image as placeholder
                'position': (10, pad_height + 20),
                'size': (pad_width, pad_height)
            },
            {
                'name': 'snare',
                'sound': 'snare.wav',
                'image': 'snare.png',
                'position': (screen_width // 2 - pad_width // 2, pad_height + 20),
                'size': (pad_width, pad_height)
            },
            {
                'name': 'tom1',
                'sound': 'hightom.wav',
                'image': 'tom1.png',
                'position': (screen_width - pad_width - 10, pad_height + 20),
                'size': (pad_width, pad_height)
            },
            # Bottom row
            {
                'name': 'kick',
                'sound': 'kick.wav',
                'image': 'kick.png',
                'position': (10, 2 * pad_height + 30),
                'size': (pad_width, pad_height)
            },
            {
                'name': 'tom2',
                'sound': 'midtom.wav',
                'image': 'tom2.png',
                'position': (screen_width // 2 - pad_width // 2, 2 * pad_height + 30),
                'size': (pad_width, pad_height)
            },
            {
                'name': 'tom3',
                'sound': 'lowtom.wav',
                'image': 'tom3.png',
                'position': (screen_width - pad_width - 10, 2 * pad_height + 30),
                'size': (pad_width, pad_height)
            }
        ]

        # Create drum pads
        self.drum_pads = []
        for config in drum_configs:
            sound_path = self.audio_dir / config['sound']
            image_path = self.image_dir / config['image']

            pad = DrumPad(
                name=config['name'],
                sound_file=str(sound_path),
                image_file=str(image_path),
                position=config['position'],
                size=config['size']
            )
            self.drum_pads.append(pad)

    def trigger_by_position(self, x, y):
        """
        Trigger drum pad at given position

        Args:
            x, y: Tongue tip coordinates

        Returns:
            str: Name of triggered pad, or None
        """
        for pad in self.drum_pads:
            if pad.contains_point(x, y):
                if pad.trigger():
                    self.active_pad = pad.name
                    return pad.name

        return None

    def trigger_by_direction(self, direction):
        """
        Trigger drum based on tongue direction

        Args:
            direction: Direction string ('left', 'right', 'up', 'down', 'center')

        Returns:
            str: Name of triggered pad, or None
        """
        if direction == 'none':
            return None

        # Get drum name from direction
        drum_name = self.direction_map.get(direction)

        if drum_name:
            # Find and trigger the drum pad
            for pad in self.drum_pads:
                if pad.name == drum_name:
                    if pad.trigger():
                        self.active_pad = pad.name
                        return pad.name

        return None

    def reset_all_active(self):
        """Reset all pad active states"""
        for pad in self.drum_pads:
            pad.reset_active()
        self.active_pad = None

    def get_drum_pad(self, name):
        """
        Get drum pad by name

        Args:
            name: Name of the drum pad

        Returns:
            DrumPad object or None
        """
        for pad in self.drum_pads:
            if pad.name == name:
                return pad
        return None

    def cleanup(self):
        """Clean up pygame mixer"""
        pygame.mixer.quit()
