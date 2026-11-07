import mysql.connector

import config


def get_db_connection():
    try:
        conn = mysql.connector.connect(**config.DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print("Error koneksi database:", err)
        return None