# Hand-Controlled Music Generator (Python)

A hand-controlled arpeggiator, drum machine, and audio reactive visualizer built with Python, MediaPipe, OpenCV, and Pygame. **Raise your hands to raise the roof!**

https://github.com/user-attachments/assets/demo-video

## Features

- **Hand #1 (Left)**: Controls the Arpeggiator
  - Raise hand higher → Higher pitch
  - Pinch fingers (thumb + index) → Control volume

- **Hand #2 (Right)**: Controls the Drum Machine
  - Different finger combinations → Different drum patterns
  - 5 unique drum patterns to choose from

- **Real-time Visualizer**
  - Audio-reactive particle effects
  - Waveform visualization for arpeggiator
  - Step sequencer display for drums
  - Live camera feed with hand tracking overlay

## Requirements

- Python 3.10 or higher
- Webcam
- `uv` package manager (recommended) or `pip`

## Installation

### Using uv (Recommended)

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt
```

### Using pip

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Make sure your virtual environment is activated
python main.py
```

### Controls

- **Left Hand** (Arpeggiator):
  - Move hand up/down to change pitch (higher hand = higher notes)
  - Pinch thumb and index finger together to decrease volume
  - Spread thumb and index finger apart to increase volume

- **Right Hand** (Drums):
  - **1 finger up** (index): Basic 4/4 pattern
  - **2 fingers up** (index + middle): Pattern with claps
  - **3 fingers up** (index + middle + ring): Syncopated pattern
  - **4 fingers up** (all except thumb): Breakbeat pattern
  - **5 fingers up** (all fingers): Minimal pattern

- **Keyboard**:
  - `Q` or `ESC`: Quit application

## Project Structure

```
MusikBeat/
├── main.py                 # Main application entry point
├── hand_tracker.py         # MediaPipe hand tracking module
├── arpeggiator.py          # Arpeggiator synthesizer
├── drum_machine.py         # Drum machine with synthetic sounds
├── visualizer.py           # Audio-reactive visualization
├── requirements.txt        # Python dependencies
└── PYTHON_README.md        # This file
```

## How It Works

### Hand Tracking
Uses **MediaPipe Hands** to detect and track hand landmarks in real-time with advanced smoothing:
- **Model Complexity**: Uses full model (complexity=1) for better accuracy
- **High Confidence Thresholds**: 0.7 for both detection and tracking for stable results
- **Exponential Smoothing**: Reduces jitter while maintaining responsiveness
- Extracts gestures:
  - Hand height (Y-position of wrist)
  - Pinch distance (distance between thumb and index finger)
  - Extended fingers (which fingers are raised)

### Arpeggiator
Generates melodic patterns using synthesized tones:
- Major pentatonic scale across 3 octaves
- ADSR envelope for smooth note transitions
- Multiple harmonics for richer sound
- Real-time volume control via pinch gesture

### Drum Machine
Produces rhythmic patterns using synthetic drum sounds:
- 5 drum sounds: kick, snare, hi-hat, clap, tom
- 5 pre-programmed patterns
- 16-step sequencer (16th notes)
- Tempo: 120 BPM

### Visualizer
Creates real-time visual feedback:
- Split-screen design (left for arp, right for drums)
- Particle effects triggered by note/drum hits
- Waveform display showing arpeggio melody
- Step sequencer grid showing drum pattern
- Live camera feed with hand landmarks

## Troubleshooting

### Camera Not Working
- Ensure your webcam is connected and not being used by another application
- Try changing the camera index in `main.py`:
  ```python
  self.camera = cv2.VideoCapture(0)  # Try 1, 2, etc.
  ```

### No Sound
- Check your system volume
- Ensure pygame mixer is initialized properly
- Try restarting the application

### Low FPS / Lag
- Reduce camera resolution in `main.py`:
  ```python
  self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
  self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
  ```
- Close other applications using the camera
- Adjust target FPS in `main.py`:
  ```python
  self.target_fps = 30  # Lower FPS if needed
  ```

### Hands Not Detected
- Ensure good lighting conditions
- Keep hands visible in camera frame
- Avoid cluttered backgrounds
- Try adjusting detection confidence in `hand_tracker.py`:
  ```python
  min_detection_confidence=0.5  # Lower for easier detection (currently 0.7)
  ```

### Tracking Too Jerky or Too Smooth
- Adjust smoothing factor in `hand_tracker.py`:
  ```python
  self.smoothing_factor = 0.5  # Higher (0.5-0.8) = more responsive, Lower (0.1-0.3) = smoother
  ```

## Customization

### Change BPM (Tempo)
```python
# In main.py, after initialization:
controller.arpeggiator.set_bpm(140)  # Set to 140 BPM
controller.drum_machine.set_bpm(140)
```

### Add Custom Drum Patterns
Edit `drum_machine.py` and add new patterns to the `patterns` dictionary:
```python
'pattern6': {
    'kick': [0, 4, 8, 12],
    'snare': [4, 12],
    'hihat': [2, 6, 10, 14],
}
```

### Change Musical Scale
Edit `arpeggiator.py` and modify the scale:
```python
self.scale = [0, 2, 3, 5, 7, 8, 10, 12]  # Minor pentatonic
```

## Dependencies

- `opencv-python`: Camera capture and image processing
- `mediapipe`: Hand tracking and gesture recognition
- `numpy`: Numerical computations
- `pygame`: Audio generation and playback
- `scipy`: Signal processing
- `matplotlib`: Additional visualization tools
- `pillow`: Image processing

## Credits

Inspired by the web-based version at [Fun With Computer Vision](https://funwithcomputervision.com/)

## License

MIT License

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## Future Enhancements

- [ ] MIDI output support
- [ ] Recording and playback
- [ ] More musical scales
- [ ] Custom drum sound loading
- [ ] Save/load presets
- [ ] Multi-camera support
- [ ] OSC (Open Sound Control) support

---

**Made with ❤️ using Python, MediaPipe, and OpenCV**
