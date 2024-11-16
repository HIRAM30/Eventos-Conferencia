from db_conector import crear_conexion
from werkzeug.security import generate_password_hash

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
