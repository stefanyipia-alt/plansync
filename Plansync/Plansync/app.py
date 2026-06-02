from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    send_from_directory,
    url_for
)

import mysql.connector
import os
import smtplib
import json
import calendar
import calendar
from calendar import monthrange

from flask import send_from_directory
import os

from datetime import datetime

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

from werkzeug.utils import secure_filename

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
from emails import *
from flask import send_from_directory

from flask import flash
from werkzeug.exceptions import RequestEntityTooLarge

from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash
import re
from itsdangerous import URLSafeTimedSerializer

#FLASK

app = Flask(__name__)

app.secret_key = os.urandom(24)

# =========================
# TOKEN RECUPERACIÓN
# =========================

serializer = URLSafeTimedSerializer(
    app.secret_key
)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# =========================
# CARPETA UPLOADS
# =========================

UPLOAD_FOLDER = os.path.join(
    os.getcwd(),
    "uploads"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# =========================
# LÍMITE 10 MB
# =========================

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

# =========================
# ERROR ARCHIVO MUY GRANDE
# =========================

@app.errorhandler(RequestEntityTooLarge)
def archivo_grande(e):

    return """
    <h2>Archivo demasiado grande</h2>
    <p>El tamaño máximo permitido es 10 MB.</p>
    """, 413

# =========================
# CORREO
# =========================

EMAIL = "stefanyipia@unicomfacauca.edu.co"

PASSWORD = "lmzx ijiw fgtq noia"

#ruta descargar archivo

def get_db():

    try:

        conexion = mysql.connector.connect(

            host="zephyr.proxy.rlwy.net",
            port=49847,
            user="root",
            password="tJOsKMkhwElcZTZqlPdfkOXumWMibnco",
            database="railway"

        )

        print("MYSQL CONECTADO")

        return conexion

    except Exception as e:

        print("ERROR MYSQL:", e)

        return None


@app.route("/")
@app.route("/inicio")
def dashboard():

    # =========================
    # VALIDAR LOGIN
    # =========================

    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        conn = get_db()

        cursor = conn.cursor()

        usuario_id = session["usuario_id"]

        # =========================
        # CONTACTOS
        # =========================

        cursor.execute("""
            SELECT COUNT(*)
            FROM contactos
            WHERE usuario_id = %s
        """, (usuario_id,))

        total_contactos = cursor.fetchone()[0]

        # =========================
        # TOTAL TAREAS
        # =========================

        if session["rol"] == "profesor":

            cursor.execute("""
                SELECT COUNT(*)
                FROM tareas
                WHERE usuario_id = %s
            """, (usuario_id,))

        else:

            cursor.execute("""
                SELECT COUNT(*)
                FROM tareas
                WHERE estudiante_id = %s
            """, (usuario_id,))

        total_tareas = cursor.fetchone()[0]

        # =========================
        # REUNIONES
        # =========================

        if session["rol"] == "profesor":

            cursor.execute("""
                SELECT COUNT(*)
                FROM reuniones
                WHERE profesor_id = %s
            """, (usuario_id,))

        else:

            cursor.execute("""
                SELECT COUNT(*)
                FROM reunion_participantes
                WHERE usuario_id = %s
            """, (usuario_id,))

        total_agenda = cursor.fetchone()[0]

        # =========================
        # TAREAS PENDIENTES
        # =========================

        if session["rol"] == "profesor":

            cursor.execute("""
                SELECT COUNT(*)
                FROM tareas
                WHERE usuario_id = %s
                AND estado = 'pendiente'
            """, (usuario_id,))

        else:

            cursor.execute("""
                SELECT COUNT(*)
                FROM tareas
                WHERE estudiante_id = %s
                AND estado = 'pendiente'
            """, (usuario_id,))

        tareas_pendientes = cursor.fetchone()[0]

        # =========================
        # TAREAS COMPLETADAS
        # =========================

        if session["rol"] == "profesor":

            cursor.execute("""
                SELECT COUNT(*)
                FROM tareas
                WHERE usuario_id = %s
                AND estado = 'completada'
            """, (usuario_id,))

        else:

            cursor.execute("""
                SELECT COUNT(*)
                FROM tareas
                WHERE estudiante_id = %s
                AND estado = 'completada'
            """, (usuario_id,))

        tareas_completadas = cursor.fetchone()[0]

        # =========================
        # ACTIVIDAD RECIENTE
        # =========================

        if session["rol"] == "profesor":

            cursor.execute("""
                SELECT titulo, fecha
                FROM tareas
                WHERE usuario_id = %s
                ORDER BY id DESC
                LIMIT 5
            """, (usuario_id,))

        else:

            cursor.execute("""
                SELECT titulo, fecha
                FROM tareas
                WHERE estudiante_id = %s
                ORDER BY id DESC
                LIMIT 5
            """, (usuario_id,))

        actividad = cursor.fetchall()

        # =========================
        # REUNIONES PRÓXIMAS
        # =========================

        if session["rol"] == "profesor":

            cursor.execute("""
                SELECT *
                FROM reuniones
                WHERE profesor_id = %s
                ORDER BY fecha ASC
                LIMIT 2
            """, (usuario_id,))

        else:

            cursor.execute("""
                SELECT r.*
                FROM reuniones r
                JOIN reunion_participantes rp
                ON r.id = rp.reunion_id
                WHERE rp.usuario_id = %s
                ORDER BY r.fecha ASC
                LIMIT 2
            """, (usuario_id,))

        reuniones_proximas = cursor.fetchall()

        # =========================
        # RENDER
        # =========================

        return render_template(

            "dashboard.html",

            total_contactos=total_contactos,

            total_tareas=total_tareas,

            total_agenda=total_agenda,

            tareas_pendientes=tareas_pendientes,

            tareas_completadas=tareas_completadas,

            reuniones_proximas=reuniones_proximas,

            actividad=actividad

        )

    except Exception as e:

        print("ERROR DASHBOARD:", e)

        return f"Error dashboard: {e}"

    finally:

        if conn and conn.is_connected():
            conn.close()

@app.route("/register", methods=["GET", "POST"])
def register():

    error = None

    if request.method == "POST":

        conn = get_db()

        if conn is None:
            return "Error MySQL"

        try:

            nombre = request.form["nombre"].strip()

            email = request.form["email"].strip()
            

            password = request.form["password"]

            rol = request.form["rol"]

            # =========================
            # VALIDAR CORREO INSTITUCIONAL
            # =========================

            if not email.endswith("@unicomfacauca.edu.co"):

             return render_template(
             "registro.html",
             error="Solo se permiten correos institucionales"
             )

            password_hash = generate_password_hash(password)

            cursor = conn.cursor()

            cursor.execute("""
                SELECT id
                FROM usuario
                WHERE email = %s
            """, (email,))

            existe = cursor.fetchone()

            if existe:

                error = "Correo ya registrado"

                return render_template(
                    "register.html",
                    error=error
                )

            cursor.execute("""
                INSERT INTO usuario
                (
                    nombre,
                    email,
                    password,
                    rol
                )

                VALUES (%s, %s, %s, %s)
            """, (

                nombre,
                email,
                password_hash,
                rol

            ))

            conn.commit()

            return redirect("/login")

        except Exception as e:

            print("ERROR REGISTER:", e)

            return f"Error register: {e}"

        finally:

            if conn and conn.is_connected():
                conn.close()

    return render_template("register.html", error=error)

# ------------------------
# LOGIN
# ------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    error = None

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]

        conn = None

        try:

            conn = get_db()

            # VALIDAR MYSQL
            if conn is None:

                error = "Error conectando con MySQL"

                return render_template(
                    "login.html",
                    error=error
                )

            cursor = conn.cursor()

            # BUSCAR USUARIO
            cursor.execute("""
                SELECT *
                FROM usuario
                WHERE email = %s
            """, (email,))

            usuario = cursor.fetchone()

            # USUARIO NO EXISTE
            if not usuario:

                error = "Usuario no registrado"

                return render_template(
                    "login.html",
                    error=error
                )

            # VALIDAR PASSWORD
            if not check_password_hash(usuario[3], password):

                  error = "Contraseña incorrecta"

                  return render_template(
                    "login.html",
                      error=error
                                   )

            # VALIDAR ROL
            if usuario[4] not in [
                "profesor",
                "estudiante"
            ]:

                error = "Acceso denegado"

                return render_template(
                    "login.html",
                    error=error
                )

            # CREAR SESIÓN
            session["usuario_id"] = usuario[0]

            session["nombre"] = usuario[1]

            session["rol"] = usuario[4]

            print("LOGIN CORRECTO")

            return redirect("/inicio")

        except Exception as e:

            print("ERROR LOGIN:", e)

            error = "Error de conexión con el servidor"

        finally:

            if conn and conn.is_connected():

                conn.close()

    return render_template(
        "login.html",
        error=error
    )

# =========================
# IMPORTS CORREO
# =========================

import smtplib
import os

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


# =========================
# ENVIAR CORREO
# =========================

def enviar_correo(destino, asunto, html):

    try:

        # =========================
        # MENSAJE PRINCIPAL
        # =========================

        mensaje = MIMEMultipart()

        mensaje["Subject"] = asunto
        mensaje["From"] = EMAIL
        mensaje["To"] = destino

        # =========================
        # PARTE RELACIONADA
        # =========================

        parte_relacionada = MIMEMultipart("related")

        mensaje.attach(parte_relacionada)

        # =========================
        # HTML
        # =========================

        cuerpo = MIMEText(html, "html")

        parte_relacionada.attach(cuerpo)

        # =========================
        # RUTA BASE
        # =========================

        BASE_DIR = os.path.dirname(
            os.path.abspath(__file__)
        )

        print("BASE_DIR =", BASE_DIR)

        # =========================
        # LOGO PLANSYNC
        # =========================

        ruta_logo = os.path.join(
            BASE_DIR,
            "static",
            "img",
            "logo.png"
        )

        print("BUSCANDO LOGO:", ruta_logo)
        print("EXISTE:", os.path.exists(ruta_logo))

        if os.path.exists(ruta_logo):

            with open(ruta_logo, "rb") as f:

                logo = MIMEImage(
                    f.read(),
                    _subtype="png"
                )

                logo.add_header(
                    "Content-ID",
                    "<logo_plansync>"
                )

                logo.add_header(
                    "Content-Disposition",
                    "inline",
                    filename="logo.png"
                )

                parte_relacionada.attach(logo)

        else:

            print("LOGO PLANSYNC NO ENCONTRADO")

        # =========================
        # LOGO UNIVERSIDAD
        # =========================

        ruta_uni = os.path.join(
            BASE_DIR,
            "static",
            "img",
            "Unicomfacauca.png"
        )

        print("BUSCANDO UNIVERSIDAD:", ruta_uni)
        print("EXISTE:", os.path.exists(ruta_uni))

        if os.path.exists(ruta_uni):

            with open(ruta_uni, "rb") as f:

                uni = MIMEImage(
                    f.read(),
                    _subtype="png"
                )

                uni.add_header(
                    "Content-ID",
                    "<logo_uni>"
                )

                uni.add_header(
                    "Content-Disposition",
                    "inline",
                    filename="Unicomfacauca.png"
                )

                parte_relacionada.attach(uni)

        else:

            print("LOGO UNIVERSIDAD NO ENCONTRADO")

        # =========================
        # SMTP GMAIL
        # =========================

        print("================================")
        print("DESTINO:", destino)
        print("ASUNTO:", asunto)
        print("EMAIL CONFIGURADO:", EMAIL)
        print("================================")

        servidor = smtplib.SMTP(
            "smtp.gmail.com",
            587,
            timeout=20
        )

        servidor.starttls()

        servidor.login(
            EMAIL,
            PASSWORD
        )

        print("LOGIN GMAIL OK")

        servidor.sendmail(
            EMAIL,
            destino,
            mensaje.as_string()
        )

        servidor.quit()

        print("CORREO ENVIADO")

        return True

    except Exception as e:

        print("ERROR CORREO:", str(e))

        return False
    # =========================
# HTML REUNIÓN
# =========================

def correo_reunion(

    titulo,
    fecha,
    hora,
    lugar,
    descripcion,
    tipo="invitacion"

):

    color = "#0b57d0"
    encabezado = "¡Tienes una nueva invitación!"

    if tipo == "recordatorio":

        color = "#16a34a"
        encabezado = "¡Recordatorio!"

    elif tipo == "confirmacion":

        color = "#2563eb"
        encabezado = "¡Reunión confirmada!"

    html = f"""

    <html>
    <body style="margin:0;padding:0;background:#f4f6f9;font-family:Arial,sans-serif;">

    <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
    <td align="center">

    <table width="650" cellpadding="0" cellspacing="0"
    style="background:white;margin-top:20px;border-radius:18px;overflow:hidden;
    box-shadow:0 4px 12px rgba(0,0,0,0.1);">

    <!-- LOGO -->

    <tr>
    <td align="center" style="padding:30px;">

    <img src="https://i.imgur.com/9V6mG5D.png"
    width="220">

    </td>
    </tr>

    <!-- HEADER -->

    <tr>
    <td style="background:{color};padding:40px;text-align:center;color:white;">

    <h1 style="margin:0;font-size:34px;">
    {encabezado}
    </h1>

    </td>
    </tr>

    <!-- CONTENIDO -->

    <tr>
    <td style="padding:40px;">

    <h2 style="color:#1e293b;">
    Hola,
    </h2>

    <p style="font-size:16px;color:#475569;">
    Tienes información importante sobre una reunión.
    </p>

    <table width="100%" cellpadding="18"
    style="border:1px solid #e2e8f0;border-radius:14px;margin-top:25px;">

    <tr>
    <td>

    <p>📌 <b>Título:</b> {titulo}</p>

    <p>📅 <b>Fecha:</b> {fecha}</p>

    <p>⏰ <b>Hora:</b> {hora}</p>

    <p>📍 <b>Lugar:</b> {lugar}</p>

    <p>📝 <b>Descripción:</b> {descripcion}</p>

    </td>
    </tr>

    </table>

    </td>
    </tr>

    <!-- FOOTER -->

    <tr>
    <td style="
    background:#02132b;
    color:white;
    text-align:center;
    padding:20px;
    ">

    © 2026 PlanSync

    </td>
    </tr>

    </table>

    </td>
    </tr>
    </table>

    </body>
    </html>

    """

    return html



# =========================
# HTML NUEVA TAREA
# =========================

def correo_nueva_tarea(

    titulo,
    fecha,
    descripcion

):

    html = f"""

    <html>
    <body style="font-family:Arial;background:#f4f6f9;padding:40px;">

    <div style="
    max-width:650px;
    margin:auto;
    background:white;
    border-radius:18px;
    overflow:hidden;
    ">

    <div style="
    background:#0b57d0;
    color:white;
    text-align:center;
    padding:40px;
    ">

    <h1>📚 Nueva Tarea Asignada</h1>

    </div>

    <div style="padding:40px;">

    <p>Tienes una nueva tarea en PlanSync.</p>

    <p><b>Título:</b> {titulo}</p>

    <p><b>Fecha:</b> {fecha}</p>

    <p><b>Descripción:</b> {descripcion}</p>

    </div>

    <div style="
    background:#02132b;
    color:white;
    text-align:center;
    padding:20px;
    ">

    © 2026 PlanSync

    </div>

    </div>

    </body>
    </html>

    """

    return html
    

# =========================
# CAMBIAR PASSWORD
# =========================

@app.route("/cambiar_password", methods=["GET", "POST"])
def cambiar_password():

    import re

    mensaje = None

    if request.method == "POST":

        # =========================
        # OBTENER DATOS
        # =========================

        email = request.form["email"].strip()

        nueva = request.form["nueva"]

        confirmar = request.form["confirmar"]

        # =========================
        # CAMPOS VACÍOS
        # =========================

        if not email or not nueva or not confirmar:

            mensaje = "Todos los campos son obligatorios"

            return render_template(
                "cambiar_password.html",
                mensaje=mensaje
            )

        # =========================
        # VALIDAR ESPACIOS
        # =========================

        if " " in nueva:

            mensaje = "La contraseña no puede contener espacios"

            return render_template(
                "cambiar_password.html",
                mensaje=mensaje
            )

        # =========================
        # LONGITUD
        # =========================

        if len(nueva) < 8:

            mensaje = "La contraseña debe tener mínimo 8 caracteres"

            return render_template(
                "cambiar_password.html",
                mensaje=mensaje
            )

        # =========================
        # MAYÚSCULA
        # =========================

        if not re.search(r"[A-Z]", nueva):

            mensaje = "Debe contener al menos una letra mayúscula"

            return render_template(
                "cambiar_password.html",
                mensaje=mensaje
            )

        # =========================
        # MINÚSCULA
        # =========================

        if not re.search(r"[a-z]", nueva):

            mensaje = "Debe contener al menos una letra minúscula"

            return render_template(
                "cambiar_password.html",
                mensaje=mensaje
            )

        # =========================
        # NÚMERO
        # =========================

        if not re.search(r"[0-9]", nueva):

            mensaje = "Debe contener al menos un número"

            return render_template(
                "cambiar_password.html",
                mensaje=mensaje
            )

        # =========================
        # SÍMBOLO
        # =========================

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", nueva):

            mensaje = "Debe contener al menos un símbolo especial"

            return render_template(
                "cambiar_password.html",
                mensaje=mensaje
            )

        # =========================
        # CONFIRMAR PASSWORD
        # =========================

        if nueva != confirmar:

            mensaje = "Las contraseñas no coinciden"

            return render_template(
                "cambiar_password.html",
                mensaje=mensaje
            )

        # =========================
        # CONEXIÓN MYSQL
        # =========================

        conn = None

        try:

            conn = get_db()

            cursor = conn.cursor()

            # =========================
            # VALIDAR USUARIO
            # =========================

            cursor.execute("""

                SELECT *
                FROM usuario
                WHERE email = %s

            """, (email,))

            usuario = cursor.fetchone()

            if not usuario:

                mensaje = "Usuario no encontrado"

                return render_template(
                    "cambiar_password.html",
                    mensaje=mensaje
                )

            # =========================
            # ENCRIPTAR PASSWORD
            # =========================

            password_hash = generate_password_hash(
                nueva
            )

            # =========================
            # ACTUALIZAR PASSWORD
            # =========================

            cursor.execute("""

                UPDATE usuario
                SET password = %s
                WHERE email = %s

            """, (

                password_hash,
                email

            ))

            conn.commit()

            print("PASSWORD ACTUALIZADA")

            return redirect("/login")

        except Exception as e:

            print("ERROR CAMBIAR PASSWORD:", e)

            mensaje = "Ocurrió un error al cambiar la contraseña"

        finally:

            if conn and conn.is_connected():

                conn.close()

    return render_template(
        "cambiar_password.html",
        mensaje=mensaje
    )

# =========================
# SOLICITAR RECUPERACIÓN
# =========================

@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():

    mensaje = None

    if request.method == "POST":

        email = request.form["email"]

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id
            FROM usuario
            WHERE email = %s
        """, (email,))

        usuario = cursor.fetchone()

        if usuario:

            # =========================
            # CREAR TOKEN
            # =========================

            token = serializer.dumps(
                email,
                salt="recuperar-password"
            )

            link = url_for(
                "reset_password",
                token=token,
                _external=True
            )

            # =========================
            # HTML CORREO
            # =========================

            html = f"""

            <html>
            <body style="font-family:Arial;background:#f4f6f9;padding:40px;">

            <div style="
            max-width:600px;
            margin:auto;
            background:white;
            border-radius:16px;
            overflow:hidden;
            ">

            <div style="
            background:#0b1b4d;
            color:white;
            padding:35px;
            text-align:center;
            ">

            <h1>🔒 Recuperar contraseña</h1>

            </div>

            <div style="padding:40px;">

            <p>
            Recibimos una solicitud para cambiar tu contraseña.
            </p>

            <p>
            Haz clic en el siguiente botón:
            </p>

            <a href="{link}"
            style="
            display:inline-block;
            background:#2563eb;
            color:white;
            padding:14px 25px;
            border-radius:10px;
            text-decoration:none;
            margin-top:20px;
            ">

            Cambiar contraseña

            </a>

            <p style="margin-top:30px;color:#64748b;">
            Este enlace expira en 15 minutos.
            </p>

            </div>

            </div>

            </body>
            </html>

            """

            enviar_correo(
                email,
                "Recuperar contraseña",
                html
            )

        mensaje = "Si el correo existe, se enviaron instrucciones."

    return render_template(
    "recuperar_password.html",
    mensaje=mensaje
)

# =========================
# CAMBIAR CONTRASEÑA
# =========================

@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):

    try:

        email = serializer.loads(
            token,
            salt="recuperar-password",
            max_age=900
        )

    except:

        return "El enlace expiró o es inválido"

    if request.method == "POST":

        nueva = request.form["password"]

        # =========================
        # VALIDAR SEGURIDAD
        # =========================

        if len(nueva) < 8:

            return """
            La contraseña debe tener mínimo 8 caracteres
            """

        password_hash = generate_password_hash(
            nueva
        )

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE usuario
            SET password = %s
            WHERE email = %s
        """, (

            password_hash,
            email

        ))

        conn.commit()
        conn.close()
        session.clear()

        return redirect("/login")

    return render_template(
        "reset_password.html"
    )
# ------------------------
# LOGOUT
# ------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


#------------------------------------------------------------------#

@app.route("/imagenes/<nombre>")
def imagenes(nombre):

    return send_from_directory(
        "static/img",
        nombre
    )

# ------------------------
# CONTACTOS
# ------------------------

@app.route("/contactos")
def contactos():

    # VALIDAR SESIÓN
    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        conn = get_db()

        cursor = conn.cursor()

        cursor.execute("""
            SELECT *
            FROM contactos
            WHERE usuario_id = %s
        """, (session["usuario_id"],))

        contactos = cursor.fetchall()

        return render_template(
            "contactos.html",
            contactos=contactos
        )

    except Exception as e:

        print("ERROR CONTACTOS:", e)

        return f"""
        <h2>Error en contactos</h2>
        <p>{e}</p>
        """

    finally:

        if conn and conn.is_connected():
            conn.close()


@app.route("/agregar_contacto")
def agregar_contacto():

    # VALIDAR SESIÓN
    if "usuario_id" not in session:
        return redirect("/login")

    return render_template("agregar_contacto.html")

# =========================
# CREAR CONTACTO
# =========================

@app.route("/crear_contacto", methods=["POST"])
def crear_contacto():

    # =========================
    # VALIDAR SESIÓN
    # =========================

    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        conn = get_db()

        cursor = conn.cursor()

        # =========================
        # BUSCAR USUARIO RELACIONADO
        # =========================

        cursor.execute("""
            SELECT id
            FROM usuario
            WHERE email = %s
        """, (request.form["email"],))

        usuario = cursor.fetchone()

        usuario_relacionado = None

        # =========================
        # SI EXISTE USUARIO
        # =========================

        if usuario:
            usuario_relacionado = usuario[0]

        # =========================
        # DATOS
        # =========================

        datos = (

            request.form["nombre"],
            request.form["telefono"],
            request.form["email"],

            session["usuario_id"],

            usuario_relacionado
        )

        # =========================
        # INSERTAR CONTACTO
        # =========================

        cursor.execute("""
            INSERT INTO contactos
            (
                nombre,
                telefono,
                email,
                usuario_id,
                usuario_relacionado
            )

            VALUES (%s, %s, %s, %s, %s)
        """, datos)

        conn.commit()

        print("CONTACTO CREADO")

        return redirect("/contactos")

    except Exception as e:

        print("ERROR CREAR CONTACTO:", e)

        return f"Error al crear contacto: {e}"

    finally:

        if conn and conn.is_connected():
            conn.close()

# =========================
# EDITAR CONTACTO
# =========================

@app.route("/editar_contacto/<int:id>", methods=["GET", "POST"])
def editar_contacto(id):

    # =========================
    # VALIDAR SESIÓN
    # =========================

    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        conn = get_db()

        cursor = conn.cursor()

        # =========================
        # EDITAR CONTACTO
        # =========================

        if request.method == "POST":

            nombre = request.form["nombre"]

            telefono = request.form["telefono"]

            email = request.form["email"]

            direccion = request.form["direccion"]

            notas = request.form["notas"]

            cursor.execute("""
                UPDATE contactos
                SET nombre = %s,
                    telefono = %s,
                    email = %s,
                    direccion = %s,
                    notas = %s
                WHERE id = %s
                AND usuario_id = %s
            """, (

                nombre,
                telefono,
                email,
                direccion,
                notas,
                id,
                session["usuario_id"]

            ))

            conn.commit()

            print("CONTACTO EDITADO")

            return redirect("/contactos")

        # =========================
        # OBTENER CONTACTO
        # =========================

        cursor.execute("""
            SELECT *
            FROM contactos
            WHERE id = %s
            AND usuario_id = %s
        """, (

            id,
            session["usuario_id"]

        ))

        contacto = cursor.fetchone()

        # =========================
        # CONTACTO NO EXISTE
        # =========================

        if not contacto:
            return "Contacto no encontrado"

        return render_template(
            "editar_contacto.html",
            contacto=contacto
        )

    except Exception as e:

        print("ERROR EDITAR CONTACTO:", e)

        return f"Error al editar contacto: {e}"

    finally:

        if conn and conn.is_connected():
            conn.close()

# =========================
# BUSCAR CONTACTO
# =========================

@app.route("/buscar_contacto")
def buscar_contacto():

    # =========================
    # VALIDAR SESIÓN
    # =========================

    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        query = request.args.get("q", "").strip()

        conn = get_db()

        cursor = conn.cursor()

        # =========================
        # BUSCAR CONTACTOS
        # =========================

        cursor.execute("""
            SELECT *
            FROM contactos
            WHERE nombre LIKE %s
            AND usuario_id = %s
        """, (

            '%' + query + '%',
            session["usuario_id"]

        ))

        resultados = cursor.fetchall()

        return render_template(
            "contactos.html",
            contactos=resultados
        )

    except Exception as e:

        print("ERROR BUSCAR CONTACTO:", e)

        return f"Error al buscar contacto: {e}"

    finally:

        if conn and conn.is_connected():
            conn.close()

# =========================
# CONFIRMAR ELIMINAR CONTACTO
# =========================

@app.route("/eliminar_contacto/<int:id>")
def confirmar_eliminar_contacto(id):

    # =========================
    # VALIDAR SESIÓN
    # =========================

    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        conn = get_db()

        cursor = conn.cursor()

        # =========================
        # OBTENER CONTACTO
        # =========================

        cursor.execute("""
            SELECT *
            FROM contactos
            WHERE id = %s
            AND usuario_id = %s
        """, (
            id,
            session["usuario_id"]
        ))

        contacto = cursor.fetchone()

        return render_template(
            "eliminar_contacto.html",
            contacto=contacto
        )

    except Exception as e:

        print("ERROR ELIMINAR CONTACTO:", e)

        return "Error al cargar contacto"

    finally:

        if conn and conn.is_connected():
            conn.close()


# ------------------------
# TAREAS (RF07–RF10)
# ------------------------
@app.route("/tareas")
def tareas():

    # =========================
    # VALIDAR SESIÓN
    # =========================

    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        conn = get_db()

        cursor = conn.cursor()

        # =========================
        # TAREAS
        # =========================

        if session["rol"] == "profesor":

            cursor.execute("""
                SELECT *
                FROM tareas
                WHERE usuario_id = %s
            """, (session["usuario_id"],))

        else:

            cursor.execute("""
                SELECT *
                FROM tareas
                WHERE estudiante_id = %s
            """, (session["usuario_id"],))

        tareas = cursor.fetchall()

        # =========================
        # CONTACTOS / ESTUDIANTES
        # =========================

        cursor.execute("""

      SELECT
        c.id,
        c.nombre,
        c.telefono,
        c.email,
        u.id

        FROM contactos c

        INNER JOIN usuario u
        ON c.email = u.email

        WHERE c.usuario_id = %s
        AND u.rol = 'estudiante'

        """, (session["usuario_id"],))

        contactos = cursor.fetchall()

        # =========================
        # ARCHIVOS
        # =========================

        cursor.execute("""
            SELECT *
            FROM archivos
        """)

        archivos = cursor.fetchall()

        # =========================
        # RENDER TEMPLATE
        # =========================

        return render_template(

            "tareas.html",

            tareas=tareas,

            rol=session["rol"],

            contactos=contactos,

            archivos=archivos
        )

    except Exception as e:

        print("ERROR TAREAS:", e)

        return f"Error en tareas: {e}"

    finally:

        if conn and conn.is_connected():
            conn.close()


# =========================
# CREAR TAREA
# =========================
@app.route("/crear_tarea", methods=["POST"])
def crear_tarea():

    # =========================
    # VALIDAR SESIÓN
    # =========================

    if "usuario_id" not in session:
        return redirect("/login")

    # =========================
    # SOLO PROFESOR
    # =========================

    if session.get("rol") != "profesor":
        return "No tienes permiso"

    conn = None

    try:

        # =========================
        # DATOS FORMULARIO
        # =========================

        titulo = request.form["titulo"]

        descripcion = request.form["descripcion"]

        fecha = request.form["fecha"]

        estudiante_id = int(
            request.form["estudiante_id"]
        )

        archivo = request.files.get("archivo")

        conn = get_db()

        cursor = conn.cursor()

        # =========================
        # CREAR TAREA
        # =========================

        cursor.execute("""

            INSERT INTO tareas
            (
                titulo,
                descripcion,
                fecha,
                estado,
                usuario_id,
                estudiante_id
            )

            VALUES (%s, %s, %s, %s, %s, %s)

        """, (

            titulo,
            descripcion,
            fecha,
            "pendiente",
            session["usuario_id"],
            estudiante_id

        ))

        conn.commit()

        # =========================
        # ID TAREA
        # =========================

        tarea_id = cursor.lastrowid

        # =========================
        # SUBIR ARCHIVO
        # =========================

        if archivo and archivo.filename != "":

            nombre_archivo = secure_filename(
                archivo.filename
            )

            ruta = os.path.join(
                UPLOAD_FOLDER,
                nombre_archivo
            )

            archivo.save(ruta)

            cursor.execute("""

                INSERT INTO archivos
                (
                    nombre,
                    ruta,
                    tarea_id
                )

                VALUES (%s, %s, %s)

            """, (

                nombre_archivo,
                ruta,
                tarea_id

            ))

            conn.commit()

        # =========================
        # BUSCAR ESTUDIANTE
        # =========================

        cursor.execute("""

            SELECT email
            FROM usuario
            WHERE id = %s

        """, (estudiante_id,))

        estudiante = cursor.fetchone()

        # =========================
        # ENVIAR CORREO
        # =========================

        if estudiante:

            asunto = "Nueva actividad"

            # =========================
            # HTML DEL CORREO
            # =========================

            html = correo_nueva_tarea(

                titulo,
                fecha,
                descripcion

            )

            # =========================
            # ENVIAR
            # =========================

            enviar_correo(

                estudiante[0],
                asunto,
                html

            )

        print("TAREA CREADA")

        return redirect("/tareas")

    except Exception as e:

        print("ERROR CREAR TAREA:", e)

        return f"Error al crear tarea: {e}"

    finally:

        if conn and conn.is_connected():
            conn.close()
# =========================
# ELIMINAR TAREA
# =========================
@app.route("/eliminar_tarea/<int:id>")
def eliminar_tarea(id):

    if "usuario_id" not in session:
        return redirect("/login")

    conn = get_db()

    try:

        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM tareas
            WHERE id = %s
            AND usuario_id = %s
        """, (

            id,
            session["usuario_id"]

        ))

        conn.commit()

        return redirect("/tareas")

    finally:

        conn.close()



# =========================
# COMPLETAR TAREA
# =========================

@app.route("/completar_tarea/<int:id>")
def completar_tarea(id):

    # =========================
    # VALIDAR SESIÓN
    # =========================

    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        conn = get_db()

        cursor = conn.cursor()

        # =========================
        # COMPLETAR TAREA
        # =========================

        cursor.execute("""
            UPDATE tareas
            SET estado = 'completada'
            WHERE id = %s
        """, (id,))

        conn.commit()

        print("TAREA COMPLETADA")

        return redirect("/tareas")

    except Exception as e:

        print("ERROR COMPLETAR TAREA:", e)

        return f"Error al completar tarea: {e}"

    finally:

        if conn and conn.is_connected():
            conn.close()

# =========================
# VER PDF / DESCARGAR
# =========================

@app.route("/descargar/<nombre>")
def descargar(nombre):

    try:

        return send_from_directory(
            UPLOAD_FOLDER,
            nombre
        )

    except Exception as e:

        return f"Error archivo: {e}"

# ------------------------
# REUNIONES
# ------------------------
@app.route("/reuniones")
def reuniones():

    # =========================
    # VALIDAR SESIÓN
    # =========================

    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        conn = get_db()

        cursor = conn.cursor()

        # =========================
        # PROFESOR
        # =========================

        if session["rol"] == "profesor":

            cursor.execute("""
                SELECT *
                FROM reuniones
                WHERE profesor_id = %s
                ORDER BY fecha ASC, hora ASC
            """, (session["usuario_id"],))

        # =========================
        # ESTUDIANTE
        # =========================

        else:

            cursor.execute("""
                SELECT r.*
                FROM reuniones r

                INNER JOIN reunion_participantes rp
                ON r.id = rp.reunion_id

                WHERE rp.usuario_id = %s

                ORDER BY r.fecha ASC, r.hora ASC
            """, (session["usuario_id"],))

        reuniones = cursor.fetchall()

        return render_template(
            "reuniones.html",
            reuniones=reuniones,
            rol=session["rol"]
        )

    except Exception as e:

        print("ERROR REUNIONES:", e)

        return "Error al cargar reuniones"

    finally:

        if conn and conn.is_connected():
            conn.close()

# =========================
# CREAR REUNIÓN
# =========================

@app.route("/crear_reunion", methods=["POST"])
def crear_reunion():



    # =========================
    # VALIDAR SESIÓN
    # =========================

    if "usuario_id" not in session:
        return redirect("/login")

    # =========================
    # DATOS FORMULARIO
    # =========================

    titulo = request.form["titulo"]

    descripcion = request.form["descripcion"]

    fecha = request.form["fecha"]

    hora = request.form["hora"]

    lugar = request.form["lugar"]

    participantes = request.form.getlist(
        "participantes"
    )

    conexion = get_db()

    cursor = conexion.cursor()

    # =========================
    # INSERTAR REUNIÓN
    # =========================

    cursor.execute("""
        INSERT INTO reuniones
        (
            titulo,
            descripcion,
            fecha,
            hora,
            lugar,
            profesor_id
        )

        VALUES (%s, %s, %s, %s, %s, %s)

    """, (

        titulo,
        descripcion,
        fecha,
        hora,
        lugar,
        session["usuario_id"]

    ))

    reunion_id = cursor.lastrowid

    # =========================
    # PARTICIPANTES
    # =========================

    for contacto_id in participantes:

        # =========================
        # BUSCAR USUARIO RELACIONADO
        # =========================

        cursor.execute("""

            SELECT usuario_relacionado

            FROM contactos

            WHERE id = %s

        """, (contacto_id,))

        usuario = cursor.fetchone()

        if usuario:

            usuario_id = usuario[0]

            # =========================
            # INSERTAR PARTICIPANTE
            # =========================

            cursor.execute("""

                INSERT INTO reunion_participantes
                (
                    reunion_id,
                    usuario_id,
                    estado
                )

                VALUES (%s, %s, %s)

            """, (

                reunion_id,
                usuario_id,
                "pendiente"

            ))

            # =========================
            # BUSCAR EMAIL
            # =========================

            cursor.execute("""

                SELECT email

                FROM usuario

                WHERE id = %s

            """, (usuario_id,))

            estudiante = cursor.fetchone()

            # =========================
            # ENVIAR CORREO
            # =========================
            print("ENVIANDO A:", estudiante[0])

            if estudiante:

                print("ENVIANDO A:", estudiante[0])
                asunto = "Nueva reunión programada"

                html = correo_nueva_reunion(

                    titulo,
                    fecha,
                    hora,
                    lugar,
                    descripcion

                )

                try:

                 enviar_correo(
                 estudiante[0],
                 asunto,
                 html
                 )

                except Exception as e:

                 print("ERROR EMAIL:", e)

    # =========================
    # GUARDAR CAMBIOS
    # =========================

    conexion.commit()

    conexion.close()

    print("REUNIÓN CREADA")

    return redirect("/agenda")

# =========================
# ACEPTAR REUNIÓN
# =========================

@app.route("/aceptar_reunion/<int:reunion_id>")
def aceptar_reunion(reunion_id):

    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        conn = get_db()

        cursor = conn.cursor()

        # VALIDAR SI YA RESPONDIÓ
        cursor.execute("""
            SELECT *
            FROM asistencia
            WHERE reunion_id = %s
            AND estudiante_id = %s
        """, (

            reunion_id,
            session["usuario_id"]

        ))

        existe = cursor.fetchone()

        # SI NO EXISTE -> INSERTAR
        if not existe:

            cursor.execute("""
                INSERT INTO asistencia
                (
                    reunion_id,
                    estudiante_id,
                    estado
                )

                VALUES (%s, %s, %s)
            """, (

                reunion_id,
                session["usuario_id"],
                "aceptado"

            ))

        else:

            # ACTUALIZAR
            cursor.execute("""
                UPDATE asistencia
                SET estado = %s
                WHERE reunion_id = %s
                AND estudiante_id = %s
            """, (

                "aceptado",
                reunion_id,
                session["usuario_id"]

            ))

        conn.commit()

        return redirect("/agenda")

    except Exception as e:

        print("ERROR ACEPTAR REUNION:", e)

        return "Error al aceptar reunión"

    finally:

        if conn and conn.is_connected():
            conn.close()


# =========================
# RECHAZAR REUNIÓN
# =========================

@app.route("/rechazar_reunion/<int:reunion_id>")
def rechazar_reunion(reunion_id):

    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        conn = get_db()

        cursor = conn.cursor()

        # VALIDAR SI YA EXISTE
        cursor.execute("""
            SELECT *
            FROM asistencia
            WHERE reunion_id = %s
            AND estudiante_id = %s
        """, (

            reunion_id,
            session["usuario_id"]

        ))

        existe = cursor.fetchone()

        # INSERTAR
        if not existe:

            cursor.execute("""
                INSERT INTO asistencia
                (
                    reunion_id,
                    estudiante_id,
                    estado
                )

                VALUES (%s, %s, %s)
            """, (

                reunion_id,
                session["usuario_id"],
                "rechazado"

            ))

        else:

            # ACTUALIZAR
            cursor.execute("""
                UPDATE asistencia
                SET estado = %s
                WHERE reunion_id = %s
                AND estudiante_id = %s
            """, (

                "rechazado",
                reunion_id,
                session["usuario_id"]

            ))

        conn.commit()

        return redirect("/agenda")

    except Exception as e:

        print("ERROR RECHAZAR REUNION:", e)

        return "Error al rechazar reunión"

    finally:

        if conn and conn.is_connected():
            conn.close()

# =========================================
# RESPONDER REUNION
# =========================================

@app.route("/asistencia/<int:reunion_id>/<estado>")
def asistencia(reunion_id, estado):

    if "usuario_id" not in session:
        return redirect("/login")

    conn = get_db()

    cursor = conn.cursor()

    try:

        comentario = request.args.get(
            "comentario",
            ""
        )

        # =====================================
        # ACTUALIZAR ESTADO
        # =====================================

        cursor.execute("""

            UPDATE reunion_participantes

            SET
                estado = %s,
                respuesta = %s

            WHERE reunion_id = %s
            AND usuario_id = %s

        """, (

            estado,
            comentario,
            reunion_id,
            session["usuario_id"]

        ))

        conn.commit()

        return redirect("/agenda")

    except Exception as e:

        print("ERROR ASISTENCIA:", e)

        return "Error al responder reunión"

    finally:

        conn.close()


@app.route("/agenda")
def agenda():

    # =========================
    # VALIDAR SESIÓN
    # =========================

    if "usuario_id" not in session:
        return redirect("/login")

    conn = None

    try:

        conn = get_db()

        cursor = conn.cursor()

        contactos = []

        # =========================
        # OBTENER MES Y AÑO
        # =========================

        hoy = datetime.now()

        mes = request.args.get("mes", type=int)
        anio = request.args.get("anio", type=int)

        if not mes:
            mes = hoy.month

        if not anio:
            anio = hoy.year

        # =========================
        # VALIDAR CAMBIO DE AÑO
        # =========================

        if mes < 1:
            mes = 12
            anio -= 1

        if mes > 12:
            mes = 1
            anio += 1

        # =========================
        # CONTACTOS PROFESOR
        # =========================

        if session["rol"] == "profesor":

            cursor.execute("""
                SELECT *
                FROM contactos
                WHERE usuario_id = %s
            """, (session["usuario_id"],))

            contactos = cursor.fetchall()

        # =========================
        # REUNIONES PROFESOR
        # =========================

        if session["rol"] == "profesor":

            cursor.execute("""

                SELECT

                    r.id,
                    r.titulo,
                    r.descripcion,
                    r.fecha,
                    r.hora,
                    r.lugar,

                    rp.estado,
                    rp.respuesta,

                    u.nombre

                FROM reuniones r

                LEFT JOIN reunion_participantes rp
                    ON r.id = rp.reunion_id

                LEFT JOIN usuario u
                    ON rp.usuario_id = u.id

                WHERE r.profesor_id = %s
                AND r.eliminada = 0
                AND MONTH(r.fecha) = %s
                AND YEAR(r.fecha) = %s

                ORDER BY r.fecha ASC,
                         r.hora ASC

            """, (

                session["usuario_id"],
                mes,
                anio

            ))

        # =========================
        # REUNIONES ESTUDIANTE
        # =========================

        else:

            cursor.execute("""

                SELECT

                    r.id,
                    r.titulo,
                    r.descripcion,
                    r.fecha,
                    r.hora,
                    r.lugar,

                    rp.estado,
                    rp.respuesta,

                    u.nombre

                FROM reuniones r

                INNER JOIN reunion_participantes rp
                    ON r.id = rp.reunion_id

                LEFT JOIN usuario u
                    ON rp.usuario_id = u.id

                WHERE rp.usuario_id = %s
                AND r.eliminada = 0
                AND MONTH(r.fecha) = %s
                AND YEAR(r.fecha) = %s

                ORDER BY r.fecha ASC,
                         r.hora ASC

            """, (

                session["usuario_id"],
                mes,
                anio

            ))

        reuniones_db = cursor.fetchall()

        # =========================
        # TAREAS DEL MES
        # =========================

        if session["rol"] == "profesor":

         cursor.execute("""

        SELECT

            id,
            titulo,
            descripcion,
            fecha

        FROM tareas

        WHERE usuario_id = %s
        AND MONTH(fecha) = %s
        AND YEAR(fecha) = %s

        ORDER BY fecha ASC

       """, (

        session["usuario_id"],
        mes,
        anio

        ))

        else:

         cursor.execute("""

        SELECT

            id,
            titulo,
            descripcion,
            fecha

        FROM tareas

        WHERE estudiante_id = %s
        AND MONTH(fecha) = %s
        AND YEAR(fecha) = %s

        ORDER BY fecha ASC

        """, (

        session["usuario_id"],
        mes,
        anio

        ))

        tareas_mes = cursor.fetchall()

        # =========================
        # EVENTOS JSON
        # =========================

        eventos = []

        for r in reuniones_db:

            eventos.append({

                "title": r[1],

                "start": f"{r[3]}T{r[4]}"

            })

        eventos_json = json.dumps(eventos)

        # =========================
        # CALENDARIO DINÁMICO
        # =========================

        calendario_mes = calendar.monthcalendar(
            anio,
            mes
        )

        # =========================
        # NOMBRE DEL MES
        # =========================

        meses_es = [

            "",
            "Enero",
            "Febrero",
            "Marzo",
            "Abril",
            "Mayo",
            "Junio",
            "Julio",
            "Agosto",
            "Septiembre",
            "Octubre",
            "Noviembre",
            "Diciembre"

        ]

        mes_actual = meses_es[mes]

        # =========================
        # MES ANTERIOR
        # =========================

        mes_anterior = mes - 1
        anio_anterior = anio

        if mes_anterior < 1:
            mes_anterior = 12
            anio_anterior -= 1

        # =========================
        # MES SIGUIENTE
        # =========================

        mes_siguiente = mes + 1
        anio_siguiente = anio

        if mes_siguiente > 12:
            mes_siguiente = 1
            anio_siguiente += 1

        # =========================
        # RENDER TEMPLATE
        # =========================

        return render_template(

            "agenda.html",

            contactos=contactos,

            reuniones=reuniones_db,

            eventos_json=eventos_json,

            calendario=calendario_mes,

            mes_actual=mes_actual,

            anio_actual=anio,

            mes=mes,

            reuniones_calendario=reuniones_db,

            mes_anterior=mes_anterior,
            anio_anterior=anio_anterior,

            mes_siguiente=mes_siguiente,
            anio_siguiente=anio_siguiente,

            tareas_mes=tareas_mes
        )

    except Exception as e:

        print("ERROR AGENDA:", e)

        return f"Error agenda: {e}"

    finally:

        if conn and conn.is_connected():
            conn.close()



@app.route("/editar_reunion/<int:id>", methods=["POST"])
def editar_reunion(id):

    if "usuario_id" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]
    fecha = request.form["fecha"]
    hora = request.form["hora"]
    lugar = request.form["lugar"]

    cursor.execute("""

        UPDATE reuniones
        SET
            titulo=%s,
            descripcion=%s,
            fecha=%s,
            hora=%s,
            lugar=%s

        WHERE id=%s

        """, (
  
        titulo,
        descripcion,
        fecha,
        hora,
        lugar,
        id

    ))

    conn.commit()
    conn.close()

    return redirect("/agenda")

@app.route("/eliminar_reunion/<int:id>")
def eliminar_reunion(id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE reuniones
        SET eliminada = 1
        WHERE id = %s

    """, (id,))

    conn.commit()
    conn.close()

    return redirect("/agenda")


if __name__ == "__main__":
    app.run(debug=True)