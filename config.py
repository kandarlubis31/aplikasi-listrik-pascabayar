"""Konfigurasi aplikasi yang dibaca dari `.env`.

Nilai sensitif (kredensial database, secret key, akun debug) tidak lagi
ditulis di kode. Salin `.env.example` menjadi `.env`, file `.env` sudah
di-ignore oleh git sehingga tidak ikut ter-commit.
"""

import os
import secrets
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _muat_env():
    """Baca `.env` sederhana tanpa dependensi tambahan."""
    env_path = BASE_DIR / ".env"
    if not env_path.exists():
        return
    for baris in env_path.read_text(encoding="utf-8").splitlines():
        baris = baris.strip()
        if not baris or baris.startswith("#") or "=" not in baris:
            continue
        kunci, nilai = baris.split("=", 1)
        os.environ.setdefault(kunci.strip(), nilai.strip().strip("'\""))


_muat_env()

SECRET_KEY = os.getenv("SECRET_KEY") or secrets.token_hex(24)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "bayarlistrik_db"),
}

# Endpoint /debug_login_* hanya aktif kalau FLASK_DEBUG menyala DAN
# DEBUG_LOGIN_ENABLED=true, sehingga tidak pernah hidup di produksi.
DEBUG_LOGIN_ENABLED = os.getenv("DEBUG_LOGIN_ENABLED", "false").lower() == "true"
DEBUG_ADMIN_USER = os.getenv("DEBUG_ADMIN_USER", "")
DEBUG_ADMIN_PASSWORD = os.getenv("DEBUG_ADMIN_PASSWORD", "")
