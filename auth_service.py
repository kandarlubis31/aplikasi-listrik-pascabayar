import mysql.connector
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(db_conn, username, password_input):
    try:
        cursor = db_conn.cursor(dictionary=True)

        query_user = "SELECT id_user, username, password, nama_admin, id_level FROM user WHERE username = %s"
        cursor.execute(query_user, (username,))
        user_data = cursor.fetchone()

        if user_data:
            if user_data['password'] == hash_password(password_input):
                return user_data

        query_pelanggan = "SELECT id_pelanggan, username, password, nama_pelanggan, id_tarif FROM pelanggan WHERE username = %s"
        cursor.execute(query_pelanggan, (username,))
        pelanggan_data = cursor.fetchone()

        if pelanggan_data:
            if pelanggan_data['password'] == hash_password(password_input):
                pelanggan_data['id_level'] = 3
                pelanggan_data['id_user'] = pelanggan_data['id_pelanggan']
                return pelanggan_data

        return None
    except mysql.connector.Error as err:
        print("Error saat login:", err)
        return None
    finally:
        cursor.close()

def get_level_name(db_conn, id_level):
    try:
        cursor = db_conn.cursor(dictionary=True)
        query = "SELECT nama_level FROM level WHERE id_level = %s"
        cursor.execute(query, (id_level,))
        result = cursor.fetchone()
        if result:
            return result['nama_level']
        return "Tidak Dikenal"
    except mysql.connector.Error as err:
        print("Error mengambil nama level:", err)
        return "Tidak Dikenal"
    finally:
        cursor.close()