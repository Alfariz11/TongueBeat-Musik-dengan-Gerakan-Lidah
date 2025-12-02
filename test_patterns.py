import time
from audio_engine import AudioEngine

def test_pattern_switching():
    print("Initializing AudioEngine...")
    engine = AudioEngine()
    print("AudioEngine initialized.")
    
    print("Starting scheduler...")
    
    try:
        # Test pattern switching
        for i in range(8):
            print(f"Current Pattern Index: {engine.current_pattern_index}")
            # Simulate active drums to hear the pattern
            engine.update_drums({'kick', 'snare', 'hihat'})
            
            time.sleep(2)
            
            print("Switching pattern...")
            new_idx = engine.next_pattern()
            print(f"New Pattern Index: {new_idx}")
            
    except Exception as e:
        print(f"Crash detected: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Cleaning up...")
        engine.cleanup()
        print("Done.")

if __name__ == "__main__":
    test_pattern_switching()
