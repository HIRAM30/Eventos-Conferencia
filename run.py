import sqlite3
<<<<<<< HEAD
from flask import Flask, render_template, redirect, url_for, flash, session, jsonify, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from crud_usuario import insertar_usuario, obtener_usuario_por_nombre_usuario, obtener_usuario_por_id, enviar_email_restablecimiento, insertar_conferencia
=======
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
from flask_sqlalchemy import SQLAlchemy
from flask import jsonify
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
import pytz
from datetime import datetime, timedelta
from wtforms import StringField, TextAreaField, DateField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired
from crud_usuario import insertar_conferencia
from crud_usuario import actualizar_contraseña 
from crud_usuario import obtener_usuarios
from db_conector import crear_conexion
from config import mail
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Esta es tu clave secreta
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/conferencias'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'toral.carrera.yair@gmail.com'
app.config['MAIL_PASSWORD'] = 'urjz gweo uach kymn'
app.config['MAIL_DEFAULT_SENDER'] = 'toral.carrera.yair@gmail.com'
db = SQLAlchemy(app)
# Instancia de generador de tokens
serializer = URLSafeTimedSerializer(app.secret_key)
# Configuración de la app y login manager
login_manager = LoginManager()
login_manager.init_app(app)
# Configuración de Mail
mail.init_app(app)

# Define la ruta de inicio de sesión
login_manager.login_view = "login"
@login_manager.user_loader
def load_user(user_id):
    # Asegúrate de que esta función recupere el usuario según su ID
    return obtener_usuario_por_id(user_id)

@app.route('/api/user')
def api_user():
    if 'user_id' in session:
        return jsonify({
            'user_id': session['user_id'],
            'user_type': session['user_type']
        })
    else:
        return jsonify({'error': 'Usuario no autenticado'}), 401
#----------------------------------------------------------------------------------------------------------------------------------------------
# Definir el modelo User
class User(db.Model):
    __tablename__ = 'usuario'  # Nombre de la tabla en la base de datos

    id = db.Column(db.Integer, primary_key=True)  # Cambié 'id_usuario' por 'id'
    username = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    correo_electronico = db.Column(db.String(100), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Conferencia(db.Model):
    __tablename__ = 'conferencia'

    id_conferencia = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date, nullable=False)
    id_organizador = db.Column(db.Integer, db.ForeignKey('usuario.id'))

    sesiones = db.relationship('Sesion', backref='conferencia_rel', lazy=True)

class Sesion(db.Model):
    __tablename__ = 'sesion'

    id_sesion = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    id_conferencia = db.Column(db.Integer, db.ForeignKey('conferencia.id_conferencia'))

class Inscripcion(db.Model):
    __tablename__ = 'inscripcion'

    id_inscripcion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)  # Cambié 'id_usuario' a 'id'
    id_sesion = db.Column(db.Integer, db.ForeignKey('sesion.id_sesion'), nullable=False)

    usuario = db.relationship('User', backref='inscripciones')  # Cambié 'Usuario' a 'User'
    sesion = db.relationship('Sesion', backref='inscripciones')


#----------------------------------------------------------------------------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Ajusta esto a tu modelo de datos
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

<<<<<<< HEAD


#----------------------------------------------------------------------------------------------------------------------------------------------

from flask import Flask, request, render_template, redirect, url_for, session, flash
from werkzeug.security import check_password_hash

=======
>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre_usuario = request.form["correo"]
        contraseña = request.form["contraseña"]

        # Verificamos si el usuario existe
        usuario = obtener_usuario_por_nombre_usuario(nombre_usuario)  # Esta función debe devolver un dict o un objeto

        if usuario:
            # Comprobamos si la contraseña es correcta
<<<<<<< HEAD
            if 'id_usuario' in usuario:
                if check_password_hash(usuario['contraseña'], contraseña):
                    # Aquí usas el modelo User para crear el objeto
                    user = User(id=usuario['id_usuario'], username=usuario['correo_electronico'], user_type=usuario['tipo_usuario'])
                    
                    # Guardamos los datos del usuario en la sesión
                    session['user_id'] = user.id
                    session['user_type'] = user.user_type
                    print("ID de usuario guardado en la sesión:", session['user_id'])  # Depuración
=======
            if check_password_hash(usuario['contraseña'], contraseña):
                # Guardamos los datos del usuario en la sesión
                session['user_id'] = usuario['id_usuario']
                session['user_type'] = usuario['tipo_usuario']
>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6

                flash("Inicio de sesión exitoso", "success")

                    # Redirigir al tipo de usuario
<<<<<<< HEAD
                    if user.user_type == 'admin':
                        return redirect(url_for("admin"))  # Redirige al administrador
                    elif user.user_type == 'organizador':
                        return redirect(url_for("organizador"))  # Redirige al organizador
                    elif user.user_type == 'asistente':
                        return redirect(url_for("asistente"))  # Redirige al asistente
=======
                    if usuario['tipo_usuario'] == 'organizador':
                        return redirect(url_for("organizador"))  # Redirige al organizador
>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6
                    else:
                        return redirect(url_for("asistente"))  # Redirige al asistente

                else:
                    return redirect(url_for("asistente"))

            else:
                flash("Contraseña incorrecta", "error")
        else:
            flash("Usuario no encontrado", "error")

    return render_template("inicio_sesion.html")

<<<<<<< HEAD

#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
=======
#----------------------------------------------------------------------------------------------------------------------------------------------

>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6
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
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
@app.route('/index')
def index():
    return render_template("index.html")
#////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
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
<<<<<<< HEAD
#----------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/api/conferenias', methods=['GET'])
def get_conferencias():
    """ Devuelve las conferencias para la fecha proporcionada. """
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'error': 'Fecha no proporcionada'}), 400

    try:
        selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()

        filtered_conferences = [
            conferencias for conference in conferencias if conferencias["date"] == date_str
        ]
        return jsonify(filtered_conferences)

    except ValueError:
        return jsonify({'error': 'Formato de fecha no válido. Usa YYYY-MM-DD'}), 400
#---------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/api/events', methods=['GET'])
def get_events():
    date_filter = request.args.get('date')  # Fecha seleccionada
    if date_filter:
        filtered_events = [conf for conf in conferencias if conf["start"].startswith(date_filter)]
        return jsonify(filtered_events)
    return jsonify(conferencias)
#----------------------------------------------------------------------------------------------------------------------------------------------
# Ruta para obtener todas las sesiones

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Devuelve las sesiones asociadas a una conferencia, filtradas por ID de conferencia."""
    conference_id = request.args.get('conference_id')  # Obtener el ID de la conferencia desde los parámetros
    
    if not conference_id:
        return jsonify({'error': 'ID de conferencia no proporcionado'}), 400

    try:
        # Verificar conexión con la base de datos
        conexion = crear_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Consulta SQL para obtener las sesiones
        query = """
        SELECT 
            s.id_sesion AS id,
            s.titulo AS title,
            s.descripcion AS description,
            s.fecha AS start,
            s.hora_inicio AS start_time,
            s.hora_fin AS end_time,
            s.id_conferencia AS conference_id
        FROM sesion s
        WHERE s.id_conferencia = %s
        """
        
        cursor.execute(query, (conference_id,))
        sessions = cursor.fetchall()

        # Si no hay sesiones, devolver un mensaje adecuado
        if not sessions:
            return jsonify({'message': 'No se encontraron sesiones para esta conferencia.'}), 404
        
        # Ajustar el formato de fecha y hora
        for session in sessions:
            # Convertir fechas y horas a formato ISO 8601
            start_datetime = datetime.combine(session['start'], datetime.min.time())  # Iniciar con la fecha base
            start_datetime += session['start_time']  # Sumar la hora de inicio (timedelta)
            
            end_datetime = datetime.combine(session['start'], datetime.min.time())  # Iniciar con la fecha base
            end_datetime += session['end_time']  # Sumar la hora de fin (timedelta)
            
            session['start'] = start_datetime.isoformat()  # Convertir a cadena ISO
            session['end'] = end_datetime.isoformat()  # Convertir a cadena ISO

            # Convertir timedelta a segundos para evitar error de serialización JSON
            session['start_time'] = session['start_time'].total_seconds()  # Convertir a segundos
            session['end_time'] = session['end_time'].total_seconds()  # Convertir a segundos
        
        cursor.close()
        conexion.close()

        return jsonify(sessions)

    except Exception as e:
        # Capturar cualquier error de la base de datos y devolverlo como respuesta
        print(f"Error al obtener sesiones: {e}")
        return jsonify({'error': str(e)}), 500
    
    #---------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/api/conferences', methods=['GET'])
def get_conferences():
    try:
        # Conexión a la base de datos
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
        conferencias = cursor.fetchall()
        cursor.close()
        conexion.close()

        # Ajustar el formato de fecha
        for conferencia in conferencias:
            conferencia['start'] = conferencia['start'].isoformat()
            conferencia['end'] = conferencia['end'].isoformat() if conferencia['end'] else None

        return jsonify(conferencias)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
=======
>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6
#----------------------------------------------------------------------------------------------------------------------------------------------

    
   #--------------------------------------------------------------------------------------------------------------------------------------------- 
    
@app.route('/api/user/registrations', methods=['GET'])
def get_user_registrations():
    """Obtener las sesiones en las que un usuario está inscrito."""
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({'error': 'user_id es requerido'}), 400

    try:
        conexion = crear_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Consulta para obtener las sesiones a las que el usuario está inscrito
        query = """
        SELECT s.id_sesion, s.titulo, s.fecha, s.hora_inicio, s.hora_fin
        FROM sesion s
        INNER JOIN inscripcion i ON s.id_sesion = i.id_sesion
        WHERE i.id_usuario = %s
        """
        cursor.execute(query, (user_id,))
        registrations = cursor.fetchall()

        cursor.close()
        conexion.close()

        if not registrations:
            return jsonify({'message': 'No tienes inscripciones registradas.'}), 404

        return jsonify(registrations)

    except Exception as e:
        print(f"Error al obtener inscripciones: {e}")
        return jsonify({'error': str(e)}), 500
#---------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/conferencias', methods=['GET'])
def conferencias():
    return render_template("conferencias.html")
<<<<<<< HEAD
#----------------------------------------------------------------------------------------------------------------------------------------------
=======

>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6

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
<<<<<<< HEAD
=======

>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6
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
#---------------------------------------------------------------------------------------------------------------------------------------------
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
<<<<<<< HEAD
@app.route("/recover", methods=["POST"])
def recover():
    correo = request.form["correo_electronico"]
    
    # Aquí va tu lógica para generar un token y enviar el correo
    msg = Message('Recuperar contraseña', sender='tu_correo@dominio.com', recipients=[correo])
    msg.body = 'Este es el correo de recuperación de contraseña.'
    
    # Usamos el objeto 'mail' para enviar el correo
    mail.send(msg)
    flash("Correo de recuperación enviado", "success")
    return redirect(url_for('login'))
#----------------------------------------------------------------------------------------------------------------------------------------------
=======

>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6
@app.route('/logout')
def logout():
    session.clear()  # Limpiar todos los datos de la sesión
    flash("Has cerrado sesión exitosamente", "success")
<<<<<<< HEAD

    # Redirige al login después de cerrar sesión
    return redirect(url_for("login"))  # Redirige al login
=======
    return redirect(url_for("login"))

>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6
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
    
<<<<<<< HEAD
    return render_template("index.html")  # Página principal del organizador
#---------------------------------------------------------------------------------------------------------------------------------------------
=======
    return render_template("index.html")

#----------------------------------------------------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------------------------------------------------------

>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6
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
<<<<<<< HEAD
@app.route('/admin/editar_usuario/<int:id_usuario>', methods=['GET', 'POST'])
def editar_usuario(id_usuario):
    # Verificamos si el usuario está autenticado y es un administrador
    if 'user_id' not in session or session['user_type'] != 'admin':
        flash("Acceso no autorizado", "error")
        return redirect(url_for("login"))

    # Obtener los datos del usuario a editar
=======
@app.route('/sesiones', methods=["GET", "POST"])
def sesiones():
>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6
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

<<<<<<< HEAD
    return render_template("editar_usuario.html", usuario=usuario)
#---------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/admin/eliminar_usuario/<int:id_usuario>', methods=['GET'])
def eliminar_usuario(id_usuario):
    # Verificamos si el usuario está autenticado y es un administrador
    if 'user_id' not in session or session['user_type'] != 'admin':
        flash("Acceso no autorizado", "error")
        return redirect(url_for("login"))

    # Eliminar el usuario de la base de datos
    conexion = crear_conexion()
    cursor = conexion.cursor()
    query = "DELETE FROM usuario WHERE id_usuario = %s"
    cursor.execute(query, (id_usuario,))
    conexion.commit()
    cursor.close()
    conexion.close()

    flash("Usuario eliminado exitosamente", "success")
    return redirect(url_for('ver_usuarios_admin'))
#----------------------------------------------------------------------------------------------------------------------------------------------
# Formulario para agregar sesión
class SesionForm(FlaskForm):
    titulo = StringField('Título de la sesión', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    fecha = DateField('Fecha', validators=[DataRequired()])
    hora_inicio = TimeField('Hora de inicio', validators=[DataRequired()])
    hora_fin = TimeField('Hora de fin', validators=[DataRequired()])
    conferencia = SelectField('Conferencia Asociada', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar Sesión')
#----------------------------------------------------------------------------------------------------------------------------------------------
# Ruta para agregar sesión
@app.route('/sesiones', methods=['GET', 'POST'])
def agregar_sesion():
    # Conexión y consulta de conferencias
    conexion = crear_conexion()
    cursor = conexion.cursor(dictionary=True)
    cursor.execute("SELECT id_conferencia, nombre FROM conferencia")
    conferencias = cursor.fetchall()
    cursor.close()
    conexion.close()

    # Inicializar formulario
    form = SesionForm()

    # Llenar el campo de conferencia con las opciones obtenidas
    form.conferencia.choices = [(conferencia['id_conferencia'], conferencia['nombre']) for conferencia in conferencias]

    # Si el formulario es enviado
    if form.validate_on_submit():
        titulo = form.titulo.data
        descripcion = form.descripcion.data
        fecha = form.fecha.data
        hora_inicio = form.hora_inicio.data
        hora_fin = form.hora_fin.data
        id_conferencia = form.conferencia.data

        # Guardar la sesión en la base de datos
        conexion = crear_conexion()
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO sesion (titulo, descripcion, fecha, hora_inicio, hora_fin, id_conferencia)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (titulo, descripcion, fecha, hora_inicio, hora_fin, id_conferencia))
        conexion.commit()
        cursor.close()
        conexion.close()

        # Redirigir a la misma página después de agregar la sesión
        return redirect(url_for('agregar_sesion'))

    return render_template('sesiones.html', form=form)


class CrearConferenciaForm(FlaskForm):
    nombre = StringField('Nombre de la conferencia', validators=[DataRequired()])
    descripcion = TextAreaField('Descripción', validators=[DataRequired()])
    fecha_inicio = DateField('Fecha de inicio', validators=[DataRequired()])
    fecha_fin = DateField('Fecha de fin', validators=[DataRequired()])
#---------------------------------------------------------------------------------------------------------------------------------------------
@app.route('/conferencia2', methods=['GET', 'POST'])
def conferencia2():
    # Inicializamos el formulario
    form = CrearConferenciaForm()

    # Si el formulario es enviado y validado
    if form.validate_on_submit():
        nombre = form.nombre.data
        descripcion = form.descripcion.data
        fecha_inicio = form.fecha_inicio.data
        fecha_fin = form.fecha_fin.data

        # Obtenemos el ID del usuario desde la sesión
        id_usuario = session['user_id']

        # Insertamos la conferencia en la base de datos (función de inserción)
        resultado = insertar_conferencia(nombre, descripcion, fecha_inicio, fecha_fin, id_usuario)

        # Comprobamos si la inserción fue exitosa
        if resultado:
            flash("Conferencia creada exitosamente", "success")
            # Verificamos el tipo de usuario
            tipo_usuario = session.get('tipo_usuario')  # Asumiendo que el tipo de usuario está en la sesión
            if tipo_usuario == 'administrador':
                # Redirige a la página del administrador
                return redirect(url_for("index_admin"))
            elif tipo_usuario == 'organizador':
                # Redirige a la página del organizador
                return redirect(url_for("organizador"))
            else:
                # Redirige a la página del usuario
                return redirect(url_for("index"))
        else:
            flash("Hubo un error al crear la conferencia", "error")
    
    # Si no es una solicitud de POST o el formulario no es válido, se renderiza el formulario
    return render_template("crear_conferencia.html", form=form)



@app.route('/api/inscribe', methods=['POST'])
def inscribe():
    try:
        # Obtener los datos enviados por el cliente
        data = request.get_json()
        print("Datos recibidos en el backend:", data)

        if not data:
            return jsonify({"error": "No se recibieron datos"}), 400

        id_usuario = data.get('id_usuario')
        id_sesion = data.get('id_sesion')

        # Validar los datos
        if not id_usuario or not id_sesion:
            print(f"Datos incompletos: id_usuario={id_usuario}, id_sesion={id_sesion}")
            return jsonify({"error": "Faltan datos necesarios"}), 400
        
        # Comprobar si el usuario ya está inscrito en la sesión
        existing_inscription = Inscripcion.query.filter_by(id_usuario=id_usuario, id_sesion=id_sesion).first()

        if existing_inscription:
            return jsonify({'message': 'Ya estás inscrito en esta sesión.'}), 400

        # Crear inscripción
        nueva_inscripcion = Inscripcion(id_usuario=id_usuario, id_sesion=id_sesion)
        db.session.add(nueva_inscripcion)
        db.session.commit()

        return jsonify({"message": "Inscripción exitosa"}), 200

    except Exception as e:
        print(f"Error en el backend: {e}")
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    app.run(debug=True)
=======
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
>>>>>>> 2dc8fa7f8231c61cc1be7cac096e0d361c1f3ae6
