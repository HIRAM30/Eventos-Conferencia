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
    cursor.execute("SELECT id_usuario, correo_electronico, tipo_usuario, contraseña FROM usuario WHERE correo_electronico = %s", (nombre_usuario,))
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


def insertar_conferencia(nombre, descripcion, fecha_inicio, fecha_fin, id_usuario):
    # Aquí va el código para insertar en la base de datos
    conexion = crear_conexion()
    cursor = conexion.cursor()
    query = """
    INSERT INTO conferencia (nombre, descripcion, fecha_inicio, fecha_fin, id_organizador)
    VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(query, (nombre, descripcion, fecha_inicio, fecha_fin, id_usuario))
    conexion.commit()
    cursor.close()
    conexion.close()
    return True  # O el valor correspondiente según el resultado de la inserción


def obtener_conferencias():
    # Simulando datos de conferencias desde la base de datos
    return [
        {
            "id": 1,
            "title": "Conferencia de Ciencia",
            "start": "2024-11-25T09:00:00",
            "end": "2024-11-25T17:00:00",
            "description": "Una conferencia sobre los avances en la ciencia."
        },
        {
            "id": 2,
            "title": "Conferencia de Tecnología",
            "start": "2024-11-26T10:00:00",
            "end": "2024-11-26T16:00:00",
            "description": "Una conferencia sobre el futuro de la tecnología."
        }
    ]

def obtener_sesiones_por_conferencia(conference_id):
    # Simulando datos de sesiones
    if conference_id == 1:
        return [
            {
                "id": 1,
                "title": "Sesión sobre física cuántica",
                "start": "2024-11-25T10:00:00",
                "end": "2024-11-25T12:00:00",
                "description": "Una introducción a la física cuántica."
            },
            {
                "id": 2,
                "title": "Sesión sobre biología molecular",
                "start": "2024-11-25T13:00:00",
                "end": "2024-11-25T15:00:00",
                "description": "Exploración de los conceptos de la biología molecular."
            }
        ]
    elif conference_id == 2:
        return [
            {
                "id": 3,
                "title": "Sesión sobre Inteligencia Artificial",
                "start": "2024-11-26T11:00:00",
                "end": "2024-11-26T13:00:00",
                "description": "Exploración de la IA y su impacto en la sociedad."
            }
        ]
    return []

def registrar_usuario_en_sesion(user_id, session_id):
    # Aquí puedes agregar la lógica para registrar al usuario en la sesión (por ejemplo, en la base de datos)
    # Para este ejemplo, simplemente retornamos True para simular una inscripción exitosa.
    return True