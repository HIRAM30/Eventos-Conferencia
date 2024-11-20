from flask import Flask, render_template, request, redirect, url_for, flash, session  # Importamos session
from crud_usuario import insertar_usuario, obtener_usuario_por_nombre_usuario  # Importamos las funciones CRUD
from werkzeug.security import check_password_hash  # Para verificar las contraseñas

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Necesaria para usar flash y mensajes

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

@app.route('/index')
def index():
    # Verificamos si el usuario está autenticado
    if 'user_id' not in session:  # Si no hay una sesión activa
        flash("Por favor inicia sesión primero", "error")
        return redirect(url_for("login"))  # Redirige al login si no está autenticado
    return render_template("index.html", user_name=session.get('user_name'))  # Pasamos el nombre del usuario

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/login', methods=["GET", "POST"])
def login():
    if 'user_id' in session:  # Si ya está autenticado, redirige a la página de inicio
        return redirect(url_for("index"))

    if request.method == "POST":
        # Recibimos los datos del formulario
        nombre_usuario = request.form["correo"]  # Lo tratamos como nombre de usuario
        contraseña = request.form["contraseña"]

        # Verificamos si el usuario existe
        usuario = obtener_usuario_por_nombre_usuario(nombre_usuario)
        
        if usuario:
            # Comprobamos si la contraseña es correcta
            if check_password_hash(usuario['contraseña'], contraseña):
                # Guardamos los datos del usuario en la sesión
                session['user_id'] = usuario.get('id_usuario')
                session['user_name'] = usuario.get('nombre_usuario')
                session['user_type'] = usuario.get('tipo_usuario')

                # Mensaje de éxito
                flash("Inicio de sesión exitoso", "success")

                # Redirigir al tipo de usuario
                if session['user_type'] == 'organizador':
                    return redirect(url_for("organizador"))  # Redirige al organizador
                else:
                    return redirect(url_for("asistente"))  # Redirige al asistente

            else:
                flash("Contraseña incorrecta", "error")
        else:
            flash("Usuario no encontrado", "error")

        return redirect(url_for("login"))  # Redirige al formulario de login si hubo error

    return render_template("inicio_sesion.html")  # Página de inicio de sesión

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/registro_usuario', methods=["GET", "POST"])
def registro_usuario():
    if request.method == "POST":
        # Recibimos los datos del formulario
        nombre_usuario = request.form["nombre_usuario"]
        correo_electronico = request.form["correo_electronico"]
        contraseña = request.form["contraseña"]
        confirmar_contraseña = request.form["confirmar"]
        tipo_usuario = request.form["tipo_usuario"]  # Obtienes el valor 'asistente'

        # Verificar si las contraseñas coinciden
        if contraseña != confirmar_contraseña:
            flash("Las contraseñas no coinciden", "error")
            return redirect(url_for("registro_usuario"))

        # Usamos la función CRUD para insertar el usuario
        resultado = insertar_usuario(nombre_usuario, correo_electronico, contraseña, tipo_usuario)

        if "exitosamente" in resultado:
            flash("Usuario registrado exitosamente", "success")
            return redirect(url_for("login"))  # Redirigir al login
        else:
            flash(resultado, "error")
            return redirect(url_for("registro_usuario"))

    return render_template("registro_usuario.html")  # Página del formulario de registro

#----------------------------------------------------------------------------------------------------------------------------------------------

@app.route('/perfil')
def perfil():
    # Verificamos si el usuario está autenticado
    if 'user_id' not in session:
        flash("Por favor, inicia sesión primero", "error")
        return redirect(url_for("login"))
    
    # Obtener los datos del usuario desde la sesión
    usuario = {
        'nombre_usuario': session.get('user_name'),
        'correo_electronico': session.get('correo_electronico'),  # Debes agregar esto cuando guardes la información en la sesión
        'tipo_usuario': session.get('user_type')
    }
    
    return render_template("perfil.html", usuario=usuario)


def obtener_usuario_por_id(user_id):
    # Suponiendo que usas SQLite, ajusta la conexión a tu base de datos
    conn = sqlite3.connect('basededatos.db')
    cursor = conn.cursor()

    query = "SELECT nombre_usuario, correo_electronico, tipo_usuario FROM usuarios WHERE id_usuario = ?"
    cursor.execute(query, (user_id,))
    usuario = cursor.fetchone()

    conn.close()

    if usuario:
        return {
            'nombre_usuario': usuario[0],
            'correo_electronico': usuario[1],
            'tipo_usuario': usuario[2]
        }
    else:
        return None


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