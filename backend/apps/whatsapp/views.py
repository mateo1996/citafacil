from config import settings

from collections import OrderedDict
from threading import Lock

from flask import Blueprint, request, jsonify

from apps.establishment.repositories import (
    obtener_establecimiento_por_whatsapp_phone_id
)

from apps.whatsapp.services import enviar_mensaje_whatsapp

from apps.whatsapp.conversation import procesar_mensaje


# =====================================================
# CONFIGURACIÓN
# =====================================================

WHATSAPP_VERIFY_TOKEN = settings.WHATSAPP_VERIFY_TOKEN

MENSAJE_TIPO_NO_ADMITIDO = (
    "Por el momento, CitaFácil solo puede procesar "
    "mensajes de texto. Por favor, envía tu solicitud "
    "escribiendo un mensaje."
)


# =====================================================
# BLUEPRINT
# =====================================================

whatsapp_bp = Blueprint(
    "whatsapp",
    __name__,
    url_prefix="/api/whatsapp"
)


# =====================================================
# CONTROL DE MENSAJES DUPLICADOS
# =====================================================

mensajes_procesados = OrderedDict()

mensajes_en_proceso = set()

bloqueo_mensajes = Lock()

MAX_MENSAJES_PROCESADOS = 10000


def reservar_mensaje_para_procesar(id_mensaje):

    if not id_mensaje:
        return False

    with bloqueo_mensajes:

        if id_mensaje in mensajes_procesados:
            return False

        if id_mensaje in mensajes_en_proceso:
            return False

        mensajes_en_proceso.add(id_mensaje)

        return True


def liberar_mensaje_en_proceso(id_mensaje):

    if not id_mensaje:
        return

    with bloqueo_mensajes:

        mensajes_en_proceso.discard(id_mensaje)


def registrar_mensaje_procesado(id_mensaje):

    if not id_mensaje:
        return

    with bloqueo_mensajes:

        mensajes_en_proceso.discard(id_mensaje)

        mensajes_procesados[id_mensaje] = True

        mensajes_procesados.move_to_end(id_mensaje)

        if len(mensajes_procesados) > MAX_MENSAJES_PROCESADOS:

            mensajes_procesados.popitem(last=False)


def mensaje_ya_procesado(id_mensaje):

    if not id_mensaje:
        return False

    with bloqueo_mensajes:

        return id_mensaje in mensajes_procesados


# =====================================================
# VERIFICACIÓN DEL WEBHOOK
# =====================================================

@whatsapp_bp.route("/webhook", methods=["GET"])
def verificar_webhook():

    modo = request.args.get("hub.mode")

    token = request.args.get("hub.verify_token")

    challenge = request.args.get("hub.challenge")

    if (
        modo == "subscribe"
        and token
        and token == WHATSAPP_VERIFY_TOKEN
        and challenge
    ):

        return challenge, 200

    return jsonify({
        "ok": False,
        "mensaje": "No se pudo verificar el webhook."
    }), 403


# =====================================================
# EXTRAER MENSAJES DEL WEBHOOK
# =====================================================

def extraer_mensajes(datos):

    mensajes_extraidos = []

    entradas = datos.get("entry", [])

    if not isinstance(entradas, list):
        return mensajes_extraidos

    for entrada in entradas:

        if not isinstance(entrada, dict):
            continue

        cambios = entrada.get("changes", [])

        if not isinstance(cambios, list):
            continue

        for cambio in cambios:

            if not isinstance(cambio, dict):
                continue

            if cambio.get("field") != "messages":
                continue

            valor = cambio.get("value", {})

            if not isinstance(valor, dict):
                continue

            metadata = valor.get("metadata", {})

            if not isinstance(metadata, dict):
                metadata = {}

            phone_number_id = metadata.get(
                "phone_number_id"
            )

            mensajes = valor.get("messages", [])

            if not isinstance(mensajes, list):
                continue

            for mensaje in mensajes:

                if not isinstance(mensaje, dict):
                    continue

                texto = mensaje.get("text", {})

                if not isinstance(texto, dict):
                    texto = {}

                mensajes_extraidos.append({

                    "phone_number_id": phone_number_id,

                    "id_mensaje": mensaje.get("id"),

                    "remitente": mensaje.get("from"),

                    "tipo": mensaje.get("type"),

                    "contenido": (
                        texto.get("body")
                        if mensaje.get("type") == "text"
                        else None
                    )

                })

    return mensajes_extraidos


# =====================================================
# IDENTIFICAR ESTABLECIMIENTO
# =====================================================

def identificar_establecimiento(phone_number_id):

    if not phone_number_id:
        return None

    establecimiento = (
        obtener_establecimiento_por_whatsapp_phone_id(
            phone_number_id
        )
    )

    if not establecimiento:
        return None

    if not establecimiento.get("estado"):
        return None

    return establecimiento


# =====================================================
# ENVIAR MENSAJE DE WHATSAPP
# =====================================================

def enviar_respuesta_whatsapp(
    destinatario,
    contenido,
    phone_number_id
):

    if not destinatario or not contenido:
        return False

    resultado = enviar_mensaje_whatsapp(
        destinatario=destinatario,
        contenido=contenido,
        phone_number_id=phone_number_id
    )
    
    if not isinstance(resultado, dict) or not resultado.get("ok"):
        print(
            "Error de envío WhatsApp:",
            resultado.get("error", "Respuesta inválida")
            if isinstance(resultado, dict)
            else "Resultado inválido"
        )

        if isinstance(resultado, dict):
            print(
                "Código de error Meta:",
                resultado.get("codigo_error")
            )

    return bool(
        isinstance(resultado, dict)
        and resultado.get("ok")
    )


# =====================================================
# PROCESAR MENSAJES DE TEXTO
# =====================================================

def procesar_mensaje_texto(
    mensaje,
    id_establecimiento
):

    remitente = mensaje.get("remitente")

    contenido = mensaje.get("contenido")

    phone_number_id = mensaje.get("phone_number_id")

    if not remitente:

        return {
            "ok": False,
            "procesado": False
        }

    resultado = procesar_mensaje(
        remitente=remitente,
        id_establecimiento=id_establecimiento,
        mensaje=contenido or ""
    )

    if not isinstance(resultado, dict):

        return {
            "ok": False,
            "procesado": False
        }

    respuesta = resultado.get("mensaje")

    if not respuesta:

        return {
            "ok": False,
            "procesado": True
        }

    enviado = enviar_respuesta_whatsapp(
        destinatario=remitente,
        contenido=respuesta,
        phone_number_id=phone_number_id
    )

    if enviado:

        print(
            "Respuesta conversacional enviada correctamente."
        )

    else:

        print(
            "No fue posible enviar la respuesta conversacional."
        )

    return {
        "ok": enviado,
        "procesado": True
    }


# =====================================================
# PROCESAR MENSAJES QUE NO SON DE TEXTO
# =====================================================

def procesar_mensaje_no_admitido(mensaje):

    remitente = mensaje.get("remitente")

    phone_number_id = mensaje.get("phone_number_id")

    if not remitente:

        return {
            "ok": False,
            "procesado": False
        }

    enviado = enviar_respuesta_whatsapp(
        destinatario=remitente,
        contenido=MENSAJE_TIPO_NO_ADMITIDO,
        phone_number_id=phone_number_id
    )

    if enviado:

        print(
            "Aviso de tipo de mensaje no admitido enviado."
        )

    else:

        print(
            "No fue posible enviar el aviso de tipo de mensaje."
        )

    return {
        "ok": enviado,
        "procesado": enviado
    }


# =====================================================
# PROCESAR NOTIFICACIÓN INDIVIDUAL
# =====================================================

def procesar_notificacion_whatsapp(
    mensaje,
    id_establecimiento
):

    if mensaje.get("tipo") == "text":

        return procesar_mensaje_texto(
            mensaje,
            id_establecimiento
        )

    return procesar_mensaje_no_admitido(mensaje)


# =====================================================
# RECEPCIÓN DE NOTIFICACIONES
# =====================================================

@whatsapp_bp.route("/webhook", methods=["POST"])
def recibir_webhook():

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):

        return jsonify({
            "ok": False,
            "mensaje": "El cuerpo de la solicitud no es válido."
        }), 400

    mensajes = extraer_mensajes(datos)

    print("Notificación de WhatsApp recibida.")

    print(
        "Cantidad de mensajes:",
        len(mensajes)
    )

    for mensaje in mensajes:

        id_mensaje = mensaje.get("id_mensaje")

        try:

            establecimiento = identificar_establecimiento(
                mensaje.get("phone_number_id")
            )

            if establecimiento is None:

                print(
                    "Mensaje recibido desde un número "
                    "de WhatsApp no asociado a un establecimiento."
                )

                continue

            if not id_mensaje:

                print(
                    "Mensaje ignorado porque no contiene "
                    "un identificador."
                )

                continue

            if not reservar_mensaje_para_procesar(id_mensaje):

                print(
                    "Mensaje duplicado o en proceso ignorado:",
                    id_mensaje
                )

                continue

            try:

                resultado = procesar_notificacion_whatsapp(
                    mensaje=mensaje,
                    id_establecimiento=(
                        establecimiento["id_establecimiento"]
                    )
                )

                if resultado.get("procesado"):

                    registrar_mensaje_procesado(
                        id_mensaje
                    )

                else:

                    liberar_mensaje_en_proceso(
                        id_mensaje
                    )

            except Exception:

                liberar_mensaje_en_proceso(
                    id_mensaje
                )

                raise

        except Exception as error:

            print(
                "Error al procesar la notificación de WhatsApp:",
                str(error)
            )

    return jsonify({
        "ok": True,
        "mensaje": "Notificación recibida correctamente.",
        "cantidad_mensajes": len(mensajes)
    }), 200