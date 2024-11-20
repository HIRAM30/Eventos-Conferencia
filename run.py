
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from crud_usuario import insertar_usuario, obtener_usuario_por_nombre_usuario, obtener_usuario_por_id, enviar_email_restablecimiento
from werkzeug.security import check_password_hash
from crud_usuario import actualizar_contraseña 
from db_conector import crear_conexion
from config import mail
from itsdangerous import URLSafeTimedSerializer

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Esta es tu clave secreta
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tu_contraseña@localhost/conferencias'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Usa el puerto 587 para TLS o 465 para SSL
app.config['MAIL_USE_TLS'] = True  # Habilita TLS
app.config['MAIL_USE_SSL'] = False  # Asegúrate de que SSL está deshabilitado si usas TLS
app.config['MAIL_USERNAME'] = 'toral.carrera.yair@gmail.com'  # Tu dirección de correo de Gmail
app.config['MAIL_PASSWORD'] = 'urjz gweo uach kymn'  # Contraseña de Gmail o contraseña de aplicación
app.config['MAIL_DEFAULT_SENDER'] = 'toral.carrera.yair@gmail.com'

# Instancia de generador de tokens
serializer = URLSafeTimedSerializer(app.secret_key)

# Configuración de Mail
mail.init_app(app)

#----------------------------------------------------------------------------------------------------------------------------------------------

# Ruta para enviar un correo
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
        # Si ya está autenticado, redirigimos al dashboard correspondiente
        if session['user_type'] == 'organizador':
            return redirect(url_for('organizador'))
        elif session['user_type'] == 'asistente':
            return redirect(url_for('asistente'))
    
    # Si no está autenticado, mostramos la página home con el botón "Empezar"
    return render_template("home.html")  # Página de inicio con el botón de "Empezar"
# Evitar que las páginas se almacenen en caché

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.after_request
def no_cache(response):
    response.cache_control.no_store = True  # Evita que la página se almacene en caché
    response.headers['Pragma'] = 'no-cache'  # Esto también ayuda con navegadores antiguos
    response.headers['Expires'] = '0'  # Previene la caché de contenido viejo
    return response

#----------------------------------------------------------------------------------------------------------------------------------------------



#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Recibimos los datos del formulario
        nombre_usuario = request.form["correo"]  # Lo tratamos como nombre de usuario
        contraseña = request.form["contraseña"]

        # Verificamos si el usuario existe
        usuario = obtener_usuario_por_nombre_usuario(nombre_usuario)

        if usuario:
            # Mostrar en consola el usuario obtenido para depuración
            print("Usuario obtenido:", usuario)  # Verificamos qué contiene 'usuario'

            # Comprobamos si la contraseña es correcta
            if 'id_usuario' in usuario:
                if check_password_hash(usuario['contraseña'], contraseña):
                    # Guardamos los datos del usuario en la sesión
                    session['user_id'] = usuario['id_usuario']
                    session['user_type'] = usuario['tipo_usuario']
                    print("ID de usuario guardado en la sesión:", session['user_id'])  # Depuración

                    # Mensaje de éxito
                    flash("Inicio de sesión exitoso", "success")

                    # Redirigir al tipo de usuario
                    if usuario['tipo_usuario'] == 'organizador':
                        return redirect(url_for("organizador"))  # Redirige al organizador
                    else:
                        return redirect(url_for("asistente"))  # Redirige al asistente

                else:
                    print("Contraseña incorrecta")
                    flash("Contraseña incorrecta", "error")
            else:
                print("No se encontró 'id_usuario' en el usuario")
                flash("Usuario mal formado", "error")
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
    # Verificamos si el usuario está autenticado
    if 'user_id' not in session:
        flash("Por favor, inicia sesión primero", "error")
        return redirect(url_for("login"))

    # Verificar si 'user_id' está en la sesión
    print("User ID en la sesión:", session.get('user_id'))  # Depuración
    
    # Obtener el ID del usuario desde la sesión
    user_id = session['user_id']
    
    # Consultar los datos del usuario en la base de datos
    usuario = obtener_usuario_por_id(user_id)
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
        correo_electronico = serializer.loads(token, salt="reset-password", max_age=3600)  # 1 hora de validez
    except Exception as e:
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

@app.route('/logout')
def logout():
    # Elimina todos los datos de la sesión
    session.clear()  # Esto limpia todos los datos de la sesión

    # Mensaje flash para indicar que el usuario cerró sesión
    flash("Has cerrado sesión exitosamente", "success")

    # Redirige al login después de cerrar sesión
    return redirect(url_for("login"))  # Redirige al login

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/asistente')
def asistente():
    # Verificamos si el usuario está autenticado
    if 'user_id' not in session or session['user_type'] != 'asistente':  # Verificamos que sea un asistente
        flash("Acceso no autorizado", "error")
        return redirect(url_for("login"))
    
    return render_template("index_asistente.html")  # Página principal del asistente

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/organizador')
def organizador():
    # Verificamos si el usuario está autenticado
    if 'user_id' not in session or session['user_type'] != 'organizador':  # Verificamos que sea un organizador
        flash("Acceso no autorizado", "error")
        return redirect(url_for("login"))
    
    return render_template("index.html")  # Página principal del organizador

if __name__ == "__main__":
    app.run(debug=True)

#----------------------------------------------------------------------------------------------------------------------------------------------