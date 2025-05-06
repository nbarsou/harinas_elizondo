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
from datetime import date


# Bibliotecas para mandar certificados
from xhtml2pdf import pisa  # falta en requirements
from io import BytesIO
import os

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
from services.address_service import (
    list_addresses,
    create_address,
    update_address,
    delete_address,
)

from services.inspection_service import (
    create_inspection,
    list_inspections,
    update_inspection,
    delete_inspection,
    get_all_inspections,
    get_inspection,
)
from services.equipment_service import (
    create_equipment,
    list_equipment,
    update_equipment,
    deactivate_equipment,
    delete_equipment,
)
from services.certificate_service import (
    list_certificates,
    delete_certificate,
    create_certificate,
)
from services.mail_service import send_certificate

# Inicializa la aplicación Flask
app = Flask(__name__)

# Configura el manejador de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "sign_in"  # type: ignore
app.secret_key = "75495d1095c8b21c5533b9e8b68e5fbae6f17f9cde886c6636eb2cea8bede721"

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


# -----------------------------------
# Usuarios
# -----------------------------------

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


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión exitosamente.", "info")
    return redirect(url_for("sign_in"))


# Ruta principal (dashboard) después del login
@app.route("/dashboard")
@login_required
@role_required("Admin", "Gerencia de Control de Calidad", "Gerencia de laboratorio","Gerencia de Aseguramiento de Calidad","Gerentes de Plantas", "Director de Operaciones")
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
@role_required("Admin", "Equipo de ventas", "Gerencia de Control de Calidad", "Gerencia de laboratorio")
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
@role_required("Admin", "Equipo de ventas", "Gerencia de Control de Calidad", "Gerencia de laboratorio")
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
@role_required("Admin", "Equipo de ventas", "Gerencia de Control de Calidad", "Gerencia de laboratorio")
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
# DIRECCIONES DE CLIENTE
# -----------------------------------

# (GET) Lista de direcciones de un cliente
@app.route("/clients/<int:id>/addresses", methods=["GET"])
@login_required
@role_required("Admin", "Director de Operaciones")
def list_addresses_route(id: int):
    cliente = get_client(id)
    if cliente is None:
        abort(404)
    direcciones = list_addresses(id)
    return render_template(
        "addresses.html",
        cliente=cliente,
        direcciones=direcciones,
    )


# (POST) Crear nueva dirección
@app.route("/clients/<int:id>/addresses/create", methods=["POST"])
@login_required
@role_required("Admin", "Director de Operaciones")
def create_address_route(id: int):
    try:
        create_address(
            id_cliente=id,
            calle=request.form["calle"],
            num_exterior=request.form.get("num_exterior"),
            num_interior=request.form.get("num_interior"),
            codigo_postal=request.form["codigo_postal"],
            delegacion=request.form["delegacion"],
            estado=request.form["estado"],
        )
        flash("Dirección agregada correctamente", "success")
    except Exception as e:
        flash(f"Error al agregar dirección: {e}", "danger")
    return redirect(url_for("list_addresses_route", id=id))


# (POST) Actualizar dirección existente
@app.route("/clients/<int:id>/addresses/update/<int:id_dir>", methods=["POST"])
@login_required
@role_required("Admin", "Director de Operaciones")
def update_address_route(id: int, id_dir: int):
    try:
        update_address(
            id_direccion=id_dir,
            calle=request.form["calle"],
            num_exterior=request.form.get("num_exterior"),
            num_interior=request.form.get("num_interior"),
            codigo_postal=request.form["codigo_postal"],
            delegacion=request.form["delegacion"],
            estado=request.form["estado"],
        )
        flash("Dirección actualizada", "info")
    except Exception as e:
        flash(f"Error al actualizar dirección: {e}", "danger")
    return redirect(url_for("list_addresses_route", id=id))


# (POST) Eliminar dirección
@app.route("/clients/<int:id>/addresses/delete/<int:id_dir>", methods=["POST"])
@login_required
@role_required("Admin", "Director de Operaciones")
def delete_address_route(id: int, id_dir: int):
    try:
        delete_address(id_dir)
        flash("Dirección eliminada", "warning")
    except Exception as e:
        flash(f"Error al eliminar dirección: {e}", "danger")
    return redirect(url_for("list_addresses_route", id=id))

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

    today = date.today().isoformat()  # o como calcules la fecha por defecto
    equipments = list_equipment()
    users = list_users()
    return render_template(
    "create_inspection.html",
    today=today,
    equipments=equipments,
    users=users
    )

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
# Eliminación de certificados
@app.route("/certificates/delete/<int:id>", methods=["POST"])
def delete_certificate_route(id):
    from services.certificate_service import delete_certificate

    delete_certificate(id)
    return redirect(url_for("certifications"))  # Usa 'certifications' como me dijiste


# Crear certificados
@app.route("/certifications/create", methods=["POST"])
def create_certificate_route():

    # 1. Leer datos del formulario
    form = request.form
    try:
        id_inspeccion = int(form["id_inspeccion"])
    except (KeyError, ValueError):
        flash("Inspección no válida", "danger")
        return redirect(url_for("certifications"))

    inspeccion = get_inspection(id_inspeccion)
    if not inspeccion:
        flash("Inspección no encontrada", "danger")
        return redirect(url_for("certifications"))

    # 2. Insertar en la base de datos
    try:
        cert_id = create_certificate(
            id_cliente=int(form.get("id_cliente", 0)),
            id_inspeccion=id_inspeccion,
            secuencia_inspeccion=form.get("secuencia_inspeccion", ""),
            orden_compra=form.get("orden_compra", ""),
            cantidad_solicitada=float(form.get("cantidad_solicitada") or 0),
            cantidad_entregada=float(form.get("cantidad_entregada") or 0),
            numero_factura=form.get("numero_factura", ""),
            fecha_envio=form.get("fecha_envio", ""),
            fecha_caducidad=form.get("fecha_caducidad", ""),
            resultados_analisis=inspeccion["parametros_analizados"],
            compara_referencias=form.get("compara_referencias", ""),
            desviaciones=form.get("desviaciones", ""),
            destinatario_correo=form.get("destinatario_correo", ""),
        )
    except Exception as e:
        flash(f"Error al crear certificado: {e}", "danger")
        return redirect(url_for("certifications"))

    # 3. Preparar datos para el PDF
    cert = {
        "id_certificado": cert_id,
        "id_cliente": int(form.get("id_cliente", 0)),
        "id_inspeccion": id_inspeccion,
        "secuencia_inspeccion": form.get("secuencia_inspeccion", ""),
        "orden_compra": form.get("orden_compra", ""),
        "cantidad_solicitada": form.get("cantidad_solicitada", ""),
        "cantidad_entregada": form.get("cantidad_entregada", ""),
        "numero_factura": form.get("numero_factura", ""),
        "fecha_envio": form.get("fecha_envio", ""),
        "fecha_caducidad": form.get("fecha_caducidad", ""),
        "resultados_analisis": inspeccion["parametros_analizados"],
        "compara_referencias": form.get("compara_referencias", ""),
        "desviaciones": form.get("desviaciones", ""),
        "destinatario_correo": form.get("destinatario_correo", ""),
    }

    # 4. Generar PDF desde template
    html = render_template("certificado_pdf.html", cert=cert)
    pdf_dir = os.path.join(os.path.dirname(__file__), "services", "certificados")
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_filename = f"certificado_{cert_id}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    with open(pdf_path, "wb") as pdf_file:
        pisa.CreatePDF(BytesIO(html.encode("utf-8")), dest=pdf_file)

    # 5. Enviar correo con el PDF
    try:
        send_certificate(cert["destinatario_correo"], pdf_filename)
        flash(f"Certificado #{cert_id} emitido y enviado por correo", "success")
    except Exception as e:
        flash(
            f"Certificado #{cert_id} emitido, pero fallo al enviar correo: {e}",
            "warning",
        )

    return redirect(url_for("certifications"))


# ---- Ver certificados ----
@app.route("/certification")
def certification():
    certificados = list_certificates()
    inspecciones = get_all_inspections()
    return render_template(
        "certifications.html", certificados=certificados, inspecciones=inspecciones
    )


# -----------------------------------
# EQUIPOS DE LABORATORIO
# -----------------------------------

# Registro de nuevo equipo
@login_required
@role_required("Admin", "Gerencia de laboratorio", "Gerencia de Control de Calidad")
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
    users = list_users()  
    return render_template("create_equipment.html", users=users)


# Listado de equipos
@app.route("/equipment")
@login_required
def list_equipment_route():
    equipos = list_equipment()
    return render_template("equipment.html", equipos=equipos)


# Edición de equipo
@app.route("/equipos/<int:id>/edit", methods=["POST"])
@login_required
@role_required("Admin", "Gerencia de laboratorio", "Gerencia de Control de Calidad")
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
@role_required("Admin", "Gerencia de laboratorio", "Gerencia de Control de Calidad")
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
@role_required("Admin", "Gerencia de Control de Calidad", "Gerencia de laboratorio","Gerencia de Aseguramiento de Calidad","Gerentes de Plantas", "Director de Operaciones")
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
@role_required("Admin", "Gerencia de Control de Calidad", "Gerencia de laboratorio")
def list_users_route():
    users = list_users()
    return render_template("users.html", users=users)


# Actualización de usuario
@app.route("/usuarios/update/<int:user_id>", methods=["POST"])
@login_required
@role_required("Admin","Gerencia de Control de Calidad", "Gerencia de laboratorio")
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
