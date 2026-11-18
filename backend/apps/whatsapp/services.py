import requests

from config import settings

# =====================================================
# CONFIGURACIÓN
# =====================================================

WHATSAPP_ACCESS_TOKEN = settings.WHATSAPP_ACCESS_TOKEN

WHATSAPP_PHONE_NUMBER_ID = settings.WHATSAPP_PHONE_NUMBER_ID

WHATSAPP_API_VERSION = settings.WHATSAPP_API_VERSION


# =====================================================
# ENVÍO DE MENSAJES
# =====================================================

def enviar_mensaje_whatsapp(
    destinatario,
    contenido,
    phone_number_id=None
):
    """
    Envía un mensaje de texto mediante WhatsApp Cloud API.
    """

    token = WHATSAPP_ACCESS_TOKEN

    numero_id = (
        phone_number_id
        or WHATSAPP_PHONE_NUMBER_ID
    )

    if not token:
        return {
            "ok": False,
            "error": "Token de acceso no configurado."
        }

    if not numero_id:
        return {
            "ok": False,
            "error": "Phone Number ID no configurado."
        }

    if not destinatario or not contenido:
        return {
            "ok": False,
            "error": "Destinatario y contenido son obligatorios."
        }

    url = (
        f"https://graph.facebook.com/"
        f"{WHATSAPP_API_VERSION}/"
        f"{numero_id}/messages"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": str(destinatario),
        "type": "text",
        "text": {
            "preview_url": False,
            "body": str(contenido)
        }
    }

    try:
        respuesta = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=20
        )

        try:
            datos = respuesta.json()
        except ValueError:
            datos = {}

        if respuesta.ok:
            return {
                "ok": True,
                "datos": datos
            }

        error_meta = datos.get("error", {})

        if isinstance(error_meta, dict):
            mensaje_error = error_meta.get(
                "message",
                "Meta rechazó el envío del mensaje."
            )
            codigo_error = error_meta.get("code")
        else:
            mensaje_error = "Meta rechazó el envío del mensaje."
            codigo_error = None

        return {
            "ok": False,
            "error": mensaje_error,
            "codigo_error": codigo_error
        }

    except requests.RequestException:
        return {
            "ok": False,
            "error": "No fue posible conectar con WhatsApp."
        }

    except Exception:
        return {
            "ok": False,
            "error": "Ocurrió un error inesperado al enviar el mensaje."
        }