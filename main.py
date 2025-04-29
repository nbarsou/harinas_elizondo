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
import os
import json
from services.user_service import create_user, list_users
from services.client_service import create_client, list_clients
from services.inspection_service import create_inspection, list_inspections
from services.equipment_service import create_equipment, list_equipment


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
@app.route('/inspections/create', methods=['GET', 'POST'])
def register_inspection():
    if request.method == 'POST':
        # 1) Campos básicos
        numero_lote     = request.form['numero_lote']
        secuencia       = request.form['secuencia']
        tipo_inspeccion = request.form['tipo_inspeccion']
        fecha           = request.form['fecha']
        id_equipo       = int(request.form['id_equipo'])

        # 2) Construir lista de parámetros según el equipo
        lista_params = []
        if id_equipo == 1:
            # Alveógrafo
            lista_params = [
                {"parametro": "W",            "valor": float(request.form['valor_W'])},
                {"parametro": "P",            "valor": float(request.form['valor_P'])},
                {"parametro": "L",            "valor": float(request.form['valor_L'])},
                {"parametro": "relacion_P_L", "valor": float(request.form['valor_relacion_P_L'])},
            ]
        else:
            # Farinógrafo
            lista_params = [
                {"parametro": "absorcion_de_agua",    "valor": float(request.form['valor_absorcion_de_agua'])},
                {"parametro": "tiempo_de_desarrollo", "valor": float(request.form['valor_tiempo_de_desarrollo'])},
                {"parametro": "estabilidad",          "valor": float(request.form['valor_estabilidad'])},
                {"parametro": "indice_de_tolerancia", "valor": float(request.form['valor_indice_de_tolerancia'])},
            ]

        # 3) Serializar a JSON
        parametros_json = json.dumps(lista_params)

        # 4) Llamar al service
        try:
            create_inspection(
                numero_lote=numero_lote,
                fecha=fecha,
                id_equipo=id_equipo,
                secuencia=secuencia,
                tipo_inspeccion=tipo_inspeccion,
                parametros_analizados=parametros_json
            )
            flash('Inspección registrada con éxito', 'success')
            return redirect(url_for('list_inspections_route'))
        except Exception as e:
            flash(f'Error al registrar inspección: {e}', 'danger')
            return redirect(url_for('register_inspection'))

    # GET → mostrar formulario
    return render_template('create_inspection.html')


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
@app.route('/clients', methods=['GET'])
def list_clients_route():
    clients = list_clients()
    return render_template('clients.html', clients=clients)




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

