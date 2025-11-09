# 🥁 TongueBeat — Musik dengan Gerakan Lidah
*“Bermain drum tanpa tangan, hanya dengan gerakan lidah!”*

---

## 🎶 Deskripsi Proyek

Proyek ini mengembangkan sistem multimedia yang memungkinkan pengguna memainkan suara drum hanya dengan gerakan lidah. Kamera akan mendeteksi posisi dan pergerakan lidah, lalu menampilkan respon suara sesuai alat musik yang disentuh secara visual di layar.

---

## 🚀 Quick Start

### Instalasi

1. Clone repository ini
2. Install dependencies: `pip install -r requirements.txt`
3. Download model [shape_predictor_68_face_landmarks.dat](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)
4. Extract dan letakkan file `.dat` di root directory

### Menjalankan

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
- **Gesture pinch (ibu jari + telunjuk)**: Mengatur volume suara, semakin kecil jarak ibu jari dan telunjuk semakin kecil, begitu juga sebaliknya

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
- Jaga jarak yang nyaman dengan webcam
- Pastikan kedua tangan terlihat jelas dalam frame kamera
- Visualizer akan menampilkan efek partikel sesuai instrumen yang dimainkan

---

## 📅 Logbook Mingguan

| Tanggal | Kegiatan | Hasil / Progress |
|---------|-----------|------------------|
<<<<<<< HEAD
| 10/28/2025 | Pembuatan Repositori github Tugas Besar | Repositori github tugas besar |
=======
| 10/28/2025 | Pembuatan Repositori github Tugas Besar | Repositori github tugas besar berhasil dibuat dengan struktur awal proyek |
| 11/2/2025 | Implementasi Komponen Utama & Integrasi Aplikasi | Hand tracker dengan MediaPipe, Arpeggiator (kontrol pitch & volume), Drum Machine (5 pola ritme), Audio Reactive Visualizer, dan integrasi semua komponen di main application. Perbaikan audio system dengan real audio samples, optimisasi code, Custom BPM feature |
<<<<<<< HEAD
| 11/9/2025 | Integrasi Proyek (Visualizer) dari CV2 ke PyGame, Penambahan pattern beat baru dan aset drum terbaru, Perbaikan visualisasi |
>>>>>>> 8905165 (Update README.md)
=======
| 11/9/2025 | Integrasi PyGame pada proyek dan penambahan fitur | Integrasi Proyek (Visualizer) dari CV2 ke PyGame, Penambahan pattern beat baru dan aset drum terbaru, Perbaikan visualisasi |
>>>>>>> f265e1d (Update README.md)

---
