from flask import Flask, flash, render_template, request, redirect, url_for, session
import os
import json
from datetime import datetime
from werkzeug.utils import secure_filename
from flask_mysqldb import MySQL
app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

# Configuración de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'gestor_talleres'

mysql = MySQL(app)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
            session["usuario"] = email  # Necesario para validar sesión en dashboard
            session["nombre"] = user[2]  # Nombre (columna 2)
            session["genero"] = user[6]  # Género (columna 6)
            return redirect(url_for("dashboard"))
        else:
            return "Credenciales incorrectas"
    return render_template("login.html")

# Dashboard
@app.route("/dashboard")
def dashboard():
    if "usuario" in session:
        return render_template("dashboard.html")
    return redirect(url_for("login"))

#Consultas 
@app.route('/consultar', methods=['GET', 'POST'])
def consultar():
    resultados = []

    if request.method == 'POST':
        tipo = request.form['tipo']
        busqueda = request.form['busqueda']

        cur = mysql.connection.cursor()

        if tipo == 'estudiante':
            query = "SELECT Nombre, Apellido_P, Apellido_M, Matricula FROM estudiante WHERE Nombre LIKE %s OR Matricula LIKE %s"
        elif tipo == 'docente':
            query = "SELECT Nombre_D, Apellido_P_D, Apellido_M_D, Matricula_Docente FROM docentes WHERE Nombre_D LIKE %s OR Matricula_Docente LIKE %s"
        elif tipo == 'taller':
            query = "SELECT Nombre_T, Nombre_D FROM taller WHERE Nombre_T LIKE %s OR Nombre_D LIKE %s"
        else:
            query = ""

        if query:
            cur.execute(query, (f"%{busqueda}%", f"%{busqueda}%"))
            resultados = cur.fetchall()

        cur.close()

    return render_template('consultar.html', resultados=resultados)


#Registro Taller
@app.route("/registroTaller", methods=["GET", "POST"])
def registroTaller():
    errors = {}

    if request.method == "POST":
        Nombre_T = request.form.get('Nombre_T')
        Nombre_D = request.form["Nombre_D"]
        dias_t = request.form.getlist("dias_t[]")  # lista de días
        dias_unidos = ",".join(dias_t)  # ejemplo: "Lunes,Miércoles,Viernes"

        # Crear JSON de horarios por día
        horarios = {}
        for dia in dias_t:
            inicio = request.form.get(f"horario_{dia}_inicio")
            fin = request.form.get(f"horario_{dia}_fin")
            if inicio and fin:
                horarios[dia] = f"{inicio}-{fin}"

        estatus = request.form.get('estatus')
        # Validaciones
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM taller WHERE Nombre_T = %s", (Nombre_T,))
        if cursor.fetchone():
            errors['Nombre_T'] = "El taller ya está registrado."

        if errors:
            return render_template("registroTaller.html", errors=errors, form_data=request.form)
        
        # Insertar en la base de datos
        cursor.execute("""
            INSERT INTO taller (
                Nombre_T, Nombre_D, Dias_T, Horarios, Estatus
            ) VALUES (%s, %s, %s, %s, %s)
        """, (
            Nombre_T, Nombre_D, dias_unidos, json.dumps(horarios), estatus))
        
        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("login"))
    return render_template('registroTaller.html', form_data={})

@app.route("/editarTaller/<int:idTaller>", methods=["GET", "POST"])
def editarTaller(idTaller):
    cursor = mysql.connection.cursor()

    # Buscar taller por ID
    cursor.execute("SELECT * FROM taller WHERE Id_Taller = %s", (idTaller,))
    taller = cursor.fetchone()

    if not taller:
        cursor.close()
        return "Taller no encontrado", 404

    # Mapear resultados a diccionario
    columnas = [desc[0] for desc in cursor.description]
    datos = dict(zip(columnas, taller))
    cursor.close()

    # Normalizar valores para renderizar HTML correctamente
    estatus_original = datos["Estatus"] if datos["Estatus"] is not None else ""
    estado = ""
    if estatus_original.lower().startswith("a"):  # Activo
        estado = "A"
    elif estatus_original.lower().startswith("b"):  # Baja
        estado = "B"
    else:
        estado = "BT"  # Baja temporal

    datos["Estatus"] = estado

    # Convertir los días seleccionados en una lista
    dias_seleccionados = datos.get("Dias_Taller", "").split(',') if datos.get("Dias_Taller") else []
    
    # Convertir los horarios
    horarios = {}
    for dia in dias_seleccionados:
        horarios[dia] = {
            'inicio': datos.get(f'Horario_{dia}_inicio', ''),
            'fin': datos.get(f'Horario_{dia}_fin', '')
        }

    if request.method == "POST":
        # Obtener datos del formulario
        nombre_T = request.form["nombre_T"]
        nombre_D = request.form["nombre_D"]
        dias_t = request.form.getlist("dias_t[]")
        estado = request.form["estado"]
        
        # Crear diccionario de horarios
        horarios = {}
        for dia in dias_t:
            horarios[dia] = {
                'inicio': request.form[f'horario_{dia}_inicio'],
                'fin': request.form[f'horario_{dia}_fin']
            }

        # Actualizar datos del taller en la base de datos
        cursor = mysql.connection.cursor()

        cursor.execute("""
            UPDATE taller
            SET Nombre_T=%s, Nombre_D=%s, Dias_T=%s, Estatus=%s
            WHERE Id_Taller=%s
        """, (
            nombre_T, nombre_D, ','.join(dias_t), estado, idTaller
        ))

        # Actualizar horarios dinámicamente
        for dia, horario in horarios.items():
            cursor.execute(f"""
                UPDATE taller
                SET Horario_{dia}_inicio=%s, Horario_{dia}_fin=%s
                WHERE Id_Taller=%s
            """, (horario['inicio'], horario['fin'], idTaller))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("dashboard"))  # Cambia según tu vista de destino

    return render_template("editarTaller.html", datos=datos, dias_seleccionados=dias_seleccionados, horarios=horarios)
# Registro Alumno
@app.route("/registro", methods=["GET", "POST"])
def registro():
    errors = {}

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
        foto = request.files["foto_credencial"]

        # Validaciones
        if contrasena != confirmar:
            errors['contrasena'] = "Las contraseñas no coinciden."

        cursor = mysql.connection.cursor()

        cursor.execute("SELECT * FROM estudiante WHERE Correo = %s", (correo,))
        if cursor.fetchone():
            errors['correo'] = "El correo ya está registrado."

        cursor.execute("SELECT * FROM estudiante WHERE Matricula = %s", (matricula,))
        if cursor.fetchone():
            errors['matricula'] = "La matrícula ya está registrada."

        cursor.execute("SELECT * FROM estudiante WHERE NSS = %s", (nss,))
        if cursor.fetchone():
            errors['nss'] = "El NSS ya está registrado."

        if errors:
            return render_template("registro.html", errors=errors, form_data=request.form)

        # Guardar imagen si existe
        if foto and foto.filename != '':
            carpeta_fotos = os.path.join("static", "fotos")
            os.makedirs(carpeta_fotos, exist_ok=True)
            ruta_foto = secure_filename(foto.filename)
            foto.save(os.path.join(carpeta_fotos, ruta_foto))
        else:
            ruta_foto = None

        # Insertar en la base de datos
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
    return render_template('registro.html', form_data={})
# Editar Alumno
@app.route("/editarAlumno/<matricula>", methods=["GET", "POST"])
def editar(matricula):
    cursor = mysql.connection.cursor()

    # Buscar alumno por matrícula
    cursor.execute("SELECT * FROM estudiante WHERE Matricula = %s", (matricula,))
    alumno = cursor.fetchone()

    if not alumno:
        cursor.close()
        return "Alumno no encontrado", 404

    # Mapear resultados a diccionario
    columnas = [desc[0] for desc in cursor.description]
    datos = dict(zip(columnas, alumno))
    cursor.close()

    # Horarios disponibles por taller
    horarios_taller = {
        'voleibol': ["Martes 14:00-17:00", "Jueves 14:00-16:00"],
        'futbol7': ["Lunes 14:00-17:00"],
        'futbolS': ["Martes 15:00-17:00", "Jueves 15:00-17:00"],
        'escolta': ["Martes 14:00-15:00", "Jueves 14:00-15:00"],
        'beisbol': ["Miércoles 14:00-16:00"],
        'atletismo': ["Lunes 16:00-17:00", "Martes 16:00-17:00"],
        'basquetbol': ["Lunes 13:00-16:00", "Martes 13:00-16:00"],
        'ajedrezC': ["Miércoles 14:00-17:00"],
        'ajedrezR': ["Martes 14:00-17:00", "Jueves 14:00-17:00"],
        'danza': ["Martes 13:00-14:30", "Viernes 13:00-14:30"],
        'porristas': ["Martes 14:30-16:00", "Viernes 14:30-16:00"],
        'banda_guerra': ["Miércoles 14:00-17:00", "Viernes 14:00-17:00"]
    }

    # Normalizar valores para renderizar HTML correctamente
    genero_original = datos["Genero"]
    genero = ""
    if genero_original.lower().startswith("h"):  # Hombre
        genero = "H"
    elif genero_original.lower().startswith("m"):  # Mujer
        genero = "M"
    else:
        genero = "LGBTQ"

    datos["Genero"] = genero

    datos["Taller_Inscripcion"] = datos.get("Taller_Inscripcion", "").strip().lower()
    datos["Horario"] = datos.get("Horario", "").strip()
    datos["horarios_disponibles"] = horarios_taller.get(datos["Taller_Inscripcion"], [])

    if request.method == "POST":
        # Obtener datos del formulario
        nombre = request.form["nombre"]
        apellido_p = request.form["apellido_p"]
        apellido_m = request.form["apellido_m"]
        carrera = request.form["carrera"]
        genero = request.form["genero"]
        edad = request.form["edad"]
        grado_grupo = request.form["grado_grupo"]
        telefono = request.form["telefono"]
        tutor = request.form["tutor"]
        telefono_emergencia = request.form["telefono_emergencia"]
        taller_inscripcion = request.form["taller_inscripcion"]
        horario = request.form["horario"]
        foto = request.files["foto_credencial"]

        cursor = mysql.connection.cursor()

        # Actualizar datos en la BD
        cursor.execute("""
            UPDATE estudiante
            SET Nombre=%s, Apellido_P=%s, Apellido_M=%s, Carrera=%s, Genero=%s, Edad=%s,
                Grado_Grupo=%s, Telefono=%s, Tutor=%s, Telefono_Emergencia=%s,
                Taller_Inscripcion=%s, Horario=%s
            WHERE Matricula=%s
        """, (
            nombre, apellido_p, apellido_m, carrera, genero, edad,
            grado_grupo, telefono, tutor, telefono_emergencia,
            taller_inscripcion, horario, matricula
        ))

        # Ruta para guardar las fotos
        carpeta_fotos = os.path.join("static", "fotos")
        os.makedirs(carpeta_fotos, exist_ok=True)

        # Verificar si se subió una nueva foto
        if 'foto_credencial' in request.files:
            foto = request.files['foto_credencial']
            if foto and allowed_file(foto.filename):
                # Nombre único para la nueva imagen
                ruta_foto = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(foto.filename)}"
                foto.save(os.path.join(carpeta_fotos, ruta_foto))

                # Eliminar foto anterior si existe
                if datos.get("Foto_Credencial"):
                    ruta_antigua = os.path.join(carpeta_fotos, datos["Foto_Credencial"])
                    if os.path.exists(ruta_antigua):
                        os.remove(ruta_antigua)

                # Actualizar en base de datos
                cursor.execute(
                    "UPDATE estudiante SET Foto_Credencial=%s WHERE Matricula=%s",
                    (ruta_foto, matricula)
                )
                flash("Foto de credencial actualizada con éxito.")
            elif foto.filename != '':
                flash("Archivo no permitido. Usa una imagen PNG, JPG, JPEG o GIF.")

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("dashboard"))

    return render_template("editarAlumno.html", datos=datos)

#Registro Docente
@app.route("/registroDocente", methods=["GET", "POST"])
def registroDocente():
    errors = {}

    if request.method == "POST":
        matriculaD = request.form["matriculaD"]
        nombreD = request.form["nombreD"]
        apellido_p_D = request.form["apellido_p_D"]
        apellido_m_D = request.form["apellido_m_D"]
        correo_D = request.form["correo_D"]
        cedula_profesional = request.form["cedula_profesional"]
        taller_impartir = request.form["taller_impartir"]
        foto = request.files["foto_credencialD"]

        # Validaciones
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM docentes WHERE Correo_D = %s", (correo_D,))
        if cursor.fetchone():
            errors['correo_D'] = "El correo ya está registrado."

        cursor.execute("SELECT * FROM docentes WHERE Matricula_Docente = %s", (matriculaD,))
        if cursor.fetchone():
            errors['matriculaD'] = "La matrícula ya está registrada."

        cursor.execute("SELECT * FROM docentes WHERE Cedula_P_D = %s", (cedula_profesional,))
        if cursor.fetchone():
            errors['cedula_profesional'] = "La cédula ya está registrada."

        if errors:
            return render_template("registroDocentes.html", errors=errors, form_data=request.form)

        # Guardar imagen si existe
        if foto and foto.filename != '':
            carpeta_fotos = os.path.join("static", "fotos")
            os.makedirs(carpeta_fotos, exist_ok=True)
            ruta_foto = secure_filename(foto.filename)
            foto.save(os.path.join(carpeta_fotos, ruta_foto))
        else:
            ruta_foto = None

        # Insertar en la base de datos
        cursor.execute("""
            INSERT INTO docentes (
                Matricula_Docente, Nombre_D, Apellido_P_D, Apellido_M_D, Correo_D, Cedula_P_D, Taller_Impartir, 
                Foto_CredencialD
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            matriculaD, nombreD, apellido_p_D, apellido_m_D, correo_D, cedula_profesional, taller_impartir,
            ruta_foto
        ))

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("login"))
    return render_template('registroDocente.html', form_data={})

# Editar Docente
@app.route("/editarDocente/<matriculaD>", methods=["GET", "POST"])
def editarDocente(matriculaD):
    cursor = mysql.connection.cursor()

    # Buscar docente por matrícula
    cursor.execute("SELECT * FROM docentes WHERE Matricula_Docente = %s", (matriculaD,))
    docentes = cursor.fetchone()

    if not docentes:
        cursor.close()
        return "Docente no encontrado", 404

    # Mapear resultados a diccionario
    columnas = [desc[0] for desc in cursor.description]
    datos = dict(zip(columnas, docentes))
    cursor.close()


    # Normalizar valores para renderizar HTML correctamente
    estatus_original = datos["Estatus"]
    estado = ""
    if estatus_original.lower().startswith("a"):  # Activo
        estado = "A"
    elif estatus_original.lower().startswith("b"):  # Baja
        estado = "B"
    else:
        estado = "BT" #Baja temporal

    datos["Estatus"] = estado

    datos["taller_impartir"] = datos.get("Taller_Impartir", "").strip().lower()

    if request.method == "POST":
        # Obtener datos del formulario
        nombreD = request.form["nombreD"]
        apellido_p_D = request.form["apellido_p_D"]
        apellido_m_D = request.form["apellido_m_D"]
        taller_impartir = request.form["taller_impartir"]
        estado = request.form["estado"]
        foto = request.files["foto_credencialD"]

        cursor = mysql.connection.cursor()

        # Actualizar datos en la BD
        cursor.execute("""
            UPDATE docentes
            SET Nombre_D=%s, Apellido_P_D=%s, Apellido_M_D=%s,Taller_Impartir=%s, Estatus=%s
            WHERE Matricula_Docente=%s
        """, (
            nombreD, apellido_p_D, apellido_m_D, taller_impartir, estado, matriculaD
        ))

        # Ruta para guardar las fotos
        carpeta_fotos = os.path.join("static", "fotos")
        os.makedirs(carpeta_fotos, exist_ok=True)

        # Verificar si se subió una nueva foto
        if 'foto_credencialD' in request.files:
            foto = request.files['foto_credencialD']
            if foto and allowed_file(foto.filename):
                # Nombre único para la nueva imagen
                ruta_foto = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(foto.filename)}"
                foto.save(os.path.join(carpeta_fotos, ruta_foto))

                # Eliminar foto anterior si existe
                if datos.get("Foto_CredencialD"):
                    ruta_antigua = os.path.join(carpeta_fotos, datos["Foto_CredencialD"])
                    if os.path.exists(ruta_antigua):
                        os.remove(ruta_antigua)

                # Actualizar en base de datos
                cursor.execute(
                    "UPDATE docentes SET Foto_CredencialD=%s WHERE Matricula_Docente=%s",
                    (ruta_foto, matriculaD)
                )
                flash("Foto de credencial actualizada con éxito.")
            elif foto.filename != '':
                flash("Archivo no permitido. Usa una imagen PNG, JPG, JPEG o GIF.")

        mysql.connection.commit()
        cursor.close()

        return redirect(url_for("dashboard"))

    return render_template("editarDocente.html", datos=datos)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Rutas a vistas de talleres
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


