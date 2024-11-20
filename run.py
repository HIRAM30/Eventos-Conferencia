from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from crud_usuario import insertar_usuario, obtener_usuario_por_nombre_usuario
from werkzeug.security import check_password_hash
from db_conector import crear_conexion

app = Flask(__name__)
app.secret_key = "clave_secreta"
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tu_contraseña@localhost/conferencias'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nombre_usuario = request.form["correo"]
        contraseña = request.form["contraseña"]

        usuario = obtener_usuario_por_nombre_usuario(nombre_usuario)
        if usuario:
            if check_password_hash(usuario['contraseña'], contraseña):
                flash("Inicio de sesión exitoso", "success")
                return redirect(url_for("index"))
            else:
                flash("Contraseña incorrecta", "error")
        else:
            flash("Usuario no encontrado", "error")
        return redirect(url_for("login"))

    return render_template("inicio_sesion.html")


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


@app.route('/index')
def index():
    return render_template("index.html")


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


@app.route('/conferencias', methods=['GET'])
def conferencias():
    return render_template("conferencias.html")


if __name__ == "__main__":
    app.run(debug=True)
