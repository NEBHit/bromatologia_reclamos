import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import html

load_dotenv()

# Configuraciones tomadas directamente del .env
SMTP_SERVER = os.getenv("MAIL_SERVER", "172.16.0.249")
SMTP_PORT = int(os.getenv("MAIL_PORT", 25))
#REMITENTE = os.getenv("MAIL_FROM", "gestionambiental@9dejulio.gov.ar")
REMITENTE = os.getenv("MAIL_FROM", "nidia@9dejulio.gov.ar")

def enviar_notificacion_expediente(
    destinatario: str,
    nombre_completo: str,
    nro_expediente: str,
    comercio: str,
    descripcion: str,
):
    """
    Función requerida por el router al crear un reclamo vecinal.
    """
    # Sanitizar entradas del usuario
    nombre_completo = html.escape(nombre_completo or "")
    comercio = html.escape(comercio or "")
    descripcion = html.escape(descripcion or "")

    encabezadoMail = """
    <h3>
    MUNICIPALIDAD DE 9 DE JULIO - DIRECCION DE BROMATOLOGIA <br>
    </h3>
    <p>
    <h3>
    RECLAMO BROMATOLOGICO <br>
    </h3>
    <hr>
    """

    footerMail = """
    <hr>
    <p>
    Líneas Rotativas: 2317 - 610000<br>
    Interno: 243 - Oficina de Bromatología
    </p>
    Municipalidad de 9 de Julio - 
    Dirección de Sistemas de Información
    """
    
    asunto = f"Confirmación de Reclamo - Expediente N° {nro_expediente}"
    
    body = f"""
    {encabezadoMail}

    <p>Estimado/a <strong>{nombre_completo}</strong>,</p>
    <p>Su reclamo ha sido recibido e ingresado satisfactoriamente al sistema.</p>
    
    <div style="background-color: #f8f9fa; border-left: 4px solid #0d6efd; padding: 12px; margin: 15px 0;">
        <p style="margin: 0; font-size: 1.1em;">
        <strong>Número de Expediente:</strong> <span style="color: #0d6efd;">{nro_expediente}</span>
        </p>
    </div>

    <p><strong>Comercio / Lugar:</strong> {comercio}</p>
    <p><strong>Detalle registrado:</strong> {descripcion}</p>

    <p style="font-size: 0.9em; color: #666; margin-top: 20px;">
        Conserve este número de expediente para consultar el estado del trámite en el portal vecinal.
    </p>

    <hr style="border: none; border-top: 1px solid #eee; margin-top: 25px;">
    <p style="font-size: 0.8em; color: #888; text-align: center;">
        Este es un correo automático, por favor no responda a esta dirección.
    </p>
    {footerMail}
    """
    
    msg = MIMEMultipart("alternative")
    msg["From"] = REMITENTE
    msg["To"] = destinatario
    #msg["Bcc"] = REMITENTE  
    msg["Subject"] = asunto

    # Versión texto plano de respaldo
    cuerpo_plano = (
        f"Hola {nombre_completo},\n\n"
        f"Su reclamo ha sido registrado con el Expediente N° {nro_expediente}.\n"
        f"Comercio/Lugar: {comercio}\n"
        f"Detalle: {descripcion}\n\n"
        f"Dirección de Bromatología"
    )

    msg.attach(MIMEText(cuerpo_plano, "plain"))
    msg.attach(MIMEText(body, "html"))

    try:
        # Conexión directa al relay interno: sin STARTTLS y sin login
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=15) as server:
            # send_message toma automáticamente To, Cc y Bcc para el sobre SMTP
            server.send_message(msg)
        print(f"✅ Correo enviado exitosamente a {destinatario} (con copia a {REMITENTE}) para el expte {nro_expediente}")
    except Exception as e:
        print(f"⚠️ Error al enviar correo en relay: {e}")