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
# Real-time detection (requires webcam)
python detect-tongue-real-time-v4.py

# Image analysis
python facial_landmarks.py -i path/to/image.jpg
```

**Lihat [SETUP.md](SETUP.md) untuk panduan instalasi lengkap dan troubleshooting.**

---

## 👨‍💻 Anggota Tim

| Nama Lengkap | NIM | ID GitHub |
|---------------|-----|-----------|
| A Edwin Krisandika Putra | 122140003 |[@aloisiusedwin]( https://github.com/aloisiusedwin) |
| Fathan Andi Kartagama | 122140055 |[@pataanggs]( https://github.com/pataanggs) |
| Rizki Alfariz Ramadhan | 122140061 | [@Alfariz11](https://github.com/Alfariz11) |

---

## 📖 Cara Penggunaan

### Menjalankan Aplikasi

1. **Pastikan folder `audios` berisi 5 file audio yang diperlukan:**
   - `kick.wav`
   - `snare.wav`
   - `hihat.wav`
   - `hightom.wav`
   - `crashcymbal.wav`

2. **Jalankan aplikasi utama:**
   ```bash
   python main.py
   ```

3. **Posisikan tangan Anda di depan webcam:**
   - **Tangan Kiri**: Kontrol Arpeggiator
   - **Tangan Kanan**: Kontrol Drum Machine

### Kontrol Aplikasi

#### Tangan Kiri (Arpeggiator)
- **Naikkan/turunkan tangan**: Mengatur pitch nada (semakin tinggi tangan, semakin tinggi pitch)
- **Gesture pinch (ibu jari + telunjuk)**: Mengatur volume suara

#### Tangan Kanan (Drum Machine - Pattern Loop dengan Velocity)
- **Thumb (Ibu jari)**: Kick pattern - Groovy pattern dengan syncopation
- **Index (Telunjuk)**: Snare pattern - Backbeat klasik dengan ghost notes
- **Middle (Tengah)**: Hihat pattern - Pattern kompleks dengan aksen dan variasi
- **Ring (Manis)**: High Tom pattern - Pattern fill yang musikal
- **Pinky (Kelingking)**: Crash pattern - Aksen strategis pada momen penting

**Cara menggunakan**: Angkat jari Anda untuk mengaktifkan pattern loop instrumen. Setiap pattern memiliki:
- **Velocity variations**: Ghost notes (lembut) dan accents (keras)
- **Swing feel**: Groove yang lebih natural
- **Mix balancing**: Volume yang dioptimalkan untuk kombinasi yang bagus

Anda dapat mengaktifkan beberapa jari sekaligus untuk combo pattern yang kompleks. Semua pattern tersinkronisasi dalam loop 16 step.

#### Keyboard Controls
- **Q atau ESC**: Keluar dari aplikasi

### Tips Penggunaan
- Pastikan pencahayaan yang cukup agar hand tracking berfungsi optimal
- Jaga jarak yang nyaman dengan webcam (sekitar 50-100 cm)
- Pastikan kedua tangan terlihat jelas dalam frame kamera
- Visualizer akan menampilkan efek partikel sesuai instrumen yang dimainkan

---

## 📅 Logbook Mingguan

| Tanggal | Kegiatan | Hasil / Progress |
|---------|-----------|------------------|
| 10/28/2025 | Pembuatan Repositori github Tugas Besar | Repositori github tugas besar |

---
