import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
import pytz
from datetime import datetime
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired
from crud_usuario import actualizar_contraseña 
from crud_usuario import obtener_usuarios
from db_conector import crear_conexion

from config import mail
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Esta es tu clave secreta
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tu_contraseña@localhost/conferencias'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'toral.carrera.yair@gmail.com'
app.config['MAIL_PASSWORD'] = 'urjz gweo uach kymn'
app.config['MAIL_DEFAULT_SENDER'] = 'toral.carrera.yair@gmail.com'

# Instancia de generador de tokens
serializer = URLSafeTimedSerializer(app.secret_key)

# Configuración de Mail
mail.init_app(app)

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route("/enviar_correo", methods=["POST"])
def enviar_correo():
    if request.method == "POST":
        destinatario = request.form["destinatario"]
        asunto = "Asunto del correo"
        cuerpo = "Este es el contenido del correo"

        # Crear el mensaje
        msg = Message(asunto, recipients=[destinatario])
        msg.body = cuerpo

        try:
            # Enviar el correo
            mail.send(msg)
            flash("Correo enviado con éxito", "success")
            return redirect('/')
        except Exception as e:
            flash(f"Error al enviar el correo: {e}", "error")
            return redirect('/')

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/')
def home():
    # Verificamos si el usuario está autenticado
    if 'user_id' in session:
        # Redirigimos según el tipo de usuario
        if session['user_type'] == 'organizador':
            return redirect(url_for('organizador'))
        elif session['user_type'] == 'asistente':
            return redirect(url_for('asistente'))
        elif session['user_type'] == 'admin':
            return redirect(url_for('admin'))        
    
    # Si no está autenticado, mostramos la página home
    return render_template("home.html")  # Página de inicio con el botón de "Empezar"

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.after_request
def no_cache(response):
    response.cache_control.no_store = True
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre_usuario = request.form["correo"]
        contraseña = request.form["contraseña"]

        # Verificamos si el usuario existe
        usuario = obtener_usuario_por_nombre_usuario(nombre_usuario)

        if usuario:
            # Comprobamos si la contraseña es correcta
            if check_password_hash(usuario['contraseña'], contraseña):
                # Guardamos los datos del usuario en la sesión
                session['user_id'] = usuario['id_usuario']
                session['user_type'] = usuario['tipo_usuario']

                flash("Inicio de sesión exitoso", "success")

                    # Redirigir al tipo de usuario
                    if usuario['tipo_usuario'] == 'organizador':
                        return redirect(url_for("organizador"))  # Redirige al organizador
                    else:
                        return redirect(url_for("asistente"))  # Redirige al asistente

                else:
                    return redirect(url_for("asistente"))

            else:
                flash("Contraseña incorrecta", "error")
        else:
            flash("Usuario no encontrado", "error")

    return render_template("inicio_sesion.html")

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/registro_usuario', methods=["GET", "POST"])
def registro_usuario():
    if request.method == "POST":
        nombre_usuario = request.form["nombre_usuario"]
        correo_electronico = request.form["correo_electronico"]
        contraseña = request.form["contraseña"]
        confirmar_contraseña = request.form["confirmar"]
        tipo_usuario = request.form["tipo_usuario"]

        if contraseña != confirmar_contraseña:
            flash("Las contraseñas no coinciden", "error")
            return redirect(url_for("registro_usuario"))

        resultado = insertar_usuario(nombre_usuario, correo_electronico, contraseña, tipo_usuario)

        if "exitosamente" in resultado:
            flash("Usuario registrado exitosamente", "success")
            return redirect(url_for("login"))
        else:
            flash(resultado, "error")
            return redirect(url_for("registro_usuario"))

    return render_template("registro_usuario.html")

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/index')
def index():
    return render_template("index.html")

#----------------------------------------------------------------------------------------------------------------------------------------------

# Endpoint para obtener eventos desde la base de datos
@app.route('/api/events', methods=['GET'])
def obtener_eventos():
    conexion = crear_conexion()
    cursor = conexion.cursor(dictionary=True)
    query = """
    SELECT 
        c.id_conferencia AS id, 
        c.nombre AS title, 
        c.descripcion AS description, 
        c.fecha_inicio AS start, 
        c.fecha_fin AS end
    FROM conferencia c
    """
    cursor.execute(query)
    eventos = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Ajustar el formato de fecha
    for evento in eventos:
        evento['start'] = evento['start'].isoformat()
        evento['end'] = evento['end'].isoformat() if evento['end'] else None

    print("Eventos obtenidos de la base de datos:", eventos)  # Depuración
    return jsonify(eventos)
#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/conferencias', methods=['GET'])
def conferencias():
    return render_template("conferencias.html")


#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/perfil')
def perfil():
    if 'user_id' not in session:
        flash("Por favor, inicia sesión primero", "error")
        return redirect(url_for("login"))
    
    # Obtener los datos del usuario desde la base de datos
    usuario = obtener_usuario_por_id(session['user_id'])
    if not usuario:
        flash("No se pudieron obtener los datos del usuario", "error")
        return redirect(url_for("login"))
    
    return render_template("perfil.html", usuario=usuario)

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/recuperar_contraseña', methods=['GET', 'POST'])
def recuperar_contraseña():
    if request.method == 'POST':
        correo_electronico = request.form['correo_electronico']
        usuario = obtener_usuario_por_nombre_usuario(correo_electronico)
        if usuario:
            # Enviar enlace de recuperación de contraseña
            enviar_email_restablecimiento(correo_electronico, serializer)
            flash('Hemos enviado un enlace para restablecer tu contraseña a tu correo.', 'success')
            return redirect(url_for('login'))
        else:
            flash('El correo no está registrado en nuestro sistema.', 'error')
    
    return render_template('recuperar_contraseña.html')

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/restablecer_contraseña/<token>', methods=['GET', 'POST'])
def restablecer_contraseña(token):
    try:
        correo_electronico = serializer.loads(token, salt="reset-password", max_age=3600)
    except Exception:
        flash('El enlace para restablecer la contraseña ha expirado o es inválido.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        nueva_contraseña = request.form['nueva_contraseña']
        confirmar_contraseña = request.form['confirmar_contraseña']

        if nueva_contraseña != confirmar_contraseña:
            flash('Las contraseñas no coinciden.', 'error')
            return redirect(url_for('restablecer_contraseña', token=token))

        # Actualizar la contraseña en la base de datos
        actualizar_contraseña(correo_electronico, nueva_contraseña)
        flash('Tu contraseña ha sido actualizada exitosamente. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))

    return render_template('restablecer_contraseña.html', token=token)

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/logout')
def logout():
    session.clear()  # Limpiar todos los datos de la sesión
    flash("Has cerrado sesión exitosamente", "success")
    return redirect(url_for("login"))

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/asistente')
def asistente():
    if 'user_id' not in session or session['user_type'] != 'asistente':
        flash("Acceso no autorizado", "error")
        return redirect(url_for("login"))
    
    return render_template("index_asistente.html")

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/organizador')
def organizador():
    if 'user_id' not in session or session['user_type'] != 'organizador':
        flash("Acceso no autorizado", "error")
        return redirect(url_for("login"))
    
    return render_template("index.html")

#----------------------------------------------------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/admin')
def admin():
    if 'user_id' not in session or session['user_type'] != 'admin':
        flash("Acceso no autorizado", "error")
        return redirect(url_for("login"))
    return render_template("index_administrador.html")



#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/ver_usuarios_admin', methods=['GET'])
def ver_usuarios_admin():
    # Verificamos si el usuario está autenticado y es un administrador
    if 'user_id' not in session or session['user_type'] != 'admin':
        flash("Acceso no autorizado", "error")
        return redirect(url_for("login"))

    # Usamos el CRUD para obtener los usuarios
    usuarios = obtener_usuarios()

    # Verificamos que los usuarios se hayan obtenido correctamente
    if not usuarios:
        flash("No se encontraron usuarios en la base de datos.", "warning")

    # Pasamos los usuarios a la plantilla
    return render_template("ver_usuarios.html", usuarios=usuarios)

#----------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/sesiones', methods=["GET", "POST"])
def sesiones():
    conexion = crear_conexion()

    if request.method == "POST":
        # Captura de datos del formulario
        titulo = request.form["titulo"]
        descripcion = request.form["descripcion"]
        fecha = request.form["fecha"]
        hora_inicio = request.form["hora_inicio"]
        hora_fin = request.form["hora_fin"]
        id_conferencia = request.form["id_conferencia"]

        # Insertar en la base de datos
        cursor = conexion.cursor()
        query = """
        INSERT INTO sesion (titulo, descripcion, fecha, hora_inicio, hora_fin, id_conferencia)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (titulo, descripcion, fecha, hora_inicio, hora_fin, id_conferencia))
        conexion.commit()
        cursor.close()
        conexion.close()

        # Respuesta con redirección y alerta
        return jsonify({"success": True, "redirect": "/index"})

    else:
        # Obtener las conferencias disponibles
        cursor = conexion.cursor(dictionary=True)
        query = "SELECT id_conferencia, nombre FROM conferencia"
        cursor.execute(query)
        conferencias = cursor.fetchall()
        cursor.close()
        conexion.close()

        # Renderizar la plantilla de sesiones
    return render_template("sesiones.html", conferencias=conferencias)
