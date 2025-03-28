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

from flask import Flask, render_template

app = Flask(__name__)

# ---- SIGN IN ----
@app.route("/signin")
def sign_in():
    """
    Vista de inicio de sesión.
    Muestra el formulario para iniciar sesión en el sistema.
    """
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
@app.route("/inspection")
def inspection():
    """
    Vista de inspecciones.
    Permite visualizar y gestionar las inspecciones realizadas en los equipos.
    """
    return render_template("inspection.html")


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
@app.route("/users")
def users():
    """
    Vista de usuarios.
    Permite la gestión de los usuarios con acceso al sistema.
    """
    return render_template("users.html")


if __name__ == "__main__":
    app.run(debug=True)
