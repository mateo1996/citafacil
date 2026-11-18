
from flask import jsonify, request

from apps.schedules import services
from apps.establishment.views import obtener_establecimiento_autenticado


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
# OBTENER ID DEL ESTABLECIMIENTO AUTENTICADO
# =====================================================

def obtener_id_establecimiento():
    """Obtiene el identificador del establecimiento autenticado."""

    establecimiento, error = obtener_establecimiento_autenticado()

    if error:
        return None, error

    id_establecimiento = establecimiento.get("id_establecimiento")

    if not id_establecimiento:
        return None, (jsonify({
            "ok": False,
            "mensaje": "No fue posible identificar el establecimiento."
        }), 401)

    return id_establecimiento, None


# =====================================================
# LISTAR HORARIOS
# =====================================================

def listar_horarios():
    """Lista los horarios del establecimiento autenticado."""

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    try:
        resultado = services.obtener_horarios(
            id_establecimiento
        )

        return respuesta_http(
            resultado,
            codigo_exito=200,
            codigo_error=400
        )

    except Exception:
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible consultar los horarios.",
            "data": None,
            "errores": {}
        }), 500


# =====================================================
# OBTENER HORARIO POR ID
# =====================================================

def obtener_horario(id_horario):
    """Consulta un horario del establecimiento autenticado."""

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    try:
        resultado = services.obtener_horario(
            id_horario,
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
            "mensaje": "No fue posible consultar el horario.",
            "data": None,
            "errores": {}
        }), 500


# =====================================================
# REGISTRAR HORARIO
# =====================================================

def registrar_horario():
    """Registra un horario para el establecimiento autenticado."""

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Debes enviar datos válidos.",
            "data": None,
            "errores": {}
        }), 400

    try:
        resultado = services.registrar_horario(
            id_establecimiento,
            datos
        )

        return respuesta_http(
            resultado,
            codigo_exito=201,
            codigo_error=400
        )

    except Exception:
        return jsonify({
            "ok": False,
            "mensaje": "Ocurrió un error interno al registrar el horario.",
            "data": None,
            "errores": {}
        }), 500


# =====================================================
# ACTUALIZAR HORARIO
# =====================================================

def actualizar_horario(id_horario):
    """Actualiza un horario del establecimiento autenticado."""

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict):
        return jsonify({
            "ok": False,
            "mensaje": "Debes enviar datos válidos.",
            "data": None,
            "errores": {}
        }), 400

    try:
        resultado = services.actualizar_horario(
            id_horario,
            id_establecimiento,
            datos
        )

        return respuesta_http(
            resultado,
            codigo_exito=200,
            codigo_error=404
            if not resultado.get("ok")
            and "no existe" in resultado.get("mensaje", "").lower()
            else 400
        )

    except Exception:
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible actualizar el horario.",
            "data": None,
            "errores": {}
        }), 500


# =====================================================
# CAMBIAR ESTADO DEL HORARIO
# =====================================================

def cambiar_estado_horario(id_horario):
    """Activa o desactiva el horario de un día."""

    id_establecimiento, error = obtener_id_establecimiento()

    if error:
        return error

    datos = request.get_json(silent=True)

    if not isinstance(datos, dict) or "estado" not in datos:
        return jsonify({
            "ok": False,
            "mensaje": "Debes indicar el estado del horario.",
            "data": None,
            "errores": {
                "estado": "Este campo es obligatorio."
            }
        }), 400

    try:
        resultado = services.cambiar_estado_horario(
            id_horario,
            id_establecimiento,
            datos["estado"]
        )

        return respuesta_http(
            resultado,
            codigo_exito=200,
            codigo_error=404
            if not resultado.get("ok")
            and "no existe" in resultado.get("mensaje", "").lower()
            else 400
        )

    except Exception:
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible cambiar el estado del horario.",
            "data": None,
            "errores": {}
        }), 500


# =====================================================
# LISTAR HORARIOS DISPONIBLES PARA CLIENTES
# =====================================================

def listar_horarios_disponibles(id_establecimiento):
    """Lista los horarios activos de un establecimiento."""

    try:
        resultado = services.obtener_horarios_activos(
            id_establecimiento
        )

        return respuesta_http(
            resultado,
            codigo_exito=200,
            codigo_error=400
        )

    except Exception:
        return jsonify({
            "ok": False,
            "mensaje": "No fue posible consultar los horarios disponibles.",
            "data": None,
            "errores": {}
        }), 500