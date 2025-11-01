# Quick Start Guide - Hand-Controlled Music Generator (Python)

## Installation Complete! ✓

Your environment is already set up and ready to use.

## Running the Application

### Option 1: Using the Run Script (Easiest)
```bash
# On Windows
run.bat

# On Linux/Mac
./run.sh
```

### Option 2: Direct Python Command
```bash
".venv/Scripts/python.exe" main.py
```

## Controls

### Left Hand - Arpeggiator
- **Move hand up/down**: Change pitch (higher hand = higher notes)
- **Pinch thumb & index finger**: Control volume
  - Fingers close together = lower volume
  - Fingers apart = higher volume

### Right Hand - Drum Machine
- **1 finger** (index): Basic 4/4 pattern
- **2 fingers** (index + middle): Pattern with claps
- **3 fingers** (index + middle + ring): Syncopated pattern
- **4 fingers** (all except thumb): Breakbeat pattern
- **5 fingers** (all): Minimal pattern

### Keyboard
- **Q** or **ESC**: Quit application

## What You'll See

- **Split-screen visualization**:
  - Left side: Arpeggiator with waveform display
  - Right side: Drum machine with step sequencer
- **Live camera feed** (bottom-left corner) with hand tracking
- **Particle effects** triggered by music
- **Real-time visual feedback** for all controls

## Troubleshooting

### Camera not detected
Try changing camera index in `main.py` line 34:
```python
self.camera = cv2.VideoCapture(0)  # Try 1, 2, etc.
```

### Application running slow
Lower the resolution in `main.py`:
```python
self.visualizer = Visualizer(width=640, height=480)
```

### No hands detected
- Ensure good lighting
- Keep hands in frame
- Avoid busy backgrounds

## Tips for Best Experience

1. **Lighting**: Use good lighting for better hand detection
2. **Background**: Plain backgrounds work best
3. **Distance**: Position yourself 1-2 feet from camera
4. **Hand Position**: Keep hands visible and separated
5. **Have Fun**: Experiment with different movements!

---

**Enjoy making music with your hands!** 🎵
