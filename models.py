import mysql.connector
import logging
import decimal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_all_pelanggan(db_conn):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = "SELECT id_pelanggan, username, nomor_kwh, nama_pelanggan, alamat, id_tarif FROM pelanggan"
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil data semua pelanggan: {err}", exc_info=True)
        return []
    finally:
        if cursor: cursor.close()

def get_pelanggan_by_id(db_conn, id_pelanggan):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = "SELECT id_pelanggan, username, password, nomor_kwh, nama_pelanggan, alamat, id_tarif FROM pelanggan WHERE id_pelanggan = %s"
        cursor.execute(query, (id_pelanggan,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil data pelanggan berdasarkan ID: {err}", exc_info=True)
        return None
    finally:
        if cursor: cursor.close()

def add_new_pelanggan(db_conn, username, password, nomor_kwh, nama_pelanggan, alamat, id_tarif):
    cursor = None
    try:
        cursor = db_conn.cursor()
        query = "INSERT INTO pelanggan (username, password, nomor_kwh, nama_pelanggan, alamat, id_tarif) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (username, password, nomor_kwh, nama_pelanggan, alamat, id_tarif)
        cursor.execute(query, values)
        db_conn.commit()
        return True
    except mysql.connector.Error as err:
        logging.error(f"Error menambahkan pelanggan baru: {err}", exc_info=True)
        db_conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

def update_pelanggan_data(db_conn, id_pelanggan, nama_pelanggan, alamat, id_tarif):
    cursor = None
    try:
        cursor = db_conn.cursor()
        query = "UPDATE pelanggan SET nama_pelanggan = %s, alamat = %s, id_tarif = %s WHERE id_pelanggan = %s"
        values = (nama_pelanggan, alamat, id_tarif, id_pelanggan)
        cursor.execute(query, values)
        db_conn.commit()
        return True
    except mysql.connector.Error as err:
        logging.error(f"Error update data pelanggan: {err}", exc_info=True)
        db_conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

def delete_pelanggan_data(db_conn, id_pelanggan):
    cursor = None
    try:
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM pembayaran WHERE id_pelanggan = %s", (id_pelanggan,))
        cursor.execute("DELETE FROM tagihan WHERE id_pelanggan = %s", (id_pelanggan,))
        cursor.execute("DELETE FROM penggunaan WHERE id_pelanggan = %s", (id_pelanggan,))

        query = "DELETE FROM pelanggan WHERE id_pelanggan = %s"
        cursor.execute(query, (id_pelanggan,))
        db_conn.commit()
        return True
    except mysql.connector.Error as err:
        logging.error(f"Error menghapus pelanggan: {err}", exc_info=True)
        db_conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

def add_penggunaan_listrik(db_conn, id_pelanggan, bulan, tahun, meter_awal, meter_akhir):
    cursor = None
    try:
        cursor = db_conn.cursor()
        
        query = "INSERT INTO penggunaan (id_pelanggan, bulan, tahun, meter_awal, meter_akhir) VALUES (%s, %s, %s, %s, %s)"
        values = (id_pelanggan, bulan, tahun, meter_awal, meter_akhir)
        cursor.execute(query, values)

        db_conn.commit()
        logging.info(f"Penggunaan listrik berhasil di-insert ke tabel 'penggunaan' untuk Pelanggan {id_pelanggan}, Bulan {bulan}, Tahun {tahun}. Tagihan akan dibuat otomatis oleh trigger.")
        return True
    except mysql.connector.Error as err:
        logging.error(f"Error menambahkan penggunaan listrik di models (add_penggunaan_listrik): {err}", exc_info=True)
        db_conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

def get_all_penggunaan_with_status(db_conn):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = """
            SELECT
                pg.id_penggunaan,
                p.nama_pelanggan,
                pg.bulan,
                pg.tahun,
                pg.meter_awal,
                pg.meter_akhir,
                (pg.meter_akhir - pg.meter_awal) AS jumlah_kwh,
                COALESCE(t.status, 'Belum Ada Tagihan') AS status_pembayaran,
                COALESCE(t.total_tagihan, 0.00) AS total_tagihan_hitung
            FROM penggunaan pg
            JOIN pelanggan p ON pg.id_pelanggan = p.id_pelanggan
            LEFT JOIN tagihan t ON pg.id_penggunaan = t.id_penggunaan
            ORDER BY pg.tahun DESC, pg.bulan DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil semua penggunaan dengan status: {err}", exc_info=True)
        return []
    finally:
        if cursor: cursor.close()

def get_penggunaan_by_id(db_conn, id_penggunaan):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = "SELECT id_penggunaan, id_pelanggan, bulan, tahun, meter_awal, meter_akhir FROM penggunaan WHERE id_penggunaan = %s"
        cursor.execute(query, (id_penggunaan,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil penggunaan listrik berdasarkan ID: {err}", exc_info=True)
        return None
    finally:
        if cursor: cursor.close()

def update_penggunaan_data(db_conn, id_penggunaan, bulan, tahun, meter_awal, meter_akhir):
    cursor = None
    try:
        cursor = db_conn.cursor()
        
        cursor.execute("SELECT id_pelanggan FROM penggunaan WHERE id_penggunaan = %s", (id_penggunaan,))
        id_pelanggan_current = cursor.fetchone()[0]

        check_duplicate_period_query = """
            SELECT COUNT(*) FROM penggunaan
            WHERE id_pelanggan = %s AND bulan = %s AND tahun = %s AND id_penggunaan != %s
        """
        cursor.execute(check_duplicate_period_query, (id_pelanggan_current, bulan, tahun, id_penggunaan))
        if cursor.fetchone()[0] > 0:
            logging.warning(f"Percobaan update penggunaan ke periode duplikat untuk Pelanggan {id_pelanggan_current}, Bulan {bulan}, Tahun {tahun}")
            return False

        query = "UPDATE penggunaan SET bulan = %s, tahun = %s, meter_awal = %s, meter_akhir = %s WHERE id_penggunaan = %s"
        values = (bulan, tahun, meter_awal, meter_akhir, id_penggunaan)
        cursor.execute(query, values)

        jumlah_meter = meter_akhir - meter_awal

        cursor.execute("SELECT id_tarif FROM pelanggan WHERE id_pelanggan = %s", (id_pelanggan_current,))
        id_tarif_pelanggan = cursor.fetchone()[0]

        cursor.execute("SELECT tarifperkwh, biaya_beban FROM tarif WHERE id_tarif = %s", (id_tarif_pelanggan,))
        tarif_data = cursor.fetchone()

        if tarif_data:
            tarifperkwh = tarif_data[0]
            biaya_beban = tarif_data[1]
            total_tagihan_calculated = (decimal.Decimal(jumlah_meter) * tarifperkwh) + biaya_beban
            
            query_update_tagihan = """
                UPDATE tagihan SET jumlah_meter = %s, total_tagihan = %s, bulan = %s, tahun = %s
                WHERE id_penggunaan = %s
            """
            values_update_tagihan = (jumlah_meter, total_tagihan_calculated, bulan, tahun, id_penggunaan)
            cursor.execute(query_update_tagihan, values_update_tagihan)
            logging.info(f"Tagihan untuk penggunaan {id_penggunaan} berhasil diupdate berdasarkan perubahan penggunaan.")

        db_conn.commit()
        return True
    except mysql.connector.Error as err:
        logging.error(f"Error update penggunaan listrik: {err}", exc_info=True)
        db_conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

def delete_penggunaan_data(db_conn, id_penggunaan):
    cursor = None
    try:
        cursor = db_conn.cursor()
        cursor.execute("DELETE FROM pembayaran WHERE id_tagihan IN (SELECT id_tagihan FROM tagihan WHERE id_penggunaan = %s)", (id_penggunaan,))
        cursor.execute("DELETE FROM tagihan WHERE id_penggunaan = %s", (id_penggunaan,))
        query = "DELETE FROM penggunaan WHERE id_penggunaan = %s"
        cursor.execute(query, (id_penggunaan,))
        db_conn.commit()
        return True
    except mysql.connector.Error as err:
        logging.error(f"Error menghapus penggunaan listrik: {err}", exc_info=True)
        db_conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

def get_pelanggan_usage_and_bill(db_conn, id_pelanggan):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = """
            SELECT
                tg.id_tagihan,
                pg.bulan,
                pg.tahun,
                pg.meter_awal,
                pg.meter_akhir,
                tg.jumlah_meter,
                tg.status AS status_tagihan,
                tr.tarifperkwh,
                tr.biaya_beban,
                COALESCE(tg.total_tagihan, 0.00) AS total_tagihan_final 
            FROM
                penggunaan pg
            LEFT JOIN
                tagihan tg ON pg.id_penggunaan = tg.id_penggunaan
            JOIN
                pelanggan p ON pg.id_pelanggan = p.id_pelanggan
            JOIN
                tarif tr ON p.id_tarif = tr.id_tarif
            WHERE
                pg.id_pelanggan = %s
            ORDER BY pg.tahun DESC, pg.bulan DESC
        """
        cursor.execute(query, (id_pelanggan,))
        riwayat_data = cursor.fetchall()

        for item in riwayat_data:
            if not isinstance(item['total_tagihan_final'], decimal.Decimal):
                item['total_tagihan_final'] = decimal.Decimal(str(item['total_tagihan_final']))
        
        return riwayat_data
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil riwayat penggunaan dan tagihan: {err}", exc_info=True)
        return []
    finally:
        if cursor: cursor.close()

def get_all_tarif(db_conn):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = "SELECT id_tarif, daya, tarifperkwh, biaya_beban FROM tarif ORDER BY daya"
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil semua tarif: {err}", exc_info=True)
        return []
    finally:
        if cursor: cursor.close()

def get_tarif_by_id(db_conn, id_tarif):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = "SELECT id_tarif, daya, tarifperkwh, biaya_beban FROM tarif WHERE id_tarif = %s"
        cursor.execute(query, (id_tarif,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil tarif berdasarkan ID: {err}", exc_info=True)
        return None
    finally:
        if cursor: cursor.close()

def update_tarif_data(db_conn, id_tarif, daya, tarifperkwh, biaya_beban):
    cursor = None
    try:
        cursor = db_conn.cursor()
        query = "UPDATE tarif SET daya = %s, tarifperkwh = %s, biaya_beban = %s WHERE id_tarif = %s"
        values = (daya, tarifperkwh, biaya_beban, id_tarif)
        cursor.execute(query, values)
        db_conn.commit()
        return True
    except mysql.connector.Error as err:
        logging.error(f"Error update data tarif: {err}", exc_info=True)
        db_conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

def get_all_users(db_conn):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = """
            SELECT u.id_user, u.username, u.nama_admin, l.nama_level
            FROM user u JOIN level l ON u.id_level = l.id_level
            ORDER BY u.id_user
        """
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil semua user admin/petugas: {err}", exc_info=True)
        return []
    finally:
        if cursor: cursor.close()

def get_tagihan_by_id(db_conn, id_tagihan):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = """
            SELECT
                tg.id_tagihan,
                tg.id_penggunaan,
                tg.id_pelanggan,
                tg.bulan,
                tg.tahun,
                pg.meter_awal,
                pg.meter_akhir,
                tg.jumlah_meter,
                tg.status,
                p.nomor_kwh,
                p.nama_pelanggan,
                t.daya,
                t.tarifperkwh,
                t.biaya_beban,
                COALESCE(tg.total_tagihan, 0.00) AS total_tagihan_final 
            FROM
                tagihan tg
            JOIN
                pelanggan p ON tg.id_pelanggan = p.id_pelanggan
            JOIN
                penggunaan pg ON tg.id_penggunaan = pg.id_penggunaan
            JOIN
                tarif t ON p.id_tarif = t.id_tarif
            WHERE
                tg.id_tagihan = %s
        """
        cursor.execute(query, (id_tagihan,))
        tagihan_data = cursor.fetchone()

        if tagihan_data and not isinstance(tagihan_data['total_tagihan_final'], decimal.Decimal):
            tagihan_data['total_tagihan_final'] = decimal.Decimal(str(tagihan_data['total_tagihan_final']))

        return tagihan_data
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil tagihan berdasarkan ID: {err}", exc_info=True)
        return None
    finally:
        if cursor: cursor.close()

def add_pembayaran(db_conn, id_tagihan, id_pelanggan, biaya_admin, total_bayar, id_user_pencatat):
    cursor = None
    try:
        cursor = db_conn.cursor()

        user_id_to_store = None
        if id_user_pencatat:
            cursor.execute("SELECT id_level FROM user WHERE id_user = %s", (id_user_pencatat,))
            user_level_row = cursor.fetchone()
            if user_level_row and user_level_row[0] in [1, 2]:
                user_id_to_store = id_user_pencatat
        
        query_pembayaran = """
            INSERT INTO pembayaran (id_tagihan, id_pelanggan, tanggal_pembayaran, bulan_bayar, tahun_bayar, biaya_admin, total_bayar, id_user)
            VALUES (%s, %s, CURRENT_TIMESTAMP(), MONTH(CURRENT_TIMESTAMP()), YEAR(CURRENT_TIMESTAMP()), %s, %s, %s)
        """
        values_pembayaran = (id_tagihan, id_pelanggan, biaya_admin, total_bayar, user_id_to_store)
        cursor.execute(query_pembayaran, values_pembayaran)

        query_tagihan = "UPDATE tagihan SET status = 'sudah_bayar' WHERE id_tagihan = %s"
        cursor.execute(query_tagihan, (id_tagihan,))

        db_conn.commit()
        logging.info(f"Pembayaran tagihan {id_tagihan} berhasil dicatat oleh user {user_id_to_store if user_id_to_store else 'Pelanggan'}.")
        return True
    except mysql.connector.Error as err:
        logging.error(f"Error saat menambahkan pembayaran: {err}", exc_info=True)
        db_conn.rollback()
        return False
    finally:
        if cursor: cursor.close()

# Fungsi baru untuk Dashboard Pelanggan: Menghitung total tagihan BELUM LUNAS
def get_total_unpaid_bill_for_pelanggan(db_conn, id_pelanggan):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = """
            SELECT
                SUM(COALESCE(t.total_tagihan, 0)) AS total_tagihan_belum_lunas
            FROM
                tagihan t
            WHERE
                t.id_pelanggan = %s AND t.status = 'belum_bayar';
        """
        cursor.execute(query, (id_pelanggan,))
        result = cursor.fetchone()
        if result and result['total_tagihan_belum_lunas'] is not None:
            return decimal.Decimal(str(result['total_tagihan_belum_lunas']))
        return decimal.Decimal('0.00')
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil total tagihan belum lunas: {err}", exc_info=True)
        return decimal.Decimal('0.00')
    finally:
        if cursor: cursor.close()

# Fungsi baru untuk Dashboard Pelanggan: Menghitung total KWH terpakai
def get_total_kwh_for_pelanggan(db_conn, id_pelanggan):
    cursor = None
    try:
        cursor = db_conn.cursor()
        query = """
            SELECT SUM(meter_akhir - meter_awal)
            FROM penggunaan
            WHERE id_pelanggan = %s;
        """
        cursor.execute(query, (id_pelanggan,))
        result = cursor.fetchone()[0]
        return result if result is not None else 0
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil total KWH terpakai: {err}", exc_info=True)
        return 0
    finally:
        if cursor: cursor.close()

# Fungsi Opsional: Menghitung total semua tagihan (lunas dan belum lunas)
def get_total_all_bills_for_pelanggan(db_conn, id_pelanggan):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = """
            SELECT
                SUM(COALESCE(t.total_tagihan, 0)) AS total_semua_tagihan
            FROM
                tagihan t
            WHERE
                t.id_pelanggan = %s;
        """
        cursor.execute(query, (id_pelanggan,))
        result = cursor.fetchone()
        if result and result['total_semua_tagihan'] is not None:
            return decimal.Decimal(str(result['total_semua_tagihan']))
        return decimal.Decimal('0.00')
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil total semua tagihan: {err}", exc_info=True)
        return decimal.Decimal('0.00')
    finally:
        if cursor: cursor.close()

# Fungsi untuk data grafik bulanan (revisi)
def get_monthly_usage_and_bill_data(db_conn, id_pelanggan):
    cursor = None
    try:
        cursor = db_conn.cursor(dictionary=True) # <<< Pastikan ini dictionary=True
        query = """
            SELECT
                pg.bulan,
                pg.tahun,
                CAST(SUM(pg.meter_akhir - pg.meter_awal) AS DECIMAL(10,2)) AS total_kwh_bulan,
                CAST(SUM(COALESCE(t.total_tagihan, 0)) AS DECIMAL(10,2)) AS total_tagihan_bulan
            FROM
                penggunaan pg
            LEFT JOIN
                tagihan t ON pg.id_penggunaan = t.id_penggunaan
            WHERE
                pg.id_pelanggan = %s
            GROUP BY
                pg.tahun, pg.bulan
            ORDER BY
                pg.tahun ASC, pg.bulan ASC;
        """
        cursor.execute(query, (id_pelanggan,))
        data = cursor.fetchall()

        # Konversi Decimal ke float jika perlu, untuk kompatibilitas JSON.
        # Jinja2's tojson should handle Decimal, but explicit conversion can help.
        for item in data:
            if 'total_kwh_bulan' in item and isinstance(item['total_kwh_bulan'], decimal.Decimal):
                item['total_kwh_bulan'] = float(item['total_kwh_bulan'])
            if 'total_tagihan_bulan' in item and isinstance(item['total_tagihan_bulan'], decimal.Decimal):
                item['total_tagihan_bulan'] = float(item['total_tagihan_bulan'])
        
        return data
    except mysql.connector.Error as err:
        logging.error(f"Error mengambil data penggunaan dan tagihan bulanan: {err}", exc_info=True)
        return []
    finally:
        if cursor: cursor.close()