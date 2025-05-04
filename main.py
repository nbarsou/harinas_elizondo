# Importación de módulos de Flask necesarios para vistas, formularios, sesiones y autenticación
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user,
)
from functools import wraps
from flask import abort

# Inicialización de base de datos y servicios (lógica de negocio)
from db import init_db
from services.user_service import (
    create_user,
    get_user,
    list_users,
    update_user,
    delete_user,
    authenticate_user,
)
from services.client_service import (
    create_client,
    get_client,
    list_clients,
    update_client,
    deactivate_client,
    delete_client,
)
from services.inspection_service import (
    create_inspection,
    list_inspections,
    update_inspection,
    delete_inspection,
)
from services.equipment_service import (
    create_equipment,
    list_equipment,
    update_equipment,
    deactivate_equipment,
    delete_equipment,
)

# Inicializa la aplicación Flask
app = Flask(__name__)

# Configura el manejador de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sign_in"  # type: ignore
app.secret_key = "clave_super_secreta_y_unica_123"

# Clase que representa al usuario autenticado (usado por Flask-Login)
class User(UserMixin):
    def __init__(self, id_usuario, mail, rol, nombre):
        self.id = id_usuario
        self.mail = mail
        self.rol = rol
        self.nombre = nombre


# Carga los datos del usuario desde la base de datos usando su ID
@login_manager.user_loader
def load_user(user_id):
    user_data = get_user(user_id)
    if user_data:
        return User(
            id_usuario=user_data["id_usuario"],
            mail=user_data["mail"],
            rol=user_data["rol"],
            nombre=user_data["nombre"],
        )
    return None


# Decorador para restringir rutas a roles específicos
def role_required(*roles):
    """
    Gerencia de Control de Calidad
    Gerencia de laboratorio
    Gerencia de Aseguramiento de Calidad
    Gerente de Plantas
    Director de Operaciones
    Admin
    """

    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated or current_user.rol not in roles:
                return abort(403)
            return f(*args, **kwargs)

        return wrapped

    return decorator


# Inicializa la base de datos
init_db()

# Redirige la raíz a la pantalla de inicio de sesión
@app.route("/")
def home():
    return redirect(url_for("sign_in"))


# Ruta de inicio de sesión
@app.route("/signin", methods=["GET", "POST"])
def sign_in():
    if request.method == "POST":
        mail = request.form["mail"]
        contrasena = request.form["contrasena"]

        usuario = authenticate_user(mail, contrasena)  # ya la usas
        if usuario:
            user_obj = User(
                id_usuario=usuario["id_usuario"],
                mail=usuario["mail"],
                rol=usuario["rol"],
                nombre=usuario["nombre"],
            )
            login_user(user_obj)
            flash(f"Bienvenido/a {usuario['nombre']}", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Correo o contraseña incorrectos", "danger")

    return render_template("signin.html")


# Ruta principal (dashboard) después del login
@app.route("/dashboard")
@login_required
def dashboard():
    """
    Vista del dashboard principal.
    Muestra un resumen de la información relevante del sistema.
    """
    return render_template("dashboard.html")


# -----------------------------------
# CLIENTES
# -----------------------------------

# Registro de nuevos clientes
@app.route("/clients/create", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Director de Operaciones")
def register_client():
    if request.method == "POST":
        # Extrae los datos del formulario
        nombre = request.form["nombre"]
        rfc = request.form["rfc"]
        nombre_contacto = request.form["nombre_contacto"]
        correo_contacto = request.form["correo_contacto"]
        activo = bool(int(request.form["activo"]))
        requiere_cert = bool(int(request.form["requiere_certificado"]))
        use_custom = bool(int(request.form.get("use_custom_params", 0)))
        # Llama al servicio para crear el cliente
        try:
            create_client(
                nombre=nombre,
                rfc=rfc,
                nombre_contacto=nombre_contacto,
                correo_contacto=correo_contacto,
                activo=activo,
                requiere_certificado=requiere_cert,
                contrasena="changeme",  # Provisional
                motivo_baja=None,
                use_custom_params=use_custom,
                form_data=request.form,
            )
            flash("Cliente dado de alta correctamente", "success")
            return redirect(url_for("list_clients_route"))
        except Exception as e:
            flash(f"Error al dar de alta cliente: {e}", "danger")
            return redirect(url_for("register_client"))

    # GET: muestra el formulario
    return render_template("create_client.html")


# Listado de clientes
@app.route("/clients")
@login_required
def list_clients_route():
    clients = list_clients()
    return render_template("clients.html", clients=clients)


# Edición de cliente existente
@app.route("/clients/<int:id>/edit", methods=["POST"])
@login_required
@role_required("Admin", "Gerente de Operaciones")
def update_client_route(id):
    # Extrae datos y obtiene cliente original
    nombre = request.form["nombre"]
    rfc = request.form["rfc"]
    nombre_contacto = request.form["nombre_contacto"]
    correo_contacto = request.form["correo_contacto"]
    requiere_cert = bool(int(request.form["requiere_certificado"]))
    activo = bool(int(request.form["activo"]))

    original = get_client(id)
    if not original:
        flash("Cliente no encontrado", "danger")
        return redirect(url_for("list_clients_route"))

    motivo_baja = original.get("motivo_baja")
    configuracion_json = original.get("configuracion_json") or ""

    # Actualiza cliente
    try:
        updated = update_client(
            id,
            nombre,
            rfc,
            nombre_contacto,
            correo_contacto,
            requiere_cert,
            activo,
            motivo_baja,
            configuracion_json,
        )
        if updated:
            flash("Cliente actualizado correctamente", "success")
        else:
            flash("No se realizaron cambios", "info")
    except Exception as e:
        flash(f"Error al actualizar cliente: {e}", "danger")

    return redirect(url_for("list_clients_route"))


# Baja lógica del cliente (sin borrarlo de la BD)
@app.route("/clients/<int:id>/deactivate", methods=["POST"])
@login_required
@role_required("Admin", "Gerente de Operaciones")
def deactivate_client_route(id):
    motivo = request.form["motivo_baja"]
    try:
        deactivate_client(id, motivo)
        flash("Cliente dado de baja", "warning")
    except Exception as e:
        flash(f"Error al dar de baja cliente: {e}", "danger")
    return redirect(url_for("list_clients_route"))


# Eliminación permanente del cliente
@app.route("/clientes/delete/<int:client_id>", methods=["POST"])
@login_required
@role_required("Admin")
def delete_client_route(client_id):
    try:
        affected = delete_client(client_id)

        if affected == 1:
            flash("Cliente eliminado correctamente.", "success")
        else:
            flash("No se encontró el cliente a eliminar.", "warning")

    except Exception as e:
        flash(f"Error al eliminar el cliente: {e}", "danger")

    return redirect(
        url_for("list_clients_route")
    )  # Ajusta con tu nombre real de la vista


# -----------------------------------
# INSPECCIONES
# -----------------------------------

# Registro de nueva inspección
@app.route("/inspections/create", methods=["GET", "POST"])
@login_required
@role_required("Admin", "Gerencia de laboratorio", "Gerencia de Control de Calidad")
def register_inspection():
    if request.method == "POST":
        # Extrae datos del formulario
        numero_lote = request.form["numero_lote"]
        secuencia = request.form["secuencia"]
        tipo_inspeccion = request.form["tipo_inspeccion"]
        fecha = request.form["fecha"]
        id_equipo = request.form["id_equipo"]
        id_laboratorista = current_user.id  # type: ignore

        # Construye diccionario de parámetros analizados
        parametros_analizados = {}
        for key in request.form:
            if key.startswith("valor_") and request.form[key]:
                parametros_analizados[key[6:]] = float(request.form[key])
        # Crea inspección
        create_inspection(
            numero_lote=numero_lote,
            fecha=fecha,
            id_equipo=id_equipo,
            secuencia=secuencia,
            tipo_inspeccion=tipo_inspeccion,
            parametros_analizados=parametros_analizados,
            id_laboratorista=id_laboratorista,
        )

        flash("Inspección registrada correctamente.", "success")
        return redirect(url_for("list_inspections_route"))

    return render_template("create_inspection.html")


# Listado de inspecciones
# TODO: arreglar el query y como se registran
@app.route("/inspections")
@login_required
def list_inspections_route():
    inspections = list_inspections()
    print(inspections)  # Debug: Check what's being returned
    return render_template("inspections.html", inspections=inspections)


# Edición de inspección
@app.route("/inspections/<int:id>/edit", methods=["POST"])
@login_required
@role_required("Admin", "Gerencia de laboratorio", "Gerencia de Control de Calidad")
def edit_inspection(id):
    update_inspection(
        id_inspeccion=id,
        numero_lote=request.form["numero_lote"],
        fecha=request.form["fecha"],
        id_equipo=None,
        secuencia=request.form.get("secuencia"),
        parametros_analizados=None,
        tipo_inspeccion=request.form["tipo_inspeccion"],
        id_laboratorista=current_user.id,  # type: ignore
    )
    flash("Inspección actualizada correctamente.", "success")
    return redirect(url_for("list_inspections_route"))


# Eliminación de inspección
@app.route("/inspections/<int:id>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def delete_inspection_route(id):
    delete_inspection(id)
    flash("Inspección eliminada correctamente.", "success")
    return redirect(url_for("list_inspections_route"))


# -----------------------------------
# CERTIFICADOS
# -----------------------------------


@app.route("/certification")
def certification():
    """
    Vista de certificación.
    Permite gestionar la emisión de certificados de calidad basados en inspecciones.
    """
    return render_template("certification.html")


# -----------------------------------
# EQUIPOS DE LABORATORIO
# -----------------------------------

# Registro de nuevo equipo
@login_required
@role_required("Admin")
@app.route("/equipment/create", methods=["GET", "POST"])
def register_equipment():
    if request.method == "POST":
        try:
            create_equipment(
                tipo=request.form["tipo"],
                clave=request.form["clave"],
                marca=request.form["marca"],
                modelo=request.form["modelo"],
                serie=request.form["serie"],
                descripcion_larga=request.form["descripcion_larga"],
                descripcion_corta=request.form["descripcion_corta"],
                proveedor=request.form["proveedor"],
                fecha_adquisicion=request.form["fecha_adquisicion"],
                garantia=request.form["garantia"],
                vigencia_garantia=request.form["vigencia_garantia"],
                ubicacion=request.form["ubicacion"],
                encargado=int(request.form["encargado"]),
                estado=request.form["estado"],
                causa_baja=request.form["causa_baja"],
            )
            flash("Equipo registrado correctamente", "success")
            return redirect(url_for("list_equipment_route"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("create_equipment.html")


# Listado de equipos
@app.route("/equipment")
@login_required
def list_equipment_route():
    equipos = list_equipment()
    return render_template("equipment.html", equipos=equipos)


# Edición de equipo
@app.route("/equipos/<int:id>/edit", methods=["POST"])
@login_required
@role_required("Admin")
def edit_equipment(id):
    update_equipment(
        id_equipo=id,
        tipo=request.form["tipo"],
        clave=request.form.get("clave"),
        marca=request.form.get("marca"),
        modelo=request.form.get("modelo"),
        serie=request.form.get("serie"),
        descripcion_larga=request.form.get("descripcion_larga"),
        descripcion_corta=request.form.get("descripcion_corta"),
        proveedor=request.form.get("proveedor"),
        fecha_adquisicion=request.form.get("fecha_adquisicion"),
        garantia=request.form.get("garantia"),
        vigencia_garantia=request.form.get("vigencia_garantia"),
        ubicacion=request.form.get("ubicacion"),
        encargado=int(request.form["encargado"])
        if request.form.get("encargado")
        else None,
        estado=request.form.get("estado"),
        causa_baja=request.form.get("causa_baja"),
    )
    flash("Equipo actualizado correctamente.", "success")
    return redirect(url_for("list_equipment_route"))


# Baja lógica del equipo
@app.route("/equipos/<int:id>/deactivate", methods=["POST"])
@login_required
@role_required("Admin")
def deactivate_equipment_route(id):
    try:
        causa_baja = request.form.get("motivo_baja")

        if not causa_baja:
            flash("Debes proporcionar un motivo de baja.", "warning")
            return redirect(url_for("list_equipments_route"))

        affected = deactivate_equipment(id, causa_baja)

        if affected == 1:
            flash("Equipo dado de baja correctamente.", "success")
        else:
            flash("No se encontró el equipo o no se realizó ningún cambio.", "warning")

    except Exception as e:
        flash(f"Error al dar de baja el equipo: {e}", "danger")

    return redirect(url_for("list_equipment_route"))


# Eliminación definitiva de equipo
@app.route("/equipos/<int:id>/delete", methods=["POST"])
@login_required
@role_required("Admin")
def delete_equipment_route(id):
    affected = delete_equipment(id)

    if affected == 1:
        flash("Equipo eliminado correctamente.", "success")
    else:
        flash("No se encontró el equipo a eliminar.", "warning")

    return redirect(url_for("list_equipment_route"))


# -----------------------------------
# USUARIOS
# -----------------------------------

# Registro de nuevo usuario
@app.route("/users/create", methods=["GET", "POST"])
@login_required
@role_required("Admin")
def register_user():
    if request.method == "POST":
        nombre = request.form["nombre"]
        mail = request.form["mail"]
        contrasena = request.form["contrasena"]
        rol = request.form["rol"]
        try:
            new_id = create_user(mail, contrasena, rol, nombre)
            flash(f"Usuario creado con ID {new_id}", "success")
            return redirect(url_for("list_users_route"))
        except Exception as e:
            flash(f"Error al crear usuario: {e}", "danger")
            return redirect(url_for("register_user"))
    # GET
    return render_template("create_user.html")


# Listado de usuarios
@app.route("/users", methods=["GET"])
@login_required
def list_users_route():
    users = list_users()
    return render_template("users.html", users=users)


# Actualización de usuario
@app.route("/usuarios/update/<int:user_id>", methods=["POST"])
@login_required
@role_required("Admin")
def update_user_route(user_id):
    try:
        # Recoger datos del formulario
        mail = request.form["mail"]
        contrasena = request.form["contrasena"]
        rol = request.form["rol"]
        nombre = request.form["nombre"]

        affected = update_user(user_id, mail, contrasena, rol, nombre)

        if affected == 1:
            flash("Usuario actualizado correctamente.", "success")
        else:
            flash("No se encontró el usuario o no se realizaron cambios.", "warning")

    except Exception as e:
        flash(f"Error al actualizar el usuario: {e}", "danger")

    return redirect(url_for("list_users_route"))


# Eliminación de usuario
@app.route("/usuarios/delete/<int:user_id>", methods=["POST"])
@login_required
@role_required("Admin")
def delete_user_route(user_id):
    try:
        affected = delete_user(user_id)

        if affected == 1:
            flash("Usuario eliminado correctamente.", "success")
        else:
            flash("No se encontró el usuario a eliminar.", "warning")

    except Exception as e:
        flash(f"Error al eliminar el usuario: {e}", "danger")

    return redirect(url_for("list_users_route"))


# Punto de entrada del servidor
if __name__ == "__main__":
    app.run(debug=True)
