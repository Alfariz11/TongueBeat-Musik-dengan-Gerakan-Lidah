# TongueBeat Quick Start Guide

Play drums using your tongue movements! This guide will help you get started.

## Prerequisites

- Python 3.8 - 3.11 (Python 3.12+ may have compatibility issues with dlib)
- Webcam
- Windows/Linux/macOS

## Installation

### 1. Install Dependencies

If you have a virtual environment activated (`.venv`), install the requirements:

```bash
pip install -r requirements.txt
```

This will install:
- OpenCV for video capture
- MediaPipe for facial landmark detection
- Pygame for audio playback
- NumPy, SciPy, Matplotlib for processing
- And other necessary dependencies

### 2. Verify Audio Files

Make sure you have drum audio files in the `audios/` directory:
- `kick.wav`
- `snare.wav`
- `hihat.wav`
- `crashcymbal.wav`
- `ridecymbal.wav`
- `hightom.wav`
- `midtom.wav`
- `lowtom.wav`

### 3. Verify Image Files

Make sure you have drum pad images in the `images/` directory:
- `kick.png`
- `snare.png`
- `crash.png`
- `tom1.png`, `tom2.png`, `tom3.png`, `tom4.png`

## Running TongueBeat

### Start the Application

**Option 1: Interactive Camera Selection (Recommended)**
```bash
python tonguebeat.py
```
The app will automatically detect all available cameras and let you choose the best one.

**Option 2: Specify Camera Index**
```bash
python tonguebeat.py 0    # Use camera index 0
python tonguebeat.py 1    # Use camera index 1
python tonguebeat.py 2    # Use external camera
```

### Camera Selection Features

When you run the app without specifying a camera:
1. **Auto-detection** - Lists all available cameras with their resolutions
2. **Preview mode** - Press 'P' to preview each camera before selecting
3. **Easy selection** - Just enter the camera number you want to use

💡 **Tip:** If your laptop webcam quality is poor, connect an external webcam and select it during startup!

### How to Play

1. **Position yourself** in front of the webcam
2. **Open your mouth** to activate tongue detection
3. **Move your tongue** in different directions:
   - **UP** → Kick drum
   - **LEFT** → Hi-hat
   - **RIGHT** → Crash cymbal
   - **CENTER/DOWN** → Snare

### Controls

- **M** - Switch between control modes (direction/position)
- **C** - Toggle confidence mode (reduces false triggers)
- **Q** - Quit the application

## Control Modes

### Direction Mode (Default)
Tongue direction triggers specific drums:
- More intuitive for quick playing
- Each direction maps to a drum sound

### Position Mode
Tongue position maps to drum pad locations on screen:
- More precise control
- Point your tongue at the drum pad you want to play

## Detection Modes

### Confidence Mode (Default: ON)
**Multi-frame confidence checking:**
- ✅ Reduces false triggers significantly
- ✅ More stable detection
- ✅ Better for gameplay
- ⚠️ Slight delay (~50-100ms)

**When to turn OFF:**
- For testing/debugging
- When you want instant response
- For very quick tongue flicks

### Smoothing (Always ON)
**EMA (Exponential Moving Average) filtering:**
- Reduces jitter and noise
- Makes tracking more stable
- Smoother visual feedback

## Tips for Best Results

1. **Good lighting** - Make sure your face is well-lit
2. **Stable position** - Keep your head relatively still
3. **Webcam angle** - Position webcam at face level
4. **Exaggerated movements** - Make clear tongue movements
5. **Practice** - It may take a few tries to get the hang of it!

## Troubleshooting

### Camera not detected
- Check if another application is using the camera
- Make sure camera drivers are installed
- Try unplugging and replugging external cameras
- Run the app without arguments to see camera selection menu

### No sound
- Check system volume
- Verify audio files exist in `audios/` directory
- Make sure pygame mixer initialized correctly

### Tongue not detected or only detects DOWN
- Ensure mouth is open wide enough
- Check lighting conditions (face should be well-lit)
- Make **exaggerated** tongue movements
- Try toggling confidence mode OFF (press 'C') for instant response
- If detection only works for DOWN direction:
  - Check the debug info (dx/dy values on screen)
  - Make sure you're moving tongue far enough in each direction
  - The magenta line should point in the direction of your tongue

### Low FPS / Laggy
- Close other applications
- Try reducing video resolution
- Check CPU usage

## Project Structure

```
TongueBeat-Musik-dengan-Gerakan-Lidah/
├── tonguebeat.py           # Main application
├── tongue_detector.py      # MediaPipe tongue detection
├── drum_controller.py      # Drum pad and audio management
├── requirements.txt        # Python dependencies
├── audios/                 # Drum sound files
├── images/                 # Drum pad images
└── result/                 # Output/test files
```

## Development

### Adjusting Detection Sensitivity

Edit `tongue_detector.py`:
- `mouth_open_threshold` - Minimum mouth opening to detect tongue
- `min_detection_confidence` - Face detection confidence
- `min_tracking_confidence` - Landmark tracking confidence

### Adding More Drums

Edit `drum_controller.py`:
1. Add audio file to `audios/` directory
2. Add image to `images/` directory
3. Update `drum_configs` in `setup_drum_pads()`
4. Update `direction_map` for direction mode

### Customizing UI

Edit `tonguebeat.py`:
- `camera_width`, `camera_height` - Video resolution
- `ui_width` - Drum pad panel width
- Color schemes and overlay positions

## Credits

**Team:**
- A Edwin Krisandika Putra (122140003)
- Fathan Andi Kartagama (122140055)
- Rizki Alfariz Ramadhan (122140061)

**Institution:** Institut Teknologi Sumatera (ITERA)

**Technologies:**
- MediaPipe (Google)
- OpenCV
- Pygame

## Have Fun!

Experiment with different tongue movements and create your own rhythms! 🥁
