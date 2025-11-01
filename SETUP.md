# TongueBeat Setup Guide

This guide will help you set up and run the TongueBeat project - a system that detects tongue movements to play drum sounds.

## Prerequisites

- Python 3.8 - 3.11 (Python 3.12+ may have compatibility issues with dlib)
- Webcam (for real-time detection scripts)
- Windows/Linux/macOS

## Installation Steps

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd TongueBeat-Musik-dengan-Gerakan-Lidah
```

### 2. Create a Virtual Environment (Recommended)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

**Important for Windows users:**
- If you're on Windows and have issues installing dlib, you may need to install Visual Studio Build Tools first
- Download from: https://visualstudio.microsoft.com/downloads/ (Build Tools for Visual Studio)
- Or install dlib from a pre-built wheel: https://github.com/sachadee/Dlib

**Install all packages:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Download Required Model

Download the facial landmark predictor model:

**Option 1 - Direct Download:**
1. Download `shape_predictor_68_face_landmarks.dat.bz2` from:
   http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
2. Extract the .bz2 file to get `shape_predictor_68_face_landmarks.dat`
3. Place it in the project root directory

**Option 2 - Using wget (Linux/macOS):**
```bash
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
```

**Option 3 - Using PowerShell (Windows):**
```powershell
Invoke-WebRequest -Uri "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2" -OutFile "shape_predictor_68_face_landmarks.dat.bz2"
# Then extract using 7-Zip or WinRAR
```

## Available Scripts

### Real-Time Detection Scripts (Require Webcam)

1. **detect-tongue-real-time-v4.py** - Latest version with rotated mouth detection
   ```bash
   python detect-tongue-real-time-v4.py
   ```

2. **detect-tongue-real-time-v2.py** - Simplified real-time detection
   ```bash
   python detect-tongue-real-time-v2.py
   ```

3. **detect-tongue-tip-real-time.py** - Focuses on tongue tip detection
   ```bash
   python detect-tongue-tip-real-time.py
   ```

4. **detedt-tongue-real-time-v1.py** - Initial real-time version
   ```bash
   python detedt-tongue-real-time-v1.py
   ```

### Video Processing Scripts (Require Test Video)

These scripts process a video file located at `test/test_vid.mp4`:

1. **detect-tongue-with-blob-tracking-revised.py** - Revised blob tracking
   ```bash
   python detect-tongue-with-blob-tracking-revised.py
   ```

2. **detect-tongue-with-blob-tracking.py** - Original blob tracking
   ```bash
   python detect-tongue-with-blob-tracking.py
   ```

3. **detect-tongue.py** - Basic tongue detection with optical flow
   ```bash
   python detect-tongue.py
   ```

### Image Analysis Scripts

1. **facial_landmarks.py** - Detect facial landmarks in an image
   ```bash
   python facial_landmarks.py -i path/to/your/image.jpg
   ```

2. **detect_face_parts.py** - Analyze different face parts
   ```bash
   python detect_face_parts.py -i path/to/your/image.jpg -p shape_predictor_68_face_landmarks.dat
   ```

## Usage Tips

### Running Real-Time Detection

1. Make sure your webcam is connected and working
2. Run one of the real-time detection scripts
3. Position your face in front of the camera
4. Open your mouth to trigger tongue detection
5. Press 'q' to quit the application

### Processing Videos

1. Place your test video in the `test/` directory as `test_vid.mp4`
2. Run one of the video processing scripts
3. Output frames will be saved in the `frames/` directory
4. Press 'q' to quit early

### Processing Images

1. Place your test images in any directory
2. Run the image analysis scripts with the `-i` flag pointing to your image
3. Results will be saved in the `result/` directory

## Troubleshooting

### Common Issues

**Issue: "No module named 'dlib'"**
- Solution: dlib installation can be tricky. Try:
  ```bash
  pip install cmake
  pip install dlib
  ```
- On Windows, consider using pre-built wheels from https://github.com/sachadee/Dlib

**Issue: "shape_predictor_68_face_landmarks.dat not found"**
- Solution: Download the model file as described in step 4 of installation

**Issue: "No Face Found!" message**
- Solution: Ensure good lighting and position your face clearly in front of the camera
- Try adjusting the camera angle

**Issue: Camera not working**
- Solution: Check if another application is using the camera
- Try changing the camera index in the script (0 to 1 or 2)

**Issue: Slow performance**
- Solution: The face detection is computationally intensive
- Try reducing the frame resolution in the scripts
- Consider using a more powerful computer

## Project Structure

```
TongueBeat-Musik-dengan-Gerakan-Lidah/
├── face_utils.py                          # Utility functions for face detection
├── detect-tongue-real-time-v4.py          # Main real-time detection script
├── facial_landmarks.py                    # Facial landmark detection
├── requirements.txt                       # Python dependencies
├── shape_predictor_68_face_landmarks.dat  # dlib model (download required)
├── frames/                                # Output frames directory
├── result/                                # Output results directory
├── test/                                  # Test videos directory
└── SETUP.md                               # This file
```

## How It Works

1. **Face Detection**: Uses dlib's HOG-based face detector to locate faces in frames
2. **Landmark Detection**: Identifies 68 facial landmarks including mouth points
3. **Mouth Analysis**: Calculates mouth aspect ratio to detect if mouth is open
4. **Tongue Detection**: Uses ORB feature detection to identify tongue position
5. **Tracking**: Monitors tongue movement to trigger drum sounds (future feature)

## Next Steps

- Integrate audio playback for drum sounds using pygame
- Add drum kit interface overlay
- Implement gesture mapping to different drum sounds
- Optimize performance for smoother real-time detection

## Contributing

This is a student project from Institut Teknologi Sumatera. Feel free to contribute improvements!

## License

This project is for educational purposes.

## Credits

- Team Members: A Edwin Krisandika Putra, Fathan Andi Kartagama, Rizki Alfariz Ramadhan
- Institution: Institut Teknologi Sumatera
- Libraries: OpenCV, dlib, imutils
