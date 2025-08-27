import sqlite3
import os


def guardar_ip(ip_value):
    try:
        with sqlite3.connect("qrdatabase.db") as sql_conect:
            query = sql_conect.cursor()

            query.execute(
                """CREATE TABLE IF NOT EXISTS ip_saved (
                    ip_address TEXT PRIMARY KEY
                )"""
            )

            query.execute(
                "INSERT OR REPLACE INTO ip_saved (ip_address) VALUES (?)", (ip_value,)
            )
            return True
    except sqlite3.Error as Err:
        print(f"Error de base de datos: {Err}")
        return False
    except Exception as ex:
        print(f"Error inesperado: {ex}")
        return False


def obtener_ips():
    try:
        with sqlite3.connect("qrdatabase.db") as sql_conect:
            query = sql_conect.cursor()
            query.execute("SELECT ip_address FROM ip_saved ORDER BY ip_address")
            ips = query.fetchall()
            return [ip[0] for ip in ips]  # Devuelve la lista de ips

    except sqlite3.Error as Err:
        print(f"Error al obtener IPs: {Err}")
        return []


def eliminar_ip(delete_ip):
    try:
        with sqlite3.connect("qrdatabase.db") as sql_connect:
            query = sql_connect.cursor()
            query.execute("DELETE from ip_saved WHERE ip_address=?", (delete_ip,))
            # Verificar si se eliminó alguna fila
            if query.rowcount > 0:
                return True
            else:
                return False

    except sqlite3.Error as Err:
        print(f"Error al borrar los datos {Err}")
        return False
