# =========================
# CORREO NUEVA TAREA
# =========================

def correo_nueva_tarea(
    titulo,
    fecha,
    descripcion
):

    return f"""

    <html>

    <body style="
        background:#f4f6f9;
        font-family:Arial,sans-serif;
        padding:30px;
    ">

    <div style="
        max-width:700px;
        margin:auto;
        background:white;
        border-radius:18px;
        overflow:hidden;
        box-shadow:0 4px 15px rgba(0,0,0,0.08);
    ">

        <!-- HEADER -->

        <div style="
            background:#0b1b4d;
            padding:30px;
            text-align:center;
        ">

            <img
                src="cid:logo_plansync"
                width="220"
                style="display:block;margin:auto;"
            >

        </div>

        <!-- BANNER -->

        <div style="
            background:#1d4ed8;
            color:white;
            padding:35px;
            text-align:center;
        ">

            <h1 style="
                margin:0;
                font-size:32px;
            ">
                📚 Nueva tarea asignada
            </h1>

            <p style="
                margin-top:12px;
                font-size:16px;
            ">
                PlanSync - Gestión académica inteligente
            </p>

        </div>

        <!-- CONTENIDO -->

        <div style="padding:40px;">

            <p style="
                color:#334155;
                font-size:16px;
            ">
                Tienes una nueva actividad asignada:
            </p>

            <div style="
                background:#f8fafc;
                padding:25px;
                border-radius:12px;
                border:1px solid #e2e8f0;
                margin-top:20px;
            ">

                <p>
                    <b>📌 Título:</b>
                    {titulo}
                </p>

                <p>
                    <b>📅 Fecha:</b>
                    {fecha}
                </p>

                <p>
                    <b>📝 Descripción:</b>
                    {descripcion}
                </p>

            </div>

        </div>

        <!-- FOOTER LOGOS -->

        <div style="
            text-align:center;
            padding:20px;
            background:#ffffff;
        ">

            <img
                src="cid:logo_uni"
                width="180"
            >

        </div>

        <!-- FOOTER -->

        <div style="
            background:#0b1b4d;
            color:white;
            text-align:center;
            padding:20px;
            font-size:14px;
        ">

            © 2026 PlanSync

        </div>

    </div>

    </body>

    </html>

    """


# =========================
# CORREO NUEVA REUNIÓN
# =========================

def correo_nueva_reunion(
    titulo,
    fecha,
    hora,
    lugar,
    descripcion
):

    return f"""

    <html>

    <body style="
        background:#f4f6f9;
        font-family:Arial,sans-serif;
        padding:30px;
    ">

    <div style="
        max-width:700px;
        margin:auto;
        background:white;
        border-radius:18px;
        overflow:hidden;
        box-shadow:0 4px 15px rgba(0,0,0,0.08);
    ">

        <!-- HEADER -->

        <div style="
            background:#0b1b4d;
            padding:30px;
            text-align:center;
        ">

            <img
                src="cid:logo_plansync"
                width="220"
                style="display:block;margin:auto;"
            >

        </div>

        <!-- BANNER -->

        <div style="
            background:#16a34a;
            color:white;
            padding:35px;
            text-align:center;
        ">

            <h1 style="
                margin:0;
                font-size:32px;
            ">
                📅 Nueva reunión programada
            </h1>

        </div>

        <!-- CONTENIDO -->

        <div style="padding:40px;">

            <p style="
                color:#334155;
                font-size:16px;
            ">
                Se ha programado una nueva reunión en PlanSync.
            </p>

            <div style="
                background:#f8fafc;
                padding:25px;
                border-radius:12px;
                border:1px solid #e2e8f0;
                margin-top:20px;
            ">

                <p><b>📌 Título:</b> {titulo}</p>

                <p><b>📅 Fecha:</b> {fecha}</p>

                <p><b>⏰ Hora:</b> {hora}</p>

                <p><b>📍 Lugar:</b> {lugar}</p>

                <p><b>📝 Descripción:</b> {descripcion}</p>

            </div>

        </div>

        <!-- FOOTER LOGOS -->

        <div style="
            text-align:center;
            padding:20px;
            background:#ffffff;
        ">

            <img
                src="cid:logo_uni"
                width="180"
            >

        </div>

        <!-- FOOTER -->

        <div style="
            background:#0b1b4d;
            color:white;
            text-align:center;
            padding:20px;
            font-size:14px;
        ">

            © 2026 PlanSync

        </div>

    </div>

    </body>

    </html>

    """


# =========================
# CORREO RECORDATORIO
# =========================

def correo_recordatorio(
    titulo,
    fecha,
    hora
):

    return f"""

    <html>

    <body style="
        background:#f4f6f9;
        font-family:Arial,sans-serif;
        padding:30px;
    ">

    <div style="
        max-width:700px;
        margin:auto;
        background:white;
        border-radius:18px;
        overflow:hidden;
        box-shadow:0 4px 15px rgba(0,0,0,0.08);
    ">

        <!-- HEADER -->

        <div style="
            background:#0b1b4d;
            padding:30px;
            text-align:center;
        ">

            <img
                src="cid:logo_plansync"
                width="220"
                style="display:block;margin:auto;"
            >

        </div>

        <!-- BANNER -->

        <div style="
            background:#f59e0b;
            color:white;
            padding:35px;
            text-align:center;
        ">

            <h1 style="
                margin:0;
                font-size:32px;
            ">
                ⏰ Recordatorio de reunión
            </h1>

        </div>

        <!-- CONTENIDO -->

        <div style="padding:40px;">

            <p style="
                color:#334155;
                font-size:16px;
            ">
                Tienes una reunión próxima:
            </p>

            <div style="
                background:#f8fafc;
                padding:25px;
                border-radius:12px;
                border:1px solid #e2e8f0;
                margin-top:20px;
            ">

                <p><b>📌 Reunión:</b> {titulo}</p>

                <p><b>📅 Fecha:</b> {fecha}</p>

                <p><b>🕓 Hora:</b> {hora}</p>

            </div>

        </div>

        <!-- FOOTER LOGOS -->

        <div style="
            text-align:center;
            padding:20px;
            background:#ffffff;
        ">

            <img
                src="cid:logo_uni"
                width="180"
            >

        </div>

        <!-- FOOTER -->

        <div style="
            background:#0b1b4d;
            color:white;
            text-align:center;
            padding:20px;
            font-size:14px;
        ">

            © 2026 PlanSync

        </div>

    </div>

    </body>

    </html>

    """
