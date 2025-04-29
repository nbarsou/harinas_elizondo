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
import os, json
from services.user_service import create_user, list_users, authenticate_user
from services.client_service import create_client, list_clients, get_client, update_client, deactivate_client 
from services.inspection_service import create_inspection, list_inspections
from services.equipment_service import create_equipment, list_equipment



app = Flask(__name__)
app.secret_key = (
    "cualquier_clave_secreta_para_session"  # necesaria para flash y session
)

# Database
init_db()

# ---- SIGN IN ----
@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    if request.method == 'POST':
        mail = request.form['mail']
        contrasena = request.form['contrasena']
        
        usuario = authenticate_user(mail, contrasena)
        
        if usuario:
            session['user_id'] = usuario['id_usuario']
            session['nombre'] = usuario['nombre']
            flash(f"Bienvenido/a {usuario['nombre']}", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
    
    return render_template('signin.html')


# ---- DASHBOARD ----
@app.route("/dashboard")
def dashboard():
    """
    Vista del dashboard principal.
    Muestra un resumen de la información relevante del sistema.
    """
    return render_template("dashboard.html")


# ---- INSPECTION ----
@app.route('/inspections/create', methods=['GET', 'POST'])
def register_inspection():
    if 'user_id' not in session:
        flash("Debes iniciar sesión primero.", "danger")
        return redirect(url_for('sign_in'))

    if request.method == 'POST':
        numero_lote = request.form['numero_lote']
        secuencia = request.form['secuencia']
        tipo_inspeccion = request.form['tipo_inspeccion']
        fecha = request.form['fecha']
        id_equipo = request.form['id_equipo']
        id_laboratorista = session['user_id']
        
        parametros_analizados = {}
        for key in request.form:
            if key.startswith('valor_') and request.form[key]:
                parametros_analizados[key[6:]] = float(request.form[key])

        create_inspection(
            numero_lote=numero_lote,
            fecha=fecha,
            id_equipo=id_equipo,
            secuencia=secuencia,
            tipo_inspeccion=tipo_inspeccion,
            parametros_analizados=parametros_analizados,
            id_laboratorista=id_laboratorista
        )

        flash("Inspección registrada correctamente.", "success")
        return redirect(url_for('list_inspections_route'))

    return render_template('create_inspection.html')

@app.route('/inspections')
def list_inspections_route():
    if 'user_id' not in session:
        return redirect(url_for('sign_in'))

    inspections = list_inspections()
    return render_template('inspections.html', inspections=inspections)


# ---- CERTIFICATION ----
@app.route("/certification")
def certification():
    """
    Vista de certificación.
    Permite gestionar la emisión de certificados de calidad basados en inspecciones.
    """
    return render_template("certification.html")


# ---- EQUIPMENT ----
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
            return redirect(url_for("equipment"))
        except Exception as e:
            flash(f"Error: {e}", "danger")
    return render_template("create_equipment.html")

# ---- EQUIPMENT: Ver equipos registrados ----
@app.route("/equipment")
def equipment():
    equipos = list_equipment()
    return render_template("equipment.html", equipos=equipos)

from services.client_service import create_client, list_clients

# ---- CLIENTS: Alta de cliente ----
@app.route('/clients/create', methods=['GET', 'POST'])
def register_client():
    if request.method == 'POST':
        # Extraemos campos básicos
        nombre           = request.form['nombre']
        rfc              = request.form['rfc']
        nombre_contacto  = request.form['nombre_contacto']
        correo_contacto  = request.form['correo_contacto']
        activo           = bool(int(request.form['activo']))
        requiere_cert    = bool(int(request.form['requiere_certificado']))
        use_custom       = bool(int(request.form.get('use_custom_params', 0)))
        # Llamamos al servicio (le pasamos todo el form si necesita los params)
        try:
            create_client(
                nombre=nombre,
                rfc=rfc,
                nombre_contacto=nombre_contacto,
                correo_contacto=correo_contacto,
                activo=activo,
                requiere_certificado=requiere_cert,
                contrasena="changeme",            # Provisional
                motivo_baja=None,
                use_custom_params=use_custom,
                form_data=request.form
            )
            flash('Cliente dado de alta correctamente', 'success')
            return redirect(url_for('list_clients_route'))
        except Exception as e:
            flash(f'Error al dar de alta cliente: {e}', 'danger')
            return redirect(url_for('register_client'))

    # GET → renderizamos el formulario
    return render_template('create_client.html')


# ---- CLIENTS: Ver clientes registrados ----
@app.route('/clients')
def list_clients_route():
    clients = list_clients()
    return render_template('clients.html', clients=clients)

# ---- CLIENTS: Modificar clientes registrados ----
@app.route('/clients/<int:id>/edit', methods=['POST'])
def update_client_route(id):
    # 2.1) Lee los campos enviados por el formulario
    nombre          = request.form['nombre']
    rfc             = request.form['rfc']
    nombre_contacto = request.form['nombre_contacto']
    correo_contacto = request.form['correo_contacto']
    requiere_cert   = bool(int(request.form['requiere_certificado']))
    activo          = bool(int(request.form['activo']))  # viene del hidden

    # 2.2) Recupera el cliente original para obtener motivo_baja y config JSON
    original = get_client(id)
    if not original:
        flash('Cliente no encontrado', 'danger')
        return redirect(url_for('list_clients_route'))

    motivo_baja          = original.get('motivo_baja')
    configuracion_json   = original.get('configuracion_json')

    # 2.3) Llama al servicio con todos los parámetros
    try:
        updated = update_client(
            id,
            nombre,
            rfc,
            nombre_contacto,
            correo_contacto,
            requiere_cert,       # orden igual al de la firma: requiere_certificado
            activo,
            motivo_baja,
            configuracion_json
        )
        if updated:
            flash('Cliente actualizado correctamente', 'success')
        else:
            flash('No se realizaron cambios', 'info')
    except Exception as e:
        flash(f'Error al actualizar cliente: {e}', 'danger')

    return redirect(url_for('list_clients_route'))

# ---- CLIENTS: Dar de baja clientes registrados ----
@app.route('/clients/<int:id>/deactivate', methods=['POST'])
def deactivate_client_route(id):
    motivo = request.form['motivo_baja']
    try:
        deactivate_client(id, motivo)
        flash('Cliente dado de baja', 'warning')
    except Exception as e:
        flash(f'Error al dar de baja cliente: {e}', 'danger')
    return redirect(url_for('list_clients_route'))


# ---- USERS ----
@app.route('/users/create', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        nombre    = request.form['nombre']
        mail      = request.form['mail']
        contrasena= request.form['contrasena']
        rol       = request.form['rol']
        try:
            new_id = create_user(mail, contrasena, rol, nombre)
            flash(f'Usuario creado con ID {new_id}', 'success')
            return redirect(url_for('list_users_route'))
        except Exception as e:
            flash(f'Error al crear usuario: {e}', 'danger')
            return redirect(url_for('register_user'))
    # GET
    return render_template('create_user.html')

# Ruta para LISTAR usuarios
@app.route('/users', methods=['GET'])
def list_users_route():
    users = list_users()
    return render_template('users.html', users=users)


if __name__ == "__main__":
    app.run(debug=True)

