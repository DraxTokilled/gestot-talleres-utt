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
        matricula = request.form["matricula"]
        nombre = request.form["nombre"]
        apellido_p = request.form["apellido_p"]
        apellido_m = request.form["apellido_m"]
        carrera = request.form['carrera']
        genero = request.form["genero"]
        edad = request.form["edad"]
        nss = request.form["nss"]
        grado_grupo = request.form["grado_grupo"]
        telefono = request.form["telefono"]
        tutor = request.form["tutor"]
        telefono_emergencia = request.form["telefono_emergencia"]
        correo = request.form["correo"]
        taller_inscripcion = request.form["taller_inscripcion"]
        horario = request.form["horario"]
        contrasena = request.form["contrasena"]
        confirmar = request.form["confirmar"]
        foto = request.files["foto_credencial"] #Esto es un archivo

        if foto and foto.filename != '':
            foto.save(os.path.join("ruta/a/carpeta", secure_filename(foto.filename)))
            ruta_foto = secure_filename(foto.filename)
        else:
            ruta_foto = None


        if contrasena != confirmar:
            return "Las contraseñas no coinciden"

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM estudiante WHERE Correo = %s", (correo,))
        existente = cursor.fetchone()

        if existente:
            return "El correo ya está registrado"

        cursor.execute("""
            INSERT INTO estudiante (
                Matricula, Nombre, Apellido_P, Apellido_M, Carrera, Genero, Edad, 
                NSS, Grado_Grupo, Telefono, Tutor, Telefono_Emergencia, Correo, Taller_Inscripcion, 
                Horario, Contraseña, Foto_Credencial
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            matricula, nombre, apellido_p, apellido_m, carrera, genero, edad, nss, grado_grupo,
            telefono, tutor, telefono_emergencia, correo, taller_inscripcion, horario, contrasena,
            ruta_foto
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

@app.route('/taller')
def taller():
    return render_template('taller.html')

@app.route('/taller1')
def taller1():
    return render_template('taller1.html')

@app.route('/taller2')
def taller2():
    return render_template('taller2.html')

@app.route('/taller3')
def taller3():
    return render_template('taller3.html')

@app.route('/taller4')
def taller4():
    return render_template('taller4.html')

@app.route('/taller5')
def taller5():
    return render_template('taller5.html')

@app.route('/taller6')
def taller6():
    return render_template('taller6.html')

@app.route('/taller7')
def taller7():
    return render_template('taller7.html')

@app.route('/taller8')
def taller8():
    return render_template('taller8.html')

if __name__ == '__main__':
    app.run(debug=True)