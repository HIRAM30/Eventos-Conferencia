from flask import Flask, render_template, request, redirect, url_for, flash
from crud_usuario import insertar_usuario, obtener_usuario_por_nombre_usuario  # Importamos las funciones CRUD
from werkzeug.security import check_password_hash  # Para verificar las contraseñas

app = Flask(__name__)
app.secret_key = "clave_secreta"  # Necesaria para usar flash y mensajes

@app.route('/')
def home():
    return render_template("home.html")  # Página de inicio con el botón de "Empezar"

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Recibimos los datos del formulario
        nombre_usuario = request.form["correo"]  # Lo tratamos como nombre de usuario
        contraseña = request.form["contraseña"]

        # Verificamos si el usuario existe
        usuario = obtener_usuario_por_nombre_usuario(nombre_usuario)
        
        if usuario:
            # Comparamos la contraseña ingresada con la almacenada (hashed)
            if check_password_hash(usuario['contraseña'], contraseña):
                flash("Inicio de sesión exitoso", "success")
                return redirect(url_for("home"))  # Redirige a la página de inicio
            else:
                flash("Contraseña incorrecta", "error")
        else:
            flash("Usuario no encontrado", "error")

        return redirect(url_for("login"))  # Redirige al formulario de login si hubo error

    return render_template("inicio_sesion.html")  # Página de inicio de sesión

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

if __name__ == "__main__":
    app.run(debug=True)
