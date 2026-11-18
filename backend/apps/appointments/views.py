
from flask import jsonify, request

from apps.appointments import services

from apps.establishment.views import (
    obtener_establecimiento_autenticado
)


# =====================================================
# RESPUESTA HTTP
# =====================================================

def respuesta_http(
    resultado,
    codigo_exito=200,
    codigo_error=400
):
    """Convierte la respuesta del servicio en una respuesta HTTP."""

    if not isinstance(resultado, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Error interno al procesar la solicitud.",
            "data": None,
            "errores": {}
        }), 500

    codigo = (
        codigo_exito
        if resultado.get("ok")
        else codigo_error
    )

    return jsonify(resultado), codigo


# =====================================================
# OBTENER ID DEL ESTABLECIMIENTO AUTENTICADO
# =====================================================

def obtener_id_establecimiento():

    establecimiento, error = obtener_establecimiento_autenticado()

    if error:
        return None, error

    if not establecimiento:
        return None, (jsonify({
            "ok": False,
            "mensaje": "No se encontró el establecimiento autenticado."
        }), 401)

    id_establecimiento = establecimiento.get("id_establecimiento")

    if not id_establecimiento:
        return None, (jsonify({
            "ok": False,
            "mensaje": "No fue posible identificar el establecimiento."
        }), 401)

    return id_establecimiento, None


# =====================================================
# VALIDAR IDENTIFICADOR
# =====================================================

def validar_id(valor):
    """Comprueba que un identificador sea un entero positivo."""

    try:
        if isinstance(valor, bool):
            return False

        numero = int(valor)

        return numero > 0 and str(numero) == str(valor).strip()

    except (ValueError, TypeError):
        return False


# =====================================================
# LISTAR CITAS
# =====================================================

def listar_citas():

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    fecha_desde = request.args.get("fecha_desde")
    fecha_hasta = request.args.get("fecha_hasta")
    estado = request.args.get("estado")

    resultado = services.listar_citas(
        id_establecimiento,
        fecha_desde,
        fecha_hasta,
        estado
    )

    return respuesta_http(resultado)


# =====================================================
# CONSULTAR PRÓXIMAS CITAS
# =====================================================

def listar_proximas_citas():
    """Obtiene las próximas citas del establecimiento."""

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    if not id_establecimiento:
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible identificar el establecimiento.",
            "data": None,
            "errores": {}
        }), 401

    limite = request.args.get("limite", default=5, type=int)

    if limite is None or limite < 1 or limite > 50:
        return jsonify({
            "ok": False,
            "mensaje": "El límite debe estar entre 1 y 50.",
            "data": None,
            "errores": {
                "limite": "Introduce un límite válido."
            }
        }), 400

    resultado = services.listar_proximas_citas(
        id_establecimiento,
        limite
    )

    return respuesta_http(resultado)


# =====================================================
# CONSULTAR UNA CITA
# =====================================================

def consultar_cita(id_cita):
    """Consulta una cita específica."""

    if not validar_id(id_cita):
        return jsonify({
            "ok": False,
            "mensaje": "El identificador de la cita no es válido.",
            "data": None,
            "errores": {}
        }), 400

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    if not id_establecimiento:
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible identificar el establecimiento.",
            "data": None,
            "errores": {}
        }), 401

    resultado = services.consultar_cita(
        int(id_cita),
        id_establecimiento
    )

    return respuesta_http(resultado, codigo_error=404)


# =====================================================
# REGISTRAR CITA
# =====================================================


def registrar_cita():
    """Registra una nueva cita."""

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Debes enviar un objeto JSON válido.",
            "data": None,
            "errores": {}
        }), 400

    resultado = services.registrar_cita(
        datos,
        id_establecimiento
    )

    return respuesta_http(resultado, codigo_exito=201)



# =====================================================
# ACTUALIZAR CITA
# =====================================================

def actualizar_cita(id_cita):
    """Actualiza una cita existente."""

    if not validar_id(id_cita):
        return jsonify({
            "ok": False,
            "mensaje": "El identificador de la cita no es válido.",
            "data": None,
            "errores": {}
        }), 400

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Debes enviar un objeto JSON válido.",
            "data": None,
            "errores": {}
        }), 400

    resultado = services.actualizar_cita(
        int(id_cita),
        datos,
        id_establecimiento
    )

    return respuesta_http(resultado, codigo_error=400)


# =====================================================
# CAMBIAR ESTADO DE UNA CITA
# =====================================================

def cambiar_estado_cita(id_cita):
    """Actualiza el estado de una cita."""

    if not validar_id(id_cita):
        return jsonify({
            "ok": False,
            "mensaje": "El identificador de la cita no es válido.",
            "data": None,
            "errores": {}
        }), 400

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error
    
    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Debes enviar un objeto JSON válido.",
            "data": None,
            "errores": {}
        }), 400

    resultado = services.cambiar_estado_cita(
        int(id_cita),
        datos,
        id_establecimiento
    )

    return respuesta_http(resultado)


