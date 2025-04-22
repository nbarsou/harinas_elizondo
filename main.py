"""
Punto de entrada principal para la aplicación Flask.

Define las rutas principales de la aplicación y maneja la carga de vistas para:
- Inicio de sesión (Sign In)
- Dashboard
- Inspecciones
- Certificación
- Equipos
- Clientes
- Usuarios
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session

from db import init_db
from services.user_service import create_user, list_users
from services.inspection_service import create_inspection, list_inspections


app = Flask(__name__)
app.secret_key = (
    "cualquier_clave_secreta_para_session"  # necesaria para flash y session
)

# Database
init_db()

# ---- SIGN IN ----
@app.route("/signin", methods=["GET", "POST"])
def sign_in():
    """
    Inicio de sesión con correo y contraseña.
    GET  -> muestra el formulario actualizado.
    POST -> valida contra la tabla USUARIO:
             - mail
             - contrasena
           Si coincide, guarda session y redirige a dashboard.
           Si falla, muestra flash de error.
    """
    if request.method == "POST":
        mail = request.form["mail"].strip().lower()
        contrasena = request.form["contrasena"].strip()

        # Buscamos usuario válido
        usuario = None
        for u in list_users():
            if u["mail"].lower() == mail and u["contrasena"] == contrasena:
                usuario = u
                break

        if usuario:
            session["user_id"] = usuario["id_usuario"]
            session["user_name"] = usuario["nombre"]
            return redirect(url_for("dashboard"))
        else:
            flash("Correo o contraseña incorrectos", "danger")

    return render_template("signin.html")


# ---- DASHBOARD ----
@app.route("/dashboard")
def dashboard():
    """
    Vista del dashboard principal.
    Muestra un resumen de la información relevante del sistema.
    """
    return render_template("dashboard.html")


# ---- INSPECTION ----
@app.route("/inspections/create", methods=["GET", "POST"])
def register_inspection():
    if request.method == "POST":
        # 1) Datos generales
        numero_lote = request.form["numero_lote"]
        secuencia = request.form["secuencia"]
        tipo_inspeccion = request.form["tipo_inspeccion"]
        fecha = request.form["fecha"]
        id_equipo = int(request.form["id_equipo"])

        # 2) Extraer parámetros según equipo
        parámetros = []
        if id_equipo == 1:
            # Alveógrafo
            parámetros = [
                {"parametro": "W", "valor": float(request.form["valor_W"])},
                {"parametro": "P", "valor": float(request.form["valor_P"])},
                {"parametro": "L", "valor": float(request.form["valor_L"])},
                {
                    "parametro": "relacion_P_L",
                    "valor": float(request.form["valor_relacion_P_L"]),
                },
            ]
        elif id_equipo == 2:
            # Farinógrafo
            parámetros = [
                {
                    "parametro": "absorcion_de_agua",
                    "valor": float(request.form["valor_absorcion_de_agua"]),
                },
                {
                    "parametro": "tiempo_de_desarrollo",
                    "valor": float(request.form["valor_tiempo_de_desarrollo"]),
                },
                {
                    "parametro": "estabilidad",
                    "valor": float(request.form["valor_estabilidad"]),
                },
                {
                    "parametro": "indice_de_tolerancia",
                    "valor": float(request.form["valor_indice_de_tolerancia"]),
                },
            ]
        else:
            flash("Equipo inválido", "danger")
            return redirect(url_for("register_inspection"))

        # 3) Llamar al service
        try:
            create_inspection(
                numero_lote=numero_lote,
                secuencia=secuencia,
                tipo_inspeccion=tipo_inspeccion,
                fecha=fecha,
                id_equipo=id_equipo,
                parametros=parámetros,
            )
            flash("Inspección registrada con éxito", "success")
            return redirect(url_for("list_inspections_route"))
        except Exception as e:
            flash(f"Error al registrar inspección: {e}", "danger")

    # En GET simplemente renderiza el formulario
    return render_template("create_inspection.html")


# ---- INSPECTION: Ver inspecciones registradas ----
@app.route("/inspections", methods=["GET"])
def list_inspections_route():
    # 1) Obtiene todas las inspecciones
    inspections = list_inspections()
    # 2) Renderiza la plantilla con la lista
    return render_template("inspections.html", inspections=inspections)


# ---- CERTIFICATION ----
@app.route("/certification")
def certification():
    """
    Vista de certificación.
    Permite gestionar la emisión de certificados de calidad basados en inspecciones.
    """
    return render_template("certification.html")


# ---- EQUIPMENT ----
@app.route("/equipment")
def equipment():
    """
    Vista de equipos.
    Permite la administración de los equipos de laboratorio.
    """
    return render_template("equipment.html")


# ---- CLIENTS ----
@app.route("/clients")
def clients():
    """
    Vista de clientes.
    Permite la administración de los registros de clientes en el sistema.
    """
    return render_template("clients.html")


# ---- USERS ----
@app.route("/users/create", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
        # Extrae los campos del form
        nombre = request.form["nombre"]
        mail = request.form["mail"]
        contrasena = request.form["contrasena"]
        rol = request.form["rol"]
        rfc = request.form["rfc"]
        domicilio = request.form["domicilio"]
        nombre_contacto = request.form["nombre_contacto"]
        requiere_cert = request.form["requiere_certificado"] == "1"
        use_custom = request.form.get("use_custom_params") == "1"

        try:
            # create_client es tu función que internamente construye el JSON
            # y hace el INSERT en la tabla USUARIO/CLIENTE
            create_client(
                nombre=nombre,
                mail=mail,
                contrasena=contrasena,
                rol=rol,
                rfc=rfc,
                domicilio=domicilio,
                nombre_contacto=nombre_contacto,
                requiere_certificado=requiere_cert,
                use_custom_params=use_custom,
                form_data=request.form,  # pásale todo el form para que arme el JSON
            )
            flash("Usuario creado correctamente", "success")
            return redirect(url_for("list_users_route"))
        except Exception as e:
            flash(f"Error al crear usuario: {e}", "danger")
            return redirect(url_for("register_user"))

    # GET → muestra el formulario create_user.html
    return render_template("create_user.html")


# ---- USERS / CLIENTS: Listado ----
@app.route("/users", methods=["GET"])
def list_users_route():
    users = (
        list_users()
    )  # lista ya con todos los campos incl. RFC, domicilio, contacto, certificado…
    return render_template("users.html", users=users)


if __name__ == "__main__":
    app.run(debug=True)
