
# ⚡ Aplikasi Pembayaran Listrik Pascabayar

Aplikasi ini memudahkan pelanggan pascabayar dalam mencatat penggunaan dan membayar tagihan listrik bulanan. Dibuat dengan Flask dan MySQL, sistem ini mendukung login multi-level, manajemen pelanggan, pencatatan otomatis, dashboard interaktif, dan proses pembayaran online.

## ✨ Fitur Utama (Ringkasan)
- Login aman (admin & pelanggan)
- CRUD data pelanggan & penggunaan
- Tagihan otomatis dengan trigger & function
- Dashboard dengan grafik penggunaan/tagihan
- Proses pembayaran tagihan
- Validasi data & UI responsif
- Format Rupiah untuk semua nilai uang

## 🚀 Teknologi
- **Backend**: Flask, MySQL, Flask-Login, hashlib, decimal
- **Frontend**: HTML, CSS, JS, Chart.js, Font Awesome
- **Database**: MySQL/MariaDB + Trigger, View, Function

## 📁 Struktur Proyek (Ringkas)
- `app.py` - Routing utama
- `models.py` - Query & logika CRUD
- `templates/` - HTML halaman login, dashboard, form, pembayaran
- `static/` - style.css & script.js
- `bayarlistrik_db.sql` - Struktur dan data awal database

## ⚙️ Instalasi Cepat
1. **Database**: Buat DB `bayarlistrik_db`, impor SQL, ubah kolom `id_pelanggan` jadi BIGINT, tambahkan kolom `total_tagihan`, perbarui trigger & function hitung tagihan.
2. **Python**: Clone repo, buat virtualenv, install dependensi (`Flask`, `mysql-connector-python`, dll).
3. **Konfigurasi**: salin `.env.example` menjadi `.env`, lalu isi `SECRET_KEY` dan kredensial MySQL di sana. File `.env` sudah di-ignore git, jadi kredensial tidak ikut ter-commit.
4. **Deploy (PythonAnywhere)**: Atur path project, WSGI file, environment variable, dan reload aplikasi.

Database? Kirim Email ke: kandarlubis31@gmail.com
