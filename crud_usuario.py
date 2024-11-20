import mysql.connector
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from flask import url_for
from werkzeug.security import generate_password_hash
from config import mail
from db_conector import crear_conexion

def insertar_usuario(nombre_usuario, correo_electronico, contraseña, tipo_usuario="asistente"):
    conexion = crear_conexion()
    cursor = conexion.cursor()
    try:
        contraseña_hash = generate_password_hash(contraseña)
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

def obtener_usuario_por_nombre_usuario(nombre_usuario):
    conexion = crear_conexion()
    cursor = conexion.cursor(dictionary=True)
    query = "SELECT * FROM usuario WHERE correo_electronico = %s"
    cursor.execute(query, (nombre_usuario,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return usuario

def obtener_usuario_por_id(user_id):
    conexion = crear_conexion()
    cursor = conexion.cursor(dictionary=True)
    query = "SELECT * FROM usuario WHERE id_usuario = %s"
    cursor.execute(query, (user_id,))
    usuario = cursor.fetchone()
    cursor.close()
    conexion.close()
    return usuario

def generar_token_reset(correo_electronico, serializer):
    return serializer.dumps(correo_electronico, salt="reset-password")

# Función para enviar el correo de restablecimiento
def enviar_email_restablecimiento(correo_electronico, serializer):
    token = serializer.dumps(correo_electronico, salt='reset-password')
    mensaje = Message('Restablecimiento de Contraseña',
                      sender='noreply@tuaplicacion.com',
                      recipients=[correo_electronico])
    url = url_for('restablecer_contraseña', token=token, _external=True)

    mensaje.body = f'Para restablecer tu contraseña, haz clic en el siguiente enlace: {url}'
    try:
        mail.send(mensaje)
    except Exception as e:
        print(f'Error al enviar el correo: {e}')
        raise

# Función para actualizar la contraseña del usuario
def actualizar_contraseña(correo_electronico, nueva_contraseña):
    conexion = crear_conexion()
    cursor = conexion.cursor()
    try:
        nueva_contraseña_hash = generate_password_hash(nueva_contraseña)
        consulta = """
            UPDATE usuario
            SET contraseña = %s
            WHERE correo_electronico = %s
        """
        cursor.execute(consulta, (nueva_contraseña_hash, correo_electronico))
        conexion.commit()
        return True
    except mysql.connector.Error as e:
        print(f"Error al actualizar la contraseña: {e}")
        return False
    finally:
        cursor.close()
        conexion.close()


# Función para obtener todos los usuarios
def obtener_usuarios():
    # Crear la conexión a la base de datos
    conexion = crear_conexion()
    cursor = conexion.cursor(dictionary=True)
    
    # Consultar los usuarios en la base de datos
    query = "SELECT * FROM usuario"
    cursor.execute(query)
    usuarios = cursor.fetchall()
    
    # Cerrar la conexión
    cursor.close()
    conexion.close()

    return usuarios


