# 🎵 Gestune: Musik dari Gerakan Tangan

---

## 🎶 Deskripsi Proyek

**Gestune** adalah aplikasi musik interaktif yang memungkinkan pengguna menciptakan musik secara real-time menggunakan gerakan tangan. Memanfaatkan teknologi **MediaPipe Hand Tracking** dan **PyQt6**, aplikasi ini mendeteksi posisi dan gerakan tangan untuk mengontrol dua instrumen musik virtual:

### 🎹 Arpeggiator (Tangan Kiri)

- **Pitch Control**: Tinggi posisi tangan mengatur nada (3 oktaf penuh)
- **Volume Control**: Pinch gesture (jarak ibu jari & telunjuk) mengatur volume
- **BPM Control**: Pinch gesture + gerakan vertikal untuk mengatur tempo (40-200 BPM)
- Sintesis audio real-time dengan waveform kaya harmonik

### 🥁 Drum Machine (Tangan Kanan)

- **Finger Mapping**: Setiap jari mengontrol satu instrumen drum spesifik
- **5 Instrumen Drum**: Kick, Snare, Hi-hat, Clap (mapped to Ring & Pinky)
- **Real-time Triggering**: Mengangkat jari mengaktifkan instrumen dalam loop sequencer
- **16-Step Sequencer**: Engine audio terpadu untuk timing yang presisi

### 🎨 Fitur Visual

- UI modern dengan dark theme menggunakan PyQt6
- Live camera feed dengan hand tracking overlay
- Visualisasi drum hits real-time dengan animasi
- Performance metrics (FPS, hand detection status)

---

## 👨‍💻 Anggota Tim

| Nama Lengkap             | NIM       | ID GitHub                                          |
| ------------------------ | --------- | -------------------------------------------------- |
| A Edwin Krisandika Putra | 122140003 | [@aloisiusedwin](https://github.com/aloisiusedwin) |
| Fathan Andi Kartagama    | 122140055 | [@pataanggs](https://github.com/pataanggs)         |
| Rizki Alfariz Ramadhan   | 122140061 | [@Alfariz11](https://github.com/Alfariz11)         |

---

## 🚀 Instalasi

### Prasyarat

- **Python 3.8** atau lebih tinggi
- **Webcam** (untuk hand tracking)
- **Sistem Operasi**: Windows, macOS, atau Linux
- **RAM**: Minimal 4GB (disarankan 8GB)
- **Processor**: Dual-core atau lebih tinggi

### Langkah Instalasi

1. **Clone repository**

   ```bash
   git clone https://github.com/Alfariz11/Gestune-Musik-dari-gerakan-tangan.git
   cd Gestune-Musik-dari-gerakan-tangan
   ```

2. **Buat virtual environment (disarankan)**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Verifikasi instalasi** (opsional)
   ```bash
   python test_audio_engine.py
   ```

---

## 📖 Penggunaan

### Menjalankan Aplikasi

1. **Aktifkan virtual environment** (jika menggunakan venv)

   ```bash
   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

2. **Jalankan aplikasi utama**

   ```bash
   python main.py
   ```

3. **Interface akan muncul** dengan:

   - Live camera feed di sisi kiri
   - Kontrol panel di sisi kanan
   - Status indicator untuk deteksi tangan
   - BPM control dan pattern selector

4. **Mulai bermain musik**:
   - Posisikan tangan kiri di zona biru untuk kontrol melodi
   - Posisikan tangan kanan di zona pink untuk kontrol drum
   - Eksperimen dengan berbagai gesture dan pattern!

### 🎮 Kontrol Aplikasi

#### 👈 Tangan Kiri - Arpeggiator Zone (Area Biru)

- **🎹 Pitch Control**: Gerakkan tangan naik/turun untuk mengubah nada
  - Semakin tinggi tangan = nada semakin tinggi
  - Range: 3 oktaf penuh (C2 - C5)
- **🎚️ Volume Control**: Pinch gesture (pertemukan ibu jari & telunjuk)
  - Semakin rapat jari = volume semakin kecil
  - Semakin renggang = volume semakin besar
- **⏱️ BPM Control**: Pinch rapat + gerakkan tangan naik/turun
  - Unlock BPM dengan pinch yang sangat rapat
  - Gerakkan tangan untuk mengatur tempo (40-200 BPM)

#### 👉 Tangan Kanan - Drum Machine Zone (Area Pink)

**Kontrol Instrumen** (Angkat jari untuk mengaktifkan):

- **👍 Jempol** → Kick Drum
- **☝️ Telunjuk** → Snare Drum
- **🖕 Jari Tengah** → Hi-Hat
- **💍 Jari Manis** → Clap
- **🤙 Kelingking** → Clap (Alternatif)

**Catatan**:

- Drum akan bermain dalam loop sequencer selama jari diangkat.
- Turunkan jari untuk mematikan instrumen tersebut.

#### ⌨️ Kontrol Keyboard

- **Q** atau **ESC**: Keluar dari aplikasi
- **Slider BPM**: Geser untuk mengatur tempo manual
- **Pattern Buttons**: Klik untuk ganti pattern drum langsung

### 💡 Tips Penggunaan

- ✅ Pastikan pencahayaan ruangan cukup terang untuk tracking optimal
- ✅ Posisikan diri pada jarak 50-100 cm dari webcam
- ✅ Jaga agar kedua tangan berada dalam frame kamera
- ✅ Tangan kiri di zona biru (sisi kiri), tangan kanan di zona pink (sisi kanan)
- ✅ Gerakkan tangan dengan smooth untuk hasil audio yang halus
- ✅ Eksperimen dengan berbagai pattern drum untuk menemukan ritme favorit

### 🧪 Testing Audio

Untuk memverifikasi sistem audio berfungsi dengan baik:

```bash
python test_audio_engine.py
```

Program ini akan memutar arpeggio dan drum pattern sederhana untuk memastikan engine audio berjalan lancar.

---

## 📅 Logbook Mingguan

| Tanggal    | Kegiatan                                         | Hasil / Progress                                                                                                                                                                                                                                 |
| ---------- | ------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 10/28/2025 | Pembuatan Repositori GitHub Tugas Besar          | Repositori GitHub tugas besar berhasil dibuat dengan struktur awal proyek                                                                                                                                                                        |
| 11/02/2025 | Implementasi Komponen Utama & Integrasi Aplikasi | Hand tracker dengan MediaPipe, Arpeggiator (kontrol pitch & volume), Drum Machine (7 pola ritme), Audio Reactive Visualizer, dan integrasi semua komponen. Perbaikan audio system dengan real audio samples, optimisasi code, Custom BPM feature |
| 11/09/2025 | Integrasi PyGame dan Penambahan Fitur            | Integrasi Visualizer dari CV2 ke PyGame, Penambahan pattern beat baru dan aset drum terbaru, Perbaikan visualisasi dengan efek partikel                                                                                                          |
| 11/14/2025 | UI Baru dengan PyQt6 & Bug Fixes                 | Implementasi UI modern menggunakan PyQt6, fixing bugs pada sistem tracking, penambahan kontrol interaktif                                                                                                                                        |
| 11/28/2025 | Update Asset dan Pattern Drum                    | Perubahan asset drum dengan kualitas lebih baik, penambahan 2 pattern baru (total 7 pattern), optimisasi audio mixing                                                                                                                            |
| 11/30/2025 | Remake Pinch BPM Controller                      | Implementasi kontrol BPM via gesture pinch pada tangan kanan, sinkronisasi perubahan BPM dengan UI slider, smoothing untuk transisi BPM yang halus                                                                                               |
| 12/01/2025 | Update Dokumentasi Laporan Final Proyek Fix Bug  | Update dokumentasi laporan final, perbaikan README, penambahan penjelasan fitur-fitur baru, banner. Perbaikan beberapa bug seperti BPM slider dan arpegiattor yang overlap. Tambah skrip untuk pattern drum. Perubahan minor pada UI             |
| 12/02/2025 | Refactoring Audio Engine & Integrasi Sistem      | Mengganti Arpeggiator dan Drum Machine terpisah dengan AudioEngine terpadu. Implementasi scheduler loop untuk timing yang lebih presisi. Mengubah kontrol drum menjadi finger mapping. Integrasi sukses ke main application.                     |

---
