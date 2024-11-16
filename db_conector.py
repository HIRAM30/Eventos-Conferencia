import mysql.connector

def crear_conexion():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # Cambia según tu configuración
        database="conferencias"
    )
