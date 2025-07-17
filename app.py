import os
import decimal
from datetime import datetime
import mysql.connector

from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_moment import Moment
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

import database_connector
import auth_service
import models

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
app.secret_key = os.urandom(24) 
moment = Moment(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "Harap login untuk mengakses halaman ini."
login_manager.login_message_category = "warning"

class User(UserMixin):
    def __init__(self, id_user, username, id_level, nama_tampilan, id_pelanggan_db=None):
        self.id = id_user
        self.username = username
        self.id_level = id_level
        self.nama_tampilan = nama_tampilan
        self.id_pelanggan_db = id_pelanggan_db

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    db_conn = database_connector.get_db_connection()
    if not db_conn:
        app.logger.error("Gagal koneksi database di load_user.")
        return None

    try:
        cursor = db_conn.cursor(dictionary=True)
        query_user = "SELECT id_user, username, password, nama_admin, id_level FROM user WHERE id_user = %s"
        cursor.execute(query_user, (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            return User(user_data['id_user'], user_data['username'], user_data['id_level'], user_data['nama_admin'])
        
        query_pelanggan = "SELECT id_pelanggan, username, password, nama_pelanggan, id_tarif FROM pelanggan WHERE id_pelanggan = %s"
        cursor.execute(query_pelanggan, (user_id,))
        pelanggan_data = cursor.fetchone()

        if pelanggan_data:
            return User(pelanggan_data['id_pelanggan'], pelanggan_data['username'], 3, pelanggan_data['nama_pelanggan'], pelanggan_data['id_pelanggan'])
        
        return None
    except mysql.connector.Error as err:
        app.logger.error(f"Error memuat user di load_user: {err}")
        return None
    finally:
        if db_conn: db_conn.close()
        if 'cursor' in locals() and cursor: cursor.close()

def format_rupiah_filter(value):
    if value is None:
        return "Rp 0,00"
    
    if not isinstance(value, decimal.Decimal):
        try:
            value = decimal.Decimal(str(value))
        except (decimal.InvalidOperation, TypeError):
            return str(value) 

    formatted_value = "{:,.2f}".format(value.quantize(decimal.Decimal('0.01'), rounding=decimal.ROUND_HALF_UP))
    formatted_value = formatted_value.replace('.', '_TEMP_').replace(',', '.').replace('_TEMP_', ',')
    
    return f"Rp {formatted_value}"

app.jinja_env.filters['rupiah'] = format_rupiah_filter

def check_admin_access():
    if not current_user.is_authenticated or current_user.id_level not in [1, 2]:
        flash("Anda tidak memiliki akses ke halaman ini.", "warning")
        return False
    return True

def check_pelanggan_access():
    if not current_user.is_authenticated or current_user.id_level != 3:
        flash("Anda tidak memiliki akses ke halaman ini.", "warning")
        return False
    return True

def get_db_and_handle_error():
    db_conn = database_connector.get_db_connection()
    if not db_conn:
        flash("Koneksi database gagal.", "danger")
        app.logger.error("Koneksi database gagal di get_db_and_handle_error.")
    return db_conn

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.id_level in [1, 2]:
            return redirect(url_for('admin_dashboard'))
        elif current_user.id_level == 3:
            return redirect(url_for('pelanggan_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        remember_me = request.form.get('remember_me')

        if not username or not password_input:
            flash("Username dan password harus diisi.", "danger")
            return render_template('login.html', username_input=username)

        db_conn = get_db_and_handle_error()
        if not db_conn:
            return render_template('login.html', username_input=username)

        user_data = auth_service.login_user(db_conn, username, password_input)
        db_conn.close()

        if user_data:
            if user_data['id_level'] in [1, 2]:
                user_obj = User(user_data['id_user'], user_data['username'], user_data['id_level'], user_data['nama_admin'])
            else:
                user_obj = User(user_data['id_pelanggan'], user_data['username'], user_data['id_level'], user_data['nama_pelanggan'], user_data['id_pelanggan'])

            login_user(user_obj, remember=bool(remember_me))

            flash(f"Selamat Datang, {user_obj.nama_tampilan}!", "success")
            if user_obj.id_level in [1, 2]:
                return redirect(url_for('admin_dashboard'))
            elif user_obj.id_level == 3:
                return redirect(url_for('pelanggan_dashboard'))
        else:
            flash("Username atau password salah.", "danger")
    return render_template('login.html')

# --- Start: Debug Login Routes (HANYA UNTUK PENGEMBANGAN!) ---
@app.route('/debug_login_admin')
def debug_login_admin():
    if app.debug:
        db_conn = get_db_and_handle_error()
        if not db_conn:
            flash("Gagal koneksi database untuk debug login.", "danger")
            return redirect(url_for('login'))
        
        username_dev = "admin" # GANTI DENGAN USERNAME ADMIN YANG ADA DI DB KAMU
        password_dev = "admin" # GANTI DENGAN PASSWORD ADMIN YANG ADA DI DB KAMU (Plaintext, ini hanya untuk login sementara!)

        user_data = auth_service.login_user(db_conn, username_dev, password_dev)
        db_conn.close()

        if user_data:
            user_obj = User(user_data['id_user'], user_data['username'], user_data['id_level'], user_data['nama_admin'])
            login_user(user_obj)
            flash(f"Otomatis login sebagai {user_obj.nama_tampilan} (DEBUG MODE).", "info")
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Gagal otomatis login admin dev. Cek username/password di database.", "danger")
            return redirect(url_for('login'))
    else:
        flash("Akses ditolak. Fitur ini hanya untuk mode debug.", "warning")
        return redirect(url_for('login'))

@app.route('/debug_login_pelanggan/<int:pelanggan_id>')
def debug_login_pelanggan(pelanggan_id):
    if app.debug:
        db_conn = get_db_and_handle_error()
        if not db_conn:
            flash("Gagal koneksi database untuk debug login.", "danger")
            return redirect(url_for('login'))
        
        pelanggan_data = models.get_pelanggan_by_id(db_conn, pelanggan_id)
        db_conn.close()

        if pelanggan_data:
            user_obj = User(pelanggan_data['id_pelanggan'], pelanggan_data['username'], 3, pelanggan_data['nama_pelanggan'], pelanggan_data['id_pelanggan'])
            login_user(user_obj)
            flash(f"Otomatis login sebagai pelanggan {user_obj.nama_tampilan} (DEBUG MODE).", "info")
            return redirect(url_for('pelanggan_dashboard'))
        else:
            flash(f"Pelanggan ID {pelanggan_id} tidak ditemukan untuk debug login.", "danger")
            return redirect(url_for('login'))
    else:
        flash("Akses ditolak. Fitur ini hanya untuk mode debug.", "warning")
        return redirect(url_for('login'))
# --- End: Debug Login Routes ---

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Anda telah logout.", "info")
    return redirect(url_for('login'))

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not check_admin_access():
        return redirect(url_for('login'))
    
    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('login'))

    pelanggans = models.get_all_pelanggan(db_conn)
    users = models.get_all_users(db_conn)
    tarifs = models.get_all_tarif(db_conn)
    db_conn.close()

    return render_template('admin_dashboard.html',
                            username=current_user.username,
                            nama_admin=current_user.nama_tampilan,
                            pelanggans=pelanggans,
                            users=users,
                            tarifs=tarifs)

@app.route('/admin/pelanggan/add', methods=['GET', 'POST'])
@login_required
def admin_add_pelanggan():
    if not check_admin_access():
        return redirect(url_for('login'))

    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('admin_dashboard'))

    tarifs = models.get_all_tarif(db_conn)
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        nomor_kwh = request.form.get('nomor_kwh')
        nama_pelanggan = request.form.get('nama_pelanggan')
        alamat = request.form.get('alamat')
        id_tarif_str = request.form.get('id_tarif')

        if not all([username, password, nomor_kwh, nama_pelanggan, alamat, id_tarif_str]):
            flash("Semua kolom harus diisi.", "danger")
            db_conn.close()
            return render_template('admin_pelanggan_form.html', form_action='add', tariffs=tarifs)

        try:
            id_tarif = int(id_tarif_str)
            if not (1 <= id_tarif <= 999999):
                flash("ID Tarif tidak valid.", "danger")
                db_conn.close()
                return render_template('admin_pelanggan_form.html', form_action='add', tariffs=tarifs)
        except ValueError:
            flash("ID Tarif tidak valid.", "danger")
            db_conn.close()
            return render_template('admin_pelanggan_form.html', form_action='add', tariffs=tarifs)

        hashed_password = auth_service.hash_password(password)

        if models.add_new_pelanggan(db_conn, username, hashed_password, nomor_kwh, nama_pelanggan, alamat, id_tarif):
            flash("Pelanggan berhasil ditambahkan.", "success")
            db_conn.close()
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Gagal menambahkan pelanggan. Nomor KWH atau username mungkin sudah ada.", "danger")
    
    db_conn.close()
    return render_template('admin_pelanggan_form.html', form_action='add', tariffs=tarifs)

@app.route('/admin/pelanggan/edit/<int:id_pelanggan>', methods=['GET', 'POST'])
@login_required
def admin_edit_pelanggan(id_pelanggan):
    if not check_admin_access():
        return redirect(url_for('login'))

    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('admin_dashboard'))

    pelanggan_data = models.get_pelanggan_by_id(db_conn, id_pelanggan)
    tarifs = models.get_all_tarif(db_conn)

    if not pelanggan_data:
        flash("Pelanggan tidak ditemukan.", "danger")
        db_conn.close()
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        nama_pelanggan = request.form.get('nama_pelanggan')
        alamat = request.form.get('alamat')
        id_tarif_str = request.form.get('id_tarif')

        if not all([nama_pelanggan, alamat, id_tarif_str]):
            flash("Nama pelanggan, alamat, dan ID Tarif harus diisi.", "danger")
            db_conn.close()
            return render_template('admin_pelanggan_form.html', form_action='edit', pelanggan=pelanggan_data, tariffs=tarifs)

        try:
            id_tarif = int(id_tarif_str)
            if not (1 <= id_tarif <= 999999):
                flash("ID Tarif tidak valid.", "danger")
                db_conn.close()
                return render_template('admin_pelanggan_form.html', form_action='edit', pelanggan=pelanggal_data, tariffs=tarifs)
        except ValueError:
            flash("ID Tarif tidak valid.", "danger")
            db_conn.close()
            return render_template('admin_pelanggan_form.html', form_action='edit', pelanggan=pelanggan_data, tariffs=tarifs)

        if models.update_pelanggan_data(db_conn, id_pelanggan, nama_pelanggan, alamat, id_tarif):
            flash("Data pelanggan berhasil diupdate.", "success")
            db_conn.close()
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Gagal update data pelanggan.", "danger")

    db_conn.close()
    return render_template('admin_pelanggan_form.html', form_action='edit', pelanggan=pelanggan_data, tariffs=tarifs)

@app.route('/admin/pelanggan/delete/<int:id_pelanggan>', methods=['POST'])
@login_required
def admin_delete_pelanggan(id_pelanggan):
    if not check_admin_access():
        return redirect(url_for('login'))

    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('admin_dashboard'))

    if models.delete_pelanggan_data(db_conn, id_pelanggan):
        flash("Pelanggan berhasil dihapus.", "success")
    else:
        flash("Gagal menghapus pelanggan. Mungkin ada data terkait yang tidak bisa dihapus.", "danger")

    db_conn.close()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/penggunaan')
@login_required
def admin_penggunaan_list():
    if not check_admin_access():
        return redirect(url_for('login'))

    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('admin_dashboard'))

    # Menggunakan fungsi baru yang mengambil status pembayaran
    penggunaan_data = models.get_all_penggunaan_with_status(db_conn)
    db_conn.close()
    return render_template('admin_penggunaan_list.html',
                            username=current_user.username,
                            nama_admin=current_user.nama_tampilan,
                            penggunaan_data=penggunaan_data)

@app.route('/admin/penggunaan/add', methods=['GET', 'POST'])
@login_required
def admin_add_penggunaan():
    if not check_admin_access():
        app.logger.warning(f"Akses tidak sah ke /admin/penggunaan/add oleh user: {current_user.username}")
        return redirect(url_for('login'))

    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('admin_dashboard'))

    pelanggans = models.get_all_pelanggan(db_conn)

    if request.method == 'POST':
        app.logger.info("POST request diterima untuk /admin/penggunaan/add.")
        id_pelanggan_str = request.form.get('id_pelanggan')
        bulan_str = request.form.get('bulan')
        tahun_str = request.form.get('tahun')
        meter_awal_str = request.form.get('meter_awal')
        meter_akhir_str = request.form.get('meter_akhir')

        if not all([id_pelanggan_str, bulan_str, tahun_str, meter_awal_str, meter_akhir_str]):
            flash("Semua kolom harus diisi.", "danger")
            db_conn.close()
            app.logger.warning("Validasi form gagal: kolom kosong.")
            return render_template('admin_penggunaan_form.html', form_action='add', pelanggans=pelanggans)

        try:
            id_pelanggan = int(id_pelanggan_str)
            bulan = int(bulan_str)
            tahun = int(tahun_str)
            meter_awal = int(meter_awal_str)
            meter_akhir = int(meter_akhir_str)

            if not (1 <= bulan <= 12) or not (2000 <= tahun <= 2100):
                flash("Bulan harus antara 1-12 dan Tahun antara 2000-2100.", "danger")
                db_conn.close()
                app.logger.warning("Validasi input gagal: bulan/tahun tidak valid.")
                return render_template('admin_penggunaan_form.html', form_action='add', pelanggans=pelanggans)

            if meter_akhir < meter_awal:
                flash("Meter Akhir tidak boleh kurang dari Meter Awal.", "danger")
                db_conn.close()
                app.logger.warning("Validasi input gagal: meter_akhir < meter_awal.")
                return render_template('admin_penggunaan_form.html', form_action='add', pelanggans=pelanggans)

            app.logger.info(f"[*] App: Memanggil models.add_penggunaan_listrik untuk Pelanggan={id_pelanggan}, Bulan={bulan}, Tahun={tahun}")
            
            if models.add_penggunaan_listrik(db_conn, id_pelanggan, bulan, tahun, meter_awal, meter_akhir):
                app.logger.info("[*] App: models.add_penggunaan_listrik berhasil, melakukan redirect.")
                flash("Penggunaan listrik berhasil ditambahkan. Tagihan otomatis dibuat.", "success")
                return redirect(url_for('admin_penggunaan_list'))
            else:
                app.logger.warning("[*] App: models.add_penggunaan_listrik mengembalikan False (indikasi duplikasi atau gagal).")
                flash("Gagal menambahkan penggunaan listrik. Pastikan ID Pelanggan valid dan periode belum ada.", "danger")
        except ValueError as ve:
            flash("Input tidak valid. Pastikan masukkan angka yang benar.", "danger")
            app.logger.error(f"ValueError di admin_add_penggunaan: {ve}")
        except mysql.connector.Error as db_err:
            if db_err.errno == 1062:
                flash("Gagal menambahkan penggunaan listrik: Periode untuk pelanggan ini sudah ada.", "danger")
                app.logger.warning(f"Percobaan duplikasi entry penggunaan oleh {current_user.username}: {db_err}")
            else:
                flash(f"Terjadi error database: {db_err}", "danger")
                app.logger.error(f"Database Error di admin_add_penggunaan: {db_err}", exc_info=True)
        except Exception as e:
            flash(f"Terjadi error umum saat proses data: {e}", "danger")
            app.logger.error(f"General Error di admin_add_penggunaan: {e}", exc_info=True)
        finally:
            if db_conn and db_conn.is_connected():
                db_conn.close()
                app.logger.info("[*] App: Koneksi DB ditutup di finally block.")

    db_conn.close()
    return render_template('admin_penggunaan_form.html', form_action='add', pelanggans=pelanggans)

@app.route('/admin/penggunaan/edit/<int:id_penggunaan>', methods=['GET', 'POST'])
@login_required
def admin_edit_penggunaan(id_penggunaan):
    if not check_admin_access():
        return redirect(url_for('login'))

    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('admin_dashboard'))

    penggunaan_data = models.get_penggunaan_by_id(db_conn, id_penggunaan)
    pelanggans = models.get_all_pelanggan(db_conn)

    if not penggunaan_data:
        flash("Data penggunaan tidak ditemukan.", "danger")
        db_conn.close()
        return redirect(url_for('admin_penggunaan_list'))

    if request.method == 'POST':
        bulan_str = request.form.get('bulan')
        tahun_str = request.form.get('tahun')
        meter_awal_str = request.form.get('meter_awal')
        meter_akhir_str = request.form.get('meter_akhir')

        if not all([bulan_str, tahun_str, meter_awal_str, meter_akhir_str]):
            flash("Semua kolom harus diisi.", "danger")
            db_conn.close()
            return render_template('admin_penggunaan_form.html', form_action='edit', penggunaan=penggunaan_data, pelanggans=pelanggans)

        try:
            bulan = int(bulan_str)
            tahun = int(tahun_str)
            meter_awal = int(meter_awal_str)
            meter_akhir = int(meter_akhir_str)

            if not (1 <= bulan <= 12) or not (2000 <= tahun <= 2100):
                flash("Bulan harus antara 1-12 dan Tahun antara 2000-2100.", "danger")
                db_conn.close()
                return render_template('admin_penggunaan_form.html', form_action='edit', penggunaan=penggunaan_data, pelanggans=pelanggans)

            if meter_akhir < meter_awal:
                flash("Meter Akhir tidak boleh kurang dari Meter Awal.", "danger")
                db_conn.close()
                return render_template('admin_penggunaan_form.html', form_action='edit', penggunaan=penggunaan_data, pelanggans=pelanggans)

            if models.update_penggunaan_data(db_conn, id_penggunaan, bulan, tahun, meter_awal, meter_akhir):
                flash("Data penggunaan berhasil diupdate.", "success")
                db_conn.close()
                return redirect(url_for('admin_penggunaan_list'))
            else:
                flash("Gagal update data penggunaan. Pastikan periode belum ada.", "danger")
        except ValueError:
            flash("Input tidak valid. Pastikan masukkan angka yang benar.", "danger")
        except mysql.connector.Error as db_err:
            if db_err.errno == 1062:
                flash("Gagal update data penggunaan: Periode untuk pelanggan ini sudah ada.", "danger")
            else:
                flash(f"Terjadi error database: {db_err}", "danger")
            app.logger.error(f"Database Error di admin_edit_penggunaan: {db_err}")
        except Exception as e:
            flash(f"Terjadi error umum saat update data: {e}", "danger")
            app.logger.error(f"General Error di admin_edit_penggunaan: {e}", exc_info=True)

    db_conn.close()
    return render_template('admin_penggunaan_form.html', form_action='edit', penggunaan=penggunaan_data, pelanggans=pelanggans)

@app.route('/admin/penggunaan/delete/<int:id_penggunaan>', methods=['POST'])
@login_required
def admin_delete_penggunaan(id_penggunaan):
    if not check_admin_access():
        return redirect(url_for('login'))

    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('admin_dashboard'))

    if models.delete_penggunaan_data(db_conn, id_penggunaan):
        flash("Data penggunaan berhasil dihapus.", "success")
    else:
        flash("Gagal menghapus data penggunaan.", "danger")

    db_conn.close()
    return redirect(url_for('admin_penggunaan_list'))

@app.route('/admin/tarif')
@login_required
def admin_tarif_list():
    if not check_admin_access():
        return redirect(url_for('login'))

    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('admin_dashboard'))

    tarifs = models.get_all_tarif(db_conn)
    db_conn.close()
    return render_template('admin_tarif_list.html',
                            username=current_user.username,
                            nama_admin=current_user.nama_tampilan,
                            tarifs=tarifs)

@app.route('/admin/tarif/edit/<int:id_tarif>', methods=['GET', 'POST'])
@login_required
def admin_edit_tarif(id_tarif):
    if not check_admin_access():
        return redirect(url_for('login'))

    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('admin_tarif_list'))

    tarif_data = models.get_tarif_by_id(db_conn, id_tarif)

    if not tarif_data:
        flash("Data tarif tidak ditemukan.", "danger")
        db_conn.close()
        return redirect(url_for('admin_tarif_list'))

    if request.method == 'POST':
        daya_str = request.form.get('daya')
        tarifperkwh_str = request.form.get('tarifperkwh')
        biaya_beban_str = request.form.get('biaya_beban')

        if not all([daya_str, tarifperkwh_str, biaya_beban_str]):
            flash("Semua kolom harus diisi.", "danger")
            db_conn.close()
            return render_template('admin_tarif_form.html', tarif=tarif_data)

        try:
            daya = int(daya_str)
            tarifperkwh = decimal.Decimal(tarifperkwh_str)
            biaya_beban = decimal.Decimal(biaya_beban_str)

            if models.update_tarif_data(db_conn, id_tarif, daya, tarifperkwh, biaya_beban):
                flash("Data tarif berhasil diupdate.", "success")
                db_conn.close()
                return redirect(url_for('admin_tarif_list'))
            else:
                flash("Gagal update data tarif.", "danger")
        except ValueError:
            flash("Input tidak valid. Pastikan daya adalah angka, dan tarif/biaya beban adalah format desimal yang benar (contoh: 2500.00).", "danger")
        except Exception as e:
            flash(f"Terjadi error saat update data: {e}", "danger")
            app.logger.error(f"General Error di admin_edit_tarif: {e}", exc_info=True)

    db_conn.close()
    return render_template('admin_tarif_form.html', tarif=tarif_data)

@app.route('/pelanggan_dashboard')
@login_required
def pelanggan_dashboard():
    if not check_pelanggan_access():
        return redirect(url_for('login'))

    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('login'))

    riwayat_tagihan = models.get_pelanggan_usage_and_bill(db_conn, current_user.id_pelanggan_db)
    total_tagihan_belum_lunas = models.get_total_unpaid_bill_for_pelanggan(db_conn, current_user.id_pelanggan_db)
    total_penggunaan_kwh = models.get_total_kwh_for_pelanggan(db_conn, current_user.id_pelanggan_db)
    # total_tagihan_keseluruhan = models.get_total_all_bills_for_pelanggan(db_conn, current_user.id_pelanggan_db) # Kalau diaktifkan

    # Ambil data bulanan untuk grafik
    monthly_data_for_chart = models.get_monthly_usage_and_bill_data(db_conn, current_user.id_pelanggan_db)

    db_conn.close()

    return render_template('pelanggan_dashboard.html',
                            username=current_user.username,
                            nama_pelanggan=current_user.nama_tampilan,
                            riwayat=riwayat_tagihan,
                            total_tagihan_belum_lunas=total_tagihan_belum_lunas,
                            total_penggunaan_kwh=total_penggunaan_kwh,
                            monthly_data_for_chart=monthly_data_for_chart # <-- Teruskan ini
                            # total_tagihan_keseluruhan=total_tagihan_keseluruhan 
                            )

@app.route('/pelanggan/bayar_tagihan/<int:id_tagihan>', methods=['GET', 'POST'])
@login_required
def bayar_tagihan(id_tagihan):
    if not check_pelanggan_access():
        return redirect(url_for('login'))

    db_conn = get_db_and_handle_error()
    if not db_conn:
        return redirect(url_for('pelanggan_dashboard'))

    tagihan_detail = models.get_tagihan_by_id(db_conn, id_tagihan)

    if not tagihan_detail or tagihan_detail['id_pelanggan'] != current_user.id_pelanggan_db:
        flash("Tagihan tidak ditemukan atau bukan milik Anda.", "danger")
        db_conn.close()
        return redirect(url_for('pelanggan_dashboard'))

    if tagihan_detail['status'] == 'sudah_bayar':
        flash("Tagihan ini sudah lunas.", "info")
        db_conn.close()
        return redirect(url_for('pelanggan_dashboard'))

    if request.method == 'POST':
        biaya_admin_str = request.form.get('biaya_admin', '2500.00')
        total_bayar_str = request.form.get('total_bayar')

        if not total_bayar_str:
            flash("Jumlah pembayaran harus diisi.", "danger")
            db_conn.close()
            return render_template('bayar_tagihan.html', tagihan=tagihan_detail)

        try:
            biaya_admin = decimal.Decimal(biaya_admin_str)
            total_tagihan_final_from_db = tagihan_detail['total_tagihan_final'] 

            total_bayar = decimal.Decimal(total_bayar_str)
            
            if total_bayar < total_tagihan_final_from_db + biaya_admin:
                flash(f"Jumlah pembayaran kurang dari total tagihan plus biaya admin. Anda perlu membayar minimal {format_rupiah_filter(total_tagihan_final_from_db + biaya_admin)}", "danger")
                db_conn.close()
                return render_template('bayar_tagihan.html', tagihan=tagihan_detail)

            if models.add_pembayaran(
                db_conn,
                id_tagihan,
                current_user.id_pelanggan_db,
                biaya_admin,
                total_bayar,
                current_user.id
            ):
                flash("Pembayaran berhasil dicatat. Tagihan Anda sudah lunas!", "success")
                db_conn.close()
                return redirect(url_for('pelanggan_dashboard'))
            else:
                flash("Gagal mencatat pembayaran.", "danger")
        except decimal.InvalidOperation:
            flash("Input jumlah pembayaran atau biaya admin tidak valid. Gunakan format angka desimal yang benar (contoh: 2500.00).", "danger")
            app.logger.error("Invalid decimal operation in bayar_tagihan", exc_info=True)
        except Exception as e:
            flash(f"Terjadi error saat proses pembayaran: {e}", "danger")
            app.logger.error(f"General Error in bayar_tagihan: {e}", exc_info=True)

    db_conn.close()
    return render_template('bayar_tagihan.html', tagihan=tagihan_detail)

if __name__ == '__main__':
    app.run(debug=True)