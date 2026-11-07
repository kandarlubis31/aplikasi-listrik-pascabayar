
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
- `auth_service.py` - Login & hashing password
- `database_connector.py` - Koneksi MySQL
- `config.py` - Pembacaan konfigurasi dari `.env`
- `.env.example` - Template konfigurasi (salin jadi `.env`)
- `templates/` - HTML halaman login, dashboard, form, pembayaran
- `static/` - style.css & script.js

## ⚙️ Instalasi Cepat
1. **Database**: Buat DB `bayarlistrik_db` di MySQL/MariaDB. Skema (tabel, trigger, view, function hitung tagihan) **tidak disertakan di repo ini**, jadi siapkan manual atau impor dump yang kamu simpan sendiri. Pastikan kolom `id_pelanggan` bertipe BIGINT dan kolom `total_tagihan` ada.
2. **Python**: Clone repo, buat virtualenv, lalu `pip install -r requirements.txt`.
3. **Konfigurasi**: salin `.env.example` menjadi `.env`, lalu isi `SECRET_KEY` dan kredensial MySQL di sana. File `.env` sudah di-ignore git, jadi kredensial tidak ikut ter-commit.
4. **Jalankan**: `python app.py` (default di `http://localhost:5000`).
5. **Deploy (PythonAnywhere)**: Atur path project, WSGI file, environment variable, dan reload aplikasi.

Database? Kirim Email ke: kandarlubis31@gmail.com
