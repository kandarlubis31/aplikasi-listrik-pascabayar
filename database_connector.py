import mysql.connector

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="bayarlistrik_db"
        )
        return conn
    except mysql.connector.Error as err:
        print("Error koneksi database:", err)
        return None