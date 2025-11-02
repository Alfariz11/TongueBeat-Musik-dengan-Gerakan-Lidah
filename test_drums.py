"""
Simple test script for drum sounds
"""
import pygame
import os
import time

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)

assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
print(f"Assets directory: {assets_dir}")
print(f"Assets directory exists: {os.path.exists(assets_dir)}")

sound_files = {
    'kick': 'kick.wav',
    'snare': 'snare.wav',
    'hihat': 'hihat.wav',
    'clap': 'clap.wav',
}

print("\nLoading drum sounds...")
drum_sounds = {}
for drum_name, filename in sound_files.items():
    filepath = os.path.join(assets_dir, filename)
    print(f"\nTrying to load: {filepath}")
    print(f"File exists: {os.path.exists(filepath)}")

    try:
        if os.path.exists(filepath):
            drum_sounds[drum_name] = pygame.mixer.Sound(filepath)
            print(f"[OK] Loaded {drum_name} from {filename}")
        else:
            print(f"[WARNING] {filename} not found")
            drum_sounds[drum_name] = None
    except Exception as e:
        print(f"[ERROR] Loading {filename}: {e}")
        drum_sounds[drum_name] = None

print("\n" + "="*50)
print("Testing drum sounds...")
print("Playing each drum sound with 1 second interval")
print("="*50)

for drum_name, sound in drum_sounds.items():
    if sound:
        print(f"\nPlaying {drum_name}...")
        sound.play()
        time.sleep(1)
    else:
        print(f"\nSkipping {drum_name} (not loaded)")

print("\n[DONE] Test completed!")
