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
        cursor.execute("SELECT * FROM administrador WHERE correo_A = %s AND contraseña = %s", (email, password))
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
#consultas exactas o mostrar todo#

@app.route('/consultar', methods=['GET', 'POST'])
def consultar():
    resultados = []
    tipo = ""

    if request.method == 'POST':
        tipo = request.form['tipo']
        busqueda = request.form.get('busqueda', '')
        mostrar_todo = request.form.get('mostrar_todo')

        cur = mysql.connection.cursor()

        if tipo == 'estudiante':
            query = "SELECT Nombre, Apellido_P, Apellido_M, Matricula FROM estudiante"
            if not mostrar_todo:
                query += " WHERE Nombre LIKE %s OR Matricula LIKE %s"
                cur.execute(query, (f"%{busqueda}%", f"%{busqueda}%"))
            else:
                cur.execute(query)

        elif tipo == 'docente':
            query = "SELECT Nombre_D, Apellido_P_D, Apellido_M_D, Matricula_Docente FROM docentes"
            if not mostrar_todo:
                query += " WHERE Nombre_D LIKE %s OR Matricula_Docente LIKE %s"
                cur.execute(query, (f"%{busqueda}%", f"%{busqueda}%"))
            else:
                cur.execute(query)

        elif tipo == 'taller':
            query = "SELECT Nombre_T, Nombre_D FROM taller"
            if not mostrar_todo:
                query += " WHERE Nombre_T LIKE %s OR Nombre_D LIKE %s"
                cur.execute(query, (f"%{busqueda}%", f"%{busqueda}%"))
            else:
                cur.execute(query)

        resultados = cur.fetchall()
        cur.close()

    return render_template('consultar.html', resultados=resultados, tipo=tipo)




# Ruta para registrar taller
@app.route("/registroTaller", methods=["GET", "POST"])
def registroTaller():
    errors = {}

    if request.method == "POST":
        # Recolección de datos del formulario
        Nombre_T = request.form.get('Nombre_T')
        Nombre_D = request.form.get("Nombre_D")
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

        # Validación: Taller ya existe
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM taller WHERE Nombre_T = %s", (Nombre_T,))
        if cursor.fetchone():
            errors['Nombre_T'] = "El taller ya está registrado."

        # Validaciones adicionales
        if not Nombre_T:
            errors['Nombre_T'] = "El nombre del taller es obligatorio."
        if not Nombre_D:
            errors['Nombre_D'] = "El nombre del docente es obligatorio."
        if not estatus:
            errors['estatus'] = "El estatus es obligatorio."

        if errors:
            # Devuelve formulario con errores y datos previos
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

        session["alerta"] = {
            "tipo": "success",  # o "error"
            "titulo": "Registro exitoso",
            "mensaje": "El taller fue registrado correctamente."
        }
        return redirect(url_for("dashboard"))  # Cambia esta redirección según lo que necesites

    return render_template("registroTaller.html", form_data={})

# Editar Taller
@app.route('/editarTaller/<int:id_taller>', methods=['GET', 'POST'])
def editarTaller(id_taller):
    if request.method == 'POST':
        nombre_t = request.form['nombre_t']
        nombre_docente = request.form['nombre_docente']
        dias_taller = request.form.getlist('dias_t[]')
        estatus = request.form['estatus']

        # Construir horarios desde los inputs
        horarios = {}
        for dia in dias_taller:
            inicio = request.form.get(f'horario_{dia}_inicio')
            fin = request.form.get(f'horario_{dia}_fin')
            if inicio and fin:
                horarios[dia] = f"{inicio}-{fin}"

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
        cursor.execute("""
            UPDATE taller
            SET Nombre_T=%s, Nombre_D=%s, Dias_T=%s, Horarios=%s, Estatus=%s
            WHERE id_taller=%s
        """, (
            nombre_t,
            nombre_docente,
            json.dumps(dias_taller),
            json.dumps(horarios),
            estatus,
            id_taller
        ))
        mysql.connection.commit()
        cursor.close()
        session["alerta"] = {
            "tipo": "success",
            "titulo": "Cambios guardados",
            "mensaje": "Los datos del taller fueron actualizados correctamente."
        }
        return redirect(url_for("dashboard"))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)  
    cursor.execute("SELECT * FROM taller WHERE id_taller=%s", (id_taller,))
    taller = cursor.fetchone()
    cursor.close()

    if not taller:
        flash("Taller no encontrado", "danger")
        return redirect(url_for('dashboard'))

    # Convertir Horarios a diccionario para el template
    horarios_raw = taller.get('Horarios')
    if horarios_raw:
        try:
            taller['Horarios'] = json.loads(horarios_raw)
        except json.JSONDecodeError:
            taller['Horarios'] = {}
    else:
        taller['Horarios'] = {}

    # Convertir Dias_T a lista para el template
    dias_raw = taller.get('Dias_T')
    if dias_raw:
        try:
            taller['Dias_T'] = json.loads(dias_raw)
        except json.JSONDecodeError:
            taller['Dias_T'] = []
    else:
        taller['Dias_T'] = []

    return render_template('editarTaller.html', taller=taller)


# Registro Alumno
@app.route("/registro", methods=["GET", "POST"])
def registro():
    errors = {}
    cursor = mysql.connection.cursor()

    # Obtener talleres activos con sus horarios
    cursor.execute("SELECT Nombre_T, Horarios FROM taller WHERE Estatus = 'A'")
    talleres = cursor.fetchall()

    talleres_dict = {}
    for nombre, horarios in talleres:
        try:
            talleres_dict[nombre] = json.loads(horarios) if horarios else {}
        except json.JSONDecodeError:
            talleres_dict[nombre] = {}

    if request.method == "POST":
        form = request.form
        matricula = form["matricula"]
        nombre = form["nombre"]
        apellido_p = form["apellido_p"]
        apellido_m = form["apellido_m"]
        carrera = form["carrera"]
        genero = form["genero"]
        edad = form["edad"]
        nss = form["nss"]
        grado_grupo = form["grado_grupo"]
        telefono = form["telefono"]
        tutor = form["tutor"]
        telefono_emergencia = form["telefono_emergencia"]
        correo = form["correo"]
        taller_inscripcion = form["taller_inscripcion"]
        horario = form["horario"]
        fecha_inscripcion = form.get("fecha_inscripcion")
        contrasena = form["contrasena"]
        confirmar = form["confirmar"]
        foto = request.files["foto_credencial"]

        # Validaciones
        if contrasena != confirmar:
            errors["contrasena"] = "Las contraseñas no coinciden."

        if cursor.execute("SELECT 1 FROM estudiante WHERE Correo = %s", (correo,)) and cursor.fetchone():
            errors["correo"] = "El correo ya está registrado."

        if cursor.execute("SELECT 1 FROM estudiante WHERE Matricula = %s", (matricula,)) and cursor.fetchone():
            errors["matricula"] = "La matrícula ya está registrada."

        if cursor.execute("SELECT 1 FROM estudiante WHERE NSS = %s", (nss,)) and cursor.fetchone():
            errors["nss"] = "El NSS ya está registrado."

        # Validar fecha
        try:
            fecha_inscripcion_dt = datetime.strptime(fecha_inscripcion, "%Y-%m-%d")
        except (ValueError, TypeError):
            errors["fecha_inscripcion"] = "Fecha de inscripción inválida."

        if errors:
            cursor.close()
            return render_template("registro.html", errors=errors, form_data=form, talleres=talleres_dict)

        # Guardar imagen
        ruta_foto = None
        if foto and foto.filename:
            carpeta_fotos = os.path.join("static", "fotos")
            os.makedirs(carpeta_fotos, exist_ok=True)
            ruta_foto = secure_filename(foto.filename)
            foto.save(os.path.join(carpeta_fotos, ruta_foto))

        # Insertar en la base de datos
        cursor.execute("""
            INSERT INTO estudiante (
                Matricula, Nombre, Apellido_P, Apellido_M, Carrera, Genero, Edad,
                NSS, Grado_Grupo, Telefono, Tutor, Telefono_Emergencia, Correo,
                Taller_Inscripcion, Horario, Fecha_Inscripcion, Contraseña, Foto_Credencial
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            matricula, nombre, apellido_p, apellido_m, carrera, genero, edad,
            nss, grado_grupo, telefono, tutor, telefono_emergencia, correo,
            taller_inscripcion, horario, fecha_inscripcion_dt.strftime("%Y-%m-%d"),
            contrasena, ruta_foto
        ))


        mysql.connection.commit()
        cursor.close()

        session["alerta"] = {
            "tipo": "success",  # o "error"
            "titulo": "Registro exitoso",
            "mensaje": "El alumno fue registrado correctamente."
        }
        return redirect(url_for("dashboard"))
    return render_template("registro.html", form_data={}, talleres=talleres_dict)


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

    # Obtener talleres activos con sus horarios desde la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Nombre_T, Horarios FROM taller WHERE Estatus = 'A'")
    talleres = cursor.fetchall()
    cursor.close()

    talleres_dict = {}
    for nombre, horarios in talleres:
        try:
            if horarios:
                horarios_dict = json.loads(horarios)
                # Convertir {"Martes": "12:00-19:00"} → ["Martes 12:00-19:00"]
                horarios_lista = [f"{dia} {hora}" for dia, hora in horarios_dict.items()]
                talleres_dict[nombre.strip().lower()] = horarios_lista
            else:
                talleres_dict[nombre.strip().lower()] = []
        except json.JSONDecodeError:
            talleres_dict[nombre.strip().lower()] = []


    # Normalizar valores para renderizar HTML correctamente
    genero_original = datos["Genero"]
    genero = ""
    if genero_original.lower().startswith("h"):
        genero = "H"
    elif genero_original.lower().startswith("m"):
        genero = "M"
    else:
        genero = "LGBTQ"

    datos["Genero"] = genero
    datos["Taller_Inscripcion"] = datos.get("Taller_Inscripcion", "").strip().lower()
    datos["Horario"] = datos.get("Horario", "").strip()

    # Formatear fecha para el input date
    if datos.get("Fecha_Inscripcion"):
        try:
            datos["Fecha_Inscripcion"] = datos["Fecha_Inscripcion"].strftime("%Y-%m-%d")
        except Exception:
            datos["Fecha_Inscripcion"] = str(datos["Fecha_Inscripcion"])

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
        taller_inscripcion = request.form["taller_inscripcion"].strip().lower()
        horario = request.form["horario"]
        fecha_inscripcion = request.form["fecha_inscripcion"]
        foto = request.files["foto_credencial"]

        cursor = mysql.connection.cursor()

        # Actualizar datos en la BD
        cursor.execute("""
            UPDATE estudiante
            SET Nombre=%s, Apellido_P=%s, Apellido_M=%s, Carrera=%s, Genero=%s, Edad=%s,
                Grado_Grupo=%s, Telefono=%s, Tutor=%s, Telefono_Emergencia=%s,
                Taller_Inscripcion=%s, Horario=%s, Fecha_Inscripcion=%s
            WHERE Matricula=%s
        """, (
            nombre, apellido_p, apellido_m, carrera, genero, edad,
            grado_grupo, telefono, tutor, telefono_emergencia,
            taller_inscripcion, horario, fecha_inscripcion, matricula
        ))

        # Ruta para guardar las fotos
        carpeta_fotos = os.path.join("static", "fotos")
        os.makedirs(carpeta_fotos, exist_ok=True)

        # Verificar si se subió una nueva foto
        if foto and allowed_file(foto.filename):
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

        session["alerta"] = {
            "tipo": "success",
            "titulo": "Cambios guardados",
            "mensaje": "Los datos del alumno fueron actualizados correctamente."
        }
        return redirect(url_for("dashboard"))
    
    return render_template("editarAlumno.html", datos=datos, talleres=talleres_dict)


#Registro Docente
@app.route("/registroDocente", methods=["GET", "POST"])
def registroDocente():
    errors = {}

    # Obtener talleres activos desde la base de datos
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT Nombre_T FROM taller WHERE Estatus = 'A'")
    talleres = cursor.fetchall()
    talleres_lista = [nombre.strip().lower() for (nombre,) in talleres]

    if request.method == "POST":
        matriculaD = request.form["matriculaD"]
        nombreD = request.form["nombreD"]
        apellido_p_D = request.form["apellido_p_D"]
        apellido_m_D = request.form["apellido_m_D"]
        correo_D = request.form["correo_D"]
        cedula_profesional = request.form["cedula_profesional"]
        taller_impartir = request.form["taller_impartir"]
        estatus = request.form["estatus"]
        foto = request.files["foto_credencialD"]

        # Validaciones
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
            cursor.close()
            return render_template("registroDocente.html", errors=errors, form_data=request.form, talleres=talleres_lista)

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
                Matricula_Docente, Nombre_D, Apellido_P_D, Apellido_M_D, Correo_D, Cedula_P_D,
                Taller_Impartir, Estatus, Foto_CredencialD
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            matriculaD, nombreD, apellido_p_D, apellido_m_D, correo_D, cedula_profesional,
            taller_impartir, estatus, ruta_foto
        ))

        mysql.connection.commit()
        cursor.close()

        session["alerta"] = {
            "tipo": "success",  # o "error"
            "titulo": "Registro exitoso",
            "mensaje": "El docente fue registrado correctamente."
        }
        return redirect(url_for("dashboard"))
    return render_template("registroDocente.html", form_data={}, talleres=talleres_lista)

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

        session["alerta"] = {
            "tipo": "success",
            "titulo": "Cambios guardados",
            "mensaje": f"Los datos del docente fueron actualizados correctamente."
        }
        return redirect(url_for("dashboard"))

    return render_template("editarDocente.html", datos=datos)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# Rutas a vistas de talleres
@app.route('/futbol_soccer')
def futbol_soccer():
    return render_template('futbol_soccer.html')

@app.route('/basquetbol')
def basquetbol():
    return render_template('basquetbol.html')

@app.route('/voleibol')
def voleibol():
    return render_template('voleibol.html')

@app.route('/escolta')
def escolta():
    return render_template('escolta.html')

@app.route('/banda_guerra')
def banda_guerra():
    return render_template('banda_guerra.html')

@app.route('/ajedrez_competitivo')
def ajedrez_competitivo():
    return render_template('ajedrez_competitivo.html')

@app.route('/futbol7')
def futbol7():
    return render_template('futbol7.html')

@app.route('/danza')
def danza():
    return render_template('danza.html')

@app.route('/ajedrez_recreativo')
def ajedrez_recreativo():
    return render_template('ajedrez_recreativo.html')

@app.route('/beisbol')
def beisbol():
    return render_template('beisbol.html')

@app.route('/porristas')
def porristas():
    return render_template('porristas.html')

@app.route('/atletismo')
def atletismo():
    return render_template('atletismo.html')

@app.route('/editar_imagenes')
def editar_imagenes():
    return render_template('editar_imagenes.html')

@app.route('/guardar_imagen_estatica', methods=['POST'])
def guardar_imagen_estatica():
    archivo = request.files['imagen_estatica']
    if archivo:
        archivo.save('static/img/web_banner_convo_2025_03.png')
    return redirect(url_for('dashboard'))

@app.route('/guardar_imagenes_carrusel', methods=['POST'])
def guardar_imagenes_carrusel():
    for i in range(1, 13): 
        archivo = request.files.get(f'carrusel_{i}')
        if archivo:
            archivo.save(f'static/img/carrusel_{i}.jpg')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)


