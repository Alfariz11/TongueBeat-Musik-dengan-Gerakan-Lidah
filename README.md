# 🥁 "Gestune: Musik dari gerakan tangan"

---

## 🎶 Deskripsi Proyek

Proyek ini mengembangkan sistem multimedia yang memungkinkan pengguna menghasilkan musik hanya dengan gerakan tangan secara real-time. Sistem ini memanfaatkan MediaPipe Hand Tracking untuk mendeteksi posisi dan gerakan tangan, yang kemudian digunakan untuk mengontrol dua elemen utama: Arpeggiator dan Drum Machine. Pada Arpeggiator, tinggi posisi tangan mengatur pitch nada, sementara gerakan pinch gesture mengatur volume suara. Sedangkan Drum Machine menyediakan lima pola ritme drum berbeda yang dapat diaktifkan melalui kombinasi gerakan jari. Selain itu, sistem dilengkapi dengan Audio Reactive Visualizer yang menampilkan efek partikel sesuai intensitas dan ritme musik.

---

## 👨‍💻 Anggota Tim

| Nama Lengkap | NIM | ID GitHub |
|---------------|-----|-----------|
| A Edwin Krisandika Putra | 122140003 |[@aloisiusedwin]( https://github.com/aloisiusedwin) |
| Fathan Andi Kartagama | 122140055 |[@pataanggs]( https://github.com/pataanggs) |
| Rizki Alfariz Ramadhan | 122140061 | [@Alfariz11](https://github.com/Alfariz11) |

---

## 🚀 Instalasi

### Prasyarat
- Python 3.8 atau lebih tinggi
- Webcam (untuk hand tracking)
- Sistem Operasi: Windows, macOS, atau Linux

### Langkah Instalasi

1. **Clone repository**
   ```bash
   git clone https://github.com/username/TongueBeat-Musik-dengan-Gerakan-Lidah.git
   cd TongueBeat-Musik-dengan-Gerakan-Lidah
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

---

## 📖 Penggunaan

### Menjalankan Aplikasi

1. **Jalankan aplikasi utama**
   ```bash
   python main.py
   ```

2. **Pastikan webcam Anda aktif dan terhubung**

3. **Posisikan tangan Anda di depan webcam:**
   - **Tangan Kiri**: Kontrol Arpeggiator
   - **Tangan Kanan**: Kontrol Drum Machine

### Kontrol Aplikasi

#### Tangan Kiri (Arpeggiator)
- **Naikkan/turunkan tangan**: Mengatur pitch nada (semakin tinggi tangan, semakin tinggi pitch)
- **Gesture pinch (ibu jari + telunjuk)**: Mengatur volume suara, semakin kecil jarak ibu jari dan telunjuk semakin kecil, begitu juga sebaliknya

#### Tangan Kanan (Drum Machine)
- **Tidak ada jari terangkat**: Pattern 1 (Basic 4/4)
- **Telunjuk**: Pattern 1 (Basic 4/4)
- **Telunjuk + Tengah**: Pattern 2 (With clap)
- **Telunjuk + Tengah + Manis**: Pattern 3 (Syncopated)
- **Semua kecuali ibu jari**: Pattern 4 (Break beat)
- **Semua jari**: Pattern 5 (Minimal)

#### Keyboard Controls
- **Q atau ESC**: Keluar dari aplikasi

### Tips Penggunaan
- Pastikan pencahayaan yang cukup agar hand tracking berfungsi optimal
- Jaga jarak yang nyaman dengan webcam
- Pastikan kedua tangan terlihat jelas dalam frame kamera
- Visualizer akan menampilkan efek partikel sesuai intensitas dan ritme musik

### Testing Audio
Untuk memverifikasi audio berfungsi dengan baik, jalankan:
```bash
python test_drums.py
```

---

## 📅 Logbook Mingguan

| Tanggal | Kegiatan | Hasil / Progress |
|---------|-----------|------------------|
| 10/28/2025 | Pembuatan Repositori github Tugas Besar | Repositori github tugas besar berhasil dibuat dengan struktur awal proyek |
| 11/2/2025 | Implementasi Komponen Utama & Integrasi Aplikasi | Hand tracker dengan MediaPipe, Arpeggiator (kontrol pitch & volume), Drum Machine (5 pola ritme), Audio Reactive Visualizer, dan integrasi semua komponen di main application. Perbaikan audio system dengan real audio samples, optimisasi code, Custom BPM feature |
| 11/9/2025 | Integrasi PyGame pada proyek dan penambahan fitur | Integrasi Proyek (Visualizer) dari CV2 ke PyGame, Penambahan pattern beat baru dan aset drum terbaru, Perbaikan visualisasi |

---
