
from flask import jsonify, request

from apps.establishment import services
from apps.authentication import services as auth_services


# =====================================================
# RESPUESTA HTTP
# =====================================================

def respuesta_http(resultado, codigo_exito=200, codigo_error=400):
    """Convierte la respuesta del servicio en una respuesta HTTP."""

    if not isinstance(resultado, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Error interno al procesar la solicitud.",
            "data": None,
            "errores": {}
        }), 500

    codigo = codigo_exito if resultado.get("ok") else codigo_error

    return jsonify(resultado), codigo


# =====================================================
# OBTENER ESTABLECIMIENTO AUTENTICADO
# =====================================================

def obtener_establecimiento_autenticado():
    """Valida que la sesión corresponda a un establecimiento."""

    token = request.cookies.get("access_token")

    if not token:
        return None, (jsonify({
            "ok": False,
            "mensaje": "Debes iniciar sesión."
        }), 401)

    try:
        resultado = auth_services.validar_sesion(token)

    except Exception:
        return None, (jsonify({
            "ok": False,
            "mensaje": "No fue posible verificar la sesión."
        }), 500)

    if not isinstance(resultado, dict) or not resultado.get("ok"):
        return None, (jsonify({
            "ok": False,
            "mensaje": "La sesión no es válida o ha expirado."
        }), 401)

    data = resultado.get("data") or {}

    if data.get("tipo_cuenta") != "establecimiento":
        return None, (jsonify({
            "ok": False,
            "mensaje": "Esta operación requiere una cuenta de establecimiento."
        }), 403)

    establecimiento = data.get("establecimiento")

    if not isinstance(establecimiento, dict):
        return None, (jsonify({
            "ok": False,
            "mensaje": "No fue posible identificar el establecimiento."
        }), 401)

    return establecimiento, None


# =====================================================
# REGISTRAR ESTABLECIMIENTO
# =====================================================

def registrar_establecimiento():
    """Registra un establecimiento y solicita verificar su correo."""

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Debes enviar datos válidos.",
            "data": None,
            "errores": {}
        }), 400

    try:
        resultado = services.registrar_establecimiento(datos)

        return respuesta_http(
            resultado,
            codigo_exito=201,
            codigo_error=400
        )

    except Exception:
        return jsonify({
            "ok": False,
            "mensaje": "Ocurrió un error interno al registrar el establecimiento.",
            "data": None,
            "errores": {}
        }), 500


# =====================================================
# OBTENER ESTABLECIMIENTO POR ID
# =====================================================

def obtener_establecimiento(id_establecimiento):
    """Permite consultar únicamente el establecimiento autenticado."""

    establecimiento, error = obtener_establecimiento_autenticado()

    if error:
        return error

    if str(establecimiento.get("id_establecimiento")) != str(id_establecimiento):
        return jsonify({
            "ok": False,
            "mensaje": "No puedes consultar información de otro establecimiento."
        }), 403

    try:
        resultado = services.obtener_establecimiento(
            id_establecimiento
        )

        return respuesta_http(
            resultado,
            codigo_exito=200,
            codigo_error=404
        )

    except Exception:
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible consultar el establecimiento."
        }), 500


# =====================================================
# LISTAR ESTABLECIMIENTOS DISPONIBLES PARA CLIENTES
# =====================================================

def listar_establecimientos_disponibles():
    """Lista establecimientos disponibles para reservar."""

    try:
        resultado = services.listar_establecimientos_disponibles()

        return respuesta_http(
            resultado,
            codigo_exito=200,
            codigo_error=500
        )

    except Exception:
        return jsonify({
            "ok": False,
            "mensaje": (
                "No fue posible consultar los establecimientos."
            ),
            "data": None,
            "errores": {}
        }), 500


