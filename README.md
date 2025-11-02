# MusikBeat - Hand-Controlled Music Generator

Hand-controlled music generator menggunakan computer vision untuk kontrol arpeggiator dan drum machine secara real-time.

## Features

- **Hand Tracking**: Menggunakan MediaPipe untuk deteksi tangan secara real-time
- **Arpeggiator**: Kontrol pitch dengan tinggi tangan dan volume dengan pinch gesture
- **Drum Machine**: 5 drum patterns berbeda dengan kontrol jari
- **Audio Reactive Visualizer**: Visualisasi interaktif dengan particle effects
- **Professional Sound Quality**: Menggunakan audio samples dari assets folder

## Requirements

- Python 3.8+
- Webcam untuk hand tracking
- Dependencies (install via pip):
  ```
  pygame
  opencv-python
  mediapipe
  numpy
  ```

## Installation

1. Clone repository ini:
   ```bash
   git clone <repository-url>
   cd MusikBeat
   ```

2. Install dependencies:
   ```bash
   pip install pygame opencv-python mediapipe numpy
   ```

3. Pastikan folder `assets/` berisi file audio:
   - kick.wav
   - snare.wav
   - hihat.wav
   - clap.wav

## Usage

Jalankan aplikasi:
```bash
python main.py
```

### Controls

**Left Hand (Arpeggiator):**
- Naikkan/turunkan tangan → Ubah pitch
- Pinch (thumb + index finger) → Kontrol volume

**Right Hand (Drums):**
- No fingers → Pattern 1 (Basic 4/4)
- Index finger → Pattern 1 (Basic 4/4)
- Index + Middle → Pattern 2 (With clap)
- Index + Middle + Ring → Pattern 3 (Syncopated)
- All except thumb → Pattern 4 (Break beat)
- All fingers → Pattern 5 (Minimal)

**Keyboard:**
- Press `Q` or `ESC` to quit

## Project Structure

```
MusikBeat/
├── main.py              # Main application
├── hand_tracker.py      # MediaPipe hand tracking
├── arpeggiator.py       # Arpeggiator controller
├── drum_machine.py      # Drum machine controller
├── visualizer.py        # Audio reactive visualizer
├── test_drums.py        # Test script untuk drum sounds
├── assets/              # Audio files
│   ├── kick.wav
│   ├── snare.wav
│   ├── hihat.wav
│   └── clap.wav
└── README.md
```

## Features Detail

### Hand Tracking
- Menggunakan MediaPipe Hands dengan model complexity 1
- Deteksi maksimal 2 tangan
- Smoothing untuk gerakan yang lebih halus
- Confidence threshold: 0.7

### Arpeggiator
- Major pentatonic scale
- 3 octave range
- ADSR envelope synthesis
- Real-time pitch dan volume control
- BPM: 120 (16th notes)

### Drum Machine
- 4 drum sounds: kick, snare, hihat, clap
- 5 pre-programmed patterns
- Individual volume control untuk setiap drum
- Step sequencer: 16 steps
- Real-time pattern switching

### Visualizer
- Audio reactive particle system
- Step sequencer visualization
- Hand position indicators
- Volume meters
- FPS counter
- Split screen untuk left/right hand

## Technical Details

- **Video Resolution**: 1280x720
- **Target FPS**: 60
- **Audio Sample Rate**: 44100 Hz
- **Audio Buffer**: 1024 samples
- **Pygame Mixer**: Stereo, 16-bit

## Troubleshooting

### Camera tidak terdeteksi
- Pastikan webcam terhubung dengan benar
- Check camera permissions di sistem operasi
- Coba ubah camera index di `main.py`: `cv2.VideoCapture(1)` or `cv2.VideoCapture(2)`

### Audio tidak terdengar
- Check volume sistem
- Pastikan file audio ada di folder `assets/`
- Jalankan `test_drums.py` untuk test audio loading

### Performa rendah
- Turunkan resolusi camera di `main.py`
- Gunakan model_complexity=0 di `hand_tracker.py`
- Close aplikasi lain yang menggunakan camera/CPU

## License

MIT License

## Credits

- **MediaPipe** - Hand tracking
- **Pygame** - Audio playback
- **OpenCV** - Computer vision
- **NumPy** - Numerical operations

## Contact

Untuk pertanyaan dan feedback, silakan buat issue di repository ini.
