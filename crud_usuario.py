import mysql.connector
from db_conector import crear_conexion
from werkzeug.security import generate_password_hash


# Funcion para insertar un nuevo usuario
def insertar_usuario(nombre_usuario, correo_electronico, contraseña, tipo_usuario="asistente"):
    conexion = crear_conexion()
    cursor = conexion.cursor()
    try:
        contraseña_hash = generate_password_hash(contraseña)  # Generamos el hash de la contraseña
        consulta = """
            INSERT INTO usuario (nombre_usuario, contraseña, tipo_usuario, correo_electronico)
            VALUES (%s, %s, %s, %s)
        """
        datos = (nombre_usuario, contraseña_hash, tipo_usuario, correo_electronico)
        cursor.execute(consulta, datos)
        conexion.commit()
        return "Usuario registrado exitosamente"
    except mysql.connector.Error as e:
        return f"Error al insertar usuario: {e}"
    finally:
        cursor.close()
        conexion.close()

# Función para obtener un usuario por nombre de usuario
def obtener_usuario_por_nombre_usuario(nombre_usuario):
    conexion = crear_conexion()  # Función que crea la conexión a la base de datos
    cursor = conexion.cursor(dictionary=True)  # Usamos 'dictionary=True' para obtener los resultados como un diccionario
    try:
        consulta = """
            SELECT nombre_usuario, correo_electronico, contraseña, tipo_usuario
            FROM usuario
            WHERE correo_electronico = %s
        """
        cursor.execute(consulta, (nombre_usuario,))
        usuario = cursor.fetchone()  # Obtiene solo el primer usuario que coincida

        return usuario
    except mysql.connector.Error as e:
        print(f"Error al obtener usuario: {e}")
        return None
    finally:
        cursor.close()
        conexion.close()
