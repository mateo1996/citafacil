
"""
Servicio de envío de correos electrónicos de CitaFácil.

Funcionalidades:
    - Verificación de correo electrónico.
    - Recuperación de contraseña.
"""

import smtplib
from html import escape
from urllib.parse import urlencode
from email.message import EmailMessage

from config import settings


# =====================================================
# CONFIGURACIÓN SMTP
# =====================================================

MAIL_SERVER = settings.MAIL_SERVER
MAIL_PORT = settings.MAIL_PORT
MAIL_USE_TLS = settings.MAIL_USE_TLS
MAIL_USERNAME = settings.MAIL_USERNAME
MAIL_PASSWORD = settings.MAIL_PASSWORD
MAIL_DEFAULT_SENDER = settings.MAIL_DEFAULT_SENDER
FRONTEND_URL = settings.FRONTEND_URL.rstrip("/")


# =====================================================
# FUNCIÓN INTERNA PARA ENVIAR CORREOS
# =====================================================

def _send_email(to_email, subject, text_content, html_content):
    """
    Envía un correo electrónico utilizando SMTP.

    Args:
        to_email: Correo del destinatario.
        subject: Asunto del correo.
        text_content: Contenido en texto plano.
        html_content: Contenido HTML.
    """

    if not MAIL_SERVER or not MAIL_USERNAME or not MAIL_PASSWORD:
        raise RuntimeError(
            "Falta configurar el servidor SMTP o sus credenciales."
        )

    if not MAIL_DEFAULT_SENDER:
        raise RuntimeError(
            "Falta configurar MAIL_DEFAULT_SENDER."
        )

    message = EmailMessage()

    message["From"] = MAIL_DEFAULT_SENDER
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(text_content)
    message.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP(
            MAIL_SERVER,
            MAIL_PORT,
            timeout=30
        ) as server:

            server.ehlo()

            if MAIL_USE_TLS:
                server.starttls()
                server.ehlo()

            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(message)

        return True

    except smtplib.SMTPAuthenticationError as error:
        raise RuntimeError(
            "El proveedor de correo rechazó las credenciales SMTP."
        ) from error

    except (smtplib.SMTPException, OSError) as error:
        raise RuntimeError(
            f"No fue posible enviar el correo: {error}"
        ) from error


# =====================================================
# VERIFICACIÓN DE CORREO ELECTRÓNICO
# =====================================================

def send_verification_email(to_email, user_name, verification_token):
    """
    Envía un enlace para verificar el correo electrónico.
    """

    verification_url = (
        f"{FRONTEND_URL}/verify-email?"
        f"{urlencode({'token': verification_token})}"
    )

    safe_name = escape(user_name)
    safe_url = escape(verification_url, quote=True)

    subject = "Verificación de cuenta - CitaFácil"

    text_content = f"""
Hola {user_name}.

Gracias por registrarte en CitaFácil.

Para verificar tu correo electrónico, ingresa al siguiente enlace:

{verification_url}

Este enlace es temporal.

Si no realizaste este registro, puedes ignorar este mensaje.

Saludos,
Equipo CitaFácil
"""

    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Verificación de cuenta</title>
</head>

<body style="
    margin: 0;
    padding: 30px;
    background: #f3f4f6;
    font-family: Arial, sans-serif;
">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0"
       style="background: #ffffff; border-radius: 10px;">

<tr>
<td style="
    padding: 30px;
    text-align: center;
    background: #2563eb;
    color: white;
">
    <h1>CitaFácil</h1>
    <p>Verificación de cuenta</p>
</td>
</tr>

<tr>
<td style="padding: 35px;">

    <p>Hola <strong>{safe_name}</strong>.</p>

    <p>Gracias por registrarte en CitaFácil.</p>

    <p>Para verificar tu correo electrónico,
       presiona el siguiente botón:</p>

    <p style="text-align: center;">

        <a href="{safe_url}" style="
            display: inline-block;
            padding: 14px 24px;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 6px;
        ">
            Verificar mi correo
        </a>

    </p>

    <p>Este enlace es temporal.</p>

    <p>Si no realizaste este registro,
       puedes ignorar este mensaje.</p>

</td>
</tr>

<tr>
<td style="
    padding: 20px;
    text-align: center;
    background: #f9fafb;
">
    <p>Equipo CitaFácil</p>
</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""

    return _send_email(
        to_email=to_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content
    )


# =====================================================
# RECUPERACIÓN DE CONTRASEÑA
# =====================================================

def send_password_reset_email(to_email, user_name, reset_token):
    """
    Envía un enlace temporal para restablecer la contraseña.
    """

    reset_url = (
        f"{FRONTEND_URL}/reset-password?"
        f"{urlencode({'token': reset_token})}"
    )

    safe_name = escape(user_name)
    safe_url = escape(reset_url, quote=True)

    subject = "Recuperación de contraseña - CitaFácil"

    text_content = f"""
Hola {user_name}.

Recibimos una solicitud para restablecer la contraseña
de tu cuenta de CitaFácil.

Para crear una nueva contraseña, ingresa al siguiente enlace:

{reset_url}

Este enlace es temporal y solamente puede utilizarse una vez.

Si no solicitaste recuperar tu contraseña,
puedes ignorar este mensaje.

Saludos,
Equipo CitaFácil
"""

    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Recuperación de contraseña</title>
</head>

<body style="
    margin: 0;
    padding: 30px;
    background: #f3f4f6;
    font-family: Arial, sans-serif;
">

<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0"
       style="background: #ffffff; border-radius: 10px;">

<tr>
<td style="
    padding: 30px;
    text-align: center;
    background: #2563eb;
    color: white;
">
    <h1>CitaFácil</h1>
    <p>Recuperación de contraseña</p>
</td>
</tr>

<tr>
<td style="padding: 35px;">

    <p>Hola <strong>{safe_name}</strong>.</p>

    <p>Recibimos una solicitud para restablecer
       la contraseña de tu cuenta de CitaFácil.</p>

    <p>Para crear una nueva contraseña,
       presiona el siguiente botón:</p>

    <p style="text-align: center;">

        <a href="{safe_url}" style="
            display: inline-block;
            padding: 14px 24px;
            background: #2563eb;
            color: white;
            text-decoration: none;
            border-radius: 6px;
        ">
            Restablecer contraseña
        </a>

    </p>

    <p>Este enlace es temporal y solamente
       puede utilizarse una vez.</p>

    <p>Si no solicitaste recuperar tu contraseña,
       puedes ignorar este mensaje.</p>

</td>
</tr>

<tr>
<td style="
    padding: 20px;
    text-align: center;
    background: #f9fafb;
">
    <p>Equipo CitaFácil</p>
</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
"""

    return _send_email(
        to_email=to_email,
        subject=subject,
        text_content=text_content,
        html_content=html_content
    )
