import os
import json
import smtplib
import ssl
from email.message import EmailMessage

# ---- Configuración de Zoho Mail ----
SMTP_SERVER = "smtp.zoho.com"
SMTP_PORT = 465                 # SSL
SMTP_USER = "harinas_elizondo@zohomail.com"
SMTP_PASS = "31xmQfgZHy79"     # App Password de Zoho (para pruebas)


def send_certificate(correo_cliente: str, nombre_archivo: str) -> None:
    """
    Envía un archivo .pdf a correo_cliente y al correo de almacén.

    Parámetros:
    - correo_cliente: dirección de correo del cliente.
    - nombre_archivo: nombre del archivo .pdf (p.e. "certificado_123.pdf"),
      ubicado en la carpeta 'certificados/'.
    """

    # 1) Cargar correo de almacén desde JSON
    json_path = os.path.join(os.path.dirname(__file__), "correo_almacen.json")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    correo_almacen = data.get("correo_almacen")
    if not correo_almacen:
        raise ValueError("No se encontró 'correo_almacen' en correo_almacen.json")

    # 2) Leer el archivo 
    certs_dir = os.path.join(os.path.dirname(__file__), "certificados")
    file_path = os.path.join(certs_dir, nombre_archivo)
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"No existe el archivo: {file_path}")
    with open(file_path, "rb") as fp:
        file_data = fp.read()

    # 3) Construir el mensaje
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = ", ".join([correo_cliente, correo_almacen])
    msg["Subject"] = f"Envío de certificado: {nombre_archivo}"
    msg.set_content(
        f"Hola,\n\nAdjunto encontrarás el certificado '{nombre_archivo}'.\n\nSaludos."
    )

    # Adjuntar el archivo txt
    '''msg.add_attachment(
        file_data,
        maintype="text",
        subtype="plain",
        filename=nombre_archivo
    )'''

    #Adjuntar un archivo pdf
    msg.add_attachment(
        file_data,
        maintype="application",
        subtype="pdf",
        filename=nombre_archivo
    )


    # 4) Enviar por SMTP (Zoho Mail) usando SSL
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)

    print(f"Correo enviado a: {correo_cliente} y {correo_almacen}")


# Ejemplo de uso (descomenta para probar):
#if __name__ == "__main__":
    #send_certificate("brunoravelo2525@gmail.com", "archivo.pdf")
