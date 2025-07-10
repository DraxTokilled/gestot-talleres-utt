from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gestor_talleres'

mysql = MySQL(app)

# Página de inicio
@app.route("/")
def index():
    return render_template("index.html")

# Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM estudiante WHERE Correo = %s AND Contraseña = %s", (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session["usuario"] = user[1]     # Nombre
            session["sexo"] = user[11]       # Sexo (columna 12 de la tabla estudiante)
            return redirect(url_for("dashboard"))
        else:
            return "Credenciales incorrectas"
    return render_template("login.html")

# Dashboard personalizado
@app.route("/dashboard")
def dashboard():
    if "usuario" in session:
        return render_template("dashboard.html")
    return redirect(url_for("login"))

# Registro
@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre = request.form["nombre"]
        carrera = request.form['carrera']
        apellido_p = request.form["apellido_p"]
        apellido_m = request.form["apellido_m"]
        sexo = request.form["sexo"]
        matricula = request.form["matricula"]
        correo = request.form["correo"]
        telefono = request.form["telefono"]
        edad = request.form["edad"]
        grado_grupo = request.form["grado_grupo"]
        contrasena = request.form["contrasena"]
        confirmar = request.form["confirmar"]

        if contrasena != confirmar:
            return "Las contraseñas no coinciden"

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM estudiante WHERE Correo = %s", (correo,))
        existente = cursor.fetchone()

        if existente:
            return "El correo ya está registrado"

        cursor.execute("""
            INSERT INTO estudiante (
                Nombre, Apellido_P, Apellido_M, Matricula, Correo,
                Telefono, Edad, Grado_Grupo, Carrera, Contraseña, Sexo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            nombre, apellido_p, apellido_m, matricula, correo,
            telefono, edad, grado_grupo, carrera, contrasena, sexo
        ))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("login"))
    return render_template("registro.html")

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)
