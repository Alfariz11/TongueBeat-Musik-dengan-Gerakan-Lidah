import time
from audio_engine import AudioEngine

def test_audio_engine():
    print("Initializing AudioEngine...")
    engine = AudioEngine()
    print("AudioEngine initialized.")
    
    print("Starting scheduler...")
    # Scheduler starts in __init__
    
    print("Simulating arpeggio input...")
    try:
        for i in range(10):
            print(f"Update {i}")
            engine.update_arpeggio("left_hand", i % 15, 0.5)
            time.sleep(0.5)
            
        print("Stopping arpeggio...")
        engine.stop_arpeggio("left_hand")
        time.sleep(1)
        
    except Exception as e:
        print(f"Crash detected: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Cleaning up...")
        engine.cleanup()
        print("Done.")

if __name__ == "__main__":
    test_audio_engine()
